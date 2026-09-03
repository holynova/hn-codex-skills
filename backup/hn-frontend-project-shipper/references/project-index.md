# Workspace Project Index

Use this when a workspace contains many projects and Codex keeps rediscovering the same map.

## Create `PROJECTS.md`

Place it at the workspace root, not inside a single project.

```md
# Workspace Project Index

Read this before broad project work in this workspace.

| Project | Type | Status | Run | Verify | Links | Notes |
|---|---|---|---|---|---|---|
| project-name | React/Vite app | active | pnpm dev | pnpm build | repo/pages | design docs, warnings |
```

## Status Values

- `active`: current work or likely to be edited soon.
- `paused`: real project, but not current.
- `published`: has a public repo/page and needs careful updates.
- `archive`: output, experiment, or old code.
- `runtime`: local portable runtime, vendor app, or model environment.
- `unknown`: inspect before editing.

## Discovery Checklist

Use read-only commands first:

```powershell
Get-ChildItem -Path <workspace> -Directory
rg --files -g package.json -g README.md -g AGENTS.md -g PRD.md -g DESIGN.md
```

Record only what helps future work:

- project purpose
- package manager
- run/build/test commands
- repo and page links
- generated/vendor folders to avoid
- whether README or git setup is missing

## Update Rules

- Update the index after creating a project.
- Update it when a project is published, archived, renamed, or gets a stable run command.
- Keep each row short. Put details in the project README.
