$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..")

$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_PORT = "1103"
$env:MYSQL_USER = "erp"
$env:MYSQL_PASSWORD = "erp_dev_pass"
$env:REDIS_URL = "redis://127.0.0.1:1104/1"
$env:CHANNEL_REDIS_URL = "redis://127.0.0.1:1104/2"
$env:DB_FAILOPEN_SQLITE = "False"
$env:CACHE_FAILOPEN_LOCMEM = "False"

$stdoutLog = Join-Path (Get-Location) "backend-local.out.log"
$stderrLog = Join-Path (Get-Location) "backend-local.err.log"
$pidFile = Join-Path (Get-Location) "backend-local.pid"
$pythonExe = (Resolve-Path ".\.venv\Scripts\python.exe").Path

$process = Start-Process `
  -FilePath $pythonExe `
  -ArgumentList @("-m", "uvicorn", "myproject.asgi:application", "--host", "0.0.0.0", "--port", "1102") `
  -WorkingDirectory (Get-Location).Path `
  -RedirectStandardOutput $stdoutLog `
  -RedirectStandardError $stderrLog `
  -WindowStyle Hidden `
  -PassThru

Set-Content -Path $pidFile -Value $process.Id
