# UI QA

Use this checklist when the task touches frontend design, responsive layout, interactions, animations, screenshots, or share cards.

## Responsive Checks

Check at least:

- Mobile narrow: 375 x 812.
- Mobile wider: 430 x 932.
- Desktop: 1280 x 800 or current viewport.

Look for:

- Text overflow in buttons, cards, tabs, and nav.
- Controls wrapping awkwardly.
- Content hidden behind fixed headers or panels.
- Tap targets too small.
- Horizontal scrolling caused by fixed widths.

## Visual Polish

- Match the existing product style.
- Keep compact tools compact; avoid oversized hero typography inside panels.
- Use stable dimensions for boards, canvases, toolbars, tiles, counters, and icon buttons.
- Keep motion subtle and respect reduced-motion where possible.
- Avoid decorative clutter when the product is a tool.

## Interaction QA

- Buttons show loading/disabled states for async actions.
- Forms validate invalid and empty states.
- Local storage import/export works with malformed input.
- Share-card or screenshot generation uses the same fonts and captures the intended content.
- Canvas output is nonblank and centered if the task is graphical.

## Screenshot QA

- Hide debug overlays and dev-only UI.
- Capture the real app, not a blank loading state.
- For README screenshots, prefer the main workflow over marketing-only screens.
