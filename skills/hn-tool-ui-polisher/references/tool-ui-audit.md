# Tool UI Audit

Use this checklist for compact apps, internal tools, converters, formatters, dashboards, playgrounds, and browser extension UIs.

## Workflow Clarity

- The first screen exposes the primary task immediately.
- Input, settings, and output are visually distinct.
- Primary action is obvious, but not oversized.
- Secondary actions are grouped near the thing they affect.
- Empty, invalid, loading, success, and error states are visible.

## Controls

- Buttons are commands, not mode indicators.
- Modes use tabs or segmented controls.
- Binary options use toggles or checkboxes.
- Repeated actions have consistent icon, label, tooltip, and feedback.
- Copy buttons show a short success state.
- Clear/reset actions are easy to find but not dangerously prominent.

## Layout

- Input and output panels align when comparison matters.
- Scroll containers can reach their final content.
- Fixed toolbars do not hide content.
- Responsive breakpoints preserve the primary workflow.
- Text does not overflow buttons, cards, tabs, or narrow panels.

## Visual Hierarchy

- Status colors have semantic meaning and enough contrast.
- Repaired/changed/warning/error states are visually distinct.
- Typography is compact inside panels and larger only for true page-level headings.
- Spacing groups related controls without creating card nesting.

## Verification

- Desktop viewport around 1280 x 800.
- Mobile viewport around 390 x 844.
- Primary workflow with valid input.
- Primary workflow with invalid input.
- Copy/clear/run actions.
- Any generated screenshot/export/share flow.
