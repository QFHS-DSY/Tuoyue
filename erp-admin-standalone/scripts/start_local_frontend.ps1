$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..")

$env:VITE_API_BASE_URL = "http://127.0.0.1:1102"

$stdoutLog = Join-Path (Get-Location) "frontend-local.out.log"
$stderrLog = Join-Path (Get-Location) "frontend-local.err.log"
$pidFile = Join-Path (Get-Location) "frontend-local.pid"
$npmCmd = (Get-Command "npm.cmd").Source

$process = Start-Process `
  -FilePath $npmCmd `
  -ArgumentList @("run", "dev", "--", "--host", "0.0.0.0", "--port", "1101", "--strictPort") `
  -WorkingDirectory (Get-Location).Path `
  -RedirectStandardOutput $stdoutLog `
  -RedirectStandardError $stderrLog `
  -WindowStyle Hidden `
  -PassThru

Set-Content -Path $pidFile -Value $process.Id
