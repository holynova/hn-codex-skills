---
name: hn-product-release-packager
description: Prepare small apps, Chrome extensions, GitHub Pages projects, and public tools for release. Use when the user asks to publish, package, launch, submit to Chrome Web Store, create release materials, prepare README/screenshots/privacy pages/icons/store copy, add GitHub Actions releases, or turn a finished local project into a public product package.
---

# HN Product Release Packager

## Purpose

Turn a working project into a complete public release package. Treat docs, screenshots, icons, store listing copy, privacy/support pages, release zips, GitHub Pages, and GitHub Actions as first-class deliverables.

## Operating Rules

- Inspect the current repo before changing anything: app type, build output, extension manifest, package scripts, README, deploy target, and git status.
- Preserve the user's current implementation unless release requirements expose a real gap.
- Separate local build readiness, public presentation, store submission materials, and automation.
- Verify generated artifacts from disk instead of assuming a build or zip contains the right files.
- Do not submit to a third-party store, publish a release, or push commits unless the user explicitly asks.
- Keep public copy concise, concrete, and product-facing.

## Workflow

1. Orient.
   - Identify product type: static site, frontend app, browser extension, CLI, package, or mixed project.
   - Read `package.json`, build scripts, existing README, extension `manifest.json`, deploy files, and current git status.

2. Build the release inventory.
   - Use `references/release-inventory.md`.
   - List required and missing: README, screenshots, demo URL, repo URL, icons, privacy/support pages, store copy, zip/package, release notes, GitHub Actions.

3. Fill gaps.
   - Create or update only the artifacts required for the target release path.
   - Generate app icons and screenshots only when absent, outdated, or requested.
   - Add GitHub Pages or release workflows only after confirming branch/output conventions.

4. Verify.
   - Run relevant test, lint, typecheck, and build commands.
   - Inspect zip/package contents.
   - Open local pages or static files when presentation matters.
   - Confirm public links are present where requested.

5. Handoff.
   - Report artifact paths, commands run, verification status, and what still needs user action such as manual store submission.

## Output Shape

```text
Release package:
- Target:
- Added/updated:
- Build artifact:
- Public pages:
- Store materials:

Verified:
- ...

Manual steps remaining:
- ...
```

## References

- Read `references/release-inventory.md` to decide what artifacts are required.
- Read `references/chrome-extension-release.md` for Chrome Web Store packaging and submission materials.
