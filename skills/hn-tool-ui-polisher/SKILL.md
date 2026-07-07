---
name: hn-tool-ui-polisher
description: Audit and polish compact tool UIs for real usability. Use when the user asks for UI expert feedback, layout fixes, interaction polish, responsive QA, better controls, clearer states, aligned panels, copy feedback, or making a utility app feel professional and ready to ship.
---

# HN Tool UI Polisher

## Purpose

Make a utility UI easier to use, scan, and trust. Focus on workflow clarity, control grouping, state feedback, responsive layout, and professional restraint rather than decorative redesign.

## Operating Rules

- Start from the real running UI when possible. Use screenshots or browser inspection before large visual changes.
- Treat tool surfaces as work surfaces: compact, dense when useful, clear hierarchy, no marketing hero unless the user asked for a landing page.
- Prefer familiar controls: icons for tools, segmented controls for modes, checkboxes/toggles for binary settings, selects/menus for option sets, sliders/inputs for numeric values.
- Every async or destructive command needs visible feedback: loading, success, failure, disabled state, or confirmation.
- Verify text fit, panel alignment, scroll behavior, and mobile layout after changes.
- Keep the existing product identity unless the user explicitly asks for a new visual direction.

## Workflow

1. Inspect the UI.
   - Open the app or read screenshots.
   - Identify primary workflow, secondary controls, output area, states, and failure modes.

2. Run the audit.
   - Use `references/tool-ui-audit.md`.
   - Sort issues by user impact: broken layout, unclear state, inefficient workflow, weak visual hierarchy, polish.

3. Implement polish.
   - Reduce control ambiguity.
   - Align input/output panels.
   - Add copy/success/error feedback.
   - Improve state colors and labels.
   - Preserve stable dimensions so hover, validation, and dynamic content do not shift layout.

4. Verify.
   - Check desktop and mobile viewports.
   - Interact with copy, clear, run, import/export, invalid input, and error states when present.
   - Use browser screenshots for visual changes.

5. Report.
   - Summarize what changed, what was verified, and any remaining UX tradeoff.

## Output Shape

```text
Polished:
- ...

Verified:
- ...

Remaining UX notes:
- ...
```

## References

- Read `references/tool-ui-audit.md` when evaluating or changing a tool UI.
