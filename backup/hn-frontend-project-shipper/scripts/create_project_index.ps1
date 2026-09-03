param(
  [string]$Workspace = (Get-Location).Path,
  [string]$OutputPath = "",
  [switch]$Apply
)

$ErrorActionPreference = "Stop"

function Get-ProjectType {
  param([string]$Path)

  if (Test-Path (Join-Path $Path "package.json")) { return "node/frontend" }
  if (Test-Path (Join-Path $Path "pyproject.toml")) { return "python" }
  if (Test-Path (Join-Path $Path "requirements.txt")) { return "python" }
  if (Test-Path (Join-Path $Path "project.godot")) { return "godot" }
  if (Test-Path (Join-Path $Path "SKILL.md")) { return "codex-skill" }
  if (Test-Path (Join-Path $Path "README.md")) { return "documented" }
  return "unknown"
}

function Get-RunCommand {
  param([string]$Path)

  $packagePath = Join-Path $Path "package.json"
  if (Test-Path $packagePath) {
    try {
      $package = Get-Content $packagePath -Raw | ConvertFrom-Json
      $scripts = @($package.scripts.PSObject.Properties.Name)
      if ($scripts -contains "dev") { return "npm.cmd run dev" }
      if ($scripts -contains "start") { return "npm.cmd start" }
    } catch {
      return "inspect package.json"
    }
  }
  return ""
}

function Get-VerifyCommand {
  param([string]$Path)

  $packagePath = Join-Path $Path "package.json"
  if (Test-Path $packagePath) {
    try {
      $package = Get-Content $packagePath -Raw | ConvertFrom-Json
      $scripts = @($package.scripts.PSObject.Properties.Name)
      if ($scripts -contains "build") { return "npm.cmd run build" }
      if ($scripts -contains "test") { return "npm.cmd test" }
      if ($scripts -contains "check") { return "npm.cmd run check" }
    } catch {
      return "inspect package.json"
    }
  }
  return ""
}

$resolvedWorkspace = (Resolve-Path -LiteralPath $Workspace).Path
if ($OutputPath -eq "") {
  $OutputPath = Join-Path $resolvedWorkspace "PROJECTS.generated.md"
}

$ignore = @(".git", "node_modules", "dist", "build", ".venv", ".vscode", ".claude")
$projects = Get-ChildItem -LiteralPath $resolvedWorkspace -Directory -Force |
  Where-Object { $ignore -notcontains $_.Name } |
  Sort-Object Name |
  ForEach-Object {
    $path = $_.FullName
    $hasGit = Test-Path (Join-Path $path ".git")
    $hasReadme = Test-Path (Join-Path $path "README.md")
    [PSCustomObject]@{
      Name = $_.Name
      Type = Get-ProjectType $path
      Status = "unknown"
      Run = Get-RunCommand $path
      Verify = Get-VerifyCommand $path
      Notes = ("git:{0}; readme:{1}" -f $hasGit, $hasReadme)
    }
  }

$lines = @()
$lines += "# Workspace Project Index"
$lines += ""
$lines += "Generated from: ``$resolvedWorkspace``"
$lines += ""
$lines += "| Project | Type | Status | Run | Verify | Notes |"
$lines += "|---|---|---|---|---|---|"
foreach ($project in $projects) {
  $lines += "| ``$($project.Name)`` | $($project.Type) | $($project.Status) | $($project.Run) | $($project.Verify) | $($project.Notes) |"
}
$lines += ""
$lines += "Review this draft before treating it as authoritative."

if ($Apply) {
  $finalPath = Join-Path $resolvedWorkspace "PROJECTS.md"
  $lines | Set-Content -LiteralPath $finalPath -Encoding UTF8
  Write-Output "Wrote $finalPath"
} else {
  $lines | Set-Content -LiteralPath $OutputPath -Encoding UTF8
  Write-Output "Wrote $OutputPath"
}
