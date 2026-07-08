# Asset Checklist

Use this checklist for project-ready visual assets.

## Common Outputs

- `assets/source/` or `design/source/`: master or editable inputs.
- `public/`, `src/assets/`, `extension/icons/`, or project-specific release paths.
- README screenshots under a stable path such as `docs/` or `assets/`.

## Icons

Common browser extension sizes:

- 16 x 16.
- 32 x 32.
- 48 x 48.
- 128 x 128.

Common app/site extras when useful:

- 192 x 192.
- 512 x 512.
- SVG source if the design is vector-friendly.

Checks:

- Square canvas.
- Clear silhouette at 16 px and 32 px.
- No unintended border.
- Transparent background when expected.
- Manifest or metadata references point to existing files.

## Screenshots

- Capture the primary workflow, not a blank or setup state.
- Hide dev overlays, local debug panels, and browser chrome unless needed.
- Use realistic content.
- Verify desktop and mobile when the product is responsive.
- Store screenshots in stable repo paths and update README references.

## Generated Images

- Save the final chosen output into the project, not only the generation cache.
- Record the final prompt in the handoff when useful.
- Regenerate rather than upscale a visibly poor icon master.
- For transparent requests, validate alpha and edge quality.

## Batch Conversion

- Preserve source files unless the user asks to replace them.
- Use deterministic naming.
- Detect duplicate outputs.
- Report skipped, converted, failed, and overwritten files.
