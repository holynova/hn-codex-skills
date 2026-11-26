#!/usr/bin/env python3
"""Update installed third-party skills and sync holynova/hn-codex-skills across agent dirs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

DEFAULT_REPO = "holynova/hn-codex-skills"


def resolve_skills_cli() -> list[str]:
    direct = shutil.which("skills")
    if direct:
        return [direct]
    if shutil.which("npx"):
        return ["npx", "-y", "skills"]
    return []


def discover_agent_dirs(home: Path | None = None) -> dict[str, Path]:
    base = home or Path.home()
    codex_dir = (Path(os.environ["CODEX_HOME"]) / "skills") if os.environ.get("CODEX_HOME") else (base / ".codex" / "skills")
    candidates = {
        "codex": codex_dir,
        "agents": base / ".agents" / "skills",
        "claude": base / ".claude" / "skills",
        "gemini": base / ".gemini" / "config" / "skills",
        "opencode": base / ".config" / "opencode" / "skills",
        "cursor": base / ".cursor" / "skills",
    }
    return {name: path for name, path in candidates.items() if path.exists()}


def read_skill_lock(lock_path: Path) -> dict[str, dict]:
    if not lock_path.is_file():
        return {}
    try:
        data = json.loads(lock_path.read_text(encoding="utf-8"))
        skills = data.get("skills", {})
        return skills if isinstance(skills, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def hash_skill_dir(skill_dir: Path) -> str:
    h = hashlib.sha256()
    if not skill_dir.exists():
        return ""
    for root, dirs, files in os.walk(skill_dir, followlinks=True):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        rel_root = os.path.relpath(root, skill_dir)
        for fname in sorted(files):
            if fname == ".DS_Store" or fname.startswith("."):
                continue
            fpath = Path(root) / fname
            rel_file = fname if rel_root == "." else os.path.join(rel_root, fname)
            h.update(rel_file.encode("utf-8"))
            h.update(b"\x00")
            try:
                h.update(fpath.read_bytes())
            except OSError:
                h.update(b"<unreadable>")
            h.update(b"\x00")
    return h.hexdigest()


def discover_repo_skills(repo_root: Path) -> tuple[list[str], list[str]]:
    skills_dir = repo_root / "skills"
    if not skills_dir.is_dir():
        raise FileNotFoundError(f"Missing skills directory in {repo_root}")

    active: list[str] = []
    for entry in sorted(skills_dir.iterdir(), key=lambda p: p.name):
        if entry.name.startswith(".") or not entry.is_dir():
            continue
        if (entry / "SKILL.md").is_file() and (entry / "agents" / "openai.yaml").is_file():
            active.append(entry.name)

    backup_dir = repo_root / "backup"
    archived: list[str] = []
    if backup_dir.is_dir():
        archived = sorted(
            e.name for e in backup_dir.iterdir() if e.is_dir() and not e.name.startswith(".")
        )
    return active, archived


def check_installer_allowlist(repo_root: Path, active_skills: list[str]) -> list[str]:
    installer = repo_root / "bin" / "install.mjs"
    if not installer.is_file():
        return []
    text = installer.read_text(encoding="utf-8")
    m = re.search(r"const\s+skillNames\s*=\s*\[(.*?)\];", text, re.S)
    if not m:
        return []
    listed = set(re.findall(r'"([^"]+)"', m.group(1)))
    missing = sorted(set(active_skills) - listed)
    return [f"bin/install.mjs missing skills: {', '.join(missing)}"] if missing else []


def run_cmd(cmd: list[str], timeout: int = 300) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "NO_COLOR": "1", "CI": "1"},
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout if isinstance(exc.stdout, str) else ""
        err = exc.stderr if isinstance(exc.stderr, str) else ""
        return 124, out, f"Timed out after {timeout}s\n{err}"
    except OSError as exc:
        return 127, "", str(exc)


def atomic_replace_dir(source_dir: Path, target_dir: Path) -> None:
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = Path(tempfile.mkdtemp(prefix=f".{target_dir.name}.sync-", dir=str(target_dir.parent)))
    shutil.rmtree(tmp_dir)
    shutil.copytree(source_dir, tmp_dir)
    backup_dir = None
    if target_dir.exists() or target_dir.is_symlink():
        backup_dir = target_dir.parent / f".{target_dir.name}.bak-{os.getpid()}"
        if backup_dir.exists() or backup_dir.is_symlink():
            if backup_dir.is_symlink() or backup_dir.is_file():
                backup_dir.unlink()
            else:
                shutil.rmtree(backup_dir)
        target_dir.rename(backup_dir)
    try:
        tmp_dir.rename(target_dir)
    except Exception:
        if backup_dir and backup_dir.exists():
            backup_dir.rename(target_dir)
        raise
    if backup_dir and backup_dir.exists():
        if backup_dir.is_symlink() or backup_dir.is_file():
            backup_dir.unlink()
        else:
            shutil.rmtree(backup_dir)


def ensure_symlink(source_dir: Path, link_path: Path) -> bool:
    """Ensure link_path is a symlink resolving to source_dir. Returns True if changed."""
    desired_resolved = source_dir.resolve()
    if link_path.is_symlink():
        try:
            if link_path.resolve() == desired_resolved and link_path.exists():
                return False
        except OSError:
            pass
        link_path.unlink()
    elif link_path.exists():
        if link_path.is_dir():
            shutil.rmtree(link_path)
        else:
            link_path.unlink()
    link_path.parent.mkdir(parents=True, exist_ok=True)
    os.symlink(source_dir, link_path)
    return True


def classify_repo_diff(
    repo_root: Path,
    active_skills: list[str],
    agent_dirs: dict[str, Path],
) -> tuple[list[str], list[str], list[str]]:
    added: list[str] = []
    updated: list[str] = []
    unchanged: list[str] = []

    primary_dirs = [agent_dirs[k] for k in ("codex", "agents") if k in agent_dirs] or list(agent_dirs.values())
    for name in active_skills:
        src_hash = hash_skill_dir(repo_root / "skills" / name)
        missing_primary = any(not (adir / name).exists() for adir in primary_dirs)
        missing_any = any(not (adir / name).exists() for adir in agent_dirs.values())
        changed_any = any(
            (adir / name).exists() and hash_skill_dir(adir / name) != src_hash
            for adir in agent_dirs.values()
        )
        if missing_primary:
            added.append(name)
        elif missing_any or changed_any:
            updated.append(name)
        else:
            unchanged.append(name)
    return added, updated, unchanged


def sync_all(
    apply: bool,
    repo: str,
    local_repo: str | None,
    skip_third_party: bool,
    skip_hn_skills: bool,
    home: Path | None = None,
) -> dict:
    base_home = home or Path.home()
    agent_dirs = discover_agent_dirs(base_home)
    lock_path = base_home / ".agents" / ".skill-lock.json"
    skills_cli = resolve_skills_cli()

    lock_before = read_skill_lock(lock_path)
    external_symlinks: list[dict] = []
    agents_dir = agent_dirs.get("agents")
    if agents_dir and agents_dir.is_dir():
        for entry in sorted(agents_dir.iterdir(), key=lambda p: p.name):
            if entry.is_symlink():
                external_symlinks.append({"name": entry.name, "target": os.readlink(entry)})

    third_party_before = {
        k: v for k, v in lock_before.items() if v.get("source") != repo
    }

    report: dict = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "apply" if apply else "dry-run",
        "repo": repo,
        "agent_dirs": {k: str(v) for k, v in agent_dirs.items()},
        "external_managed": external_symlinks,
        "third_party": {
            "status": "skipped" if skip_third_party else "preview",
            "tracked_count": len(third_party_before),
            "updated": [],
            "unchanged": sorted(third_party_before.keys()),
            "output": "",
        },
        "hn_skills": {
            "status": "skipped" if skip_hn_skills else "preview",
            "active_count": 0,
            "added": [],
            "updated": [],
            "unchanged": [],
            "symlink_repairs": [],
            "warnings": [],
            "archived_present": [],
        },
        "status": "ok",
    }

    # 1. Third-party skills update
    if not skip_third_party:
        if apply:
            if not skills_cli:
                report["third_party"]["status"] = "failed"
                report["third_party"]["output"] = "skills CLI not found."
            else:
                rc, out, err = run_cmd([*skills_cli, "update", "-g", "-y"], timeout=600)
                lock_after = read_skill_lock(lock_path)
                updated_tp: list[str] = []
                unchanged_tp: list[str] = []
                for name, prev in sorted(third_party_before.items()):
                    cur = lock_after.get(name, {})
                    if (
                        cur.get("skillFolderHash") != prev.get("skillFolderHash")
                        or cur.get("updatedAt") != prev.get("updatedAt")
                    ):
                        updated_tp.append(name)
                    else:
                        unchanged_tp.append(name)
                report["third_party"]["updated"] = updated_tp
                report["third_party"]["unchanged"] = unchanged_tp
                report["third_party"]["returncode"] = rc
                report["third_party"]["output"] = (out or err)[-2000:]
                report["third_party"]["status"] = "ok" if rc == 0 else "partial"

    # 2. Personal GitHub skills sync
    if not skip_hn_skills:
        tmp_clone: Path | None = None
        try:
            if local_repo:
                source_root = Path(local_repo).resolve()
            else:
                tmp_clone = Path(tempfile.mkdtemp(prefix="hn-skills-sync-"))
                clone_url = f"https://github.com/{repo}.git"
                rc, out, err = run_cmd(["git", "clone", "--depth", "1", "--quiet", clone_url, str(tmp_clone)], timeout=180)
                if rc != 0:
                    raise RuntimeError(f"git clone {clone_url} failed (rc={rc}): {err or out}")
                source_root = tmp_clone

            active_skills, archived_skills = discover_repo_skills(source_root)
            report["hn_skills"]["active_count"] = len(active_skills)
            report["hn_skills"]["warnings"].extend(check_installer_allowlist(source_root, active_skills))

            added, updated, unchanged = classify_repo_diff(source_root, active_skills, agent_dirs)
            report["hn_skills"]["added"] = added
            report["hn_skills"]["updated"] = updated
            report["hn_skills"]["unchanged"] = unchanged

            if apply:
                # 2A. Codex dir via bin/install.mjs when available, else atomic copy
                codex_dir = agent_dirs.get("codex")
                if codex_dir is not None:
                    installer_js = source_root / "bin" / "install.mjs"
                    node_bin = shutil.which("node")
                    if installer_js.is_file() and node_bin and not report["hn_skills"]["warnings"]:
                        rc, out, err = run_cmd(
                            [node_bin, str(installer_js), "install", "--force", "--path", str(codex_dir)],
                            timeout=180,
                        )
                        if rc != 0:
                            report["hn_skills"]["warnings"].append(f"install.mjs failed (rc={rc}); fell back to atomic copy: {err or out}")
                            for name in active_skills:
                                atomic_replace_dir(source_root / "skills" / name, codex_dir / name)
                    else:
                        for name in active_skills:
                            atomic_replace_dir(source_root / "skills" / name, codex_dir / name)

                # 2B. ~/.agents/skills + lockfile update via skills add (only when running against real home & skills CLI)
                agents_dir = agent_dirs.get("agents")
                if agents_dir is not None:
                    if skills_cli and home is None:
                        add_source = str(source_root) if local_repo else repo
                        agent_flags: list[str] = []
                        if "claude" in agent_dirs:
                            agent_flags.extend(["claude-code"])
                        if "gemini" in agent_dirs:
                            agent_flags.extend(["antigravity", "antigravity-cli"])
                        agent_flags.append("cline")
                        cmd = [*skills_cli, "add", add_source, "-g", "-y", "-s", *active_skills, "-a", *agent_flags]
                        rc, out, err = run_cmd(cmd, timeout=300)
                        if rc != 0:
                            report["hn_skills"]["warnings"].append(f"skills add returned rc={rc}; reconciled directly.")

                    # Reconcile every allowlisted skill inside ~/.agents/skills
                    for name in active_skills:
                        src_skill = source_root / "skills" / name
                        dst_skill = agents_dir / name
                        if not dst_skill.exists() or hash_skill_dir(dst_skill) != hash_skill_dir(src_skill):
                            atomic_replace_dir(src_skill, dst_skill)

                    # Reconcile symlinks in claude / gemini / opencode / cursor
                    for agent_key in ("claude", "gemini", "opencode", "cursor"):
                        adir = agent_dirs.get(agent_key)
                        if adir is None:
                            continue
                        for name in active_skills:
                            if ensure_symlink(agents_dir / name, adir / name):
                                report["hn_skills"]["symlink_repairs"].append(f"{agent_key}:{name}")

                # Verify no archived skill leaked into any target dir
                leaked: list[str] = []
                for agent_key, adir in agent_dirs.items():
                    for arch in archived_skills:
                        if (adir / arch).exists():
                            leaked.append(f"{agent_key}:{arch}")
                report["hn_skills"]["archived_present"] = leaked
                report["hn_skills"]["status"] = "partial" if leaked else "ok"
        except Exception as exc:
            report["hn_skills"]["status"] = "failed"
            report["hn_skills"]["error"] = str(exc)
        finally:
            if tmp_clone and tmp_clone.exists():
                shutil.rmtree(tmp_clone, ignore_errors=True)

    statuses = [report["third_party"]["status"], report["hn_skills"]["status"]]
    if any(s == "failed" for s in statuses):
        report["status"] = "partial" if any(s in {"ok", "partial", "preview"} for s in statuses) else "failed"
    elif any(s == "partial" for s in statuses):
        report["status"] = "partial"
    return report


def render_markdown(report: dict) -> str:
    lines = [
        f"## Skills 同步与更新（{report['mode']}）",
        "",
        f"- 个人仓库：`{report['repo']}`",
        f"- 目标目录：{', '.join(f'`{k}`' for k in report['agent_dirs'])}",
    ]
    tp = report["third_party"]
    if tp["status"] != "skipped":
        lines.append(
            f"- 第三方 skills（{tp['tracked_count']} 个）：状态 `{tp['status']}` | "
            f"已更新 {len(tp['updated'])} 个{('（' + ', '.join(tp['updated']) + '）') if tp['updated'] else ''} | "
            f"已是最新 {len(tp['unchanged'])} 个"
        )
    if report["external_managed"]:
        ext = ", ".join(e["name"] for e in report["external_managed"])
        lines.append(f"- 外部托管软链（保留不覆盖）：`{ext}`")

    hn = report["hn_skills"]
    if hn["status"] != "skipped":
        lines.append(
            f"- 个人仓库 skills（共 {hn['active_count']} 个正式技能）：状态 `{hn['status']}` | "
            f"新增 {len(hn['added'])} | 更新 {len(hn['updated'])} | 未变 {len(hn['unchanged'])}"
        )
        if hn["added"]:
            lines.append(f"  - 新增：{', '.join(f'`{s}`' for s in hn['added'])}")
        if hn["updated"]:
            lines.append(f"  - 更新：{', '.join(f'`{s}`' for s in hn['updated'])}")
        if hn["symlink_repairs"]:
            lines.append(f"  - 补齐/修复代理软链：{len(hn['symlink_repairs'])} 处")
        for warn in hn.get("warnings", []):
            lines.append(f"  - 提示：{warn}")
        if hn.get("error"):
            lines.append(f"  - 错误：{hn['error']}")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Apply updates and sync (default: dry-run).")
    parser.add_argument("--repo", default=os.environ.get("HN_SKILLS_REPO", DEFAULT_REPO), help="GitHub owner/repo.")
    parser.add_argument("--local-repo", help="Use a local repository directory instead of cloning GitHub.")
    parser.add_argument("--skip-third-party", action="store_true", help="Skip updating third-party skills.")
    parser.add_argument("--skip-hn-skills", action="store_true", help="Skip syncing personal GitHub skills repo.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    report = sync_all(
        apply=args.apply,
        repo=args.repo,
        local_repo=args.local_repo,
        skip_third_party=args.skip_third_party,
        skip_hn_skills=args.skip_hn_skills,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(report))
    return 1 if report["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
