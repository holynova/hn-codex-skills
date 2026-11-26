---
name: hn-token-stats
description: 统计近7日（或指定天数）AI Token 用量并输出带 1/8 精细块进度条、按万/亿取整与周累计的中文卡片（兼容 Codex、AntiGravity 含 T3 Code ACP 会话、Claude、OpenCode 等）。适用于用户询问近七日 token 消耗、AI 用量统计、日报汇总或要求按特定进度条格式输出 token 报表。
---

# HN AI Token 统计卡片

汇总近 7 日（默认截至昨日的完整 7 天，也支持 `--include-today` 包含今日）各 AI 工具 Token 消耗，并按统一中文卡片格式输出带 `1/8` 精细字符刻度进度条的统计结果。

## 快速运行

```bash
# 默认统计截至昨日的近 7 日（所有活跃 AI 工具合计 + 分工具卡片）
python3 skills/hn-token-stats/scripts/token_stats.py

# 只输出 Codex / 包含今日 / 输出 JSON
python3 skills/hn-token-stats/scripts/token_stats.py --agent codex
python3 skills/hn-token-stats/scripts/token_stats.py --include-today
python3 skills/hn-token-stats/scripts/token_stats.py --json
```

## 输出规范

每张卡片严格遵循以下排版（含缓存 Token，按 1 万四舍五入，12 格字符进度条按周内峰值归一化，每格支持 `▏▎▍▌▋▊▉█` 八档 1/8 刻度）：

```text
📊 Codex Token｜近7日（11/19–11/25）
日期 | 进度条         | Token
11/19 | █▋░░░░░░░░░░ | 6,408万
...
7日累计：约 10亿7,585万 Token
注：含缓存，按1万取整；进度按周峰值，每格含1/8刻度。
```

- **多工具展示**：`--agent auto` 下若检测到多个有消耗的代理（例如 `codex` 与 `antigravity`），先输出 `AI 合计` 总卡，再依次输出各活跃代理卡片；若只有单个活跃代理则直接输出该代理卡片。
- **AntiGravity 全量采集**：除默认 `~/.gemini/antigravity` 外，自动扫描 `~/.t3/userdata/providers/antigravity/*/antigravity-acp`（按 `realpath` 去重），避免遗漏 T3 Code 中的 AntiGravity 用量。
- **离线兜底**：优先调用本地或缓存的 `ccusage` 二进制；若不可用则直接解析本地 Codex/Claude 会话日志。
