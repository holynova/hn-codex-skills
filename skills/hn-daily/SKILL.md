---
name: hn-daily
description: 每日一站式系统维护与 AI 盘点编排技能：按依赖编排并行与串行步骤，组合调用 hn-ai-software-update（更新 AI CLI、Mole 与软件）、hn-token-stats（近七日 Token 进度条统计）、hn-skills-sync（更新第三方与个人 GitHub skills）和 hn-clean（运行 mo clean 与 mo optimize 清理优化磁盘），支持分步即时输出、失败/超时快速跳过与带近7日图形化进度条的极简汇总。适用于每日维护、批量升级同步清理或统一日报汇报。
---

# HN 每日维护编排 (`hn-daily`)

通过有向无环图（DAG）编排调用四个独立子技能，默认开启**分步即时输出**（每步完成立刻吐出该步结果，不等全部跑完）与**失败/超时快速跳过**（每个步骤都有严格超时保护与进程组清理，失败或超时立即标记并放行后续步骤）。

## 并行与串行编排架构

```text
Stage 1 (并行) ──┬──► [1A] hn-ai-software-update  (内部按包管理器再并发；遇源码重编译自动跳过)
                 └──► [1B] hn-token-stats          (纯只读统计，约十余秒率先完成并立即输出)
                         │
                         ▼ (等待 1A 完成或跳过后立即启动)
Stage 2 (串行) ───────► [2]  hn-skills-sync        (更新第三方 skills + 同步个人 GitHub 仓库)
                         │
                         ▼ (等待 1A 新版 Mole、1B Token 与 2 同步全部结束)
Stage 3 (串行) ───────► [3]  hn-clean              (运行 mo clean + mo optimize，复测 df -k)
```

### 编排与快速失败机制

- **分步即时输出**：Stage 1 使用 `as_completed` 并发收集结果，`hn-token-stats` 跑完就立刻输出近 7 日进度条；随后软件更新、Skills 同步、磁盘清理每完成一步立即打印本步结论。
- **失败/超时即跳过（`mo clean` 给予长超时必跑保障）**：`mo clean` 为必跑步骤，单步超时设至 900s（`clean` 阶段总上限 1080s，其中 `mo optimize` 上限 90s）；其余阶段维持紧缩超时（默认 `update` 240s、`tokens` 45s、`skills` 180s）。所有外部子命令均通过独立进程组执行，超时立即 `SIGTERM/SIGKILL` 整组回收并标记 `skipped_timeout`，绝不卡死整套流程。

## 使用方式

```bash
# 1. 安全预览模式（默认仅 dry-run + 只读 Token 统计，分步即时输出）
python3 skills/hn-daily/scripts/hn_daily.py

# 2. 实际执行模式（更新软件 + 同步 skills + 执行 mo clean / mo optimize + 极简汇总）
python3 skills/hn-daily/scripts/hn_daily.py --apply

# 3. 常用选项：过滤阶段 / 仅输出最终汇总 / 保存报告 / JSON 输出
python3 skills/hn-daily/scripts/hn_daily.py --apply --only "tokens,clean"
python3 skills/hn-daily/scripts/hn_daily.py --apply --skip "clean" --no-stream
python3 skills/hn-daily/scripts/hn_daily.py --apply --json --save-report ~/ai-daily-reports
```

## 终报格式规范（极简方案 C + 近 7 日图形化 Token 卡片）

全部步骤结束后，统一输出顶部 1 行 KPI 脉冲条 + 只列变化与异常的 3 条精简摘要 + 按需待办 + 完整近 7 日 `1/8` 刻度进度条卡片：

```markdown
### ✅ Daily 汇总｜YYYY-MM-DD（apply · 2m 10s）
**更新 12 项 · 同步 26 技能 · 可用空间 +5.62 GB（→ 23.18 GB）· 7日 2亿5,532万 Token**

- **软件（✅）**：升级 `mole` `cc-switch` ... · 48s
- **Skills（✅）**：第三方更新 18 项；个人库新增 ... · 32s
- **清理（⚠️）**：`mo clean` 清 `3.06GB`，可用 `17.56 → 23.18 GB`（**+5.62 GB**）；`mo optimize` 已应用 2 项 · 50s

> **待按需处理**：系统级优化需终端执行 `mo optimize`；大目录建议留存未删：`pnpm store` / `AI agent worktrees` / `Build artifacts`

📊 Codex Token｜近7日（11/19–11/25）
日期 | 进度条         | Token
11/19 | █▋░░░░░░░░░░ | 6,408万
...
7日累计：约 10亿7,585万 Token
注：含缓存，按1万取整；进度按周峰值，每格含1/8刻度。
```
