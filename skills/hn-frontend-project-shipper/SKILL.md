---
name: hn-frontend-project-shipper
description: Verify whether an existing frontend project is locally ready to hand off for release. Use when the user asks for a frontend release-readiness check, pre-publish verification, build and browser QA, or a concrete list of blockers before someone commits or deploys. This skill runs existing checks and inspects the built UI; it does not redesign the UI, create assets or documentation, commit, push, or publish.
---

# HN Frontend Project Shipper

## Responsibility

Determine whether an existing frontend project is locally ready for release handoff. Produce evidence from the repository's own checks and the built application, then return either `ready for handoff` or a concrete blocker list.

## Boundaries

- Do not implement features, fix defects, or redesign the UI under this skill.
- Do not create screenshots, icons, README content, release packages, workflows, commits, or deployments.
- If verification exposes a defect, report the reproduction and route the fix to the appropriate implementation or UI skill.
- Use the project's existing package manager, scripts, and documented release rules.
- Preserve unrelated worktree changes and never clean or switch away from them.

## Workflow

1. Establish the verification contract.
   - Read repository instructions, package manifest, lockfile, build configuration, and deploy configuration.
   - Run `git status --short --branch -uall`.
   - Identify the commands and browser paths that define local release readiness.

2. Run repository checks.
   - Run the applicable test, typecheck, lint, and production build commands already defined by the project.
   - Do not weaken configuration or skip a failing required check to obtain a pass.
   - Record the command, exit status, and relevant failure output.

3. Inspect the built application.
   - Serve the production build or the documented preview target.
   - Exercise the primary workflow and relevant error, empty, and loading states.
   - When layout matters, use `references/ui-qa.md` for desktop and mobile verification.

4. Issue the handoff decision.
   - `ready for handoff`: every required local check passed and the primary workflow was exercised against the built output.
   - `blocked`: list each failing command or reproducible browser defect with the narrowest next owner.
   - `unverified`: state which required layer could not be exercised and why.

## Output

```text
Decision: ready for handoff | blocked | unverified

Checks:
- <command or browser path> -> pass | fail | not run

Blockers:
- <reproduction and likely owner>

Handoff boundary:
- No commit, push, package, or deployment performed.
```

## Reference Routing

- Read `references/release-checklist.md` for the local readiness evidence matrix.
- Read `references/ui-qa.md` only when the built application has a visual or responsive surface.
