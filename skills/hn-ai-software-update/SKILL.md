---
name: hn-ai-software-update
description: 更新本机已安装的 AI CLI、Mole (`mo`)、skills CLI 及 AI 桌面应用。自动识别各自真实安装来源（Homebrew formulae/casks、npm、pnpm 含旧版全局 shim、uv/pipx/cargo 与原生自更新命令），避免重复装第二份，并以通道并发执行升级。适用于用户要求更新所有 AI 工具、AI CLI、Mole 或检查 AI 软件最新版本。
---

# HN AI 软件与 CLI 更新

通过各自的原生包管理器检查并升级已安装的 AI CLI、Mole（`mo`）、`skills` CLI 与 AI 桌面端应用，不跨包管理器重复安装，也不自动强杀正在运行的宿主桌面应用。

## 工作流

1. **先盘点预览（dry-run）**，确认将检查的通道与过期软件：

```bash
python3 skills/hn-ai-software-update/scripts/update_ai_software.py
```

2. **执行更新（apply）**，仅当用户明确要求更新软件或执行日常维护时运行：

```bash
python3 skills/hn-ai-software-update/scripts/update_ai_software.py --apply
```

3. **按需过滤或控制范围**：
   - `--only "mole,opencode,codex,gemini"`：只处理指定工具。
   - `--no-casks`：跳过 Homebrew GUI Cask，仅升级 CLI。
   - `--json`：输出结构化 JSON，供 `hn-daily` 等上游编排技能消费。

## 并发与安全边界

- **跨通道并行、通道内串行**：Homebrew、npm、pnpm、uv/pipx/cargo、自更新器（如 `agy update`）与 GUI 应用盘点互相独立，脚本使用线程池并行检查与升级；同一 Homebrew 通道内先 `brew update` 再逐个 `brew upgrade`，避免单包失败拖垮整批。
- **遵循原始安装源**：仅升级已检测到的条目；能识别旧版 pnpm `global/5` 遗留 shim（如 `gemini`）并在当前 pnpm 环境中原地升级，不额外往 npm 或 brew 另装副本。
- **非交互保护**：所有子进程强制 `NONINTERACTIVE=1` 与 `SUDO_ASKPASS=/usr/bin/false`；遇到需要管理员密码、GUI 应用正在占用或自更新仅支持应用内点击的条目，记为 `needs_manual` / `manual_in_app` 并继续其余条目，绝不绕过权限或杀掉正在使用的主应用进程。
- **不做破坏性清理**：不在本技能内执行 `brew cleanup` 或删除缓存，清理统一交由 `hn-clean` 处理。
