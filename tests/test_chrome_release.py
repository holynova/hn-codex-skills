import binascii
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile
import zlib


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "skills/hn-chrome-extension-publisher/scripts/audit_release.py"
PACKAGE = ROOT / "skills/hn-chrome-extension-publisher/scripts/package_extension.py"


def png_chunk(chunk_type, data):
    crc = binascii.crc32(chunk_type + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)


def write_png(path, width, height):
    path.parent.mkdir(parents=True, exist_ok=True)
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + (b"\x00" * width * 3) for _ in range(height))
    data = (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", header)
        + png_chunk(b"IDAT", zlib.compress(raw, 9))
        + png_chunk(b"IEND", b"")
    )
    path.write_bytes(data)


def write_fake_png_with_valid_chunks(path, width, height):
    path.parent.mkdir(parents=True, exist_ok=True)
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    data = (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", header)
        + png_chunk(b"IDAT", zlib.compress(b"not enough pixel data"))
        + png_chunk(b"IEND", b"")
    )
    path.write_bytes(data)


def write_materials(root):
    root.mkdir(parents=True, exist_ok=True)
    (root / "listing.md").write_text("""# Store Listing
## Name
Fixture
## Short Description
Fixture extension.
## Detailed Description
Fixture extension for release tests.
## Single Purpose
Test releases.
## Category
Developer Tools
## Language
English
## Website
https://example.com
## Support
support@example.com
## Privacy Policy
https://example.com/privacy
## Release Notes
Test release.
""", encoding="utf-8")
    (root / "privacy.md").write_text("""# Privacy Practices
## Single Purpose
Test releases.
## Permission Justifications
Not applicable.
## Host Permission Justifications
Not applicable.
## Remote Code
None.
## User Data
None.
## Data Transfers and Prohibited Uses
None.
## Limited Use
Compliant.
## Privacy Policy
https://example.com/privacy
""", encoding="utf-8")
    policy = root / "privacy-policy/index.html"
    policy.parent.mkdir(parents=True, exist_ok=True)
    policy.write_text("<h1>Privacy</h1><p>" + ("No user data is collected or transmitted. " * 20) + "</p>", encoding="utf-8")
    write_png(root / "assets/store-icon-128.png", 128, 128)
    write_png(root / "assets/promo-small-440x280.png", 440, 280)
    write_png(root / "assets/screenshot-01.png", 640, 400)


def write_manifest(root, icon="icons/icon128.png", popup="popup.html"):
    root.mkdir(parents=True, exist_ok=True)
    manifest = {
        "manifest_version": 3,
        "name": "Fixture",
        "description": "Fixture extension for release tests.",
        "version": "1.2.3",
        "icons": {"128": icon},
        "action": {"default_popup": popup},
    }
    (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


class ChromeReleaseTests(unittest.TestCase):
    def run_script(self, script, *args):
        return subprocess.run(
            [sys.executable, str(script), *map(str, args)],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_packager_rejects_private_key_filename_and_content(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            extension = temp / "extension"
            write_manifest(extension)
            (extension / "popup.html").write_text("<p>Fixture</p>", encoding="utf-8")
            write_png(extension / "icons/icon128.png", 128, 128)
            (extension / "id_rsa").write_text("not even a real key", encoding="utf-8")
            result = self.run_script(PACKAGE, extension, temp / "extension.zip")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("possible secret", result.stderr)

            (extension / "id_rsa").unlink()
            (extension / "innocent.txt").write_text(
                "-----BEGIN OPENSSH PRIVATE KEY-----\nsecret", encoding="utf-8"
            )
            result = self.run_script(PACKAGE, extension, temp / "extension.zip")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("private-key content marker", result.stderr)

    def test_packager_excludes_source_maps_unless_explicitly_allowed(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            extension = temp / "extension"
            write_manifest(extension)
            (extension / "popup.html").write_text("<p>Fixture</p>", encoding="utf-8")
            (extension / "app.js.map").write_text("{}", encoding="utf-8")
            write_png(extension / "icons/icon128.png", 128, 128)

            package = temp / "extension.zip"
            result = self.run_script(PACKAGE, extension, package)
            self.assertEqual(result.returncode, 0, result.stderr)
            with zipfile.ZipFile(package) as archive:
                self.assertNotIn("app.js.map", archive.namelist())

            allowed = temp / "extension-with-maps.zip"
            result = self.run_script(PACKAGE, extension, allowed, "--include-source-maps")
            self.assertEqual(result.returncode, 0, result.stderr)
            with zipfile.ZipFile(allowed) as archive:
                self.assertIn("app.js.map", archive.namelist())

    def test_audit_rejects_paths_outside_extension_root(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            extension = temp / "extension"
            materials = temp / "materials"
            write_manifest(extension, "../outside.png", "../outside.html")
            write_png(temp / "outside.png", 128, 128)
            (temp / "outside.html").write_text("<p>Outside</p>", encoding="utf-8")
            write_materials(materials)

            result = self.run_script(AUDIT, extension, materials)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("escapes extension root", result.stderr)

    def test_audit_rejects_fake_png_and_accepts_valid_png(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            extension = temp / "extension"
            materials = temp / "materials"
            write_manifest(extension)
            (extension / "popup.html").write_text("<p>Fixture</p>", encoding="utf-8")
            icon = extension / "icons/icon128.png"
            icon.parent.mkdir(parents=True, exist_ok=True)
            icon.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
            write_materials(materials)

            result = self.run_script(AUDIT, extension, materials)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not a valid PNG or JPEG", result.stderr)

            write_fake_png_with_valid_chunks(icon, 128, 128)
            result = self.run_script(AUDIT, extension, materials)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not a valid PNG or JPEG", result.stderr)

            write_png(icon, 128, 128)
            result = self.run_script(AUDIT, extension, materials)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
