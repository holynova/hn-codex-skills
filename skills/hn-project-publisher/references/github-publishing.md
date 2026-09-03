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
git init -b master   # 或 git init -b main
```

Add `.gitignore` before staging. Never commit `.env*`, credentials, dependencies (`node_modules`), caches, logs, or OS files.

If Git already exists, inspect history and remote state. Support both `master` and `main` branches.

## Page Enhancements (UI Repo Link & Umami Tracking)

Before packaging or building the page, ensure the following two items are injected into the HTML/UI:

### 1. Visible GitHub Repo Link
Place a clearly visible link or button to the GitHub repository in the page's header, navigation, or footer:
```html
<a href="https://github.com/OWNER/REPO" target="_blank" rel="noopener noreferrer" class="github-link" aria-label="GitHub Repository">
  <!-- GitHub icon or text -->
  GitHub
</a>
```

### 2. Umami Analytics Tracking
Add the standardized Umami tracking snippet inside the `<head>` of `index.html` (or root template/layout):
```html
<!-- Umami Analytics -->
<script defer src="https://cloud.umami.is/script.js" data-website-id="e01c9f78-4607-4e60-b01c-77c8190b12b4"></script>
```

## Screenshot & QR Code Generation

### Screenshot Guidelines
- **Wait for valid content**: Ensure the project is running and fully loaded with real content before taking a screenshot. Never capture a loading spinner, skeleton screen, or blank layout.
- **Mobile vs Desktop Viewport**: If the project is a mobile application, capture the screenshot using a mobile device viewport width (375px~430px), **never** use PC desktop stretched width.
- Save screenshot to `assets/screenshot.png` (or relative path in repository).

### QR Code for GitHub Pages
Generate a mobile QR code pointing to the live GitHub Pages URL so users can scan directly from their mobile phones:
```bash
mkdir -p assets
npx qrcode -o assets/qr.png "https://OWNER.github.io/REPO/"
```

## Cloudflare Custom Domain Convention

Every project automatically deploys to Cloudflare with its dedicated subdomain:
```text
https://<repo-name>.xiaosang.cc
```
Include this dedicated domain in the README and project demo links alongside the GitHub Pages URL.

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

- Static HTML already runnable from the repository root: use `master:/` (or `main:/`).
- Vite or another static build: set the public base to `/<repo>/`, emit into `docs/`, and commit `docs/`; use `master:/docs` (or `main:/docs`).
- User/organization Pages repository named `OWNER.github.io`: use base `/`.
- SSR, backend, or filesystem-dependent apps cannot run directly on branch-based GitHub Pages. Stop and explain the incompatibility instead of publishing a broken page.

Test the production output locally before committing. Confirm routes, scripts, styles, images, and the repository link under the repository subpath.

## Create Or Reuse Repository

Prefer an existing correct `origin`. For a new repository:

```bash
gh repo create OWNER/REPO --public --source=. --remote=origin --description "DESCRIPTION"
git add <intentional paths>
git commit -m "Publish project"
git push -u origin <branch>    # master or main
gh repo edit OWNER/REPO --default-branch <branch>
```

If the first commit must exist before repository creation, commit locally first and use `gh repo create ... --push`. Never use a force push unless the user explicitly requests history replacement.

Set public metadata after the Pages URL is known:

```bash
gh repo edit OWNER/REPO --description "DESCRIPTION" --homepage "https://OWNER.github.io/REPO/"
```

## Enable Or Update Pages

Create Pages when it does not exist (using `master` or `main`):

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

If the default branch is `main`, replace `source[branch]=master` with `source[branch]=main`.

## Verify

```bash
gh api repos/OWNER/REPO --jq '{url:.html_url,homepage:.homepage,default_branch:.default_branch}'
gh api repos/OWNER/REPO/pages --jq '{url:.html_url,status:.status,source:.source}'
gh run list --repo OWNER/REPO --limit 10
```

Poll with bounded retries because Pages deployment is asynchronous. Open the returned Pages `html_url`, verify the expected title/content and assets, then verify the repository link and new visible version on the rendered page. A `queued` or `building` response is not final success.
