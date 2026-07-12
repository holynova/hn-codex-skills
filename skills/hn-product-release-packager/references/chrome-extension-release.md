# Chrome Extension Archive Checks

Use only for inspecting an already-built Chrome extension archive.

## Required Entries

- `manifest.json` is at the archive root.
- Every file referenced by the manifest exists in the archive.
- Built JavaScript, CSS, icons, and static assets required at runtime are present.
- The manifest version matches the intended build version.

## Exclusions

- No `.git`, `node_modules`, tests, source-only configuration, local hosts, logs, secrets, or store-source screenshots.
- Do not include the repository root when the built extension directory is the runtime root.

## Inspection Boundary

This check proves archive composition only. Loading the extension, testing browser behavior, uploading to Chrome Web Store, or editing the public listing belongs to other workflows.
