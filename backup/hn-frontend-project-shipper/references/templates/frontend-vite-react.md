# Template: Frontend Vite React

Use for small web tools, UI demos, portfolio pieces, and GitHub Pages projects.

## Stack

- React + TypeScript
- Vite
- Tailwind CSS or project-local CSS
- Lucide icons when icons are useful
- Playwright or browser tooling for visual verification when UI matters

## Expected Files

```text
README.md
AGENTS.md
package.json
index.html
src/
  main.tsx
  App.tsx
  styles.css
public/
assets/
```

## Expected Scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "lint": "eslint ."
  }
}
```

## Creation Flow

1. Read the user's PRD/design direction.
2. Initialize the project with the user's preferred package manager.
3. Build the real app/tool as the first screen.
4. Add README and AGENTS notes.
5. Run build.
6. Start local dev server and verify desktop/mobile if UI matters.
7. Prepare screenshot and publishing metadata if requested.

## README Stub

```md
# Project Name

用途：
技术栈：React + TypeScript + Vite
运行：pnpm dev
构建：pnpm build
发布：
Codex 注意事项：
```
