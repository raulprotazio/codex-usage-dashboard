param([switch]$SyncUbuntu)
$ErrorActionPreference = 'Stop'
$projectDir = $PSScriptRoot
$config = Get-Content -LiteralPath (Join-Path $projectDir 'local-config.json') -Raw | ConvertFrom-Json
$pythonPath = $config.python
$expectedDigest = (Get-FileHash -LiteralPath (Join-Path $projectDir 'skills/codex-usage-dashboard/scripts/codex_usage_dashboard.py') -Algorithm SHA256).Hash.ToLowerInvariant()
if ($SyncUbuntu) {
  & $pythonPath (Join-Path $projectDir 'scripts/local_dashboard.py') --sync-ssh $config.sshTarget
  if ($LASTEXITCODE -ne 0) { throw 'Falha na atualização do Ubuntu.' }
}
try { $health = Invoke-RestMethod 'http://127.0.0.1:8765/api/health' -TimeoutSec 2 } catch { $health = $null }
if ($health -and ($health.app -ne 'codex-usage-dashboard' -or $health.local_hardening -ne 'v1')) { throw 'A porta 8765 está ocupada por outra versão. Feche-a antes de iniciar.' }
if ($health -and $health.source_sha256 -ne $expectedDigest) { throw 'O dashboard está executando código anterior. Feche o processo do painel antes de iniciar a versão atualizada.' }
if (-not $health) {
  $localData = Join-Path $projectDir 'local-data'
  New-Item -ItemType Directory -Path $localData -Force | Out-Null
  Start-Process -FilePath $pythonPath -ArgumentList @('-u', 'scripts/local_dashboard.py') -WorkingDirectory $projectDir -WindowStyle Hidden -RedirectStandardOutput (Join-Path $localData 'server.log') -RedirectStandardError (Join-Path $localData 'server-error.log')
  for ($attempt=0; $attempt -lt 30; $attempt++) {
    Start-Sleep -Milliseconds 500
    try { $health=Invoke-RestMethod 'http://127.0.0.1:8765/api/health' -TimeoutSec 2; break } catch {}
  }
}
if (-not $health) { throw 'O painel não iniciou. Consulte local-data/server-error.log.' }
Start-Process 'http://127.0.0.1:8765/'
