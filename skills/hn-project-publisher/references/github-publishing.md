# GitHub Publishing

Use this sequence as a command guide, adapting names and build paths to the inspected project.

## Preflight

```bash
gh auth status
gh api user --jq .login
git status --short --branch
git remote -v
```

Do not continue with external changes when authentication points to the wrong account.

## Initialize

For a project without npm or Git metadata:

```bash
npm init -y
git init -b master
```

Add `.gitignore` before staging. Never commit `.env*`, credentials, dependencies, caches, logs, or OS files.

If Git already exists, inspect history and remote state. Renaming a shared branch is a public migration, not initialization.

## Version Every Publication

Before rebuilding or pushing, determine the latest public version from the live page, `origin/master:package.json`, or the latest release/tag. If any prior publication exists, increase the version; default to patch unless the user requests minor or major.

For an npm-managed project, use the appropriate bump without creating an automatic version commit or tag:

```bash
npm version patch --no-git-tag-version
```

Use `minor` or `major` instead of `patch` when requested. For another package manager, use its equivalent or update `package.json` and its lockfile together. Do not bump after the build, because the published files would retain the old value.

Render `vX.Y.Z` visibly in the page. Prefer injecting the `package.json` version at build time. For a plain static page, update a durable element such as:

```html
<span class="app-version" aria-label="Version 1.2.3">v1.2.3</span>
```

Run the bundled version validator against the deployable file or build directory, then verify the rendered label in a browser.

## Prepare Pages Source

- Static HTML already runnable from the repository root: use `master:/`.
- Vite or another static build: set the public base to `/<repo>/`, emit into `docs/`, and commit `docs/`; use `master:/docs`.
- User/organization Pages repository named `OWNER.github.io`: use base `/`.
- SSR, backend, or filesystem-dependent apps cannot run directly on branch-based GitHub Pages. Stop and explain the incompatibility instead of publishing a broken page.

Test the production output locally before committing. Confirm routes, scripts, styles, images, and the repository link under the repository subpath.

## Create Or Reuse Repository

Prefer an existing correct `origin`. For a new repository:

```bash
gh repo create OWNER/REPO --public --source=. --remote=origin --description "DESCRIPTION"
git add <intentional paths>
git commit -m "Publish project"
git push -u origin master
gh repo edit OWNER/REPO --default-branch master
```

If the first commit must exist before repository creation, commit locally first and use `gh repo create ... --push`. Never use a force push unless the user explicitly requests history replacement.

Set public metadata after the Pages URL is known:

```bash
gh repo edit OWNER/REPO --description "DESCRIPTION" --homepage "https://OWNER.github.io/REPO/"
```

## Enable Or Update Pages

Create Pages when it does not exist:

```bash
gh api --method POST repos/OWNER/REPO/pages \
  -f 'source[branch]=master' \
  -f 'source[path]=/'
```

Use `/docs` for a committed build directory. If Pages already exists, update it:

```bash
gh api --method PUT repos/OWNER/REPO/pages \
  -f 'source[branch]=master' \
  -f 'source[path]=/docs'
```

If the installed GitHub CLI cannot encode the nested fields correctly, send JSON with `--input -`; do not guess repeatedly against the live API.

## Verify

```bash
gh api repos/OWNER/REPO --jq '{url:.html_url,homepage:.homepage,default_branch:.default_branch}'
gh api repos/OWNER/REPO/pages --jq '{url:.html_url,status:.status,source:.source}'
gh run list --repo OWNER/REPO --limit 10
```

Poll with bounded retries because Pages deployment is asynchronous. Open the returned Pages `html_url`, verify the expected title/content and assets, then verify the repository link and new visible version on the rendered page. A `queued` or `building` response is not final success.
