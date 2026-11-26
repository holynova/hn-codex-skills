#!/usr/bin/env python3
"""Safe Mole (mo clean + mo optimize) preview/apply wrapper with df -k verification."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]|\x1b\][^\x07]*\x07|\r")


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text or "")


def parse_df_k(output: str) -> dict | None:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if len(lines) < 2:
        return None
    parts = lines[-1].split()
    if len(parts) < 6:
        return None
    try:
        total_kb = int(parts[1])
        used_kb = int(parts[2])
        avail_kb = int(parts[3])
    except ValueError:
        return None
    capacity_pct = parts[4]
    mount_point = " ".join(parts[8:]) if len(parts) >= 9 else parts[-1]
    return {
        "filesystem": parts[0],
        "total_kb": total_kb,
        "used_kb": used_kb,
        "avail_kb": avail_kb,
        "avail_gb": round(avail_kb / (1024 * 1024), 2),
        "capacity_pct": capacity_pct,
        "mount_point": mount_point,
    }


def measure_volume(target: Path) -> dict | None:
    try:
        proc = subprocess.run(
            ["df", "-k", str(target)],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if proc.returncode == 0:
            return parse_df_k(proc.stdout)
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def find_mole() -> str | None:
    return shutil.which("mo") or shutil.which("mole")


def run_cmd(cmd: list[str], timeout: int) -> tuple[int, str, str, bool]:
    env = {
        **os.environ,
        "NONINTERACTIVE": "1",
        "NO_COLOR": "1",
        "TERM": "dumb",
        "SUDO_ASKPASS": "/usr/bin/false",
    }
    try:
        proc = subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        return proc.returncode, strip_ansi(proc.stdout), strip_ansi(proc.stderr), False
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode("utf-8", "replace")
        err = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr or b"").decode("utf-8", "replace")
        return 124, strip_ansi(out), strip_ansi(err), True
    except OSError as exc:
        return 127, "", str(exc), False


def parse_clean_output(text: str) -> dict:
    advisories: list[str] = []
    warnings: list[str] = []
    potential_space = None
    freed_space = None
    items = None
    categories = None
    clean_list_path = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("⊙"):
            advisories.append(line.lstrip("⊙").strip())
        elif line.startswith("◎") or "permission denied" in line.lower() or "eacces" in line.lower():
            warnings.append(line)

        m_pot = re.search(r"Potential space:\s*([^|\n]+)", line, re.I)
        if m_pot:
            potential_space = m_pot.group(1).strip()
        m_freed = re.search(r"(?:Removed|Space freed|Freed space|Total freed|Reclaimed):\s*([^|\n]+)", line, re.I)
        if m_freed:
            freed_space = m_freed.group(1).strip()
        m_items = re.search(r"(?:Items:\s*(\d+)|(\d+)\s*items\b)", line, re.I)
        if m_items:
            items = int(m_items.group(1) or m_items.group(2))
        m_cats = re.search(r"Categories:\s*(\d+)", line, re.I)
        if m_cats:
            categories = int(m_cats.group(1))
        m_list = re.search(r"Detailed file list:\s*(.+)$", line, re.I)
        if m_list:
            clean_list_path = m_list.group(1).strip()

    return {
        "potential_space": potential_space,
        "freed_space": freed_space,
        "items": items,
        "categories": categories,
        "clean_list_path": clean_list_path,
        "advisories": advisories,
        "warnings": warnings,
    }


def parse_optimize_output(text: str) -> dict:
    attention_items: list[str] = []
    planned_count = None
    applied_count = None
    summary_line = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("◎"):
            attention_items.append(line.lstrip("◎").strip())
        m_would = re.search(r"Would apply\s+(\d+)\s+optimization", line, re.I)
        if m_would:
            planned_count = int(m_would.group(1))
        m_applied = re.search(r"Applied\s+(\d+)\s+optimization", line, re.I)
        if m_applied:
            applied_count = int(m_applied.group(1))
        if "unchanged" in line.lower() and ("skipped" in line.lower() or "attention" in line.lower() or "failed" in line.lower()):
            summary_line = line

    return {
        "planned_count": planned_count,
        "applied_count": applied_count,
        "summary_line": summary_line,
        "attention_items": attention_items,
    }


def classify_clean_apply(rc: int, out: str, err: str, timed_out: bool) -> str:
    combined = f"{out}\n{err}".lower()
    if timed_out:
        return "timeout"
    if rc == 0:
        return "ok"
    if rc == 243 or "eacces" in combined or "permission" in combined or "cleaned" in combined or "freed" in combined:
        return "partial"
    return "failed"


def classify_optimize_apply(rc: int, out: str, err: str, timed_out: bool) -> str:
    combined = f"{out}\n{err}".lower()
    if timed_out:
        return "timeout"
    if "sudo" in combined or "password" in combined or "administrator" in combined or "requires root" in combined or "tty" in combined:
        if "applied" in combined or "refreshed" in combined or "optimized" in combined:
            return "partial_needs_admin"
        return "needs_admin"
    if rc == 0:
        return "ok"
    if "applied" in combined or "unchanged" in combined:
        return "partial"
    return "failed"


def execute(apply: bool, skip_clean: bool, skip_optimize: bool, timeout: int) -> dict:
    home = Path.home()
    before_disk = measure_volume(home)
    mo_bin = find_mole()

    report: dict = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "apply" if apply else "dry-run",
        "mole_bin": mo_bin,
        "mole_version": None,
        "before_disk": before_disk,
        "after_disk": before_disk,
        "observed_delta_kb": 0,
        "clean": {"status": "skipped"},
        "optimize": {"status": "skipped"},
        "status": "ok",
    }

    if not mo_bin:
        report["status"] = "failed"
        report["error"] = "Mole (mo / mole) not found on PATH."
        return report

    _, ver_out, _, _ = run_cmd([mo_bin, "--version"], timeout=15)
    for line in ver_out.splitlines():
        if "mole version" in line.lower():
            report["mole_version"] = line.strip()
            break
    if not report["mole_version"] and ver_out.strip():
        report["mole_version"] = ver_out.strip().splitlines()[0]

    if not skip_clean:
        rc, out, err, timed_out = run_cmd([mo_bin, "clean", "--dry-run"], timeout=timeout)
        parsed = parse_clean_output(out + "\n" + err)
        clean_res: dict = {
            "dry_run": {
                "returncode": rc,
                "timed_out": timed_out,
                **parsed,
                "tail": "\n".join((out or err).splitlines()[-25:]),
            }
        }
        if apply:
            arc, aout, aerr, atimed = run_cmd([mo_bin, "clean"], timeout=timeout)
            aparsed = parse_clean_output(aout + "\n" + aerr)
            clean_res["apply"] = {
                "returncode": arc,
                "timed_out": atimed,
                **aparsed,
                "tail": "\n".join((aout or aerr).splitlines()[-25:]),
            }
            clean_res["status"] = classify_clean_apply(arc, aout, aerr, atimed)
        else:
            clean_res["status"] = "preview_ok" if rc == 0 else ("timeout" if timed_out else "preview_partial")
        report["clean"] = clean_res

    if not skip_optimize:
        rc, out, err, timed_out = run_cmd([mo_bin, "optimize", "--dry-run"], timeout=timeout)
        parsed = parse_optimize_output(out + "\n" + err)
        opt_res: dict = {
            "dry_run": {
                "returncode": rc,
                "timed_out": timed_out,
                **parsed,
                "tail": "\n".join((out or err).splitlines()[-25:]),
            }
        }
        if apply:
            arc, aout, aerr, atimed = run_cmd([mo_bin, "optimize"], timeout=min(timeout, 120))
            aparsed = parse_optimize_output(aout + "\n" + aerr)
            opt_status = classify_optimize_apply(arc, aout, aerr, atimed)
            opt_res["apply"] = {
                "returncode": arc,
                "timed_out": atimed,
                **aparsed,
                "tail": "\n".join((aout or aerr).splitlines()[-25:]),
            }
            if "needs_admin" in opt_status:
                opt_res["manual_command"] = "mo optimize"
            opt_res["status"] = opt_status
        else:
            opt_res["status"] = "preview_ok" if rc in (0, 1) and not timed_out else ("timeout" if timed_out else "failed")
        report["optimize"] = opt_res

    after_disk = measure_volume(home)
    report["after_disk"] = after_disk
    if before_disk and after_disk:
        report["observed_delta_kb"] = after_disk["avail_kb"] - before_disk["avail_kb"]

    statuses = [report["clean"]["status"], report["optimize"]["status"]]
    if any(s == "failed" for s in statuses):
        report["status"] = "partial" if any(s in {"ok", "partial", "preview_ok", "partial_needs_admin"} for s in statuses) else "failed"
    elif any(s in {"partial", "timeout", "needs_admin", "partial_needs_admin", "preview_partial"} for s in statuses):
        report["status"] = "partial"
    return report


def format_kb(kb: int) -> str:
    sign = "+" if kb > 0 else ("-" if kb < 0 else "")
    abs_kb = abs(kb)
    if abs_kb >= 1024 * 1024:
        return f"{sign}{abs_kb / (1024 * 1024):.2f} GB"
    if abs_kb >= 1024:
        return f"{sign}{abs_kb / 1024:.1f} MB"
    return f"{sign}{abs_kb} KB"


def render_markdown(report: dict) -> str:
    lines = [
        f"## Mole 磁盘清理与优化（{report['mode']}）",
        "",
        f"- 工具：`{report.get('mole_bin') or 'missing'}`（{report.get('mole_version') or 'unknown'}）",
    ]
    before = report.get("before_disk")
    after = report.get("after_disk")
    if before and after:
        lines.append(
            f"- 目标卷 `{before['mount_point']}` 可用空间：`{before['avail_gb']:.2f} GB` -> `{after['avail_gb']:.2f} GB`（实测变化 `{format_kb(report['observed_delta_kb'])}`）"
        )

    clean = report.get("clean", {})
    if clean.get("status") != "skipped":
        dry = clean.get("dry_run", {})
        app = clean.get("apply")
        lines.append(
            f"- `mo clean` 状态：`{clean['status']}` | 预览估算：`{dry.get('potential_space') or '未知'}`（{dry.get('items') or '?'} 项）"
            + (f" | 实清释放：`{app.get('freed_space') or '见明细'}`" if app else "")
        )
        if dry.get("clean_list_path"):
            lines.append(f"  - 预览清单：`{dry['clean_list_path']}`")
        for adv in dry.get("advisories", []):
            lines.append(f"  - 未自动删除的大目录建议：`{adv}`")
        for warn in (app or dry).get("warnings", [])[:5]:
            lines.append(f"  - 跳过/受限提示：{warn}")

    opt = report.get("optimize", {})
    if opt.get("status") != "skipped":
        dry = opt.get("dry_run", {})
        app = opt.get("apply")
        lines.append(
            f"- `mo optimize` 状态：`{opt['status']}` | 预览建议优化项：`{dry.get('planned_count') if dry.get('planned_count') is not None else '?'}`"
            + (f" | 实际应用：`{app.get('applied_count') if app.get('applied_count') is not None else '见日志'}`" if app else "")
        )
        if opt.get("manual_command"):
            lines.append(f"  - 需交互/管理员权限，请按需在终端手动执行：`{opt['manual_command']}`")
        for item in dry.get("attention_items", [])[:5]:
            lines.append(f"  - 待关注项：{item}")

    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Execute mo clean and mo optimize (default: dry-run).")
    parser.add_argument("--skip-clean", action="store_true", help="Skip mo clean.")
    parser.add_argument("--skip-optimize", action="store_true", help="Skip mo optimize.")
    parser.add_argument("--timeout", type=int, default=420, help="Per-command timeout in seconds.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    report = execute(
        apply=args.apply,
        skip_clean=args.skip_clean,
        skip_optimize=args.skip_optimize,
        timeout=args.timeout,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(report))
    return 1 if report["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
