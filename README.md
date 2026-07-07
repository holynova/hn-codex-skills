# HN Codex Skills

Personal Codex skills for recurring workflows.

## Bundled Skills

- `hn-windows-stability-doctor`: Windows crash, freeze, restart, disk, memory, driver, and stability diagnosis.
- `hn-frontend-project-shipper`: frontend project polish, QA, docs, screenshots, GitHub, and release workflow.
- `hn-agent-workflow-productizer`: productize manual agent procedures into safe workflow systems.
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
Copy-Item -Recurse .\skills\hn-xiaohei-draw $HOME\.codex\skills\
```

## 中文说明

这是我的个人 Codex Skills 仓库，用来沉淀高频工作流，而不是把经验只留在某一次对话里。

- `hn-windows-stability-doctor`: 诊断 Windows 蓝屏、死机、重启、硬盘、内存、驱动和稳定性问题。
- `hn-frontend-project-shipper`: 把前端项目从修改、调试、移动端 QA、截图、README 推进到发布。
- `hn-agent-workflow-productizer`: 把手工 agent 流程产品化，设计状态机、沙盒权限、验证点和失败恢复。
- `hn-xiaohei-draw`: 为中文文章生成 Ian 风格、宇航员小黑 IP 的正文配图。

推荐安装方式：

```bash
npx github:holynova/hn-codex-skills install
```

默认安装到 `$CODEX_HOME/skills`；如果没有设置 `CODEX_HOME`，则安装到 `~/.codex/skills`。
