# Short README / AGENTS Template

Use this when a project lacks enough context for Codex to work efficiently.

## README Template

```md
# Project Name

用途：
技术栈：
运行：
构建/验证：
发布：
Codex 注意事项：
```

## AGENTS.md Template

```md
# Codex Notes

- Read README/PRD/DESIGN before editing.
- Use the existing package manager and scripts.
- Do not scan generated assets, model files, dependencies, or build output unless needed.
- Run the listed verification before final handoff.
- Update README and PROJECTS.md when status or commands change.
```

## Rules

- Keep it short enough that Codex will actually read it.
- Put stable commands in README; put agent behavior and scan boundaries in `AGENTS.md`.
- Do not invent publish links or commands. Mark unknowns as `TBD`.
