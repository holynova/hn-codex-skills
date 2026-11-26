#!/usr/bin/env python3
"""Inventory and concurrently upgrade installed AI CLIs, Mole, skills CLI, and AI apps."""

from __future__ import annotations

import argparse
import json
import os
import plistlib
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

CATALOG_PATH = Path(__file__).resolve().parents[1] / "references" / "software-catalog.json"

SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+.*)?$")


def load_catalog(path: Path | None = None) -> dict:
    target = path or CATALOG_PATH
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def match_catalog_name(full_name: str, catalog: set[str]) -> bool:
    lowered = full_name.strip().lower()
    if not lowered:
        return False
    short = lowered.rsplit("/", 1)[-1]
    stem = short.split("@", 1)[0]
    return lowered in catalog or short in catalog or stem in catalog


def matches_only(name: str, only: set[str]) -> bool:
    if not only:
        return True
    lowered = name.strip().lower()
    short = lowered.rsplit("/", 1)[-1]
    stem = short.split("@", 1)[0]
    for token in only:
        if token in lowered or token in short or token in stem:
            return True
        if token == "mo" and stem == "mole":
            return True
    return False


def parse_semver(ver: str) -> tuple[tuple[int, ...], tuple[tuple[int, int | str], ...]] | None:
    m = SEMVER_RE.match((ver or "").strip())
    if not m:
        return None
    nums = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    pre_raw = m.group(4)
    if not pre_raw:
        return (nums, ())
    pre_parts: list[tuple[int, int | str]] = []
    for part in pre_raw.split("."):
        if part.isdigit():
            pre_parts.append((0, int(part)))
        else:
            pre_parts.append((1, part))
    return (nums, tuple(pre_parts))


def is_newer_version(installed: str, candidate: str) -> bool:
    ins = (installed or "").strip()
    cand = (candidate or "").strip()
    if not cand or ins == cand:
        return False
    p_ins = parse_semver(ins)
    p_cand = parse_semver(cand)
    if p_ins is None or p_cand is None:
        return ins != cand
    ins_nums, ins_pre = p_ins
    cand_nums, cand_pre = p_cand
    if cand_nums != ins_nums:
        return cand_nums > ins_nums
    if not ins_pre and not cand_pre:
        return False
    if not ins_pre and cand_pre:
        return False
    if ins_pre and not cand_pre:
        return True
    return cand_pre > ins_pre


def run_cmd(
    cmd: list[str],
    *,
    timeout: int = 300,
    env_extra: dict[str, str] | None = None,
) -> tuple[int, str, str]:
    env = {
        **os.environ,
        "NONINTERACTIVE": "1",
        "NO_COLOR": "1",
        "SUDO_ASKPASS": "/usr/bin/false",
        **(env_extra or {}),
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
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout if isinstance(exc.stdout, str) else ""
        err = exc.stderr if isinstance(exc.stderr, str) else ""
        return 124, out, f"Timed out after {timeout}s\n{err}"
    except OSError as exc:
        return 127, "", str(exc)


def extract_json(raw: str):
    if not raw:
        return None
    for open_ch, close_ch in (("{", "}"), ("[", "]")):
        idx = raw.find(open_ch)
        if idx != -1:
            end = raw.rfind(close_ch) + 1
            if end > idx:
                try:
                    return json.loads(raw[idx:end])
                except json.JSONDecodeError:
                    pass
    return None


HEAVY_SOURCE_BUILD_FORMULAE = {"llvm", "rust", "gcc", "cmake", "go", "zig", "node"}


def detect_heavy_brew_source_build(dry_run_output: str) -> list[str]:
    """Parse `brew upgrade --dry-run` output for formulae that would build from source."""
    lines = dry_run_output.splitlines()
    building: list[str] = []
    in_section = False
    for raw in lines:
        stripped = raw.strip()
        if re.match(r"^==>\s*\d+\s+.*would build from source", stripped, re.I):
            in_section = True
            continue
        if in_section:
            if not stripped or stripped.startswith("==>") or stripped.startswith("This is ") or stripped.startswith("Please "):
                in_section = False
                continue
            building.append(stripped)
    if len(building) >= 3 or any(b.lower().split("@", 1)[0] in HEAVY_SOURCE_BUILD_FORMULAE for b in building):
        return building
    return []


def fetch_npm_latest_tag(pkg: str) -> str | None:
    rc, out, _ = run_cmd(["npm", "view", pkg, "dist-tags", "--json"], timeout=30)
    if rc == 0:
        tags = extract_json(out)
        if isinstance(tags, dict):
            latest = tags.get("latest")
            if isinstance(latest, str) and latest:
                return latest
    rc2, out2, _ = run_cmd(["npm", "view", pkg, "version"], timeout=30)
    if rc2 == 0 and out2.strip():
        return out2.strip().splitlines()[-1].strip()
    return None


def lane_homebrew(catalog: dict, apply: bool, only: set[str], no_casks: bool) -> dict:
    res: dict = {"lane": "homebrew", "upgraded": [], "outdated": [], "already_latest": [], "issues": [], "managed_apps": set()}
    if sys.platform != "darwin" or not shutil.which("brew"):
        return res

    brew_env = {"HOMEBREW_NO_AUTO_UPDATE": "1"}
    if apply:
        rc_upd, _, err_upd = run_cmd(["brew", "update"], timeout=600, env_extra={"HOMEBREW_NO_AUTO_UPDATE": "0"})
        if rc_upd != 0:
            res["issues"].append({"name": "brew update", "manager": "homebrew", "message": (err_upd or "brew update failed").strip()[-300:]})

    rc_f, out_f, _ = run_cmd(["brew", "list", "--formula", "--full-name"], timeout=60, env_extra=brew_env)
    installed_formulae = [line.strip() for line in out_f.splitlines() if line.strip()] if rc_f == 0 else []

    rc_c, out_c, _ = run_cmd(["brew", "list", "--cask", "--full-name"], timeout=60, env_extra=brew_env)
    installed_casks = [line.strip() for line in out_c.splitlines() if line.strip()] if rc_c == 0 else []

    formula_cat = {x.lower() for x in catalog.get("homebrew_formulae", [])}
    cask_cat = {x.lower() for x in catalog.get("homebrew_casks", [])}
    cask_to_apps = catalog.get("cask_to_app_names", {})

    matched_formulae = [f for f in installed_formulae if match_catalog_name(f, formula_cat) and matches_only(f, only)]
    matched_casks = [c for c in installed_casks if match_catalog_name(c, cask_cat)]
    for c in matched_casks:
        short_c = c.lower().rsplit("/", 1)[-1].split("@", 1)[0]
        for app_name in cask_to_apps.get(c.lower(), cask_to_apps.get(short_c, [])):
            res["managed_apps"].add(app_name)
    matched_casks = [c for c in matched_casks if matches_only(c, only)]

    rc_o, out_o, _ = run_cmd(["brew", "outdated", "--json=v2", "--greedy"], timeout=120, env_extra=brew_env)
    outdated_data = extract_json(out_o) if rc_o == 0 else {}
    if not isinstance(outdated_data, dict):
        outdated_data = {}

    outdated_formula_map = {
        str(item.get("name", "")).lower().rsplit("/", 1)[-1]: item
        for item in outdated_data.get("formulae", [])
        if isinstance(item, dict)
    }
    outdated_cask_map = {
        str(item.get("name", "")).lower().rsplit("/", 1)[-1]: item
        for item in outdated_data.get("casks", [])
        if isinstance(item, dict)
    }

    formula_versions: dict[str, str] = {}
    if matched_formulae:
        rc_v, out_v, _ = run_cmd(["brew", "list", "--versions", *matched_formulae], timeout=60, env_extra=brew_env)
        if rc_v == 0:
            for line in out_v.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    formula_versions[parts[0].lower()] = parts[-1]

    cask_versions: dict[str, str] = {}
    if matched_casks:
        rc_cv, out_cv, _ = run_cmd(["brew", "list", "--cask", "--versions", *matched_casks], timeout=60, env_extra=brew_env)
        if rc_cv == 0:
            for line in out_cv.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    cask_versions[parts[0].lower()] = parts[-1]

    for full_name in matched_formulae:
        short = full_name.lower().rsplit("/", 1)[-1]
        out_item = outdated_formula_map.get(short)
        if not out_item:
            res["already_latest"].append({"name": full_name, "manager": "brew-formula", "version": formula_versions.get(short, "?")})
            continue
        before = ", ".join(out_item.get("installed_versions", [])) or formula_versions.get(short, "?")
        latest = str(out_item.get("current_version", "?"))
        if not apply:
            res["outdated"].append({"name": full_name, "manager": "brew-formula", "before": before, "latest": latest})
            continue
        rc_dry, dry_out, dry_err = run_cmd(["brew", "upgrade", "--dry-run", full_name], timeout=60, env_extra=brew_env)
        heavy_src = detect_heavy_brew_source_build(f"{dry_out}\n{dry_err}") if rc_dry == 0 else []
        if heavy_src:
            preview_names = ", ".join(heavy_src[:6]) + (f" 等共 {len(heavy_src)} 项" if len(heavy_src) > 6 else "")
            res["issues"].append({
                "name": full_name,
                "manager": "brew-formula",
                "message": f"needs_manual: 无预编译 bottle，需从源码编译 {preview_names}（已跳过以免耗时卡死，可手动执行 brew upgrade {full_name}）",
            })
            continue
        rc_u, u_out, u_err = run_cmd(["brew", "upgrade", full_name], timeout=300, env_extra=brew_env)
        _, v_out, _ = run_cmd(["brew", "list", "--versions", full_name], timeout=30, env_extra=brew_env)
        after = v_out.split()[-1] if v_out.split() else latest
        if rc_u == 0:
            res["upgraded"].append({"name": full_name, "manager": "brew-formula", "before": before, "after": after})
        else:
            res["issues"].append({"name": full_name, "manager": "brew-formula", "message": (u_err or u_out).strip()[-300:]})

    if not no_casks:
        for full_name in matched_casks:
            short = full_name.lower().rsplit("/", 1)[-1]
            out_item = outdated_cask_map.get(short)
            if not out_item:
                res["already_latest"].append({"name": full_name, "manager": "brew-cask", "version": cask_versions.get(short, "?")})
                continue
            before = ", ".join(out_item.get("installed_versions", [])) or cask_versions.get(short, "?")
            latest = str(out_item.get("current_version", "?"))
            if not apply:
                res["outdated"].append({"name": full_name, "manager": "brew-cask", "before": before, "latest": latest})
                continue
            rc_u, u_out, u_err = run_cmd(["brew", "upgrade", "--cask", "--greedy", full_name], timeout=300, env_extra=brew_env)
            combined = f"{u_out}\n{u_err}"
            if rc_u == 0:
                _, cv_out, _ = run_cmd(["brew", "list", "--cask", "--versions", full_name], timeout=30, env_extra=brew_env)
                after = cv_out.split()[-1] if cv_out.split() else latest
                res["upgraded"].append({"name": full_name, "manager": "brew-cask", "before": before, "after": after})
            else:
                low = combined.lower()
                tag = "needs_manual (需密码或应用正在运行)" if any(k in low for k in ("sudo", "password", "running", "in use", "quit")) else "upgrade_failed"
                res["issues"].append({"name": full_name, "manager": "brew-cask", "message": f"{tag}: {combined.strip()[-240:]}"})
    return res


def lane_npm(catalog: dict, apply: bool, only: set[str]) -> dict:
    res: dict = {"lane": "npm", "upgraded": [], "outdated": [], "already_latest": [], "issues": [], "managed_pkgs": set()}
    if not shutil.which("npm"):
        return res

    rc, out, _ = run_cmd(["npm", "list", "-g", "--depth=0", "--json"], timeout=60)
    data = extract_json(out) if rc in (0, 1) else None
    deps = data.get("dependencies", {}) if isinstance(data, dict) else {}
    pkg_set = {p.lower() for p in catalog.get("js_packages", [])}

    for pkg_name, meta in sorted(deps.items()):
        if not isinstance(meta, dict):
            continue
        if pkg_name.lower() not in pkg_set:
            continue
        if str(meta.get("resolved", "")).startswith("file:"):
            continue
        res["managed_pkgs"].add(pkg_name.lower())
        if not matches_only(pkg_name, only):
            continue
        installed = str(meta.get("version", ""))
        latest = fetch_npm_latest_tag(pkg_name)
        if not latest:
            res["issues"].append({"name": pkg_name, "manager": "npm", "message": "无法查询 npm 最新版本"})
            continue
        if not is_newer_version(installed, latest):
            res["already_latest"].append({"name": pkg_name, "manager": "npm", "version": installed})
            continue
        if not apply:
            res["outdated"].append({"name": pkg_name, "manager": "npm", "before": installed, "latest": latest})
            continue
        rc_i, i_out, i_err = run_cmd(["npm", "install", "-g", f"{pkg_name}@latest"], timeout=300)
        if rc_i == 0:
            _, out2, _ = run_cmd(["npm", "list", "-g", pkg_name, "--depth=0", "--json"], timeout=30)
            d2 = extract_json(out2)
            after = ((d2 or {}).get("dependencies") or {}).get(pkg_name, {}).get("version", latest)
            res["upgraded"].append({"name": pkg_name, "manager": "npm", "before": installed, "after": after})
        else:
            res["issues"].append({"name": pkg_name, "manager": "npm", "message": (i_err or i_out).strip()[-240:]})
    return res


def discover_legacy_pnpm_v5(catalog: dict, active_pnpm_pkgs: set[str], npm_pkgs: set[str]) -> dict[str, str]:
    """Detect legacy ~/Library/pnpm/global/5 tools not yet managed in active pnpm global store."""
    found: dict[str, str] = {}
    v5_pkg_json = Path.home() / "Library" / "pnpm" / "global" / "5" / "package.json"
    if not v5_pkg_json.is_file():
        return found
    try:
        v5_deps = json.loads(v5_pkg_json.read_text(encoding="utf-8")).get("dependencies", {})
    except (OSError, json.JSONDecodeError):
        return found

    bin_map = catalog.get("legacy_pnpm_bin_to_pkg", {})
    pnpm_root = str((Path.home() / "Library" / "pnpm").resolve())
    for bin_name, pkg_name in bin_map.items():
        if pkg_name.lower() in active_pnpm_pkgs or pkg_name.lower() in npm_pkgs:
            continue
        if pkg_name not in v5_deps:
            continue
        which_path = shutil.which(bin_name)
        if not which_path:
            continue
        try:
            resolved_parent = str(Path(which_path).parent.resolve())
        except OSError:
            continue
        if not resolved_parent.startswith(pnpm_root):
            continue
        nm_pkg = Path.home() / "Library" / "pnpm" / "global" / "5" / "node_modules" / pkg_name / "package.json"
        ver = ""
        if nm_pkg.is_file():
            try:
                ver = str(json.loads(nm_pkg.read_text(encoding="utf-8")).get("version", ""))
            except (OSError, json.JSONDecodeError):
                ver = ""
        if not ver:
            ver = str(v5_deps.get(pkg_name, "")).lstrip("^~")
        found[pkg_name] = ver
    return found


def lane_pnpm(catalog: dict, apply: bool, only: set[str], npm_pkgs: set[str]) -> dict:
    res: dict = {"lane": "pnpm", "upgraded": [], "outdated": [], "already_latest": [], "issues": []}
    if not shutil.which("pnpm"):
        return res

    rc, out, _ = run_cmd(["pnpm", "list", "-g", "--depth=0", "--json"], timeout=60)
    data = extract_json(out) if rc == 0 else None
    deps: dict[str, str] = {}
    if isinstance(data, list):
        for store in data:
            if isinstance(store, dict):
                for pkg_name, meta in (store.get("dependencies") or {}).items():
                    if isinstance(meta, dict) and meta.get("version"):
                        deps[pkg_name] = str(meta["version"])
    elif isinstance(data, dict):
        for pkg_name, meta in (data.get("dependencies") or {}).items():
            if isinstance(meta, dict) and meta.get("version"):
                deps[pkg_name] = str(meta["version"])

    pkg_set = {p.lower() for p in catalog.get("js_packages", [])}
    active_matched = {k: v for k, v in deps.items() if k.lower() in pkg_set}

    legacy = discover_legacy_pnpm_v5(catalog, {k.lower() for k in active_matched}, npm_pkgs)
    for k, v in legacy.items():
        active_matched.setdefault(k, v)

    for pkg_name, installed in sorted(active_matched.items()):
        if not matches_only(pkg_name, only):
            continue
        latest = fetch_npm_latest_tag(pkg_name)
        if not latest:
            res["issues"].append({"name": pkg_name, "manager": "pnpm", "message": "无法查询 npm 最新版本"})
            continue
        if not is_newer_version(installed, latest):
            res["already_latest"].append({"name": pkg_name, "manager": "pnpm", "version": installed})
            continue
        if not apply:
            res["outdated"].append({"name": pkg_name, "manager": "pnpm", "before": installed, "latest": latest})
            continue
        rc_i, i_out, i_err = run_cmd(["pnpm", "add", "-g", f"{pkg_name}@latest"], timeout=300)
        if rc_i == 0:
            _, out2, _ = run_cmd(["pnpm", "list", "-g", "--depth=0", "--json"], timeout=30)
            d2 = extract_json(out2)
            after = latest
            if isinstance(d2, list):
                for store in d2:
                    v = ((store or {}).get("dependencies") or {}).get(pkg_name, {}).get("version")
                    if v:
                        after = str(v)
            res["upgraded"].append({"name": pkg_name, "manager": "pnpm", "before": installed, "after": after})
        else:
            res["issues"].append({"name": pkg_name, "manager": "pnpm", "message": (i_err or i_out).strip()[-240:]})
    return res


def lane_python_and_cargo(catalog: dict, apply: bool, only: set[str]) -> dict:
    res: dict = {"lane": "python-cargo", "upgraded": [], "outdated": [], "already_latest": [], "issues": []}

    if shutil.which("uv"):
        rc, out, _ = run_cmd(["uv", "tool", "list"], timeout=60)
        uv_cat = {x.lower() for x in catalog.get("uv_tools", [])}
        if rc == 0:
            for line in out.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("-"):
                    continue
                parts = stripped.split()
                pkg = parts[0]
                ver = parts[1].lstrip("v") if len(parts) > 1 else "?"
                if pkg.lower() not in uv_cat or not matches_only(pkg, only):
                    continue
                if not apply:
                    res["outdated"].append({"name": pkg, "manager": "uv", "before": ver, "latest": "check via uv tool upgrade"})
                    continue
                rc_u, u_out, u_err = run_cmd(["uv", "tool", "upgrade", pkg], timeout=300)
                combined = f"{u_out}\n{u_err}"
                if rc_u == 0:
                    if "nothing to upgrade" in combined.lower():
                        res["already_latest"].append({"name": pkg, "manager": "uv", "version": ver})
                    else:
                        _, out2, _ = run_cmd(["uv", "tool", "list"], timeout=30)
                        after = ver
                        for l2 in out2.splitlines():
                            p2 = l2.strip().split()
                            if len(p2) >= 2 and p2[0] == pkg:
                                after = p2[1].lstrip("v")
                                break
                        res["upgraded"].append({"name": pkg, "manager": "uv", "before": ver, "after": after})
                else:
                    res["issues"].append({"name": pkg, "manager": "uv", "message": combined.strip()[-240:]})

    if shutil.which("pipx"):
        rc, out, _ = run_cmd(["pipx", "list", "--short"], timeout=60)
        pipx_cat = {x.lower() for x in catalog.get("pipx_packages", [])}
        if rc == 0:
            for line in out.splitlines():
                parts = line.strip().split()
                if not parts:
                    continue
                pkg = parts[0]
                ver = parts[1] if len(parts) > 1 else "?"
                if pkg.lower() not in pipx_cat or not matches_only(pkg, only):
                    continue
                if not apply:
                    res["outdated"].append({"name": pkg, "manager": "pipx", "before": ver, "latest": "check via pipx upgrade"})
                    continue
                rc_u, u_out, u_err = run_cmd(["pipx", "upgrade", pkg], timeout=300)
                combined = f"{u_out}\n{u_err}"
                if rc_u == 0:
                    if "already at latest" in combined.lower():
                        res["already_latest"].append({"name": pkg, "manager": "pipx", "version": ver})
                    else:
                        res["upgraded"].append({"name": pkg, "manager": "pipx", "before": ver, "after": "upgraded"})
                else:
                    res["issues"].append({"name": pkg, "manager": "pipx", "message": combined.strip()[-240:]})

    crates_toml = Path.home() / ".cargo" / ".crates.toml"
    if shutil.which("cargo") and crates_toml.is_file():
        cargo_cat = {x.lower() for x in catalog.get("cargo_crates", [])}
        text = crates_toml.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            if "=" not in line:
                continue
            crate = line.split()[0].strip('"')
            if crate.lower() in cargo_cat and matches_only(crate, only):
                if not apply:
                    res["outdated"].append({"name": crate, "manager": "cargo", "before": "installed", "latest": "check via cargo install"})
                else:
                    rc_c, c_out, c_err = run_cmd(["cargo", "install", crate], timeout=900)
                    if rc_c == 0:
                        res["upgraded"].append({"name": crate, "manager": "cargo", "before": "installed", "after": "latest"})
                    else:
                        res["issues"].append({"name": crate, "manager": "cargo", "message": (c_err or c_out).strip()[-240:]})
    return res


def lane_self_updaters(catalog: dict, apply: bool, only: set[str]) -> dict:
    res: dict = {"lane": "self-updaters", "upgraded": [], "outdated": [], "already_latest": [], "issues": []}
    for entry in catalog.get("self_updaters", []):
        bin_name = entry.get("bin", "")
        tool_id = entry.get("id", bin_name)
        if not bin_name or not matches_only(tool_id, only):
            continue
        bin_path = shutil.which(bin_name)
        if not bin_path:
            continue
        resolved = str(Path(bin_path).resolve())
        if "/homebrew/" in resolved.lower() or "node_modules" in resolved.lower():
            continue

        rc_v, v_out, _ = run_cmd(entry.get("version_cmd", [bin_name, "--version"]), timeout=20)
        before = v_out.strip().splitlines()[0] if rc_v == 0 and v_out.strip() else "?"
        if not apply:
            res["outdated"].append({"name": tool_id, "manager": "self-updater", "before": before, "latest": "check via self-update"})
            continue

        rc_u, u_out, u_err = run_cmd(entry.get("update_cmd", [bin_name, "update"]), timeout=300)
        combined = f"{u_out}\n{u_err}"
        _, v2_out, _ = run_cmd(entry.get("version_cmd", [bin_name, "--version"]), timeout=20)
        after = v2_out.strip().splitlines()[0] if v2_out.strip() else before
        if rc_u == 0:
            if after == before and any(k in combined.lower() for k in ("up to date", "up-to-date", "already", "latest", "no update")):
                res["already_latest"].append({"name": tool_id, "manager": "self-updater", "version": after})
            elif after != before:
                res["upgraded"].append({"name": tool_id, "manager": "self-updater", "before": before, "after": after})
            else:
                res["already_latest"].append({"name": tool_id, "manager": "self-updater", "version": after})
        else:
            res["issues"].append({"name": tool_id, "manager": "self-updater", "message": combined.strip()[-240:]})
    return res


def scan_direct_apps(catalog: dict, managed_by_brew: set[str], only: set[str]) -> list[dict]:
    if sys.platform != "darwin":
        return []
    app_names = catalog.get("direct_macos_apps", [])
    roots = [Path("/Applications"), Path.home() / "Applications"]
    results: list[dict] = []
    seen: set[str] = set()
    for root in roots:
        for app_name in app_names:
            if app_name in managed_by_brew or app_name in seen:
                continue
            app_path = root / app_name
            if not app_path.exists() or not matches_only(app_name, only):
                continue
            seen.add(app_name)
            plist_path = app_path / "Contents" / "Info.plist"
            version = "?"
            has_sparkle = False
            if plist_path.is_file():
                try:
                    with plist_path.open("rb") as fh:
                        plist = plistlib.load(fh)
                    version = str(plist.get("CFBundleShortVersionString") or plist.get("CFBundleVersion") or "?")
                    has_sparkle = bool(plist.get("SUFeedURL"))
                except Exception:
                    pass
            results.append({
                "name": app_name,
                "path": str(app_path),
                "version": version,
                "has_sparkle": has_sparkle,
                "note": "内置更新器（需在应用内检查/重启更新）" if has_sparkle else "非 Homebrew 托管桌面应用（如有新版请在应用内更新）",
            })
    return results


def run_updates(
    *,
    apply: bool = False,
    only: set[str] | None = None,
    no_casks: bool = False,
    workers: int = 4,
    catalog_path: Path | None = None,
) -> dict:
    catalog = load_catalog(catalog_path)
    only_set = only or set()

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        f_brew = pool.submit(lane_homebrew, catalog, apply, only_set, no_casks)
        f_npm = pool.submit(lane_npm, catalog, apply, only_set)
        f_py = pool.submit(lane_python_and_cargo, catalog, apply, only_set)
        f_self = pool.submit(lane_self_updaters, catalog, apply, only_set)

        r_npm = f_npm.result()
        r_pnpm = lane_pnpm(catalog, apply, only_set, r_npm.get("managed_pkgs", set()))
        r_brew = f_brew.result()
        r_py = f_py.result()
        r_self = f_self.result()

    lanes = [r_brew, r_npm, r_pnpm, r_py, r_self]
    upgraded = [item for r in lanes for item in r["upgraded"]]
    outdated = [item for r in lanes for item in r["outdated"]]
    already_latest = [item for r in lanes for item in r["already_latest"]]
    issues = [item for r in lanes for item in r["issues"]]
    manual_apps = scan_direct_apps(catalog, r_brew.get("managed_apps", set()), only_set)

    status = "ok"
    if issues:
        status = "partial" if (upgraded or already_latest or not apply) else "failed"

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "apply" if apply else "dry-run",
        "only": sorted(only_set),
        "status": status,
        "upgraded": upgraded,
        "outdated": outdated,
        "already_latest": already_latest,
        "manual_apps": manual_apps,
        "issues": issues,
    }


def render_markdown(report: dict) -> str:
    lines = [
        f"## AI 软件与 CLI 更新（{report['mode']}）",
        "",
        f"- 摘要：已升级 {len(report['upgraded'])} | 待更新 {len(report['outdated'])} | 已最新 {len(report['already_latest'])} | 桌面端/手动 {len(report['manual_apps'])} | 告警 {len(report['issues'])}",
        "",
    ]
    if report["upgraded"]:
        lines.append("### 已升级")
        for item in report["upgraded"]:
            lines.append(f"- `{item['name']}` ({item['manager']}): `{item['before']}` -> `{item['after']}`")
        lines.append("")
    if report["outdated"]:
        lines.append("### 可更新（预览）")
        for item in report["outdated"]:
            lines.append(f"- `{item['name']}` ({item['manager']}): `{item['before']}` -> `{item['latest']}`")
        lines.append("")
    if report["already_latest"]:
        lines.append("### 已是最新")
        for item in report["already_latest"]:
            lines.append(f"- `{item['name']}` ({item['manager']}): `{item['version']}`")
        lines.append("")
    if report["manual_apps"]:
        lines.append("### 非 Homebrew 托管桌面应用")
        for app in report["manual_apps"]:
            lines.append(f"- `{app['name']}`: `{app['version']}`（{app['note']}）")
        lines.append("")
    if report["issues"]:
        lines.append("### 跳过 / 异常")
        for iss in report["issues"]:
            lines.append(f"- `{iss['name']}` ({iss['manager']}): {iss['message']}")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Apply detected upgrades (default: dry-run).")
    parser.add_argument("--only", default="", help="Comma-separated filter tokens (e.g. mole,opencode,codex).")
    parser.add_argument("--no-casks", action="store_true", help="Skip Homebrew GUI casks.")
    parser.add_argument("--workers", type=int, default=4, help="Max concurrent package-manager lanes.")
    parser.add_argument("--report-dir", type=Path, help="Optional directory to save JSON/Markdown reports.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    only = {p.strip().lower() for p in args.only.split(",") if p.strip()}
    report = run_updates(apply=args.apply, only=only, no_casks=args.no_casks, workers=args.workers)
    md = render_markdown(report)

    if args.report_dir:
        args.report_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        (args.report_dir / f"ai-software-update-{stamp}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        (args.report_dir / f"ai-software-update-{stamp}.md").write_text(md, encoding="utf-8")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(md)
    return 1 if report["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
