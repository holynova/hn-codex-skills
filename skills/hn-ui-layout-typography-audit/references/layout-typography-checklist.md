# UI Layout and Typography Checklist

Use this reference for both audits and new builds. Record only findings that affect comprehension, action, trust, or visual consistency. Prefer an observed symptom, its cause, and an exact repair.

## 1. Establish the reading path

Identify the primary action or message, then the secondary information and supporting detail.

- [ ] A reader can identify the page purpose in a quick glance.
- [ ] One focal point is clearly more prominent than nearby elements.
- [ ] The visual path is intentional: focal point, supporting explanation, then action or detail.
- [ ] Secondary information is present but does not compete with the focal point.
- [ ] Important actions do not compete with equally loud decorative elements, cards, badges, or headlines.

**Fix:** Make the focal point larger, heavier, warmer, more isolated, or more visually distinct. De-emphasize nonessential content instead of making every element larger.

## 2. Proximity: make relationships visible

Use distance to communicate whether items belong together.

### Do

- [ ] Keep a label, its value, help text, validation message, and control visibly associated.
- [ ] Keep headings closer to the content they introduce than to the preceding section.
- [ ] Keep captions, metadata, buttons, and status messages close to the object they describe or affect.
- [ ] Use smaller gaps within a group and larger gaps between groups.
- [ ] Use whitespace to separate unrelated groups before adding borders or containers.

### Do not

- [ ] Do not distribute every element with equal gaps when their relationships differ.
- [ ] Do not leave titles, captions, labels, or errors detached from their related content.
- [ ] Do not place unrelated content close together just because a region has empty space.
- [ ] Do not fill corners or the page center with unrelated badges, icons, or metadata.

**Audit test:** Blur or squint at the page. If more than a handful of isolated objects appear, regroup content or reduce visual noise.

## 3. Alignment: give every element an anchor

### Do

- [ ] Define page margins and a primary grid or column system.
- [ ] Align text, controls, images, cards, and section boundaries to intentional shared edges or baselines.
- [ ] Use one primary text alignment per region; left alignment is usually the clearest default for dense content.
- [ ] Reuse alignment rules across repeated modules and breakpoints.
- [ ] Let image edges, dividers, or columns establish useful alignment lines for nearby content.

### Do not

- [ ] Do not place elements where there happens to be room.
- [ ] Do not mix centered, left-aligned, and right-aligned text in one region without a clear semantic reason.
- [ ] Do not use centered layout as a default. Reserve it for deliberately formal, symmetric, or brief content.
- [ ] Do not introduce one-off offsets that make controls, cards, or headings look accidental.

**Fix:** Add or expose grid lines, normalize container padding, and align to shared edges before adjusting visual decoration.

## 4. Repetition: build a system, not a collage

### Do

- [ ] Repeat the same roles for type, color, spacing, border treatment, icons, and controls.
- [ ] Keep repeated cards, fields, list rows, tables, and section headers structurally consistent.
- [ ] Reuse a small set of intentional accents, such as one divider treatment, one badge style, or one highlight color.
- [ ] Use components or design tokens instead of manual, per-instance styling.

### Do not

- [ ] Do not give each section a new heading style, radius, color, or card treatment.
- [ ] Do not repeat an accent so often that it loses emphasis.
- [ ] Do not create a unique decoration that appears once unless it is the intentional focal point.

**Fix:** Inventory the styles already present. Keep the useful recurring ones, remove near-duplicates, and turn the remainder into reusable tokens or components.

## 5. Contrast: make hierarchy unmistakable

Use size, weight, color, spacing, shape, direction, or density to distinguish roles. If two elements differ in meaning, make the difference visible enough to be intentional.

### Do

- [ ] Make primary, secondary, and supporting text visibly distinct.
- [ ] Use contrast to separate action from explanation, section title from body, and status from neutral information.
- [ ] Pair different type structures deliberately, such as a readable text face with a distinct display face, and reinforce the difference with size or weight.
- [ ] Use large whitespace as a contrast tool in dense pages.
- [ ] Ensure every important color difference remains meaningful for users with color-vision differences; use labels, icons, or shape when needed.

### Do not

- [ ] Do not make false contrast with barely different sizes, weights, grays, line widths, or fonts.
- [ ] Do not make every heading large, bold, colored, and boxed; then nothing is primary.
- [ ] Do not let a small bold element and a large light element compete for the same focal role.
- [ ] Do not combine similar-but-not-identical fonts or visual treatments; choose one consistent treatment or make their difference obvious.

**Audit test:** View the page as a thumbnail. The focal point and major sections should still be clear.

## 6. Whitespace and containers

- [ ] Treat whitespace as structure, not unused real estate.
- [ ] Give the focal point and section boundaries enough breathing room.
- [ ] Use spacing to express hierarchy before adding nested cards, borders, shadows, or colored panels.
- [ ] Keep container padding and section gaps consistent with the spacing scale.
- [ ] Remove borders, rounded rectangles, and shadows that do not clarify grouping or hierarchy.
- [ ] Avoid deep card nesting; it obscures grouping and makes the page feel fragmented.

## 7. Color

- [ ] Assign colors semantic roles: background, surface, primary text, secondary text, accent, success, warning, and error.
- [ ] Use a limited palette. Derive tonal variations from core colors before adding another hue.
- [ ] Reserve warm or high-saturation colors for small, purposeful emphasis; they advance visually.
- [ ] Use cool or muted colors more readily for larger background areas when appropriate.
- [ ] Check text and icon contrast against every background, including hover, disabled, and selected states.
- [ ] Avoid adjacent colors with similar lightness when legibility matters; increase lightness contrast or separate them with space, stroke, or a surface.

## 8. Typography and text layout

### Hierarchy and readability

- [ ] Use a small, named type scale for display, headings, body, metadata, controls, and captions.
- [ ] Keep paragraph measure, line height, and paragraph spacing comfortable for the target viewport.
- [ ] Use body type that is plain and readable; reserve display, script, or decorative faces for short and intentional accents.
- [ ] Make headings descriptive and place them close to their content.
- [ ] Use bold sparingly to mark hierarchy or key phrases, not every important sentence.
- [ ] Check that text never overflows controls, cards, columns, or mobile viewports.

### Font pairing

- [ ] Prefer one well-equipped font family when the UI needs a calm, reliable system.
- [ ] When using multiple families, pair visibly different structures and reinforce the difference with weight, size, or case.
- [ ] Avoid pairing two similar serif faces, two similar sans faces, two scripts, or a script with an italic as if they were contrasting styles.
- [ ] Avoid synthetic italic or bold when a real font face is available.

### Chinese and bilingual interfaces

- [ ] Keep Chinese, Latin text, numbers, punctuation, and parentheses visually consistent.
- [ ] Avoid manual spaces and repeated line breaks for layout; use CSS spacing, grid, flex, and text styles.
- [ ] Check Chinese line-break rules, orphaned headings, and awkwardly split Latin words or numbers.
- [ ] Use uppercase English only for short labels or deliberate branding; do not use it to make long text more readable.

### English microtypography

- [ ] Use one space after sentence punctuation.
- [ ] Use proper quotation marks and apostrophes when the content and platform support them.
- [ ] Avoid default underlining for emphasis; use hierarchy, color, weight, or an intentional text decoration. Underlines remain appropriate for recognizable links.
- [ ] Check display text kerning manually where letter pairs create uneven visual gaps.
- [ ] Avoid widows and orphans in editorial or long-form layouts when the layout system permits control.

## 9. Responsive verification

- [ ] Recheck grouping and reading order after columns collapse.
- [ ] Ensure controls retain their labels, target size, and association with help or errors.
- [ ] Verify that actions do not move away from the content they affect.
- [ ] Verify that text wraps naturally without one-word lines, clipped labels, or accidental emphasis.
- [ ] Check at least one desktop and one narrow mobile viewport when the UI is responsive.

## New-build gate

Before coding, complete this compact specification:

| Decision | Record |
| --- | --- |
| Primary user action or message | One sentence |
| Focal point | One component or content block |
| Content groups | Group names and their order |
| Alignment model | Grid, columns, and primary text alignment |
| Spacing model | Base unit and within/between-group gaps |
| Type model | Families and semantic type roles |
| Color model | Semantic color roles and accent rule |
| Repeated elements | Components, dividers, icons, or accents |
| Responsive changes | What stacks, hides, or changes order |

## Reporting priorities

- **Blocking:** Prevents reading, finding the primary action, understanding a relationship, or using the interface at a supported viewport.
- **Important:** Weakens hierarchy, causes repeated inconsistency, or makes the interface look unreliable or difficult to scan.
- **Polish:** Improves rhythm, visual balance, or finish after structural issues are resolved.
