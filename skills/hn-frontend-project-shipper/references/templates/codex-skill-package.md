# Template: Codex Skill Package

Use when a workflow should be installed on multiple machines with `npx` or `skills`.

## Package Layout

```text
README.md
package.json
bin/
  install.mjs
skills/
  skill-name/
    SKILL.md
    agents/
      openai.yaml
    references/
    scripts/
```

## Skill Rules

- Put trigger conditions and operating rules in `SKILL.md`.
- Put long checklists in `references/`.
- Put reusable commands in `scripts/`.
- Keep each skill focused on one recurring workflow.
- Prefer stable templates and checklists over hidden assumptions in chat.

## Installer Requirements

- Install all bundled skills by default.
- Install one named skill when requested.
- Support `--path`, `--force`, and `--dry-run`.
- Refuse to write outside the target skills directory.

## Expected Scripts

```json
{
  "scripts": {
    "check": "node ./bin/install.mjs --dry-run",
    "install-skills": "node ./bin/install.mjs install"
  }
}
```

## Release Checklist

1. Validate each skill.
2. Run installer dry-run.
3. Run package dry-run.
4. Update README install examples.
5. Commit and push.
6. Install from GitHub on the target machine.
