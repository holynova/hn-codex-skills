---
name: hn-skills-sync
description: 更新本机所有已安装的第三方 skills，并从 GitHub 同步个人 skills 仓库（如 holynova/hn-codex-skills），自动加入新增 skill、更新已有 skill，同时严格跳过 backup 归档目录并同步到 Codex、Agents、Claude、Gemini 等本地代理目录。适用于用户要求更新技能、同步 GitHub skills 仓库或检查新增/过期 skill。
---

# HN Skills 同步与更新

统一更新本机已安装的第三方 skills 与个人 GitHub skills 仓库（默认 `holynova/hn-codex-skills`），保证新增 skill 自动加入、已有 skill 及时更新，且绝不误装 `backup/` 下的归档技能。

## 工作流

1. **预览差异（dry-run）**，查看待更新的第三方 skill 与 GitHub 仓库新增/变更项：

```bash
python3 skills/hn-skills-sync/scripts/sync_skills.py
```

2. **执行同步与更新（apply）**：

```bash
python3 skills/hn-skills-sync/scripts/sync_skills.py --apply
```

3. **常用参数**：
   - `--repo owner/repo`：指定个人 GitHub skills 仓库（默认 `holynova/hn-codex-skills`）。
   - `--local-repo <path>`：在离线或发布前本地联调时，直接从本地仓库目录比对/同步。
   - `--skip-third-party` / `--skip-hn-skills`：只执行其中一侧。
   - `--json`：输出结构化 JSON 供 `hn-daily` 编排汇总。

## 同步规则

- **第三方 skills**：通过 `skills update -g -y` 更新全局技能，并在更新前后对比 `~/.agents/.skill-lock.json` 记录实际变更列表；独立软链托管的技能（如 `ego-browser`）保留原样并单独标出。
- **个人仓库白名单**：仅从 `<source>/skills/` 读取同时具备 `SKILL.md` 与 `agents/openai.yaml` 的正式技能，`backup/` 与隐藏目录一律拦截。
- **多代理目录对齐**：
  - Codex 目录（`$CODEX_HOME/skills` 或 `~/.codex/skills`）优先调用仓库内 `bin/install.mjs install --force` 原子安装（或原子目录替换兜底）。
  - `~/.agents/skills` 通过 `skills add` 与内容哈希核验保持最新。
  - 已存在的软链代理目录（`~/.claude/skills`、`~/.gemini/config/skills`、`~/.config/opencode/skills`、`~/.cursor/skills`）自动补齐缺失软链并修复陈旧副本，不会为未安装的工具创建空目录。
