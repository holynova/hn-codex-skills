# Release Inventory

Use this checklist when turning a local project into a public release.

## Project Basics

- Product name and one-sentence value.
- Repository URL.
- Live demo URL or install path.
- License if public reuse matters.
- Concise README with screenshot and run/build commands.

## Visual Materials

- Main screenshot: product in its primary workflow.
- Secondary screenshots only if the product has distinct modes.
- App icon in required sizes.
- Social/share card only when the user asks or the project has a public landing page.

## Public Pages

- GitHub Pages demo or docs page.
- Privacy policy when the product is a browser extension or collects/transmits user data.
- Support/contact page or support section.
- Changelog or release notes for packaged releases.

## Build Artifacts

- Confirm build command.
- Confirm output directory.
- Confirm zip/package excludes source-only, secrets, local config, caches, and screenshots not meant for release.
- Reopen or list the final artifact after generation.

## Automation

- GitHub Pages workflow when branch deployment is requested.
- Release workflow when tags should create packaged artifacts.
- Keep workflows small and specific to this repo.

## Handoff

Report exact paths:

- README.
- Screenshots.
- Icons.
- Privacy/support pages.
- Zip/package.
- Workflow files.
