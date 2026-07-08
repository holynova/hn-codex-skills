# HN Codex Skills

Personal Codex skills for recurring workflows.

## Bundled Skills

- `hn-windows-stability-doctor`: Windows crash, freeze, restart, disk, memory, driver, and stability diagnosis.
- `hn-frontend-project-shipper`: frontend project polish, QA, docs, screenshots, GitHub, and release workflow.
- `hn-agent-workflow-productizer`: productize manual agent procedures into safe workflow systems.
- `hn-product-release-packager`: public release packaging for apps, Chrome extensions, GitHub Pages, docs, store materials, and release automation.
- `hn-tool-ui-polisher`: usability audit and polish for compact tool UIs.
- `hn-visual-asset-pipeline`: icons, screenshots, generated images, image conversion, and project-ready asset organization.
- `hn-opencli-batch-image-production`: reliable OpenCLI ChatGPT/Gemini batch image generation, validation, retries, mapping files, contact sheets, and zip delivery.
- `hn-data-to-github-pages-gallery`: turn structured data and image batches into searchable GitHub Pages galleries with batch switches and live verification.
- `hn-stateful-cron-report-pipeline`: build recurring reports with local state, deterministic comparisons, strict digest formats, and verified first runs.
- `hn-xiaohei-draw`: Ian-style Chinese article illustrations with the Xiaohei astronaut IP.

## Install With npx

Install all skills:

```bash
npx github:holynova/hn-codex-skills install
```

Install one skill:

```bash
npx github:holynova/hn-codex-skills install hn-frontend-project-shipper
npx github:holynova/hn-codex-skills install hn-agent-workflow-productizer
npx github:holynova/hn-codex-skills install hn-windows-stability-doctor
npx github:holynova/hn-codex-skills install hn-opencli-batch-image-production
npx github:holynova/hn-codex-skills install hn-data-to-github-pages-gallery
npx github:holynova/hn-codex-skills install hn-stateful-cron-report-pipeline
npx github:holynova/hn-codex-skills install hn-xiaohei-draw
```

Options:

```bash
npx github:holynova/hn-codex-skills install --force
npx github:holynova/hn-codex-skills install --path ~/.codex/skills
```

## Manual Install

Copy the wanted skill folder into your Codex skills directory:

```powershell
Copy-Item -Recurse .\skills\hn-windows-stability-doctor $HOME\.codex\skills\
Copy-Item -Recurse .\skills\hn-frontend-project-shipper $HOME\.codex\skills\
Copy-Item -Recurse .\skills\hn-agent-workflow-productizer $HOME\.codex\skills\
Copy-Item -Recurse .\skills\hn-product-release-packager $HOME\.codex\skills\
Copy-Item -Recurse .\skills\hn-tool-ui-polisher $HOME\.codex\skills\
Copy-Item -Recurse .\skills\hn-visual-asset-pipeline $HOME\.codex\skills\
Copy-Item -Recurse .\skills\hn-opencli-batch-image-production $HOME\.codex\skills\
Copy-Item -Recurse .\skills\hn-data-to-github-pages-gallery $HOME\.codex\skills\
Copy-Item -Recurse .\skills\hn-stateful-cron-report-pipeline $HOME\.codex\skills\
Copy-Item -Recurse .\skills\hn-xiaohei-draw $HOME\.codex\skills\
```

## 中文说明

这是我的个人 Codex Skills 仓库，用来沉淀高频工作流，而不是把经验只留在某一次对话里。

- `hn-windows-stability-doctor`: 诊断 Windows 蓝屏、死机、重启、硬盘、内存、驱动和稳定性问题。
- `hn-frontend-project-shipper`: 把前端项目从修改、调试、移动端 QA、截图、README 推进到发布。
- `hn-agent-workflow-productizer`: 把手工 agent 流程产品化，设计状态机、沙盒权限、验证点和失败恢复。
- `hn-product-release-packager`: 将小应用、Chrome 插件、GitHub Pages 项目整理成可发布包，包括文档、截图、图标、隐私页、商店材料和 release 自动化。
- `hn-tool-ui-polisher`: 审查和打磨工具型 UI，重点处理布局、控件分组、状态反馈、移动端和可用性。
- `hn-visual-asset-pipeline`: 生成、转换、整理并验证图标、截图、透明 PNG、README/商店素材等视觉资产。
- `hn-opencli-batch-image-production`: 用 OpenCLI 稳定批量生成 ChatGPT/Gemini 图片，处理重试、限流、补图、验图、重命名、映射表、contact sheet 和 zip 交付。
- `hn-data-to-github-pages-gallery`: 将结构化数据、抓取结果和图片批次发布成可搜索、可筛选、可切换批次的 GitHub Pages 图库/数据网站。
- `hn-stateful-cron-report-pipeline`: 构建带本地状态、历史对比、严格输出格式和首次验证的定时报告/监控任务。
- `hn-xiaohei-draw`: 为中文文章生成 Ian 风格、宇航员小黑 IP 的正文配图。

推荐安装方式：

```bash
npx github:holynova/hn-codex-skills install
```

默认安装到 `$CODEX_HOME/skills`；如果没有设置 `CODEX_HOME`，则安装到 `~/.codex/skills`。
