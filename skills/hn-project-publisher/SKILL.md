---
name: hn-project-publisher
description: 端到端初始化、版本化并发布个人 Web 项目，包括 npm、Git、GitHub、从 master 分支发布 GitHub Pages、简洁的中英文 README、截图、页面可见的仓库与版本标识，以及作品集收录。用于用户要求发布、重新发布、创建版本、推送、部署、上线项目、启用 GitHub Pages、提升公开项目版本号、将项目加入 GitHub 主页或其他作品集，或完成本地项目的完整公开发布流程。
---

# HN Project Publisher

## Goal

Turn a local web project into a verified, versioned public release: initialize missing npm and Git metadata, publish a GitHub repository, deploy from `master`, add concise bilingual presentation material, expose the repository link and current version in the UI, and update every portfolio target the user names.

## Rules

- Inspect before changing anything. Read project instructions, `package.json`, lockfiles, framework config, `.gitignore`, README files, git status, branches, and remotes.
- Preserve existing metadata and user changes. Initialize only missing npm or Git state; never replace a populated `package.json`, README, history, or remote without checking it.
- Use the project's existing package manager. If no package metadata exists, run `npm init -y` and then add only the scripts and fields the project needs.
- Use `master` for this workflow. For a new repository, run `git init -b master`. For an existing repository, inspect its published/default branch before renaming; do not rewrite shared history.
- Treat an explicit request containing “publish”, “release”, “push”, “deploy”, or “发布” as authorization to create/push the project repository, enable Pages, and update the specifically named portfolio targets. Do not publish to inferred or unnamed third-party sites.
- Never put access tokens, cookies, API keys, or local absolute paths in committed files. Reuse authenticated CLI, connector, or browser sessions.
- Keep unrelated repositories and portfolio formatting intact. Make minimal, reversible edits.
- Treat a project as previously published when its remote repository, Pages site, release tag, or earlier public commit exists. Every republish must increase the version before building or pushing; never reuse the previous public version.
- Use Semantic Versioning. Apply the user-requested major, minor, or patch bump; default to patch for an ordinary republish. Keep `package.json`, lockfile, rendered page, and build output on the same version.
- Verify each public URL after publication; do not report success from a command exit code alone.

## Workflow

1. Orient.
   - Run `git status --short --branch`, inspect remotes, and identify the GitHub owner with `gh api user --jq .login` when GitHub CLI is available.
   - Identify the app type, build command, output directory, base-path requirements, and whether the page can run as static files.
   - Determine whether this is the first publication or a republish. Record the current local version and the latest public version from `origin/master`, the live page, or the latest release/tag.
   - Identify the repository name, one-sentence Chinese and English descriptions, GitHub visibility, and every requested portfolio target from the user's message or project instructions.
   - Ask only for missing information that materially changes a public action, such as an unknown repository owner, visibility, or unnamed portfolio URL.

2. Prepare the project.
   - Initialize missing npm metadata without overwriting existing fields.
   - Install dependencies only when required and use the existing lockfile's package manager.
   - Initialize missing Git state on `master`; add a suitable `.gitignore` before staging dependencies, secrets, caches, or build debris.
   - For a republish, bump the version before editing the visible version or generating build output. Default to the next patch version unless the user requests minor or major. Update the lockfile together with `package.json`.
   - For a first publication, preserve a valid existing version or initialize `1.0.0` when none exists.
   - Run relevant tests, lint, type checks, and build. Fix release-blocking failures in scope before publishing.

3. Prepare branch-based Pages output.
   - Publish a directly runnable static site from `master:/`.
   - For projects requiring a build, publish committed static output from `master:/docs`; configure the build output and repository base path accordingly.
   - Do not select source code that requires a server or uncommitted generated output as the Pages source.
   - Read [references/github-publishing.md](references/github-publishing.md) for the command sequence and verification checks.

4. Add public presentation.
   - Add a visible GitHub repository link to the project page, preferably in an existing header, footer, about area, or compact icon action. Preserve the design and include an accessible label.
   - Add a visible version label such as `v1.2.3` in the header, footer, about area, or another durable low-noise location. Source it from the canonical project version when the stack permits; do not maintain an unrelated second version value.
   - Capture a current project screenshot after the final UI, including the repository link, is running. Store it in a stable repository path such as `assets/screenshot.png` and verify that GitHub can render it.
   - Create or replace the project README with concise Chinese and English sections totaling no more than 200 text units. Include the screenshot, GitHub repository link, and GitHub Pages link.
   - Read [references/readme-template.md](references/readme-template.md), then run `node scripts/validate_release_readme.mjs <README path> <repo URL> <Pages URL>` from this skill directory.
   - After building, run `node scripts/validate_release_version.mjs <package.json> <page file or build directory> [previous public version]` from this skill directory.

5. Publish and enable Pages.
   - Commit intentionally on `master`, create or reuse the correct public GitHub repository, push, and set the remote default branch to `master` when needed.
   - Enable or update GitHub Pages with source branch `master` and path `/` or `/docs` as selected above.
   - Set the repository homepage to the live Pages URL and keep the repository description concise.
   - Poll the Pages API/build status and open the public URL until the expected page is visible or a concrete failure is known.
   - Verify in the browser that the new `vX.Y.Z` is visible and matches `package.json`; the presence of a version string only inside JavaScript source is insufficient.

6. Update portfolios.
   - Read [references/portfolio-updates.md](references/portfolio-updates.md).
   - Update the GitHub profile README project list when the public `OWNER/OWNER` repository exists or the user asks to create it.
   - Update every additional portfolio site explicitly named by the user using its repository, API, connector, CLI, or authenticated browser session.
   - Publish the same canonical title, concise description, current version, repository URL, Pages URL, and screenshot/thumbnail everywhere when the target supports a version field or version text.
   - Verify the resulting public portfolio page or entry. Report any target not updated and the exact missing access or information.

7. Handoff.
   - Report the previous version, new version, bump type, repository URL, Pages URL, README/version validation results, branch/source path, commit, build checks, and each portfolio target with `updated`, `verified`, or `blocked` status.
   - Separate completed external changes from local-only preparation.

## Output

```text
Published:
- Version: <previous> -> <new> (<patch|minor|major|initial>)
- Repository: ...
- GitHub Pages: ...
- Source: master:/ or master:/docs

Verified:
- Build/tests: ...
- README: screenshot + links + length
- Page version: visible and matches package/build
- Page repository link: ...

Portfolios:
- GitHub profile: updated/verified/blocked
- <named target>: updated/verified/blocked

Notes:
- ...
```
