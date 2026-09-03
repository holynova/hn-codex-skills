# Release Checklist

Use this checklist when shipping a frontend or UI project.

## Orientation

- Read `package.json` and identify npm, pnpm, yarn, or bun.
- Read framework config: Vite, Next.js, Astro, Remix, Electron, or static HTML.
- Read README and design docs.
- Run `git status --short`.
- Identify deploy target: GitHub Pages, Vercel, Netlify, static files, Chrome extension, desktop app.

## Build And Verification

Run only commands that fit the project:

- install: `npm install`, `pnpm install`, `yarn install`, or existing lockfile preference.
- dev server: project `dev` script.
- tests: `test`, `vitest`, `jest`, or framework-specific tests.
- type check: `tsc --noEmit` or framework type script.
- lint: project lint script.
- build: project build script.

If a command fails:

- Report the failure.
- Fix if it is in scope.
- Avoid hiding failures by removing tests or weakening checks.

## README And Presentation

For small public projects, README should usually include:

- Project name and one-sentence value.
- Screenshot or GIF.
- Live demo link.
- GitHub repo link only if useful outside GitHub contexts.
- Local run commands.
- Tech stack in one short line.

Keep the README concise unless the project needs full docs.

## GitHub Pages

Before publishing:

- Confirm base path settings for Vite/Next/static site.
- Confirm generated output directory.
- Confirm links work under the GitHub Pages URL.
- Capture at least desktop and mobile screenshots if the README or user asks.

## Handoff

Report:

- Files changed.
- Commands run and results.
- Local URL.
- Screenshots updated.
- Commit/push/publish status.
- Any unresolved risk.
