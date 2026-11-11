# `nlm` CLI 生产调度、容错对账与提示词工程

面向无人值守或半自动批量生产的 NotebookLM 调度体系。核心目标：**永不重复消费配额、多账号互不污染、单点失败不拖垮全队列、结果可追溯可恢复**。

---

## 1. 禁用内部自动重试（防止重复扣配额）

`nlm` CLI（`notebooklm_tools`）内置的网络/RPC 重试机制在超时或瞬时报错时可能重发一次已被服务端接收的请求，导致**同一条目在远端生成多套重复幻灯片**并白白消耗配额。

**生产环境标准做法**：对所有写操作子命令（`slides create`、`studio retry`、`studio failure-info`、`notebook create`、`source add`）通过包装入口关闭自动重试：

```python
import os, sys
os.environ['NOTEBOOKLM_RATE_LIMIT_MAX_RETRIES'] = '0'
import notebooklm_tools.core.base as base
base.DEFAULT_MAX_RETRIES = 0
from notebooklm_tools.cli.main import cli_main
sys.exit(cli_main())
```

同时在父进程调用 `subprocess.run` 时也传入 `NOTEBOOKLM_RATE_LIMIT_MAX_RETRIES='0'`。

---

## 2. 多账号隔离与代理环境

### 严禁切换全局默认账号
- 不要运行切换全局默认配置状态的命令去来回切账号；并发或交替运行时会产生竞态覆盖。
- 每次调用显式指定 `--profile <profile_name>`，并在子进程环境注入 `NLM_PROFILE=<profile_name>`。

### 状态与队列隔离
- 主账号写入 `state/progress.json`，附加账号写入独立文件 `state/accounts/<profile>.json`，各自维护独立的 `notebooks`、`source_id`、`artifact_id`、`failed_artifact_ids`、`generation_cooldown_until` 与 `attempts`。
- 为附加账号划定明确的任务归属（如特定系列列表或显式 `delegated_profile`），主调度器默认跳过已委派条目，同步层仅将最终 `complete` 成果合并回主进度。
- **跨账号去重（`superseded`）**：若条目已由另一账号或手动完成，将当前账号的未完成记录标记为 `superseded`（保留历史 `artifact_id` 供追溯），严禁重复制作。

### macOS 代理自动透传
若环境中未显式设置 `HTTP_PROXY` / `HTTPS_PROXY`，可在构建 `env` 时探测 `scutil --proxy`（检查 `HTTPSEnable : 1`，提取 `HTTPSProxy` 与 `HTTPSPort`）按需注入，避免无代理超时与硬编码端口。

---

## 3. 提交前持久化 + `--focus` 标识对账协议

遇到网络抖动、CLI 进程被中断或返回值模糊时，按以下 4 步确保**幂等恢复**：

1. **唯一追踪标识**：在 `--focus` 最开头写入条目唯一 ID（如 `标识 <item_id>。...`），方便在 `studio status` 返回的 JSON 中精准定位对应的远端任务（同时结合 `source_ids` 匹配）。
2. **先落盘再调用**：持写锁将本条状态置为 `slide_status = 'submitting'`、写入 `slide_submitted_at`、`last_slide_submission_at`（并在周期计划中登记 `attempted_slide_ids`），刷盘保存后再执行 `nlm slides create`。
3. **禁止对 `submitting` 状态直接重提**：若状态停留在 `submitting`（上次提交结局不明），系统必须拒绝自动重提，强制先运行 `nlm studio status <notebook_id> --json` 对账。
4. **先对账、后新建**：每次准备提交前，先检查同轮已拉取的 `artifacts` 缓存：
   - 若远端已有匹配 `<item_id>`（或 `source_id`）且非失败、非诊断用的产物（`completed` / `in_progress` / `queued`），直接接管其 `artifact_id` 并进入收集流程；
   - 仅当所有历史相关产物均为确认失败且已归档入 `failed_artifact_ids` 时，才允许发起新提交。
5. **隔离诊断产物**：排查问题时运行的测试生成产物必须记入 `diagnostic_artifact_ids` 与 `diagnostic_inflight`，所有正式收集与提交筛选逻辑一律过滤诊断 ID，严禁将测试产物发布上线。

---

## 4. 并发、节奏与退避参数（实测安全基线）

| 参数项 | 推荐值 | 工程原因 |
| --- | --- | --- |
| `max_concurrent_slides_per_account` | **10** | 单账号最多允许 10 个 `queued`/`submitting` 在途幻灯片任务 |
| `generation_interval_seconds` | **60s** | 同一账号两次 `slides create` 提交之间至少间隔 1 分钟 |
| `generation_initial_wait_seconds` | **1200s（20 分钟）** | 幻灯片生成耗时较长，提交后前 20 分钟内不查询该笔记本状态，不误判失败 |
| `poll_interval_seconds` | **300s（5 分钟）** | 超过初始窗口后，每轮轮询间隔 ≥ 5 分钟，且**每轮每个笔记本只查一次 `studio status`** |
| `request_interval_seconds` | **15s** | 同一进程内任意连续两次 `nlm` CLI 调用之间至少间隔 15 秒 |
| `single_episode_retry_interval_seconds` | **60s** | 单条出现偶发 `status=4` 失败时，仅该条退避 1 分钟，不阻塞同账号其余队列 |
| `failure_cooldown_seconds` | **18000s（5 小时）** | 明确遇到配额耗尽/429 时触发整账号 5 小时退避 |
| `max_attempts`（每日每阶段） | **3 次/天** | 同条同阶段当天最多尝试 3 次；跨天时将昨日计数归档到 `attempt_history` 并清零当日计数 |

### 并发轮询的关键边界细节
- **混合在途判定**：当同一笔记本内既有刚提交 3 分钟的任务、又有已提交超过 20 分钟的任务时，`notebook_check_due` 应检查**是否存在任意在途任务已满 20 分钟**（`any(not generation_waiting(r) for r in active)`），而不是被最新任务阻断全部轮询；但对于尚在 20 分钟保护窗内的新产物，即使列表里出现临时状态也不应提前判死。
- **历史失败不重算冷却**：对账时遇到已经在 `failed_artifact_ids` 中的旧失败 ID，直接清理挂起指针并置回 `retry_pending`，**绝不能**重新累加当日失败次数或重启冷却计时器。
- **手动重试观察期（`manual_retry_watch`）**：若用户手动在后台触发了重试，记录 `notebook_id` 与 `check_not_before`；在该时间前不查询该笔记本，核实结果前禁止自动新建重复任务。

---

## 5. 故障分类与防饥饿队列调度

### 区分两类完全不同的失败

1. **全账号限流 / 配额耗尽**（报错含 `Rate limited`、`RESOURCE_EXHAUSTED`、`429`）：
   - 若提示短时流控（如 `Wait 1-2 minutes` / `Wait a few minutes`），仅设置短暂停（如 `180s`）。
   - 若为额度耗尽，设置账号级 `generation_cooldown_until`（+5 小时或已知真实恢复时间）；若冷却长于本次运行剩余预算（`cooldown_outlasts_budget`），提前优雅退出等待下一周期。
2. **单条云端偶发失败**（产物状态 `failed` / `error` / `status=4`）：
   - **切忌冻结全账号**：将产物 ID 归档到 `failed_artifact_ids`，仅给该条目设 `next_slide_attempt_at`（+60s）并记 `attempts['slides'] += 1`，账号其余任务继续并发推进。
   - **原地重试优先（可选）**：对已确认 `status=4` 的幻灯片产物，若需保持同一个 `artifact_id`，可用扩展命令读取原产物设置（`steering_prompt`、`language`、`source_ids`、`slide_format`、`slide_length`）调用 `start_artifact_generation` 原地重启，避免生成过多孤儿产物。
   - **防顽固条目饿死新任务**：编制周期计划时，把历史失败次数过多（如 `len(failed_artifact_ids) >= 5`）的顽固条目排序放到正常条目之后（例如排序键 `(fail_count >= 5, not article_ready)`），优先保证新鲜条目与已有文字的条目获得配额。

---

## 6. 双锁模式与固定窗口周期编排

- **运行锁（`state/cycle.lock`）+ 写锁（`state/runner.lock`）分离**：
  - `cycle.lock` 覆盖整个调度周期，防止同一时间启动两个协调器；
  - `runner.lock` 仅在读写状态 JSON 与发起短同步操作时持有，**在 `paced_sleep` 等待 5 分钟期间必须释放**，让手动校对、文本预生产或其它轻量同步任务无需死锁等待；但**完整静态构建与线上部署不得与写生成并发**。
- **锚定周期（不因午夜重置）**：按配置 `cycle_anchor_at` 划分固定 5 小时窗口（如 `anchor#slot`），周期内目标列表（`slide_ids` / `article_ids`）与已尝试集合（`attempted_slide_ids`）落盘保存；同周期中断后重跑直接复用原目标，不追加新任务，不重复扣费。
- **文字优先、共用预算**：第一阶段跑 `--text-only` 并及时发布文字版；第二阶段共享同一总运行窗口（如 `150` 分钟，扣减已耗时）补齐幻灯片，避免慢速 PPT 拖累文字上线。

---

## 7. `detailed_deck` 与配套图文提示词公式

### 幻灯片生成命令与 `--focus` 模板

```bash
nlm slides create <notebook_id> \
  --source-ids <source_id> \
  --format detailed_deck \
  --length default \
  --language zh-CN \
  --focus "标识 <item_id>。用简体中文制作详细学习幻灯片，讲清本主题的背景、关键人物/概念、主要事件、时间线与因果机制。采用《丁丁历险记》漫画风格：黑色清晰轮廓、鲜明平涂色块、还原时代或场景细节并配简洁中文旁白。严格依据所选来源，不虚构人名、数字、日期或引语；不要把文件名或标识符写进幻灯片标题。" \
  --confirm --json
```

> 迁移到其他项目时，只需替换其中的美术风格片段（如改为“扁平矢量信息图”、“手绘工程草图”等），保留**详细讲清因果 + 语言锁定 + 唯一标识前缀 + 严格忠实来源 + 禁止泄露标识**五个骨架要素即可。

### 配套结构化长文（`notebook query`）要点

若同时需要为网页生成配套深度阅读文章：
1. 调用 `nlm notebook query <nb> <PROMPT> --source-ids <source_id> --new-conversation --timeout 240 --json`。
2. 要求输出可被 `json.loads` 直接解析的纯 JSON（禁止 Markdown 代码围栏和 `[1]` 引用标记），包含：`headline`、`dek`、`takeaways`、`sections`（每章附原文真实存在的 `MM:SS` 或 `HH:MM:SS` 时间戳）、`timeline`、`people`、`connections`、`mechanism`、`glossary`、`caveats`。
3. 代码层强制执行 `validate_article()`：校验必填字段、章节最低数量、时间戳正则 `\d{1,3}:\d{2}(?::\d{2})?`，以及 `connections` 的 `from` / `to` 必须全部存在于 `people` 集合中——直接拦截模型的图谱编造。
