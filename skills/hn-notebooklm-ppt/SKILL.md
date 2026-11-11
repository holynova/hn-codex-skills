---
name: hn-notebooklm-ppt
description: 使用 NotebookLM CLI (nlm) 从长文、Markdown、逐字稿、播客音频、网页或视频批量生成高保真 PPT 幻灯片，并完成事实校对、PDF 矢量修补、原流高清晰 WebP 提取与极速 Web/PDF 交付。适用于搭建或修复 nlm 幻灯片批量生产管线、多账号并发与限流对账调度、detailed_deck 提示词工程、音视频转结构化来源，以及解决 Web 端 PDF.js 首屏卡顿与二次重采样模糊问题。
---

# HN NotebookLM PPT 生产与高清晰交付流水线

沉淀自大规模真实生产管线（数百套幻灯片、多账号并发调度、CDN 交付与画质重构）的完整工程规范。帮助任意项目把**长文、Markdown、网页、播客音频或视频**稳定转化为**事实严谨、画风统一、Web 秒开且画质锐利**的幻灯片与配套图文交付物。

> 本技能专注「素材入库 → `nlm` 生成调度 → 校对修补 → Web/PDF 交付」。站点域名上线与埋点分别复用 `hn-project-publisher` 与 `hn-web-analytics`。

---

## 核心工程铁律 (Non-Negotiable Invariants)

1. **一源一PPT，严格锁定 `--source-ids`**：每套幻灯片只绑定一份结构化来源，不让无关文档混入上下文。
2. **笔记本容量硬顶 ≤ 50 个来源**：单笔记本避免堆积 >50 个来源或 >80–100 个 Studio 产物；散篇按固定上限分桶（`单集组1..N`）并持久化分桶映射，防止笔记本臃肿触发服务端静默 `status=4` 失败。
3. **禁止 CLI 自动重试写操作**：对 `slides create`、`studio retry`、`source add`、`notebook create` 强制设置 `NOTEBOOKLM_RATE_LIMIT_MAX_RETRIES=0` 与 `DEFAULT_MAX_RETRIES=0`。提交前先持久化 `submitting` 状态，并在 `--focus` 中注入唯一追踪标识（`标识 <item_id>`）；超时或结果不明时必须先查 `studio status` 对账，禁止盲目重提交制造重复产物。
4. **多账号上下文绝对隔离**：使用 `--profile <name>` 与子进程环境变量 `NLM_PROFILE` 隔离凭证，严禁运行切换全局默认账号的命令；各账号独立保存笔记本 ID、来源 ID、产物 ID、冷却时间与每日尝试次数。
5. **故障分层退避，防止饥饿**：明确区分全账号限流（`429` / `RESOURCE_EXHAUSTED` → 5 小时冷却）与单条偶发失败（`status=4` → 仅单条退避 60 秒，日重试 ≤ 3 次）；累计多次失败的顽固条目降权排后，禁止阻塞队列中的新鲜任务。
6. **双锁不跨睡眠持有，文字与生成解耦**：本地写锁（`runner.lock`）仅在读写状态文件时短暂获取，等待轮询时必须释放；先整理并发布结构化文字，再推进幻灯片补齐，生成进程与构建部署顺序执行。
7. **非破坏性事实校对**：原始下载 PDF 永久保留在 `work/`（不进仓库或静态发布目录）；人名、日期、数字、引用边界与来源归属错误，用 `pypdf` + `reportlab` 矢量叠层覆盖修正，保留底层插画原貌。
8. **Web 端严禁 PDF.js 整包直出，也严禁 `pdftoppm` 二次重采样**：
   - CDN/代理剥离 `HTTP 206 Range` 会逼迫 PDF.js 每次下载 ~`1.7 MB` 运行时与 ~`9 MB` 整本 PDF（4G 首屏 9–22 秒）。改为构建期预拆每页为静态 WebP（`~200 KB/页`，首屏 30x–50x 提速至 `~200–600 ms`），原优化 PDF 仅用于下载按钮。
   - 对 1376px 栅格化 PDF 页面运行 `pdftoppm` 会造成约 20 dB 清晰度劣化。**纯图页直接提取 PDF 内嵌无损/原始图像流**，仅对含矢量校对叠层的页面使用 Poppler 2x 超采样（`2752px` → Lanczos 回缩），并用 `cwebp -q 90 -m 4 -sharp_yuv` 编码。

---

## 端到端工作流

### 阶段 1：多模态素材预处理与分片入库
读取 [references/input-ingestion.md](references/input-ingestion.md) 执行：
- **长文 / Markdown / 文档**：清洗导航与广告噪声；超长书籍或合集按逻辑章节拆分为独立来源。
- **网页 / YouTube 视频**：优先用 `nlm source add <nb> --url <url> --wait --json`；若遇防爬、无字幕或内容杂乱，降级为本地抽取文本/字幕再上传。
- **本地视频 / 播客音频**：提取音轨/字幕或使用 ASR（Whisper 等）转录为带 `[HH:MM:SS]`（或 `[MM:SS]`）时间戳的纯文本，去除片头混剪与口播广告，头部写入防幻觉提示与来源元信息。
- **笔记本路由与分桶**：系列专题各自独立建本；零散内容按 `≤ 50` 个来源分桶（`单集组1`, `单集组2`, ...），分组结果落盘固化（如 `state/queue.json`），不因后续新增条目导致旧条目跨本漂移。

### 阶段 2：`nlm` CLI 批量生产、对账与提示词工程
读取 [references/nlm-resilience-pipeline.md](references/nlm-resilience-pipeline.md) 执行：
- **非重试包装与代理透传**：通过包装脚本禁用内部 RPC 重试；macOS 下按需自动读取 `scutil --proxy` 注入 `HTTPS_PROXY`/`HTTP_PROXY`。
- **节奏与并发护栏**：
  - 单账号在途并发上限：`10` 个任务；提交间隔 `≥ 60s`。
  - 提交后首 `20 分钟`（`1200s`）内不查询该产物状态；之后每 `≥ 5 分钟`（`300s`）轮询一次，且每轮每个笔记本最多查一次 `studio status`。
  - 任意普通 `nlm` CLI 调用之间保持 `≥ 15s` 请求间隔。
  - 手动重试遵守 `manual_retry_watch.check_not_before`；诊断探针产物放入 `diagnostic_artifact_ids`，严禁当正式成品使用。
- **核心提示词模板**：使用 `--format detailed_deck --language zh-CN`，结合统一美术风格（如《丁丁历险记》黑色轮廓+平涂色块+时代场景）与严格忠实约束；若同步产出配套结构化文章，使用 `notebook query --new-conversation --json` 并经过严格 Schema 与时间戳/关系端点校验。

### 阶段 3：事实校对、画质无损化提取与 Web/PDF 交付
读取 [references/post-process-and-delivery.md](references/post-process-and-delivery.md) 执行：
- **下载校验与矢量修补**：检查 `%PDF-` 魔数与页数；人工复核封面归属、同音人名、年份金额与统计口径；在保留原始 PDF 于 `work/` 的前提下叠加透明文字框修补。
- **WebP 幻灯片高清晰提取（Solution 1）**：
  1. 用 `has_vector_overlay()` 检测每页是否含矢量文字或修改图层；
  2. **无叠层页面**：优先从 `work/<id>-uncompressed.pdf`（经 `64x36` 宏块差异校验确认与发布版一致）或发布版 PDF 的 `page.images[0].data` **直接提取原始图像流**，彻底跳过 Poppler 栅格重采样；
  3. **有矢量叠层页面**：用 `pdftoppm -scale-to 2752` 进行 2x 超采样后 Lanczos 缩放到目标像素尺寸；
  4. 统一通过 `cwebp -quiet -q 90 -m 4 -sharp_yuv` 输出，并以内容哈希 + 配方标签（如 `slides-v2:uncomp-q90-sharp`）缓存。
- **极速阅读器与比例全屏（Solution 4）**：
  - 前端使用 `<img id="slide-img" decoding="async">` + `N+1 / N+2` 异步预加载 + `slideRenderToken` 竞态隔离；PDF.js 仅保留作降级回退。
  - 容器按 16:9 横屏可用视口等比撑满（常规 `min(96%, ...)`，全屏 `min(98%, ...)`），提供双全屏回退（原生 Fullscreen API + `.is-fullscreen` 样式类）、键盘翻页、左右热区点击、移动端滑动与篇末同专题下一篇跳转。
- **章节插图与可下载 PDF**：抽取封面与代表性故事页（或人工选定的 `pages.json`）制作响应式缩略图；单独输出 Web 压缩 PDF（`JPEG q95 subsampling=0`，仅在体积更小时替换），且下载路径保持可再验证（不设 `immutable`），确保后续矢量校对能即时生效。

### 阶段 4：发布边界与端到端验收
- **安全边界**：`work/`、`state/`、原始逐字稿、本地路径、认证凭证与内部错误日志绝不进入 git 仓库或 `dist/`；静态资源单文件不超过部署平台限制（如 Cloudflare Workers Assets 25 MiB）。
- **状态分离**：`complete` 仅表示本地文字与幻灯片文件齐备；`publication_status = verified` 仅在真实 HTTPS 请求验证首页、专题、搜索、WebP 幻灯片、插图与 PDF 下载全部通过后才写入。

---

## 关键参数速查

| 类别 | 推荐参数 | 说明 |
| --- | --- | --- |
| 单本容量上限 | `≤ 50` 来源 / 本 | 超过后按 `单集组1..N` 固化分片 |
| 并发与提交间隔 | 最多 `10` 在途 / 账号，间隔 `60s` | 配合 `MAX_RETRIES=0` 防重复提交 |
| 状态轮询节奏 | 首等 `20 min`，后每 `5 min` | 每轮每本只查 1 次；普通 CLI 间隔 `≥ 15s` |
| 失败与限流退避 | `status=4` 单条等 `60s`（日上限 `3`）；`429` 冷却 `5h` | 多次失败条目排后，不饿死新任务 |
| WebP 幻灯片编码 | 原流直出 / 叠加页 `2752px` 2x，`cwebp -q 90 -sharp_yuv` | 单页约 `150–310 KB`，消除色度边缘模糊 |
| 缓存策略分离 | 内容哈希 WebP `immutable` 1 年；稳定 PDF URL 协商再验证 | 兼顾秒开与校对修补即时生效 |

---

## 参考文档导航

- [references/input-ingestion.md](references/input-ingestion.md)：文本、网页、YouTube/本地视频、播客音频的清洗、时间戳格式化、防幻觉头部与 `≤ 50` 来源分桶规范。
- [references/nlm-resilience-pipeline.md](references/nlm-resilience-pipeline.md)：`nlm_once` 非重试封装、多账号隔离、`runner.lock` 双锁模式、固定周期对账、故障退避与 `detailed_deck` 提示词模板。
- [references/post-process-and-delivery.md](references/post-process-and-delivery.md)：PDF 矢量校对修补、原流提取 vs 2x 超采样渲染算法、WebP 阅读器代码模式、全屏响应式 CSS 与上线校验。
