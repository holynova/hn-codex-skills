---
name: hn-daily
description: 每日一站式系统维护与 AI 盘点编排技能：按依赖编排并行与串行步骤，组合调用 hn-ai-software-update（更新 AI CLI、Mole 与软件）、hn-token-stats（近七日 Token 进度条统计）、hn-skills-sync（更新第三方与个人 GitHub skills）和 hn-clean（运行 mo clean 与 mo optimize 清理优化磁盘）。适用于每日维护、批量升级同步清理或统一日报汇报。
---

# HN 每日维护编排 (`hn-daily`)

通过明确的有向无环图（DAG）编排调用四个独立子技能，兼顾并发效率与数据一致性：

## 并行与串行编排架构

```text
Stage 1 (并行) ──┬──► [1A] hn-ai-software-update  (内部各包管理器通道再并发；brew 通道内部串行)
                 └──► [1B] hn-token-stats          (纯只读统计，抢在清理缓存前完成)
                         │
                         ▼ (依赖 1A 升级后的 skills CLI 与环境)
Stage 2 (串行) ───────► [2]  hn-skills-sync        (更新第三方 skills + 同步 holynova/hn-codex-skills)
                         │
                         ▼ (依赖 1A 新版 Mole、1B 已完成读取、2 不再写入锁/缓存)
Stage 3 (串行) ───────► [3]  hn-clean              (执行 mo clean + mo optimize，复测 df -k 并列大目录建议)
```

### 编排依据

- **为什么 `[1A]` 与 `[1B]` 并行**：Token 统计仅读取会话日志与缓存指标，与软件更新无写冲突；同时让 `hn-token-stats` 在阶段一就完成读取，可避免后续 `mo clean` 清掉 `~/.npm/_npx` 里的 `ccusage` 缓存二进制。
- **为什么 `[2]` 必须在 `[1A]` 之后串行**：`[1A]` 会先升级 `skills` CLI 与 AI CLI；在最新 CLI 就绪后再同步 skills，且避免与 npm/pnpm 并发争夺全局状态。
- **为什么 `[3]` 必须最后串行**：① 可用上 `[1A]` 刚升级好的最新版 `mole`；② 一并扫掉 `[1A]` 和 `[2]` 新产生的下载缓存；③ 避免 `mo clean` 与 `brew` / `npm` / `pnpm` / `skills` / `ccusage` 同时读写缓存引发锁竞争或半成品误删。

## 使用方式

```bash
# 1. 安全预览模式（默认仅 dry-run + 只读 Token 统计）
python3 skills/hn-daily/scripts/hn_daily.py

# 2. 实际执行模式（更新软件 + 同步 skills + 执行 mo clean / mo optimize + 输出近7日 Token 卡片）
python3 skills/hn-daily/scripts/hn_daily.py --apply

# 3. 仅运行部分阶段 / 跳过某阶段 / 输出 JSON
python3 skills/hn-daily/scripts/hn_daily.py --apply --only "tokens,clean"
python3 skills/hn-daily/scripts/hn_daily.py --apply --skip "clean"
python3 skills/hn-daily/scripts/hn_daily.py --apply --json --save-report ~/ai-daily-reports
```

## 容错与交付原则

- **单步隔离**：某个子技能部分完成或遇权限/GUI 阻塞（如 `mo optimize` 需管理员密码或某桌面端需应用内点击更新）时，记录状态并继续执行后续独立步骤，不中断整套日报。
- **分开呈现**：软件更新状态、skills 增删改明细、Mole 估算与 `df -k` 实测可用空间变化、以及未清理大目录建议（如 `pnpm store`、`worktrees`、`mo purge`）全部独立列出；Token 统计完整保留近 7 日 `1/8` 刻度进度条卡片。
