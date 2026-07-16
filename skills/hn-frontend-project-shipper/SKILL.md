---
name: hn-frontend-project-shipper
description: 端到端交付小型前端、Web 应用、作品集、GitHub Pages 和 UI 演示项目。用于用户要求构建、打磨、修复、本地运行、质量检查、截图、更新 README、添加仓库或页面链接、改善响应式布局、制作分享卡片、增加适度动效、提交、发布，或为 GitHub Release 准备前端项目。
---

# HN Frontend Project Shipper

## Purpose

Move a frontend project from request to a verified, presentable release. Use the existing stack and design direction, make focused improvements, verify desktop and mobile, capture screenshots when needed, and leave the repository ready to publish.

## Operating Rules

- Inspect the project before editing: package manager, framework, scripts, deploy target, current git status, and existing design conventions.
- Preserve the user's design taste: compact, polished, low-noise, mobile-safe, not generic AI slop.
- Prefer shipping the real usable experience over landing pages or explanation screens.
- Verify with a browser when layout, interaction, screenshots, canvas, or responsive behavior matter.
- Treat `README`, screenshots, GitHub repo links, GitHub Pages links, and publish steps as part of the shipping workflow, not afterthoughts.
- When starting a new project, prefer the reusable templates in `references/templates/` over building a fresh structure from memory.
- When working inside `G:\code` or another multi-project workspace, create or update a compact project index using `references/project-index.md`.
- Do not commit or push unless the user asks, but prepare clean changes and report what remains.

## Workflow

1. Orient.
   - Read `package.json`, framework config, README, design docs, and relevant app entry files.
   - Run `git status --short` and avoid overwriting unrelated user changes.

2. Plan the smallest useful release slice.
   - If the request is broad, split into build/fix, UI polish, QA, docs, publish.
   - Use `references/release-checklist.md` to choose the right path.

3. Implement.
   - Follow existing component, style, and state patterns.
   - For UI, check spacing, typography, responsive behavior, empty states, loading states, and button text fit.
   - For performance bugs, reproduce first and fix the root cause rather than masking symptoms.

4. Verify.
   - Install dependencies only when needed.
   - Run relevant tests, type checks, lint, and build.
   - Start the local dev server when the app needs one.
   - Use Playwright or browser inspection for desktop and mobile checks.

5. Package for presentation.
   - Update README only with concise, useful content.
   - Add or refresh screenshots if requested or if README/page links require them.
   - Confirm GitHub repo and Pages links are visible where requested.

6. Handoff.
   - Summarize changed files, verification, local URL, and any publish/commit status.

## Output Shape

```text
Done:
- ...

Verified:
- ...

Try it:
- Local URL or file path

Notes:
- ...
```

## References

- Read `references/release-checklist.md` for the end-to-end ship checklist.
- Read `references/ui-qa.md` when the task touches layout, responsive design, animations, screenshots, or share cards.
- Read `references/project-index.md` when creating or refreshing a workspace-level project map.
- Read `references/template-readme.md` when a project needs a short README or `AGENTS.md`.
- Read `references/templates/frontend-vite-react.md` when creating a small frontend/web tool project.
- Read `references/templates/chrome-extension-mv3.md` when creating a browser extension.
- Read `references/templates/codex-skill-package.md` when creating a reusable Codex skill package.
- Use `scripts/create_project_index.ps1` on Windows when a workspace needs a first-pass `PROJECTS.md` draft.
