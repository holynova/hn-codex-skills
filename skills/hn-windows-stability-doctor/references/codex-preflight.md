# Codex / Windows Preflight

Use this before repeated local development or Codex environment troubleshooting.

## Common Friction

- PowerShell execution policy blocks `npm.ps1`, `npx.ps1`, or `pnpm.ps1`.
- Chinese text appears garbled because the terminal/code page is not UTF-8.
- `git`, `gh`, `node`, `python`, `docker`, or package managers are missing from PATH.
- Existing localhost ports are already in use.
- Codex skills are installed in more than one directory.

## Safe Checks

```powershell
$PSVersionTable.PSVersion
Get-ExecutionPolicy -List
where.exe node
where.exe npm.cmd
where.exe npx.cmd
where.exe pnpm.cmd
where.exe git
where.exe gh
where.exe python
where.exe docker
git --version
gh auth status
node --version
npm.cmd --version
npx.cmd skills --version
```

## Preferred Command Forms On Windows

Use these inside PowerShell to avoid blocked shim scripts:

```powershell
npm.cmd install
npm.cmd run build
npx.cmd skills ls -g
pnpm.cmd install
pnpm.cmd build
```

## Optional Repairs

Only apply with user approval when the task asks to fix the environment.

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [System.Text.UTF8Encoding]::new()
```

## Handoff

Report:

- which tools are present
- which commands should be used
- what remains broken
- whether a reboot, shell restart, or Codex restart is needed
