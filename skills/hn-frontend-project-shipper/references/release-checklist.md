# Frontend Local Readiness Checklist

Use this checklist to decide whether an existing frontend project can be handed to a separate packaging or publishing workflow.

## Evidence Matrix

| Layer | Evidence |
|---|---|
| Repository | Instructions, clean understanding of worktree state, correct package manager |
| Static checks | Required lint and typecheck commands exit successfully |
| Tests | Required automated tests execute non-empty cases and pass |
| Build | Production build exits successfully and expected output exists |
| Runtime | Built output or documented preview starts successfully |
| Primary workflow | Main user path completes against the built application |
| Responsive surface | Required desktop/mobile viewports have no blocking defects |

## Decision Rules

- Mark `ready for handoff` only when every project-required layer has current evidence.
- Mark `blocked` when a required command fails or a built workflow has a reproducible defect.
- Mark `unverified` when tooling, credentials, services, or environment constraints prevent a required check.
- A development server is not a substitute for inspecting the production build.
- Do not fix a blocker as part of this verification skill; return the reproduction to the correct owner.
