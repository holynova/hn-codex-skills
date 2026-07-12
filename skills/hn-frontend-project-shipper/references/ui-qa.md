# Built Frontend Browser Verification

Use this checklist only to verify the existing production build. Record defects; do not polish or modify the UI under this skill.

## Viewports

Use the project's documented targets. When none exist, check representative narrow mobile and desktop viewports.

## Blocking Conditions

- The primary workflow cannot be completed.
- Required controls are unreachable, clipped, obscured, or unusable.
- Content creates unintended horizontal scrolling.
- Text needed to operate the product is truncated or unreadable.
- Loading, empty, validation, success, or error states prevent recovery.
- Keyboard or pointer interaction cannot reach a required action.
- The built application is blank, crashes, or differs materially from the verified development path.

## Evidence

For each defect, record:

- Production-build URL and viewport.
- Starting state and exact interaction sequence.
- Expected and observed behavior.
- Console or network evidence when relevant.
- The narrowest likely owner: implementation, UI, backend, configuration, or environment.

Passing browser verification means the primary workflow and required states were exercised without a blocking condition. It is not a general visual-quality approval.
