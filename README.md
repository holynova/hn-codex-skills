# HN Codex Skills

Personal Codex skills for recurring workflows:

- `hn-windows-stability-doctor`: Windows crash and instability diagnosis.
- `hn-frontend-project-shipper`: frontend project polish, QA, docs, and release workflow.
- `hn-agent-workflow-productizer`: productize manual agent procedures into safe workflow systems.
- `hn-product-release-packager`: public release packaging for apps, Chrome extensions, GitHub Pages, docs, store materials, and release automation.
- `hn-tool-ui-polisher`: usability audit and polish for compact tool UIs.
- `hn-visual-asset-pipeline`: icons, screenshots, generated images, image conversion, and project-ready asset organization.

## Install With npx

Install all skills:

```bash
npx github:holynova/hn-codex-skills install
```

Install one skill:

```bash
npx github:holynova/hn-codex-skills install hn-frontend-project-shipper
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
```

## 中文说明

这是我的个人 Codex Skills 仓库，用来沉淀高频工作流：

- `hn-windows-stability-doctor`: 诊断 Windows 蓝屏、死机、重启、硬盘/内存/驱动稳定性问题。
- `hn-frontend-project-shipper`: 将前端项目从修改、调试、移动端 QA、截图、README 一直推进到发布。
- `hn-agent-workflow-productizer`: 把手工 agent 流程产品化，设计状态机、沙盒权限、验证点和失败恢复。
- `hn-product-release-packager`: 将小应用、Chrome 插件、GitHub Pages 项目整理成可发布包，包括文档、截图、图标、隐私页、商店材料和 release 自动化。
- `hn-tool-ui-polisher`: 审查和打磨工具型 UI，重点处理布局、控件分组、状态反馈、移动端和可用性。
- `hn-visual-asset-pipeline`: 生成、转换、整理并验证图标、截图、透明 PNG、README/商店素材等视觉资产。

推荐安装方式：

```bash
npx github:holynova/hn-codex-skills install
```

默认会安装到 `$CODEX_HOME/skills`，如果没有设置 `CODEX_HOME`，则安装到 `~/.codex/skills`。
