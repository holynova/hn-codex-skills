# Changelog

## Unreleased

### Features

- Add hn-flowing-pen-art with five mandatory visual references, contour-hatching guidance, varied composition prompts, and verified image-preserving installation.

- Add `hn-ink-dance-sketch` with six required visual examples, sparse ink style guidance, and dance/costume diversity controls.
- Bundle the visual references in single-skill and full installer paths, with byte-for-byte installation verification.
- Add `hn-color-woodcut`: multicolor woodcut generation with eight mandatory visual examples, an overview, palette recipes and provenance. Include it in the bundled installer and verify reference images survive installation.

## 1.0.0 - 2026-07-13

### Breaking Changes

- Remove the broad `hn-product-release-packager` skill in favor of focused, single-responsibility publishing skills.

### Fixes

- Block private keys, credential files, unsafe source maps, and secret-bearing content from Chrome extension upload packages.
- Reject manifest path traversal and malformed or forged PNG assets during Chrome extension release audits.
- Make the skill installer preflight and stage every target before atomic replacement, with rollback on failure.

### Maintenance

- Remove orphaned references and duplicate trigger guidance from focused skills.
- Replace fourteen large PNG examples with three visually verified, compressed WebP references.
- Add regression tests for Chrome release security and transactional installation.

## 0.2.0 - 2026-07-12

### Features

- Add `hn-project-publisher` for versioned GitHub, GitHub Pages, README, and portfolio publishing workflows.
- Add `hn-chrome-extension-publisher` for Chrome Web Store audits, materials, privacy pages, deterministic packaging, upgrades, and assisted dashboard submission.
