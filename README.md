# HN Codex Skills

Personal Codex skills for recurring workflows.

## Bundled Skills

- `hn-windows-stability-doctor`: Windows crash, freeze, restart, disk, memory, driver, and stability diagnosis.
- `hn-tool-ui-polisher`: usability audit and polish for compact tool UIs.
- `hn-visual-asset-pipeline`: icons, screenshots, generated images, image conversion, and project-ready asset organization.
- `hn-xiaohei-draw`: Ian-style Chinese article illustrations with the Xiaohei astronaut IP.
- `hn-project-publisher`: end-to-end publish workflow: npm/git init, repo link, Umami analytics, bilingual README (<=500 chars) with mobile screenshot, QR code, Cloudflare domain, GitHub push, Pages deploy, and dual portfolio sync.
- `hn-chrome-extension-publisher`: audit, package, submit, and update Chrome extensions for the Chrome Web Store.
- `hn-ui-layout-typography-audit`: audit and build web/UI layouts using practical hierarchy, spacing, alignment, contrast, color, and typography checks.
- `hospital-record-collector`: capture Yueyang Hospital electronic invoices and medical records from WeChat, then save cropped screenshots to a user-selected folder.
- `hn-poem`: write four varied modern Chinese short poems using low-association juxtaposition and disciplined image construction.
- `hn-web-analytics`: add centralized Umami-based PV, UV, source, device, and custom event analytics to multiple websites.
- `hn-share-card`: turn a website result or project into a QR-enabled image share card with download and native-share fallbacks.

## Install With npx

Install all skills:

```bash
npx github:holynova/hn-codex-skills install
```

Install one skill:

```bash
npx github:holynova/hn-codex-skills install hn-project-publisher
npx github:holynova/hn-codex-skills install hn-windows-stability-doctor
npx github:holynova/hn-codex-skills install hn-tool-ui-polisher
npx github:holynova/hn-codex-skills install hn-visual-asset-pipeline
npx github:holynova/hn-codex-skills install hn-xiaohei-draw
npx github:holynova/hn-codex-skills install hn-chrome-extension-publisher
npx github:holynova/hn-codex-skills install hn-ui-layout-typography-audit
npx github:holynova/hn-codex-skills install hospital-record-collector
npx github:holynova/hn-codex-skills install hn-poem
npx github:holynova/hn-codex-skills install hn-web-analytics
npx github:holynova/hn-codex-skills install hn-share-card
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
Copy-Item -Recurse .\skills\hn-tool-ui-polisher $HOME\.codex\skills\
Copy-Item -Recurse .\skills\hn-visual-asset-pipeline $HOME\.codex\skills\
Copy-Item -Recurse .\skills\hn-xiaohei-draw $HOME\.codex\skills\
Copy-Item -Recurse .\skills\hn-project-publisher $HOME\.codex\skills\
Copy-Item -Recurse .\skills\hn-chrome-extension-publisher $HOME\.codex\skills\
Copy-Item -Recurse .\skills\hn-ui-layout-typography-audit $HOME\.codex\skills\
Copy-Item -Recurse .\skills\hospital-record-collector $HOME\.codex\skills\
Copy-Item -Recurse .\skills\hn-poem $HOME\.codex\skills\
Copy-Item -Recurse .\skills\hn-web-analytics $HOME\.codex\skills\
Copy-Item -Recurse .\skills\hn-share-card $HOME\.codex\skills\
```

## 中文说明

这是我的个人 Codex Skills 仓库，用来沉淀高频工作流，而不是把经验只留在某一次对话里。

- `hn-windows-stability-doctor`: 诊断 Windows 蓝屏、死机、重启、硬盘、内存、驱动和稳定性问题。
- `hn-tool-ui-polisher`: 审查和打磨工具型 UI，重点处理布局、控件分组、状态反馈、移动端和可用性。
- `hn-visual-asset-pipeline`: 生成、转换、整理并验证图标、截图、透明 PNG、README/商店素材等视觉资产。
- `hn-xiaohei-draw`: 为中文文章生成 Ian 风格、宇航员小黑 IP 的正文配图。
- `hn-project-publisher`: 完整项目发布流程：npm/Git 初始化、页面 Repo 链接与 Umami 埋点、简洁双语 README（各不超过 500 字，含有效内容延迟/移动端截图、二维码、Cloudflare 专属域名）、推送到 GitHub、Pages 部署及双作品集收录。
- `hn-chrome-extension-publisher`: 审计、整理、打包、提交和升级发布 Chrome Web Store 插件。
- `hn-ui-layout-typography-audit`: 用信息层级、分组、对齐、重复、对比、留白、色彩和字体检查来审查或创建网页与用户界面。
- `hospital-record-collector`: 在微信岳阳医院服务中按时间范围采集电子发票和电子病历截图，裁切后保存到用户指定文件夹。
- `hn-poem`: 使用低相关并置和四种意象构造方式，一次创作四首避免模板化重复的现代汉语短诗。
- `hn-web-analytics`: 为多个网站接入集中式 Umami PV、UV、来源、设备和自定义事件统计后台。
- `hn-share-card`: 将网站结果或整个项目生成带二维码的图片分享卡片，支持下载、复制链接和系统分享回退。

推荐安装方式：

```bash
npx github:holynova/hn-codex-skills install
```

默认安装到 `$CODEX_HOME/skills`；如果没有设置 `CODEX_HOME`，则安装到 `~/.codex/skills`。
