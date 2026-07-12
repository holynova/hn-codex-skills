---
name: hn-product-release-packager
description: Assemble and inspect a release archive from an existing, already-built project output. Use when the user asks to create a distributable zip or package, verify archive contents, exclude development files and secrets, or prove that a release artifact contains the required runtime files. This skill does not create product copy, screenshots, icons, privacy pages, CI workflows, releases, or store submissions.
---

# HN Product Release Packager

## Responsibility

Turn an existing build output into one reproducible release archive and verify the archive from disk. The deliverable is the package plus a manifest of what it contains and excludes.

## Boundaries

- Require an existing build output or documented packaging command.
- Do not implement or repair the product under this skill.
- Do not create README copy, screenshots, icons, policy/support pages, store listings, CI workflows, tags, or releases.
- Do not commit, push, upload, submit, or publish.
- Never package secrets, local configuration, caches, test fixtures, dependency directories, or unrelated source files.

## Workflow

1. Identify the package contract.
   - Read repository instructions and the existing build/package configuration.
   - Record the product type, input directory, output archive, required root files, and explicit exclusions.
   - Use `references/release-inventory.md` to write the package manifest before creating the archive.

2. Confirm the input is ready.
   - Verify the expected build output exists.
   - If the repository defines a packaging command, use it rather than inventing another layout.
   - Stop if building or fixing the product is still required; that belongs to a preceding workflow.

3. Create one release artifact.
   - Package only the documented runtime files.
   - Preserve the required archive root layout.
   - Avoid nondeterministic extras such as caches, logs, local metadata, and editor files.

4. Inspect the artifact from disk.
   - Reopen or list the final archive rather than trusting the packaging command.
   - Confirm every required entry exists and every denylisted class is absent.
   - For Chrome extensions, read `references/chrome-extension-release.md` for archive-specific checks.

5. Report the artifact boundary.
   - Return the archive path, size, checksum when useful, included root entries, exclusions checked, and any blocker.
   - State explicitly that no upload or publication was performed.

## Output

```text
Package: <absolute path>
Input: <build output>
Required entries: pass | fail
Excluded entries: pass | fail
Inspection: <command and result>
Publication: not performed
```

## Reference Routing

- Read `references/release-inventory.md` for the package manifest and denylist.
- Read `references/chrome-extension-release.md` only when packaging a Chrome extension.
