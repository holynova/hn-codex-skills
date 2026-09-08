---
name: hn-ui-layout-typography-audit
description: Audit an existing website or UI, or guide a new web or interface build, for visual hierarchy, grouping, alignment, repetition, contrast, whitespace, color, and typography. Use when a user asks whether an interface looks professional, wants a layout or type review, needs design fixes, or asks for a practical do/don't checklist before implementing a page or UI.
---

# HN UI Layout & Typography Audit

Turn layout and typography principles into specific, testable interface decisions. Prioritize scanability, information hierarchy, and legibility over decorative redesign.

## Scope

- Use for existing UIs, screenshots, designs, rendered pages, or code that can be run and inspected.
- Use for new websites and interfaces before implementation and again after rendering.
- Preserve the existing brand, product intent, and accessibility requirements unless the user requests a visual rebrand.
- Use `hn-tool-ui-polisher` as well when the task also needs interaction states, control behavior, workflow feedback, or tool-specific usability work. Share one task scope, findings list, and verification pass; do not restart intake or duplicate approvals when switching references.
- An audit-only request ends with findings and proposed edits. Implement when the user requests a build or fixes; an audit-and-fix request authorizes continuing into the in-scope repairs without another generic confirmation. Preserve explicit approval requirements for scope or brand changes.

## Workflow

1. Establish the task.
   - Identify the primary user action, intended audience, content hierarchy, target viewport, and any fixed brand constraints.
   - For an existing UI, inspect the rendered result or screenshots before recommending or making visual changes. Check both desktop and mobile when responsive behavior is in scope.

2. Run the layout and type audit.
   - Read `references/layout-typography-checklist.md`.
   - Start with the visual center and reading order, then audit proximity, alignment, repetition, contrast, whitespace, color, and typography.
   - Classify findings as blocking, important, or polish. State the visible evidence and the expected user impact; do not give vague feedback such as “make it cleaner.”

3. Create or repair the interface when implementation is requested; for audit-only work, present these as proposed corrections.
   - Group related content before changing styles.
   - Establish a small spacing scale, a clear alignment system, a limited type hierarchy, and a limited color system.
   - Make contrast deliberate: preserve sameness for one semantic level and create obvious differences between levels.
   - Remove decorative elements, borders, labels, and copy that do not support reading or action.

4. Verify the result.
   - Inspect a full-page view and a small-scale view. The primary task and focal point must remain obvious when zoomed out.
   - Verify text wrapping, alignment edges, color contrast, and information grouping at each relevant viewport.
   - For changed code, run the appropriate project checks and visually inspect the rendered UI.

## Creation Gate

Before implementing a new interface, resolve the following as an internal design checklist using the request and existing product evidence. This is not a user approval gate; ask only about unresolved choices that materially affect scope or protected brand constraints:

- Name one primary focal point and the next two pieces of information a reader should see.
- Define content groups and make within-group spacing smaller than between-group spacing.
- Choose the primary alignment axes or grid.
- Define reusable styles for headings, body text, metadata, controls, spacing, and color roles.
- Define where strong contrast is intentional and where a calm, consistent treatment is intentional.

## Output

Use the user’s language. For audits, report actionable issues in this form:

```text
Priority findings
- [Blocking|Important|Polish] Area — evidence, user impact, exact correction.

Implementation checklist
- [ ] ...

Verified
- Viewports and states inspected.
- Remaining tradeoffs or constraints.
```

For a new build, briefly state the design decisions and proceed to implementation; do not end the turn at the checklist or wait for confirmation of internal layout choices. Do not treat a complete redesign as the default remedy; fix the information structure first.

## Reference

- Read `references/layout-typography-checklist.md` for the detailed audit and creation checklist.
