---
name: hn-visual-asset-pipeline
description: 创建、规范化、验证并整理产品视觉资产。用于用户要求制作图标、截图、生成图片、转换图片、透明 PNG、资产目录、多尺寸导出、README 或商店视觉素材、清理图片质量，或为应用、扩展、网站和作品集批量处理视觉资产。
---

# HN Visual Asset Pipeline

## Purpose

Produce visual assets that are usable in a real project: correctly sized, named, placed, referenced, and verified. Cover icons, screenshots, generated images, transparent cutouts, store assets, README images, and grouped asset folders.

## Operating Rules

- Inspect existing assets and project conventions before generating or overwriting files.
- Prefer deterministic resizing/conversion for existing assets; use image generation only when a new visual concept is needed.
- Keep original/source assets separate from exported release assets.
- Verify dimensions, file format, transparency, and visual quality after generation or conversion.
- For app and extension icons, generate the full required size set from the best available master image.
- Do not leave assets only in temporary or Codex-generated directories when the project needs them.

## Workflow

1. Define the asset job.
   - Asset type: app icon, Chrome icon, screenshot, README image, store image, transparent cutout, batch conversion, gallery organization.
   - Required sizes, formats, output paths, and naming scheme.

2. Inspect current assets.
   - Find existing icons, screenshots, image folders, README references, manifest references, and build config.

3. Produce or transform.
   - Use deterministic scripts or platform tools for resizing, format conversion, cropping, compression, and alpha checks.
   - Use image generation when the user needs a new icon, illustration, product visual, or style direction.
   - Use `references/asset-checklist.md` to avoid missing formats and sizes.

4. Wire assets into the project.
   - Update README, manifest, HTML, metadata, or store material references when requested.
   - Keep paths relative and repo-friendly.

5. Verify.
   - List final files.
   - Check dimensions and format.
   - Open or inspect key assets visually.
   - Confirm referenced files exist.

## Output Shape

```text
Assets created:
- ...

Updated references:
- ...

Verified:
- ...

Source/master asset:
- ...
```

## References

- Read `references/asset-checklist.md` before creating release-ready visual assets.
