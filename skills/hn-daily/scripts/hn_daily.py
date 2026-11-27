#!/usr/bin/env python3
"""Orchestrate daily maintenance with streaming per-step output, fast-fail timeouts, and concise Plan C + 7-day charts."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Callable

ALL_STAGES = ("update", "tokens", "skills", "clean")

DEFAULT_STAGE_TIMEOUTS = {
    "update": 240,
    "tokens": 45,
    "skills": 180,
    "clean": 1080,
}

STAGE_TARGETS = {
    "update": ("hn-ai-software-update", "scripts/update_ai_software.py"),
    "tokens": ("hn-token-stats", "scripts/token_stats.py"),
    "skills": ("hn-skills-sync", "scripts/sync_skills.py"),
    "clean": ("hn-clean", "scripts/mole_cleanup.py"),
}

STAGE_TITLES = {
    "update": "软件更新",
    "tokens": "Token 统计",
    "skills": "Skills 同步",
    "clean": "磁盘清理",
}


def status_icon(status: str) -> str:
    if status in {"ok", "preview_ok"}:
        return "✅"
    if status in {"partial", "partial_needs_admin", "needs_admin", "needs_manual", "preview_partial"}:
        return "⚠️"
    if status in {"skipped", "skipped_timeout"}:
        return "⏭️"
    return "❌"


def format_duration(seconds: float) -> str:
    if seconds >= 60:
        mins = int(seconds // 60)
        rem = int(round(seconds - mins * 60))
        if rem == 60:
            mins += 1
            rem = 0
        return f"{mins}m {rem:02d}s"
    return f"{seconds:.1f}s"


def format_cn_tokens(raw_tokens: int) -> str:
    if raw_tokens <= 0:
        return "0万"
    wan = round(raw_tokens / 10_000)
    if wan == 0:
        return "<1万"
    if wan >= 10_000:
        yi, rem = divmod(wan, 10_000)
        return f"{yi}亿{rem:,}万" if rem else f"{yi}亿"
    return f"{wan:,}万"


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


def invoke_stage(stage: str, cmd: list[str], timeout: float = 240) -> dict:
    started_epoch = time.time()
    started_iso = datetime.fromtimestamp(started_epoch).isoformat(timespec="milliseconds")
    env = {**os.environ, "PYTHONUNBUFFERED": "1"}
    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            start_new_session=True,
        )
    except OSError as exc:
        ended_epoch = time.time()
        return {
            "stage": stage,
            "command": cmd,
            "returncode": 127,
            "status": "failed",
            "started_at": started_iso,
            "ended_at": datetime.fromtimestamp(ended_epoch).isoformat(timespec="milliseconds"),
            "started_epoch": started_epoch,
            "ended_epoch": ended_epoch,
            "duration_s": round(ended_epoch - started_epoch, 2),
            "payload": None,
            "stderr": str(exc),
        }

    timed_out = False
    try:
        raw_out, raw_err = proc.communicate(timeout=timeout)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            raw_out, raw_err = proc.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            raw_out, raw_err = proc.communicate()
        rc = 124

    ended_epoch = time.time()
    payload = None
    raw = (raw_out or "").strip()
    if raw:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            try:
                payload = json.loads(raw[start:end])
            except json.JSONDecodeError:
                payload = None

    if timed_out:
        status = "skipped_timeout"
        stderr_text = f"Timed out after {timeout}s (skipped)"
    else:
        status = (payload or {}).get("status")
        if not status:
            status = "ok" if rc == 0 else "failed"
        stderr_text = (raw_err or "").strip()[-800:]

    return {
        "stage": stage,
        "command": cmd,
        "returncode": rc,
        "status": status,
        "started_at": started_iso,
        "ended_at": datetime.fromtimestamp(ended_epoch).isoformat(timespec="milliseconds"),
        "started_epoch": started_epoch,
        "ended_epoch": ended_epoch,
        "duration_s": round(ended_epoch - started_epoch, 2),
        "payload": payload,
        "stderr": stderr_text,
    }


def run_stage_safe(
    stage: str,
    enabled: bool,
    extra_args: list[str],
    skills_root: Path | None = None,
    timeout: float = 240,
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


def _short_name(name: str) -> str:
    return name.rsplit("/", 1)[-1]


def _summarize_update_bullet(st: dict) -> str:
    status = st["status"]
    icon = status_icon(status)
    dur = format_duration(st["duration_s"])
    up = st.get("payload")
    if status == "skipped_timeout":
        return f"- **软件（{icon}）**：已跳过（超时：{st.get('stderr') or '超过时限'}） · {dur}"
    if not up:
        return f"- **软件（{icon}）**：失败已跳过（{st.get('stderr') or '无详情'}） · {dur}"

    upgraded = up.get("upgraded", [])
    outdated = up.get("outdated", [])
    latest = up.get("already_latest", [])
    issues = up.get("issues", [])
    manual = up.get("manual_apps", [])

    parts: list[str] = []
    if upgraded:
        names = " ".join(f"`{_short_name(x['name'])}`" for x in upgraded[:8])
        extra = f" 等 {len(upgraded)} 项" if len(upgraded) > 8 else ""
        parts.append(f"升级 {names}{extra}")
    elif outdated:
        names = " ".join(f"`{_short_name(x['name'])}`" for x in outdated[:6])
        extra = f" 等 {len(outdated)} 项" if len(outdated) > 6 else ""
        parts.append(f"待更新 {names}{extra}")
    else:
        parts.append(f"全部 {len(latest)} 项已是最新")

    if upgraded and latest:
        parts.append(f"{len(latest)} 项最新")
    if manual:
        parts.append(f"桌面端 {len(manual)} 项手动")
    if issues:
        issue_names = " ".join(f"`{_short_name(i.get('name', '?'))}`" for i in issues[:3])
        parts.append(f"跳过 {issue_names}")
    return f"- **软件（{icon}）**：{'；'.join(parts)} · {dur}"


def _summarize_skills_bullet(st: dict) -> str:
    status = st["status"]
    icon = status_icon(status)
    dur = format_duration(st["duration_s"])
    sk = st.get("payload")
    if status == "skipped_timeout":
        return f"- **Skills（{icon}）**：已跳过（超时：{st.get('stderr') or '超过时限'}） · {dur}"
    if not sk:
        return f"- **Skills（{icon}）**：失败已跳过（{st.get('stderr') or '无详情'}） · {dur}"

    tp = sk.get("third_party", {})
    hn = sk.get("hn_skills", {})
    parts: list[str] = []
    if tp.get("status") == "skipped_timeout":
        parts.append("第三方超时跳过")
    elif tp.get("status") != "skipped":
        upd_tp = tp.get("updated", [])
        parts.append(f"第三方更新 {len(upd_tp)} 项" if upd_tp else f"第三方 {len(tp.get('unchanged', []))} 项最新")

    if hn.get("status") != "skipped":
        added = hn.get("added", [])
        updated = hn.get("updated", [])
        sub: list[str] = []
        if added:
            sub.append(f"新增 {' '.join(f'`{s}`' for s in added[:6])}" + (f" 等{len(added)}个" if len(added) > 6 else ""))
        if updated:
            sub.append(f"更新 {' '.join(f'`{s}`' for s in updated[:6])}" + (f" 等{len(updated)}个" if len(updated) > 6 else ""))
        if not sub:
            sub.append(f"{hn.get('active_count', 0)} 个已是最新")
        parts.append("个人库" + "、".join(sub))
    return f"- **Skills（{icon}）**：{'；'.join(parts)} · {dur}"


def _summarize_clean_bullet(st: dict) -> str:
    status = st["status"]
    icon = status_icon(status)
    dur = format_duration(st["duration_s"])
    cl = st.get("payload")
    if status == "skipped_timeout":
        return f"- **清理（{icon}）**：已跳过（超时：{st.get('stderr') or '超过时限'}） · {dur}"
    if not cl:
        return f"- **清理（{icon}）**：失败已跳过（{st.get('stderr') or '无详情'}） · {dur}"

    before = cl.get("before_disk")
    after = cl.get("after_disk")
    c_part = cl.get("clean", {})
    o_part = cl.get("optimize", {})
    c_app = c_part.get("apply") or {}
    c_dry = c_part.get("dry_run") or {}
    o_app = o_part.get("apply") or {}
    o_dry = o_part.get("dry_run") or {}

    parts: list[str] = []
    if c_part.get("status") == "skipped_timeout":
        parts.append("`mo clean` 超时跳过")
    elif c_app:
        parts.append(f"`mo clean` 清 `{c_app.get('freed_space') or '已执行'}`")
    elif c_dry:
        parts.append(f"`mo clean` 预览可清 `{c_dry.get('potential_space') or '?'}`")

    if before and after:
        delta_mb = cl.get("observed_delta_kb", 0) / 1024
        delta_str = f"{delta_mb / 1024:+.2f} GB" if abs(delta_mb) >= 1024 else f"{delta_mb:+.0f} MB"
        parts.append(f"可用 `{before['avail_gb']:.2f} → {after['avail_gb']:.2f} GB`（**{delta_str}**）")

    o_st = o_part.get("status")
    if o_st == "skipped_timeout":
        parts.append("`mo optimize` 超时跳过")
    elif o_app:
        cnt = o_app.get("applied_count")
        parts.append(f"`mo optimize` 已应用 {cnt if cnt is not None else '?'} 项")
    elif o_dry:
        cnt = o_dry.get("planned_count")
        parts.append(f"`mo optimize` 预览 {cnt if cnt is not None else '?'} 项")

    return f"- **清理（{icon}）**：{'，'.join(parts)} · {dur}"


def _collect_pending_notes(report: dict) -> list[str]:
    notes: list[str] = []
    stages = report["stages"]
    up = stages["update"].get("payload") or {}
    for iss in up.get("issues", []):
        msg = iss.get("message", "")
        if "needs_manual" in msg:
            notes.append(f"`{_short_name(iss.get('name', '?'))}` 需手动处理")
    cl = stages["clean"].get("payload") or {}
    o_part = cl.get("optimize", {})
    if o_part.get("manual_command"):
        notes.append(f"系统级优化需终端执行 `{o_part['manual_command']}`")
    c_src = (cl.get("clean", {}).get("apply") or cl.get("clean", {}).get("dry_run") or {})
    advs = c_src.get("advisories", [])
    if advs:
        short_advs = [a.split("·")[0].strip() for a in advs[:3]]
        notes.append("大目录建议留存未删：" + " / ".join(f"`{a}`" for a in short_advs))
    return notes


def format_stage_stream_update(stage: str, st: dict, index: int, total: int) -> str:
    icon = status_icon(st["status"])
    title = STAGE_TITLES.get(stage, stage)
    dur = format_duration(st["duration_s"])
    header = f"▶ [{index}/{total}] {icon} {title}（{dur}）"

    if stage == "tokens":
        tk = st.get("payload")
        if tk and tk.get("cards"):
            return header + "\n" + "\n\n".join(card["text"] for card in tk["cards"])
        return header + f"\n- 状态：`{st['status']}` {st.get('stderr', '')}".rstrip()
    if stage == "update":
        return header + "\n" + _summarize_update_bullet(st)
    if stage == "skills":
        return header + "\n" + _summarize_skills_bullet(st)
    if stage == "clean":
        return header + "\n" + _summarize_clean_bullet(st)
    return header


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
    stage_timeouts: dict[str, float] | None = None,
    on_stage_done: Callable[[str, dict, int, int], None] | None = None,
) -> dict:
    t0 = time.time()
    enabled = set(only) if only else set(ALL_STAGES)
    if skip:
        enabled -= set(skip)

    timeouts = {**DEFAULT_STAGE_TIMEOUTS, **(stage_timeouts or {})}
    total_enabled = len([s for s in ALL_STAGES if s in enabled])
    done_count = 0

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

    def emit(stage: str) -> None:
        nonlocal done_count
        if stage in enabled and on_stage_done is not None:
            done_count += 1
            on_stage_done(stage, results[stage], done_count, total_enabled)

    # Stage 1: Parallel (update || tokens) with immediate per-step callback via as_completed
    stage1_args = {"update": update_args, "tokens": token_args}
    stage1_enabled = [s for s in ("update", "tokens") if s in enabled]
    for s in ("update", "tokens"):
        if s not in enabled:
            results[s] = run_stage_safe(s, False, [], skills_root, timeouts[s])

    if stage1_enabled:
        with ThreadPoolExecutor(max_workers=len(stage1_enabled)) as pool:
            future_map = {
                pool.submit(run_stage_safe, s, True, stage1_args[s], skills_root, timeouts[s]): s
                for s in stage1_enabled
            }
            for fut in as_completed(future_map):
                st_name = future_map[fut]
                results[st_name] = fut.result()
                emit(st_name)

    # Stage 2: Serial after update (skills sync)
    results["skills"] = run_stage_safe("skills", "skills" in enabled, skills_args, skills_root, timeouts["skills"])
    emit("skills")

    # Stage 3: Serial after Stages 1 & 2 (Mole clean + optimize)
    results["clean"] = run_stage_safe("clean", "clean" in enabled, clean_args, skills_root, timeouts["clean"])
    emit("clean")

    total_duration = round(time.time() - t0, 2)
    hard_failed = [s for s in ALL_STAGES if results[s]["status"] == "failed"]
    has_partial = any(
        results[s]["status"] in {"partial", "partial_needs_admin", "needs_manual", "skipped_timeout", "failed"}
        for s in enabled
    )

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "apply" if apply else "dry-run",
        "dag": {
            "stage_1_parallel": ["update", "tokens"],
            "stage_2_serial_after_update": ["skills"],
            "stage_3_serial_after_all": ["clean"],
        },
        "total_duration_s": total_duration,
        "status": "failed" if hard_failed and len(hard_failed) == len(enabled) else ("partial" if (hard_failed or has_partial) else "ok"),
        "stages": results,
    }


def render_markdown(report: dict) -> str:
    stages = report["stages"]
    date_part = str(report["generated_at"])[:10]
    dur_str = format_duration(report["total_duration_s"])

    # KPI bar values
    up = stages["update"].get("payload") or {}
    if stages["update"]["status"] == "skipped":
        up_kpi = "软件 已跳过"
    elif stages["update"]["status"] in {"skipped_timeout", "failed"} and not up:
        up_kpi = "软件 跳过/失败"
    else:
        n_up = len(up.get("upgraded", []))
        n_out = len(up.get("outdated", []))
        up_kpi = f"更新 {n_up} 项" if report["mode"] == "apply" else f"待更新 {n_out} 项"

    sk = stages["skills"].get("payload") or {}
    if stages["skills"]["status"] == "skipped":
        sk_kpi = "技能 已跳过"
    elif stages["skills"]["status"] in {"skipped_timeout", "failed"} and not sk:
        sk_kpi = "技能 跳过/失败"
    else:
        tp_cnt = len(sk.get("third_party", {}).get("updated", []))
        hn_cnt = len(sk.get("hn_skills", {}).get("added", [])) + len(sk.get("hn_skills", {}).get("updated", []))
        sk_kpi = f"同步 {tp_cnt + hn_cnt} 技能"

    cl = stages["clean"].get("payload") or {}
    if stages["clean"]["status"] == "skipped":
        cl_kpi = "清理 已跳过"
    elif cl.get("before_disk") and cl.get("after_disk"):
        delta_mb = cl.get("observed_delta_kb", 0) / 1024
        d_str = f"{delta_mb / 1024:+.2f} GB" if abs(delta_mb) >= 1024 else f"{delta_mb:+.0f} MB"
        cl_kpi = f"可用空间 {d_str}（→ {cl['after_disk']['avail_gb']:.2f} GB）"
    else:
        cl_kpi = "清理 跳过/无变化"

    tk = stages["tokens"].get("payload") or {}
    if stages["tokens"]["status"] == "skipped":
        tk_kpi = "Token 已跳过"
    elif tk.get("cards"):
        tk_kpi = f"7日 {format_cn_tokens(int(tk.get('combined_total', 0)))} Token"
    else:
        tk_kpi = "Token 跳过/失败"

    overall_icon = "✅" if report["status"] == "ok" else ("⚠️" if report["status"] == "partial" else "❌")
    lines = [
        f"### {overall_icon} Daily 汇总｜{date_part}（{report['mode']} · {dur_str}）",
        f"**{up_kpi} · {sk_kpi} · {cl_kpi} · {tk_kpi}**",
        "",
    ]

    if stages["update"]["status"] != "skipped":
        lines.append(_summarize_update_bullet(stages["update"]))
    if stages["skills"]["status"] != "skipped":
        lines.append(_summarize_skills_bullet(stages["skills"]))
    if stages["clean"]["status"] != "skipped":
        lines.append(_summarize_clean_bullet(stages["clean"]))

    notes = _collect_pending_notes(report)
    if notes:
        lines.append("")
        lines.append(f"> **待按需处理**：{'；'.join(notes)}")

    if stages["tokens"]["status"] != "skipped":
        lines.append("")
        if tk.get("cards"):
            lines.append("\n\n".join(card["text"] for card in tk["cards"]))
        else:
            lines.append(f"- **Token（{status_icon(stages['tokens']['status'])}）**：已跳过（{stages['tokens'].get('stderr') or '无数据'}）")

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
    parser.add_argument("--update-timeout", type=int, default=DEFAULT_STAGE_TIMEOUTS["update"])
    parser.add_argument("--tokens-timeout", type=int, default=DEFAULT_STAGE_TIMEOUTS["tokens"])
    parser.add_argument("--skills-timeout", type=int, default=DEFAULT_STAGE_TIMEOUTS["skills"])
    parser.add_argument("--clean-timeout", type=int, default=DEFAULT_STAGE_TIMEOUTS["clean"])
    parser.add_argument("--no-stream", action="store_true", help="Print only the final summary without per-step streaming output.")
    parser.add_argument("--save-report", type=Path, help="Optional directory to save JSON and Markdown reports.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    only = {p.strip().lower() for p in args.only.split(",") if p.strip()} or None
    skip = {p.strip().lower() for p in args.skip.split(",") if p.strip()} or None
    stage_timeouts = {
        "update": args.update_timeout,
        "tokens": args.tokens_timeout,
        "skills": args.skills_timeout,
        "clean": args.clean_timeout,
    }

    stream_enabled = (not args.json) and (not args.no_stream)

    def handle_stage_done(stage: str, st: dict, idx: int, total: int) -> None:
        print(format_stage_stream_update(stage, st, idx, total), flush=True)
        print("", flush=True)

    report = orchestrate(
        apply=args.apply,
        only=only,
        skip=skip,
        repo=args.repo,
        local_repo=args.local_repo,
        include_today=args.include_today,
        agent=args.agent,
        days=args.days,
        stage_timeouts=stage_timeouts,
        on_stage_done=handle_stage_done if stream_enabled else None,
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
        if stream_enabled:
            print("━━━ 最终汇总 ━━━", flush=True)
        print(md, flush=True)
    return 1 if report["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
