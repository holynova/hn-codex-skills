# Chrome Extension Release

Use this checklist for Chrome Web Store preparation.

## Required Project Checks

- `manifest.json` has correct `name`, `description`, `version`, `icons`, `permissions`, `host_permissions`, `action`, and content scripts.
- Extension works after loading the built output directory, not only the source directory.
- Permissions are minimal and explainable.
- No development-only console noise, debug URLs, local hosts, or secrets.

## Store Materials

- Short description.
- Detailed description focused on what the extension does.
- Category and language.
- At least one screenshot that shows the real extension in use.
- Icon assets required by Chrome Web Store and extension manifest.
- Privacy policy URL if required.
- Support URL or support contact.

## Package Verification

- Build the extension.
- Zip the build output, not the whole repo, unless the repo is intentionally the extension root.
- Inspect zip contents:
  - `manifest.json` at the expected root.
  - Icons included.
  - Built JS/CSS/assets included.
  - No `.git`, `node_modules`, tests, local config, screenshots source, or secrets.

## Submission Boundary

Preparing files is allowed. Uploading, submitting for review, changing public listing text, or accepting final store actions requires explicit user instruction and may require browser/computer-use confirmation.
