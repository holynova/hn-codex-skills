---
name: hn-tool-ui-polisher
description: 审核并打磨紧凑型工具界面，使其真正易用。用于用户要求 UI 专家反馈、修复布局、优化交互、响应式质量检查、改进控件、增强状态表达、对齐面板、审查界面文案，或让工具应用达到专业且可发布的完成度。
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
