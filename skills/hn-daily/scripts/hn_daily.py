#!/usr/bin/env python3
"""Orchestrate daily maintenance across hn-ai-software-update, hn-token-stats, hn-skills-sync, and hn-clean."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

ALL_STAGES = ("update", "tokens", "skills", "clean")

STAGE_TARGETS = {
    "update": ("hn-ai-software-update", "scripts/update_ai_software.py"),
    "tokens": ("hn-token-stats", "scripts/token_stats.py"),
    "skills": ("hn-skills-sync", "scripts/sync_skills.py"),
    "clean": ("hn-clean", "scripts/mole_cleanup.py"),
}


def resolve_sibling_script(skill_name: str, rel_script: str, skills_root: Path | None = None) -> Path | None:
    roots: list[Path] = []
    if skills_root is not None:
        roots.append(skills_root)
    else:
        roots.append(Path(__file__).resolve().parents[2])
        codex_dir = (Path(os.environ["CODEX_HOME"]) / "skills") if os.environ.get("CODEX_HOME") else (Path.home() / ".codex" / "skills")
        roots.extend([
            Path.home() / ".agents" / "skills",
            codex_dir,
            Path.home() / ".claude" / "skills",
        ])

    for root in roots:
        candidate = root / skill_name / rel_script
        if candidate.is_file():
            return candidate
    return None


def invoke_stage(stage: str, cmd: list[str], timeout: int = 900) -> dict:
    started_epoch = time.time()
    started_iso = datetime.fromtimestamp(started_epoch).isoformat(timespec="milliseconds")
    try:
        proc = subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
        ended_epoch = time.time()
        payload = None
        raw = proc.stdout.strip()
        if raw:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    payload = json.loads(raw[start:end])
                except json.JSONDecodeError:
                    payload = None
        status = (payload or {}).get("status")
        if not status:
            status = "ok" if proc.returncode == 0 else "failed"
        return {
            "stage": stage,
            "command": cmd,
            "returncode": proc.returncode,
            "status": status,
            "started_at": started_iso,
            "ended_at": datetime.fromtimestamp(ended_epoch).isoformat(timespec="milliseconds"),
            "started_epoch": started_epoch,
            "ended_epoch": ended_epoch,
            "duration_s": round(ended_epoch - started_epoch, 2),
            "payload": payload,
            "stderr": proc.stderr.strip()[-1500:] if proc.stderr else "",
        }
    except subprocess.TimeoutExpired:
        ended_epoch = time.time()
        return {
            "stage": stage,
            "command": cmd,
            "returncode": 124,
            "status": "failed",
            "started_at": started_iso,
            "ended_at": datetime.fromtimestamp(ended_epoch).isoformat(timespec="milliseconds"),
            "started_epoch": started_epoch,
            "ended_epoch": ended_epoch,
            "duration_s": round(ended_epoch - started_epoch, 2),
            "payload": None,
            "stderr": f"Timed out after {timeout}s",
        }


def run_stage_safe(
    stage: str,
    enabled: bool,
    extra_args: list[str],
    skills_root: Path | None = None,
    timeout: int = 900,
) -> dict:
    if not enabled:
        now = time.time()
        now_iso = datetime.fromtimestamp(now).isoformat(timespec="milliseconds")
        return {
            "stage": stage,
            "status": "skipped",
            "returncode": 0,
            "started_at": now_iso,
            "ended_at": now_iso,
            "started_epoch": now,
            "ended_epoch": now,
            "duration_s": 0.0,
            "payload": None,
            "stderr": "",
        }

    skill_name, rel_script = STAGE_TARGETS[stage]
    script_path = resolve_sibling_script(skill_name, rel_script, skills_root=skills_root)
    if script_path is None:
        now = time.time()
        now_iso = datetime.fromtimestamp(now).isoformat(timespec="milliseconds")
        return {
            "stage": stage,
            "status": "failed",
            "returncode": 127,
            "started_at": now_iso,
            "ended_at": now_iso,
            "started_epoch": now,
            "ended_epoch": now,
            "duration_s": 0.0,
            "payload": None,
            "stderr": f"Missing sibling skill script: {skill_name}/{rel_script}",
        }

    cmd = [sys.executable, str(script_path), "--json", *extra_args]
    return invoke_stage(stage, cmd, timeout=timeout)


def orchestrate(
    apply: bool = False,
    only: set[str] | None = None,
    skip: set[str] | None = None,
    repo: str | None = None,
    local_repo: str | None = None,
    include_today: bool = False,
    agent: str = "auto",
    days: int = 7,
    skills_root: Path | None = None,
) -> dict:
    t0 = time.time()
    enabled = set(only) if only else set(ALL_STAGES)
    if skip:
        enabled -= set(skip)

    update_args = ["--apply"] if apply else []
    token_args = ["--days", str(days), "--agent", agent]
    if include_today:
        token_args.append("--include-today")

    skills_args = ["--apply"] if apply else []
    if repo:
        skills_args.extend(["--repo", repo])
    if local_repo:
        skills_args.extend(["--local-repo", local_repo])

    clean_args = ["--apply"] if apply else []

    results: dict[str, dict] = {}

    # Stage 1: Parallel (update || tokens)
    with ThreadPoolExecutor(max_workers=2) as pool:
        f_update = pool.submit(run_stage_safe, "update", "update" in enabled, update_args, skills_root, 1200)
        f_tokens = pool.submit(run_stage_safe, "tokens", "tokens" in enabled, token_args, skills_root, 120)
        results["update"] = f_update.result()
        results["tokens"] = f_tokens.result()

    # Stage 2: Serial after update (skills sync)
    results["skills"] = run_stage_safe("skills", "skills" in enabled, skills_args, skills_root, 600)

    # Stage 3: Serial after Stages 1 & 2 (Mole clean + optimize)
    results["clean"] = run_stage_safe("clean", "clean" in enabled, clean_args, skills_root, 1200)

    total_duration = round(time.time() - t0, 2)
    hard_failed = [s for s in ALL_STAGES if results[s]["status"] == "failed"]

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "apply" if apply else "dry-run",
        "dag": {
            "stage_1_parallel": ["update", "tokens"],
            "stage_2_serial_after_update": ["skills"],
            "stage_3_serial_after_all": ["clean"],
        },
        "total_duration_s": total_duration,
        "status": "failed" if hard_failed and len(hard_failed) == len(enabled) else ("partial" if hard_failed else "ok"),
        "stages": results,
    }


def render_markdown(report: dict) -> str:
    stages = report["stages"]
    lines = [
        f"# 每日系统维护与 AI 盘点报告（{report['mode']}）",
        "",
        f"- 生成时间：{report['generated_at']} | 总耗时：{report['total_duration_s']}s",
        "",
        "## 编排执行序（Stage 1 并行，Stage 2/3 串行）",
        "",
        "| 阶段 | 子技能 | 依赖关系 | 状态 | 耗时 |",
        "| --- | --- | --- | --- | --- |",
        f"| Stage 1A (并行) | `hn-ai-software-update` | 无前置依赖 | `{stages['update']['status']}` | {stages['update']['duration_s']}s |",
        f"| Stage 1B (并行) | `hn-token-stats` | 无前置依赖（抢在清理前只读统计） | `{stages['tokens']['status']}` | {stages['tokens']['duration_s']}s |",
        f"| Stage 2 (串行) | `hn-skills-sync` | 等待 Stage 1A 升级 CLI 完成 | `{stages['skills']['status']}` | {stages['skills']['duration_s']}s |",
        f"| Stage 3 (串行) | `hn-clean` | 等待 1A 新版 Mole、1B Token 与 2 同步全部结束 | `{stages['clean']['status']}` | {stages['clean']['duration_s']}s |",
        "",
    ]

    # Add concise sections from each payload
    up = stages["update"].get("payload")
    if up:
        lines.append("## 1. AI 软件与 CLI 更新")
        lines.append("")
        upgraded = up.get("upgraded", [])
        outdated = up.get("outdated", [])
        latest = up.get("already_latest", [])
        manual = up.get("manual_apps", [])
        issues = up.get("issues", [])
        lines.append(f"- 已升级：{len(upgraded)} 项 | 待更新：{len(outdated)} 项 | 已是最新：{len(latest)} 项 | 桌面端/手动：{len(manual)} 项")
        for item in upgraded:
            lines.append(f"  - ✅ `{item['name']}` ({item['manager']}): `{item.get('before') or '?'}` -> `{item.get('after') or item.get('latest') or 'latest'}`")
        for item in outdated:
            lines.append(f"  - ⏳ `{item['name']}` ({item['manager']}): `{item.get('before') or '?'}` -> `{item.get('latest') or '?'}`")
        for item in manual:
            lines.append(f"  - 🖥️ `{item['name']}`: 当前 `{item.get('version') or '?'}`（{item.get('note') or '应用内更新'}）")
        for item in issues:
            lines.append(f"  - ⚠️ `{item.get('name', 'unknown')}`: {item.get('message', '')}")
        lines.append("")
    elif stages["update"]["status"] != "skipped":
        lines.extend(["## 1. AI 软件与 CLI 更新", "", f"- 状态：`{stages['update']['status']}` {stages['update'].get('stderr', '')}", ""])

    sk = stages["skills"].get("payload")
    if sk:
        tp = sk.get("third_party", {})
        hn = sk.get("hn_skills", {})
        lines.append("## 2. Skills 同步与更新")
        lines.append("")
        lines.append(f"- 第三方 skills：状态 `{tp.get('status')}` | 更新 {len(tp.get('updated', []))} 个 | 已最新 {len(tp.get('unchanged', []))} 个")
        if tp.get("updated"):
            lines.append(f"  - 已更新：{', '.join(f'`{s}`' for s in tp['updated'])}")
        lines.append(f"- 个人仓库 `{sk.get('repo')}`：共 {hn.get('active_count', 0)} 个正式技能 | 新增 {len(hn.get('added', []))} | 更新 {len(hn.get('updated', []))} | 补齐软链 {len(hn.get('symlink_repairs', []))}")
        if hn.get("added"):
            lines.append(f"  - 新增：{', '.join(f'`{s}`' for s in hn['added'])}")
        if hn.get("updated"):
            lines.append(f"  - 更新：{', '.join(f'`{s}`' for s in hn['updated'])}")
        for warn in hn.get("warnings", []):
            lines.append(f"  - 提示：{warn}")
        lines.append("")
    elif stages["skills"]["status"] != "skipped":
        lines.extend(["## 2. Skills 同步与更新", "", f"- 状态：`{stages['skills']['status']}` {stages['skills'].get('stderr', '')}", ""])

    cl = stages["clean"].get("payload")
    if cl:
        lines.append("## 3. 磁盘清理与系统优化（Mole）")
        lines.append("")
        before = cl.get("before_disk")
        after = cl.get("after_disk")
        if before and after:
            delta_mb = cl.get("observed_delta_kb", 0) / 1024
            lines.append(f"- 卷 `{before['mount_point']}` 可用空间：`{before['avail_gb']:.2f} GB` -> `{after['avail_gb']:.2f} GB`（实测变化 `{delta_mb:+.1f} MB`）")
        c_part = cl.get("clean", {})
        o_part = cl.get("optimize", {})
        c_dry = c_part.get("dry_run", {})
        c_app = c_part.get("apply")
        o_dry = o_part.get("dry_run", {})
        o_app = o_part.get("apply")
        lines.append(
            f"- `mo clean`：`{c_part.get('status')}` | 预览估算 `{c_dry.get('potential_space') or '未知'}`"
            + (f" | 实清 `{c_app.get('freed_space') or '已执行'}`" if c_app else "")
        )
        lines.append(
            f"- `mo optimize`：`{o_part.get('status')}` | 预览建议 `{o_dry.get('planned_count')}` 项"
            + (f" | 实跑 `{o_app.get('applied_count')}` 项" if o_app else "")
        )
        if o_part.get("manual_command"):
            lines.append(f"  - 管理员权限项需手动在终端执行：`{o_part['manual_command']}`")
        for adv in c_dry.get("advisories", []):
            lines.append(f"  - 未自动删除的大目录建议：`{adv}`")
        lines.append("")
    elif stages["clean"]["status"] != "skipped":
        lines.extend(["## 3. 磁盘清理与系统优化（Mole）", "", f"- 状态：`{stages['clean']['status']}` {stages['clean'].get('stderr', '')}", ""])

    tk = stages["tokens"].get("payload")
    if tk and tk.get("cards"):
        lines.append("## 4. 近 7 日 AI Token 消耗统计")
        lines.append("")
        lines.append("\n\n".join(card["text"] for card in tk["cards"]))
    elif stages["tokens"]["status"] != "skipped":
        lines.extend(["## 4. 近 7 日 AI Token 消耗统计", "", f"- 状态：`{stages['tokens']['status']}` {stages['tokens'].get('stderr', '')}"])

    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Apply updates, skills sync, and Mole clean/optimize.")
    parser.add_argument("--only", default="", help="Comma-separated stages from: update,tokens,skills,clean.")
    parser.add_argument("--skip", default="", help="Comma-separated stages to skip.")
    parser.add_argument("--repo", help="GitHub skills repo override (default holynova/hn-codex-skills).")
    parser.add_argument("--local-repo", help="Local skills repo override for offline/pre-push testing.")
    parser.add_argument("--include-today", action="store_true", help="Include today in token stats window.")
    parser.add_argument("--agent", default="auto", help="Agent filter for token stats.")
    parser.add_argument("--days", type=int, default=7, help="Number of days for token stats.")
    parser.add_argument("--save-report", type=Path, help="Optional directory to save JSON and Markdown reports.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    only = {p.strip().lower() for p in args.only.split(",") if p.strip()} or None
    skip = {p.strip().lower() for p in args.skip.split(",") if p.strip()} or None

    report = orchestrate(
        apply=args.apply,
        only=only,
        skip=skip,
        repo=args.repo,
        local_repo=args.local_repo,
        include_today=args.include_today,
        agent=args.agent,
        days=args.days,
    )
    md = render_markdown(report)

    if args.save_report:
        args.save_report.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        (args.save_report / f"hn-daily-{stamp}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        (args.save_report / f"hn-daily-{stamp}.md").write_text(md, encoding="utf-8")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(md)
    return 1 if report["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
