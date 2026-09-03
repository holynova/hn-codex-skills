# Template: Chrome Extension MV3

Use for browser extensions with popup UI, content scripts, background service workers, or options pages.

## Stack

- Manifest V3
- TypeScript
- Vite or WXT when richer extension packaging is needed

## Expected Files

```text
README.md
AGENTS.md
package.json
manifest.json
src/
  background/
  content/
  popup/
  options/
public/
scripts/
```

## Expected Scripts

```json
{
  "scripts": {
    "dev": "vite --host 127.0.0.1",
    "build": "vite build",
    "zip": "node scripts/zip-extension.mjs"
  }
}
```

## Manifest Checklist

- Use least-privilege permissions.
- Keep host permissions narrow.
- Explain why permissions are needed in README.
- Separate popup UI, content script, and background responsibilities.
- Avoid collecting or sending page data unless explicitly required.

## Verification

1. Build the extension.
2. Load unpacked extension in Chrome.
3. Test popup interactions.
4. Test content script injection on a real target page.
5. Test background/service worker behavior.
6. Document install and reload steps.
