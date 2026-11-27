#!/usr/bin/env python3
"""Render 7-day AI token consumption cards with 1/8-block precision bars."""

from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import signal
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

EIGHTHS = ["", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]

AGENT_ORDER = ["codex", "antigravity", "claude", "opencode", "gemini"]

AGENT_LABELS = {
    "codex": "Codex",
    "antigravity": "AntiGravity",
    "claude": "Claude",
    "opencode": "OpenCode",
    "gemini": "Gemini",
    "combined": "AI 合计",
}


def detect_timezone() -> str:
    try:
        resolved = os.path.realpath("/etc/localtime")
        marker = "/zoneinfo/"
        if marker in resolved:
            return resolved.split(marker, 1)[1]
    except OSError:
        pass
    return "Asia/Shanghai"


def render_bar(value: int, peak: int, width: int = 12) -> str:
    if peak <= 0 or value <= 0:
        return "░" * width
    eighths = round(value / peak * (width * 8))
    if eighths == 0 and value > 0:
        eighths = 1
    eighths = min(eighths, width * 8)
    full, rem = divmod(eighths, 8)
    partial = EIGHTHS[rem] if rem else ""
    empty = "░" * (width - full - (1 if rem else 0))
    return ("█" * full) + partial + empty


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


def render_card(label: str, daily_rows: list[tuple[str, int]], width: int = 12) -> str:
    if not daily_rows:
        return ""
    start_mmdd = f"{daily_rows[0][0][5:7]}/{daily_rows[0][0][8:10]}"
    end_mmdd = f"{daily_rows[-1][0][5:7]}/{daily_rows[-1][0][8:10]}"
    peak = max((val for _, val in daily_rows), default=0)
    total = sum(val for _, val in daily_rows)

    lines = [
        f"📊 {label} Token｜近{len(daily_rows)}日（{start_mmdd}–{end_mmdd}）",
        "日期 | 进度条         | Token",
    ]
    for day_iso, val in daily_rows:
        mmdd = f"{day_iso[5:7]}/{day_iso[8:10]}"
        lines.append(f"{mmdd} | {render_bar(val, peak, width)} | {format_cn_tokens(val)}")
    lines.append(f"{len(daily_rows)}日累计：约 {format_cn_tokens(total)} Token")
    lines.append("注：含缓存，按1万取整；进度按周峰值，每格含1/8刻度。")
    return "\n".join(lines)


def find_ccusage_cmd() -> list[str]:
    direct = shutil.which("ccusage")
    if direct:
        return [direct]
    npx_pattern = str(Path.home() / ".npm" / "_npx" / "*" / "node_modules" / "@ccusage" / "*" / "bin" / "ccusage")
    candidates = [
        Path(p)
        for p in glob.glob(npx_pattern)
        if os.path.isfile(p) and os.access(p, os.X_OK)
    ]
    if candidates:
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return [str(candidates[0])]
    if shutil.which("npx"):
        return ["npx", "-y", "ccusage@latest"]
    return []


def extract_json_object(raw: str) -> dict | None:
    if not raw:
        return None
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1 or end <= start:
        return None
    try:
        return json.loads(raw[start:end])
    except json.JSONDecodeError:
        return None


def run_ccusage_json(cmd: list[str], env_extra: dict[str, str] | None = None, timeout: int = 30) -> dict | None:
    env = {**os.environ, "NO_COLOR": "1", **(env_extra or {})}
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
    except OSError:
        return None
    try:
        out, _ = proc.communicate(timeout=timeout)
        if proc.returncode == 0:
            return extract_json_object(out)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            proc.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.communicate()
    return None


def empty_bucket() -> dict:
    return {
        "totalTokens": 0,
        "inputTokens": 0,
        "outputTokens": 0,
        "cacheReadTokens": 0,
        "cacheCreationTokens": 0,
        "totalCost": 0.0,
    }


def add_metrics(bucket: dict, src: dict) -> None:
    bucket["totalTokens"] += int(src.get("totalTokens", 0) or 0)
    bucket["inputTokens"] += int(src.get("inputTokens", 0) or 0)
    bucket["outputTokens"] += int(src.get("outputTokens", 0) or 0)
    bucket["cacheReadTokens"] += int(src.get("cacheReadTokens", 0) or 0)
    bucket["cacheCreationTokens"] += int(src.get("cacheCreationTokens", 0) or 0)
    bucket["totalCost"] += float(src.get("totalCost", 0.0) or 0.0)


def collect_via_ccusage(
    ccusage_cmd: list[str],
    since_iso: str,
    until_iso: str,
    tz: str,
) -> tuple[dict[str, dict[str, dict]], list[str]]:
    agents: dict[str, dict[str, dict]] = {}
    sources: list[str] = []

    unified = run_ccusage_json(
        [*ccusage_cmd, "daily", "--by-agent", "--json", "-O", "-z", tz, "-s", since_iso, "-u", until_iso]
    )
    if unified is None:
        return agents, sources

    sources.append("ccusage:daily:--by-agent")
    for row in unified.get("daily", []):
        day = row.get("period") or row.get("date")
        if not day:
            continue
        for ag_entry in row.get("agents", []):
            name = str(ag_entry.get("agent", "")).lower()
            if not name:
                continue
            bucket = agents.setdefault(name, {}).setdefault(day, empty_bucket())
            add_metrics(bucket, ag_entry)

    # Supplement T3 Code Antigravity ACP directories that ccusage's default path does not include.
    default_ag_real = (Path.home() / ".gemini" / "antigravity").resolve()
    t3_root = Path.home() / ".t3" / "userdata" / "providers" / "antigravity"
    seen_realpaths = {default_ag_real}
    if t3_root.is_dir():
        for candidate in sorted(t3_root.glob("*/antigravity-acp")):
            if not (candidate / "conversations").is_dir():
                continue
            resolved = candidate.resolve()
            if resolved in seen_realpaths:
                continue
            seen_realpaths.add(resolved)
            extra = run_ccusage_json(
                [*ccusage_cmd, "antigravity", "daily", "-j", "-O", "-z", tz, "-s", since_iso, "-u", until_iso],
                env_extra={"ANTIGRAVITY_DATA_DIR": str(candidate)},
            )
            if extra and extra.get("daily"):
                sources.append(f"ccusage:antigravity:{candidate.name}")
                for row in extra.get("daily", []):
                    day = row.get("date") or row.get("period")
                    if not day:
                        continue
                    bucket = agents.setdefault("antigravity", {}).setdefault(day, empty_bucket())
                    add_metrics(bucket, row)

    return agents, sources


def _read_codex_file_lines(path: Path) -> list[str]:
    if path.suffix == ".zst":
        zstd_bin = shutil.which("zstd")
        if not zstd_bin:
            return []
        try:
            proc = subprocess.run(
                [zstd_bin, "-dc", str(path)],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=20,
            )
            return proc.stdout.splitlines() if proc.returncode == 0 else []
        except (OSError, subprocess.TimeoutExpired):
            return []
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []


def collect_offline_fallback(since_iso: str, until_iso: str, tz_name: str) -> tuple[dict[str, dict[str, dict]], list[str]]:
    """Fallback direct parser for Codex JSONL/ZST and Claude JSONL logs."""
    tz = ZoneInfo(tz_name)
    agents: dict[str, dict[str, dict]] = {}
    sources: list[str] = []

    codex_root = Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex")) / "sessions"
    if codex_root.is_dir():
        found_codex = False
        start_d = date.fromisoformat(since_iso) - timedelta(days=1)
        end_d = date.fromisoformat(until_iso) + timedelta(days=1)
        cur = start_d
        while cur <= end_d:
            day_dir = codex_root / f"{cur.year:04d}" / f"{cur.month:02d}" / f"{cur.day:02d}"
            if day_dir.is_dir():
                for fpath in sorted(day_dir.iterdir()):
                    if not (fpath.name.endswith(".jsonl") or fpath.name.endswith(".jsonl.zst")):
                        continue
                    prev_total = 0
                    for line in _read_codex_file_lines(fpath):
                        if "token_count" not in line:
                            continue
                        try:
                            obj = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        payload = obj.get("payload") or {}
                        if payload.get("type") != "token_count":
                            continue
                        info = payload.get("info") or {}
                        ts = obj.get("timestamp")
                        if not ts:
                            continue
                        try:
                            dt_local = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(tz)
                        except ValueError:
                            continue
                        day_key = dt_local.strftime("%Y-%m-%d")
                        last_usage = info.get("last_token_usage") or {}
                        total_usage = info.get("total_token_usage") or {}
                        delta = 0
                        if last_usage.get("total_tokens"):
                            delta = int(last_usage["total_tokens"])
                        elif total_usage.get("total_tokens"):
                            tot = int(total_usage["total_tokens"])
                            delta = max(0, tot - prev_total)
                            prev_total = max(prev_total, tot)
                        if delta > 0 and since_iso <= day_key <= until_iso:
                            found_codex = True
                            bucket = agents.setdefault("codex", {}).setdefault(day_key, empty_bucket())
                            bucket["totalTokens"] += delta
                            bucket["inputTokens"] += int(last_usage.get("input_tokens", 0) or 0)
                            bucket["outputTokens"] += int(last_usage.get("output_tokens", 0) or 0)
                            bucket["cacheReadTokens"] += int(last_usage.get("cached_input_tokens", 0) or 0)
            cur += timedelta(days=1)
        if found_codex:
            sources.append("fallback:codex-sessions")

    return agents, sources


def compute_window(days: int, include_today: bool, end_date_str: str | None, tz_name: str) -> list[str]:
    if end_date_str:
        end_d = date.fromisoformat(end_date_str)
    else:
        now_local = datetime.now(ZoneInfo(tz_name)).date()
        end_d = now_local if include_today else now_local - timedelta(days=1)
    start_d = end_d - timedelta(days=days - 1)
    return [(start_d + timedelta(days=i)).isoformat() for i in range(days)]


def sort_agents(agent_names: list[str], totals: dict[str, int]) -> list[str]:
    def key(name: str) -> tuple[int, int, str]:
        if name in AGENT_ORDER:
            return (0, AGENT_ORDER.index(name), name)
        return (1, -totals.get(name, 0), name)

    return sorted(agent_names, key=key)


def build_report(
    days: int = 7,
    include_today: bool = False,
    end_date_str: str | None = None,
    agent_arg: str = "auto",
    tz_name: str | None = None,
    bar_width: int = 12,
) -> dict:
    tz = tz_name or detect_timezone()
    window = compute_window(days, include_today, end_date_str, tz)
    since_iso, until_iso = window[0], window[-1]

    ccusage_cmd = find_ccusage_cmd()
    agents_data: dict[str, dict[str, dict]] = {}
    sources: list[str] = []
    if ccusage_cmd:
        agents_data, sources = collect_via_ccusage(ccusage_cmd, since_iso, until_iso, tz)
    if not sources:
        agents_data, sources = collect_offline_fallback(since_iso, until_iso, tz)

    agent_totals = {
        ag: sum(day_map.get(day, {}).get("totalTokens", 0) for day in window)
        for ag, day_map in agents_data.items()
    }
    active_agents = sort_agents([ag for ag, tot in agent_totals.items() if tot > 0], agent_totals)

    requested = [part.strip().lower() for part in agent_arg.split(",") if part.strip()]
    cards: list[dict] = []

    def make_agent_card(ag_key: str, label: str, day_values: list[tuple[str, int]]) -> dict:
        return {
            "agent": ag_key,
            "label": label,
            "total_tokens": sum(v for _, v in day_values),
            "peak_tokens": max((v for _, v in day_values), default=0),
            "daily": [{"date": d, "tokens": v} for d, v in day_values],
            "text": render_card(label, day_values, width=bar_width),
        }

    combined_daily = [
        (day, sum(agents_data.get(ag, {}).get(day, {}).get("totalTokens", 0) for ag in active_agents))
        for day in window
    ]

    if requested == ["auto"] or not requested:
        if len(active_agents) >= 2:
            cards.append(make_agent_card("combined", AGENT_LABELS["combined"], combined_daily))
            for ag in active_agents:
                rows = [(d, agents_data[ag].get(d, {}).get("totalTokens", 0)) for d in window]
                cards.append(make_agent_card(ag, AGENT_LABELS.get(ag, ag.capitalize()), rows))
        elif len(active_agents) == 1:
            ag = active_agents[0]
            rows = [(d, agents_data[ag].get(d, {}).get("totalTokens", 0)) for d in window]
            cards.append(make_agent_card(ag, AGENT_LABELS.get(ag, ag.capitalize()), rows))
        else:
            cards.append(make_agent_card("combined", "AI", [(d, 0) for d in window]))
    elif requested == ["all"]:
        if len(active_agents) >= 2:
            cards.append(make_agent_card("combined", AGENT_LABELS["combined"], combined_daily))
        targets = active_agents or ["codex"]
        for ag in targets:
            rows = [(d, agents_data.get(ag, {}).get(d, {}).get("totalTokens", 0)) for d in window]
            cards.append(make_agent_card(ag, AGENT_LABELS.get(ag, ag.capitalize()), rows))
    else:
        if len(requested) >= 2:
            sub_combined = [
                (day, sum(agents_data.get(ag, {}).get(day, {}).get("totalTokens", 0) for ag in requested))
                for day in window
            ]
            cards.append(make_agent_card("combined", AGENT_LABELS["combined"], sub_combined))
        for ag in requested:
            rows = [(d, agents_data.get(ag, {}).get(d, {}).get("totalTokens", 0)) for d in window]
            cards.append(make_agent_card(ag, AGENT_LABELS.get(ag, ag.capitalize()), rows))

    return {
        "status": "ok",
        "generated_at": datetime.now(ZoneInfo(tz)).isoformat(timespec="seconds"),
        "timezone": tz,
        "window": {"since": since_iso, "until": until_iso, "days": days, "include_today": include_today},
        "sources": sources,
        "active_agents": active_agents,
        "agent_totals": agent_totals,
        "combined_total": sum(v for _, v in combined_daily),
        "cards": cards,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=7, help="Number of days in window (default: 7).")
    parser.add_argument("--include-today", action="store_true", help="End window on today instead of yesterday.")
    parser.add_argument("--end-date", help="Explicit end date YYYY-MM-DD.")
    parser.add_argument("--agent", default="auto", help="Agent filter: auto, all, codex, antigravity, claude, or csv.")
    parser.add_argument("--timezone", help="IANA timezone override.")
    parser.add_argument("--bar-width", type=int, default=12, help="Progress bar width in characters (default: 12).")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON output.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    report = build_report(
        days=args.days,
        include_today=args.include_today,
        end_date_str=args.end_date,
        agent_arg=args.agent,
        tz_name=args.timezone,
        bar_width=args.bar_width,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("\n\n".join(card["text"] for card in report["cards"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
