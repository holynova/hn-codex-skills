#!/usr/bin/env python3

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile


SKIP_DIRS = {".git", ".github", ".cache", "coverage", "node_modules", "test", "tests"}
SKIP_FILES = {".DS_Store", "Thumbs.db"}
SECRET_PATTERNS = (".env", ".pem", ".key", ".p12", ".pfx")
VERSION_RE = re.compile(r"^(?:0|[1-9]\d*)(?:\.(?:0|[1-9]\d*)){0,3}$")


def fail(message):
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def is_secret(path):
    name = path.name.lower()
    return name.startswith(".env") or any(name.endswith(suffix) for suffix in SECRET_PATTERNS[1:])


def collect_files(source, output):
    files = []
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        if path.is_symlink():
            fail(f"symlink is not allowed in the upload package: {relative}")
        if not path.is_file() or path.name in SKIP_FILES:
            continue
        if path.resolve() == output:
            continue
        if is_secret(path):
            fail(f"possible secret or signing key found in extension root: {relative}")
        if path.suffix.lower() in {".zip", ".crx"}:
            continue
        files.append((path, relative.as_posix()))
    return files


def main():
    parser = argparse.ArgumentParser(description="Create a Chrome Web Store ZIP from a built extension directory.")
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    source = args.source.resolve()
    output = args.output.resolve()
    manifest_path = source / "manifest.json"
    if not source.is_dir():
        fail(f"source is not a directory: {source}")
    if output == source or source in output.parents:
        fail("output ZIP must be outside the built extension directory")
    if not manifest_path.is_file():
        fail(f"manifest.json must exist at the extension root: {manifest_path}")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"cannot parse manifest.json: {error}")

    version = str(manifest.get("version", ""))
    if not VERSION_RE.fullmatch(version):
        fail(f"invalid Chrome extension version: {version}")
    parts = [int(part) for part in version.split(".")]
    if all(part == 0 for part in parts) or any(part > 65535 for part in parts):
        fail(f"invalid Chrome extension version: {version}")

    files = collect_files(source, output)
    if not any(name == "manifest.json" for _, name in files):
        fail("manifest.json would not be included at the ZIP root")

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for file_path, archive_name in files:
            info = zipfile.ZipInfo(archive_name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, file_path.read_bytes())

    with zipfile.ZipFile(output) as archive:
        names = archive.namelist()
        if "manifest.json" not in names or any(name.startswith("../") or name.startswith("/") for name in names):
            fail("ZIP structure verification failed")

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    print(f"Package created: {output}")
    print(f"Version: {version}")
    print(f"Files: {len(files)}")
    print(f"Size: {output.stat().st_size} bytes")
    print(f"SHA-256: {digest}")


if __name__ == "__main__":
    main()
