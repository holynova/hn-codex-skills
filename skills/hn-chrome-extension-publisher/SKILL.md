---
name: hn-chrome-extension-publisher
description: Audit, prepare, package, publish, and update Chrome extensions for the Chrome Web Store. Use when the user asks to release or upgrade a Chrome extension, inspect existing extension files and store materials, create listing descriptions, logos/icons, screenshots, promotional images, permission and privacy disclosures, publish a privacy policy with GitHub Pages, build a store-ready ZIP, or get help completing and submitting the Chrome Web Store Developer Dashboard with Computer Use or Chrome automation.
---

# HN Chrome Extension Publisher

## Goal

Turn an existing Chrome extension project into a verified Chrome Web Store submission package. Inspect before creating, preserve useful material, fill only real gaps, and keep package preparation separate from dashboard submission.

## Rules

- Inspect the repository, build system, `manifest.json`, extension behavior, existing listing copy, icons, screenshots, privacy documents, release archives, git status, and store identifiers before editing.
- Treat the built extension directory as the product. Test that directory with Chrome; do not assume the source tree is loadable or uploadable.
- Require Manifest V3 for new Chrome Web Store submissions. Keep permissions and host access to the narrowest scope needed for the extension's single purpose.
- Derive descriptions, privacy claims, permission justifications, and screenshots from verified behavior. Never invent features, user counts, endorsements, security claims, or data practices.
- Never commit or package credentials, OAuth secrets, private keys, cookies, `.env` files, developer-dashboard exports, or unrelated source material.
- Prepare files and materials without additional approval. Do not open the Developer Dashboard, upload, change a live listing, submit for review, publish, unpublish, or alter rollout until the user explicitly authorizes that external action.
- After all materials pass local checks, ask whether the user wants Computer Use or an authenticated Chrome workflow to fill the dashboard, upload the package, and submit it. Respect a no answer and provide a manual handoff.
- Let the user handle login, CAPTCHA, two-step verification, developer registration fees, legal attestations they must personally make, and any unexpected account or payment prompt.

## Workflow

1. Orient.
   - Locate source and built manifests, package-manager files, build scripts, extension ID/item ID, prior release ZIPs, and release notes.
   - Identify whether this is a first submission or an update. For an update, obtain the last published version and current store metadata from local records or the dashboard when access is authorized.
   - Inventory existing materials before proposing replacements. Read [references/release-inventory.md](references/release-inventory.md).

2. Audit behavior and policy surface.
   - Build and load the production extension unpacked in Chrome.
   - Test installation, toolbar action, popup/options/side panel, content scripts, service worker, permissions prompts, primary user flow, error states, and uninstall-sensitive behavior as applicable.
   - Inspect requested permissions, host permissions, remote requests, storage, authentication, analytics, payments, ads, user-data handling, and remotely hosted code.
   - Remove unused permissions and release-blocking debug code. Do not weaken required functionality to make the audit pass silently.

3. Set the release version.
   - For a first submission, preserve a valid intentional manifest version or establish one.
   - For every update, set `manifest.json.version` strictly higher than the published version before building. Use one to four dot-separated integers; do not use prerelease suffixes in `version`. Use `version_name` only for an optional display label.
   - Keep source manifest, built manifest, package filename, and release notes consistent. Rebuild after changing the version.

4. Prepare store materials.
   - Organize deliverables under a dedicated release directory without mixing them into the uploadable extension root.
   - Write accurate short and detailed descriptions, single-purpose statement, category/language recommendation, permission justifications, remote-code declaration, data-use answers, support details, and release notes.
   - Reuse a strong existing logo when possible. Otherwise load an available image-generation or visual-asset skill to create a suitable original icon, then export and verify required sizes.
   - Capture current, real product screenshots. Create promotional images that match the product branding without misleading claims.
   - Follow [references/store-materials.md](references/store-materials.md), then run `python scripts/audit_release.py <built-extension-dir> <materials-dir> [--previous-version X]` from this skill directory.

5. Prepare privacy and support pages.
   - Map actual permissions and data flows before writing any privacy statement.
   - Create a plain-language privacy policy that matches dashboard declarations, including local-only processing when applicable.
   - Publish it at a stable public HTTPS URL. Prefer an existing project site; GitHub Pages is an acceptable default.
   - Open the live page and verify title, extension identity, data practices, contact route, and all links. Read [references/privacy-page.md](references/privacy-page.md).

6. Package and inspect.
   - Run the real production build and all relevant tests, lint, and type checks.
   - Package the built extension directory, not the repository, with `manifest.json` at the ZIP root:
     `python scripts/package_extension.py <built-extension-dir> <output.zip>`.
   - Inspect the produced ZIP, record its version, size, and SHA-256, and install/test the exact packaged contents when practical.
   - Keep screenshots, listing documents, privacy-page source, source maps not intentionally shipped, tests, and private keys outside the upload ZIP.

7. Present readiness and ask for submission authorization.
   - Report all passed checks, warnings, unresolved policy decisions, material paths, privacy URL, package path/hash, and version transition.
   - Ask directly: “材料已经准备并验证完成。是否授权我使用 Computer Use 或已登录的 Chrome，填写 Chrome Web Store 表单、上传此版本，并点击 Submit for review？”
   - Do not continue into the dashboard until the user answers.

8. Submit only after authorization.
   - Read [references/dashboard-submission.md](references/dashboard-submission.md).
   - Use the available Computer Use or Chrome-control skill with the user's existing authenticated session.
   - Match the correct publisher and item before uploading. Fill listing, privacy, distribution, and package fields from the prepared canonical materials.
   - Stop for user-only authentication, payment, legal, or ambiguous policy decisions.
   - Click `Submit for review` only when the user's authorization explicitly covers submission. Record the resulting status and whether publishing is immediate or deferred.

9. Handoff.
   - Report `ready`, `uploaded`, `submitted`, `published`, or `blocked` separately; never collapse them into “done.”
   - For updates, report previous/new version, listing/privacy changes, permission changes, review status, rollout setting, and rollback considerations.

## Output

```text
Release:
- Type: first submission / update
- Version: previous -> new
- Package: path, size, SHA-256
- Privacy policy: URL

Materials:
- Listing copy: ready/missing
- Icons: ready/missing
- Screenshots: ready/missing
- Promo image: ready/missing
- Privacy answers: ready/blocked

Verification:
- Build/tests: ...
- Unpacked Chrome test: ...
- Audit/package checks: ...

Submission:
- Dashboard: not authorized/uploaded/submitted/published/blocked
- Next action: ...
```
