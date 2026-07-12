---
name: hn-visual-asset-pipeline
description: Normalize an existing raster master image into explicitly requested project-ready variants. Use when the user asks to resize, crop, convert, compress, rename, or export an existing PNG, JPEG, or WebP source into a defined size and format matrix while preserving a separate master. This skill does not generate new artwork, capture screenshots, design icons, update application references, or create store and README materials.
---

# HN Visual Asset Pipeline

## Responsibility

Transform one existing raster master into a deterministic set of requested variants and verify every exported file. The input concept and artwork must already exist.

## Boundaries

- Do not generate, redraw, retouch, or choose a new visual direction.
- Do not capture product screenshots or compose marketing/store graphics.
- Do not update manifests, HTML, README files, metadata, or application code.
- Do not infer an app-store or platform size matrix; require the user or project to define the requested outputs.
- Never overwrite the master asset. Write variants to an explicit output directory.

## Workflow

1. Define the transform contract.
   - Identify the master file, output directory, filename pattern, target dimensions, formats, crop/fit rule, transparency requirement, and compression target.
   - Use `references/asset-checklist.md` to record the variant matrix.

2. Inspect the master.
   - Verify the file opens and record its dimensions, format, color mode, alpha channel, and orientation metadata.
   - Stop if the requested variant would require inventing missing artwork or an unspecified crop.

3. Export deterministically.
   - Use a reproducible image-processing command or script.
   - Apply the same declared crop/fit and resampling rule across the matrix.
   - Preserve the master separately and avoid repeated lossy conversions.

4. Verify every variant.
   - Reopen each output and check filename, dimensions, format, file size, and transparency requirement.
   - Visually inspect representative smallest and largest variants for clipping, padding, blur, or halos.
   - Fail the job if any requested matrix entry is missing.

5. Report the export set.
   - Return the master path, output directory, transformation rule, variant count, and verification result.
   - State that no project references or product artwork were changed.

## Output

```text
Master: <path>
Transform: <crop/fit, resampling, format>
Variants: <count and output paths>
Verification: pass | fail
Project wiring: not performed
```

## Reference Routing

- Read `references/asset-checklist.md` before exporting variants.
