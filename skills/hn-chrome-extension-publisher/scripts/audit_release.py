#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
import re
import struct
import sys
import zlib


VERSION_RE = re.compile(r"^(?:0|[1-9]\d*)(?:\.(?:0|[1-9]\d*)){0,3}$")
REQUIRED_DOCUMENT_SECTIONS = {
    "listing.md": (
        "Name", "Short Description", "Detailed Description", "Single Purpose", "Category",
        "Language", "Website", "Support", "Privacy Policy", "Release Notes",
    ),
    "privacy.md": (
        "Single Purpose", "Permission Justifications", "Host Permission Justifications",
        "Remote Code", "User Data", "Data Transfers and Prohibited Uses", "Limited Use", "Privacy Policy",
    ),
}


def version_parts(value):
    if not VERSION_RE.fullmatch(value):
        return None
    parts = [int(part) for part in value.split(".")]
    if all(part == 0 for part in parts) or any(part > 65535 for part in parts):
        return None
    return parts + [0] * (4 - len(parts))


def png_scanlines(width, height, bit_depth, color_type, interlace):
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color_type)
    valid_depths = {
        0: {1, 2, 4, 8, 16},
        2: {8, 16},
        3: {1, 2, 4, 8},
        4: {8, 16},
        6: {8, 16},
    }
    if channels is None or bit_depth not in valid_depths[color_type] or interlace not in {0, 1}:
        return None

    passes = [(0, 0, 1, 1)] if interlace == 0 else [
        (0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8), (2, 0, 4, 4),
        (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2),
    ]
    rows = []
    for x_start, y_start, x_step, y_step in passes:
        pass_width = max(0, (width - x_start + x_step - 1) // x_step)
        pass_height = max(0, (height - y_start + y_step - 1) // y_step)
        if not pass_width or not pass_height:
            continue
        row_bytes = (pass_width * channels * bit_depth + 7) // 8
        rows.extend([row_bytes] * pass_height)
    return rows


def image_size(path):
    data = path.read_bytes()
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        offset = 8
        width = height = bit_depth = color_type = interlace = None
        compressed = bytearray()
        saw_header = saw_end = False
        while offset + 12 <= len(data):
            length = int.from_bytes(data[offset:offset + 4], "big")
            chunk_type = data[offset + 4:offset + 8]
            chunk_end = offset + 12 + length
            if chunk_end > len(data):
                return None
            chunk_data = data[offset + 8:offset + 8 + length]
            expected_crc = int.from_bytes(data[offset + 8 + length:chunk_end], "big")
            actual_crc = zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF
            if actual_crc != expected_crc:
                return None
            if chunk_type == b"IHDR":
                if saw_header or length != 13 or offset != 8:
                    return None
                width, height = struct.unpack(">II", chunk_data[:8])
                if width < 1 or height < 1:
                    return None
                bit_depth, color_type, compression, filtering, interlace = chunk_data[8:13]
                if compression != 0 or filtering != 0:
                    return None
                saw_header = True
            elif chunk_type == b"IDAT":
                compressed.extend(chunk_data)
            elif chunk_type == b"IEND":
                if length != 0:
                    return None
                saw_end = True
                offset = chunk_end
                break
            offset = chunk_end
        if not (saw_header and saw_end and compressed) or offset != len(data):
            return None
        rows = png_scanlines(width, height, bit_depth, color_type, interlace)
        if rows is None:
            return None
        expected_size = sum(row_bytes + 1 for row_bytes in rows)
        if expected_size > 100 * 1024 * 1024:
            return None
        try:
            decompressor = zlib.decompressobj()
            decoded = decompressor.decompress(bytes(compressed), expected_size + 1)
        except zlib.error:
            return None
        if len(decoded) != expected_size or not decompressor.eof or decompressor.unused_data:
            return None
        offset = 0
        for row_bytes in rows:
            if decoded[offset] > 4:
                return None
            offset += row_bytes + 1
        return width, height
    if data.startswith(b"\xff\xd8") and data.endswith(b"\xff\xd9"):
        index = 2
        width = height = None
        saw_scan = False
        while index < len(data) - 2:
            if data[index] != 0xFF:
                return None
            while index < len(data) and data[index] == 0xFF:
                index += 1
            if index >= len(data):
                return None
            marker = data[index]
            index += 1
            if marker == 0xD9:
                break
            if marker in {0x01, *range(0xD0, 0xD8)}:
                continue
            if index + 2 > len(data):
                return None
            length = int.from_bytes(data[index:index + 2], "big")
            if length < 2 or index + length > len(data):
                return None
            if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                if length < 7:
                    return None
                height = int.from_bytes(data[index + 3:index + 5], "big")
                width = int.from_bytes(data[index + 5:index + 7], "big")
            if marker == 0xDA:
                saw_scan = True
                break
            index += length
        return (width, height) if saw_scan and width and height else None
    return None


def resolve_inside(root, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        return None
    root = root.resolve()
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def referenced_paths(manifest):
    references = []
    action = manifest.get("action") if isinstance(manifest.get("action"), dict) else {}
    background = manifest.get("background") if isinstance(manifest.get("background"), dict) else {}
    options_ui = manifest.get("options_ui") if isinstance(manifest.get("options_ui"), dict) else {}
    side_panel = manifest.get("side_panel") if isinstance(manifest.get("side_panel"), dict) else {}
    scalar_paths = [
        ("action.default_popup", action.get("default_popup")),
        ("background.service_worker", background.get("service_worker")),
        ("options_page", manifest.get("options_page")),
        ("options_ui.page", options_ui.get("page")),
        ("side_panel.default_path", side_panel.get("default_path")),
    ]
    references.extend((label, value) for label, value in scalar_paths if isinstance(value, str))
    content_scripts = manifest.get("content_scripts") if isinstance(manifest.get("content_scripts"), list) else []
    for index, content_script in enumerate(content_scripts):
        if not isinstance(content_script, dict):
            continue
        for kind in ("js", "css"):
            for value in content_script.get(kind, []):
                if isinstance(value, str):
                    references.append((f"content_scripts[{index}].{kind}", value))
    return references


def main():
    parser = argparse.ArgumentParser(description="Audit a built Chrome extension and organized store materials.")
    parser.add_argument("extension", type=Path)
    parser.add_argument("materials", type=Path)
    parser.add_argument("--previous-version")
    args = parser.parse_args()

    extension = args.extension.resolve()
    materials = args.materials.resolve()
    errors = []
    warnings = []
    manifest_path = extension / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"Error: cannot parse {manifest_path}: {error}", file=sys.stderr)
        raise SystemExit(1)

    if manifest.get("manifest_version") != 3:
        errors.append("manifest_version must be 3")
    name = manifest.get("name", "")
    description = manifest.get("description", "")
    if not isinstance(name, str) or not name.strip() or len(name) > 75:
        errors.append("manifest name must be 1-75 characters")
    if not isinstance(description, str) or not description.strip() or len(description) > 132:
        errors.append("manifest description must be 1-132 characters")

    current = version_parts(str(manifest.get("version", "")))
    if current is None:
        errors.append("manifest version must contain 1-4 integers from 0 to 65535 and cannot be all zero")
    if args.previous_version:
        previous = version_parts(args.previous_version)
        if previous is None:
            errors.append(f"invalid previous version: {args.previous_version}")
        elif current is not None and current <= previous:
            errors.append(f"version did not increase: {args.previous_version} -> {manifest.get('version')}")

    icons = manifest.get("icons", {})
    if not isinstance(icons, dict) or "128" not in icons:
        errors.append("manifest icons must include a 128x128 icon")
    else:
        for size_text, relative in icons.items():
            icon_path = resolve_inside(extension, relative)
            if icon_path is None:
                errors.append(f"manifest icon path escapes extension root: {relative}")
                continue
            if not icon_path.is_file():
                errors.append(f"manifest icon is missing: {relative}")
                continue
            dimensions = image_size(icon_path)
            if dimensions is None:
                errors.append(f"manifest icon is not a valid PNG or JPEG image: {relative}")
            elif size_text.isdigit() and dimensions != (int(size_text), int(size_text)):
                errors.append(f"manifest icon {relative} is {dimensions[0]}x{dimensions[1]}, expected {size_text}x{size_text}")
        for recommended in ("16", "32", "48"):
            if recommended not in icons:
                warnings.append(f"recommended manifest icon size is missing: {recommended}")

    for label, relative in referenced_paths(manifest):
        referenced = resolve_inside(extension, relative)
        if referenced is None:
            errors.append(f"referenced path escapes extension root for {label}: {relative}")
        elif not referenced.is_file():
            errors.append(f"referenced file is missing for {label}: {relative}")

    for document, sections in REQUIRED_DOCUMENT_SECTIONS.items():
        document_path = materials / document
        if not document_path.is_file():
            errors.append(f"store material is missing: {document}")
            continue
        document_text = document_path.read_text(encoding="utf-8")
        for section in sections:
            if not re.search(rf"^##\s+{re.escape(section)}\s*$", document_text, re.MULTILINE | re.IGNORECASE):
                errors.append(f"{document} is missing section: {section}")

    assets = materials / "assets"
    required_images = {
        "store-icon-128.png": {(128, 128)},
        "promo-small-440x280.png": {(440, 280)},
    }
    for filename, allowed in required_images.items():
        path = assets / filename
        if not path.is_file():
            errors.append(f"store image is missing: assets/{filename}")
        elif image_size(path) not in allowed:
            errors.append(f"store image has wrong dimensions: assets/{filename}")

    screenshots = sorted(list(assets.glob("screenshot-*.png")) + list(assets.glob("screenshot-*.jpg")) + list(assets.glob("screenshot-*.jpeg")))
    if not 1 <= len(screenshots) <= 5:
        errors.append(f"expected 1-5 screenshots, found {len(screenshots)}")
    for screenshot in screenshots:
        if image_size(screenshot) not in {(1280, 800), (640, 400)}:
            errors.append(f"screenshot has wrong dimensions: {screenshot.name}")

    marquee = assets / "promo-marquee-1400x560.png"
    if marquee.exists() and image_size(marquee) != (1400, 560):
        errors.append("optional marquee image has wrong dimensions")

    privacy_page = materials / "privacy-policy" / "index.html"
    if not privacy_page.is_file():
        warnings.append("local privacy-policy/index.html is missing; a verified external privacy URL may be used instead")
    else:
        privacy_text = privacy_page.read_text(encoding="utf-8", errors="replace")
        visible_text = re.sub(r"<[^>]+>", " ", privacy_text)
        visible_text = re.sub(r"\s+", " ", visible_text).strip()
        if len(visible_text) < 400:
            errors.append("local privacy policy appears incomplete: fewer than 400 visible characters")

    print(f"Manifest: {manifest_path}")
    print(f"Version: {manifest.get('version', 'missing')}")
    permissions = manifest.get("permissions", [])
    host_permissions = manifest.get("host_permissions", [])
    print(f"Permissions: {', '.join(permissions) if isinstance(permissions, list) and permissions else 'none'}")
    print(f"Host permissions: {', '.join(host_permissions) if isinstance(host_permissions, list) and host_permissions else 'none'}")
    for warning in warnings:
        print(f"Warning: {warning}")
    for error in errors:
        print(f"Error: {error}", file=sys.stderr)
    if errors:
        raise SystemExit(1)
    print("Release audit passed.")


if __name__ == "__main__":
    main()
