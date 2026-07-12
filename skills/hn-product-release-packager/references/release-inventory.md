# Release Archive Manifest

Define this manifest before creating an archive.

## Required Fields

- Input build directory or existing package command.
- Output archive path and format.
- Required files at the archive root.
- Required runtime directories and assets.
- Version source, when the runtime exposes a version.
- Expected executable bits, when applicable.

## Default Denylist

- `.git/`, `.github/`, editor metadata, and OS metadata.
- `node_modules/`, dependency caches, build caches, and test caches.
- Tests, fixtures, coverage, source maps not intended for users, and internal screenshots.
- `.env*`, credentials, tokens, signing material, local configuration, and logs.
- Previous archives and unrelated build variants.

## Verification

- List or reopen the final artifact from disk.
- Compare root entries with the required list.
- Search archive paths for every denylisted class.
- Confirm the archive is non-empty and its size is plausible for the documented output.
- Compute a checksum when the artifact will cross machines or systems.
