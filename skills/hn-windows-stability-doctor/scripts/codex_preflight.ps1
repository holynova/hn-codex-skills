param(
  [switch]$Json
)

$ErrorActionPreference = "Continue"

function Find-CommandPath {
  param([string]$Name)
  $command = Get-Command $Name -ErrorAction SilentlyContinue
  if ($null -eq $command) { return $null }
  return $command.Source
}

function Run-Version {
  param(
    [string]$Command,
    [string[]]$Arguments
  )
  try {
    $output = & $Command @Arguments 2>&1 | Select-Object -First 3
    return ($output -join " ").Trim()
  } catch {
    return $null
  }
}

$checks = [ordered]@{
  timestamp = (Get-Date).ToString("s")
  powershell = @{
    version = $PSVersionTable.PSVersion.ToString()
    executionPolicy = Get-ExecutionPolicy -List | ForEach-Object {
      @{ scope = $_.Scope.ToString(); policy = $_.ExecutionPolicy.ToString() }
    }
  }
  encoding = @{
    consoleOutput = [Console]::OutputEncoding.WebName
    outputEncoding = $OutputEncoding.WebName
  }
  tools = @{
    node = @{ path = Find-CommandPath "node"; version = Run-Version "node" @("--version") }
    npmCmd = @{ path = Find-CommandPath "npm.cmd"; version = Run-Version "npm.cmd" @("--version") }
    npxCmd = @{ path = Find-CommandPath "npx.cmd"; version = Run-Version "npx.cmd" @("--version") }
    pnpmCmd = @{ path = Find-CommandPath "pnpm.cmd"; version = Run-Version "pnpm.cmd" @("--version") }
    git = @{ path = Find-CommandPath "git"; version = Run-Version "git" @("--version") }
    gh = @{ path = Find-CommandPath "gh"; version = Run-Version "gh" @("--version") }
    python = @{ path = Find-CommandPath "python"; version = Run-Version "python" @("--version") }
    docker = @{ path = Find-CommandPath "docker"; version = Run-Version "docker" @("--version") }
  }
  skills = @{
    codexSkills = Join-Path $HOME ".codex\skills"
    sharedAgentSkills = Join-Path $HOME ".agents\skills"
    codexSkillsExists = Test-Path (Join-Path $HOME ".codex\skills")
    sharedAgentSkillsExists = Test-Path (Join-Path $HOME ".agents\skills")
  }
  recommendations = @(
    "Use npm.cmd/npx.cmd/pnpm.cmd in PowerShell when script shims are blocked.",
    "If npm.ps1/npx.ps1 must work, consider Set-ExecutionPolicy -Scope CurrentUser RemoteSigned after user approval.",
    "Use UTF-8 output when reading Chinese project files."
  )
}

if ($Json) {
  $checks | ConvertTo-Json -Depth 8
  exit 0
}

Write-Output "Codex / Windows Preflight"
Write-Output "========================="
Write-Output ""
Write-Output "PowerShell: $($checks.powershell.version)"
Write-Output "Console encoding: $($checks.encoding.consoleOutput)"
Write-Output ""
Write-Output "Execution Policy:"
$checks.powershell.executionPolicy | ForEach-Object {
  Write-Output ("- {0}: {1}" -f $_.scope, $_.policy)
}
Write-Output ""
Write-Output "Tools:"
$checks.tools.GetEnumerator() | ForEach-Object {
  $value = $_.Value
  Write-Output ("- {0}: {1} {2}" -f $_.Key, $(if ($value.path) { $value.path } else { "missing" }), $(if ($value.version) { "($($value.version))" } else { "" }))
}
Write-Output ""
Write-Output "Skills:"
Write-Output "- Codex: $($checks.skills.codexSkills) exists=$($checks.skills.codexSkillsExists)"
Write-Output "- Shared: $($checks.skills.sharedAgentSkills) exists=$($checks.skills.sharedAgentSkillsExists)"
Write-Output ""
Write-Output "Recommendations:"
$checks.recommendations | ForEach-Object { Write-Output "- $_" }
