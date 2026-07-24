# start_pilote.ps1 — Mise en ligne immediate de KinéCotation depuis ce poste.
#
# Ce que ca fait :
#   1. lance le serveur (waitress via python server.py) sur http://127.0.0.1:8770,
#      en process detache (survit a la fermeture de cette fenetre PowerShell) ;
#   2. lance un tunnel Cloudflare (cloudflared) qui expose ce serveur local
#      derriere une URL publique HTTPS https://xxxxx.trycloudflare.com ;
#   3. affiche l'URL publique a coller/dicter a Malcom.
#
# AUCUN compte d'hebergeur requis. La machine doit rester allumee pendant les
# sessions de Malcom. L'URL est EPHEMERE : elle change a chaque relance du tunnel.
#
# Usage :   powershell -ExecutionPolicy Bypass -File start_pilote.ps1
# Arret :   ferme les fenetres/process "python" et "cloudflared" (Gestionnaire des taches),
#           ou :  Get-Process python,cloudflared | Stop-Process

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

$port        = 8770
$serverLog   = Join-Path $here "pilote_server.log"
$tunnelLog   = Join-Path $here "pilote_tunnel.log"
$cloudflared = "C:\Program Files (x86)\cloudflared\cloudflared.exe"

if (-not (Test-Path $cloudflared)) {
    # repli : cloudflared dans le PATH
    $cmd = Get-Command cloudflared -ErrorAction SilentlyContinue
    if ($cmd) { $cloudflared = $cmd.Source }
    else { Write-Host "cloudflared introuvable. Installe-le :  winget install --id Cloudflare.cloudflared --exact" -ForegroundColor Red; exit 1 }
}

$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $python) { Write-Host "python introuvable dans le PATH." -ForegroundColor Red; exit 1 }

Write-Host "1/3  Demarrage du serveur KinéCotation (port $port)..." -ForegroundColor Cyan
# purge d'un ancien log serveur pour ne pas confondre les runs
if (Test-Path $serverLog) { Remove-Item $serverLog -Force }
Start-Process -FilePath $python -ArgumentList "server.py" -WorkingDirectory $here `
    -RedirectStandardOutput $serverLog -RedirectStandardError (Join-Path $here "pilote_server_err.log") `
    -WindowStyle Hidden | Out-Null

# attend que le serveur reponde avant d'ouvrir le tunnel
$up = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Milliseconds 500
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:$port/healthz" -UseBasicParsing -TimeoutSec 2
        if ($r.StatusCode -eq 200) { $up = $true; break }
    } catch { }
}
if (-not $up) { Write-Host "  Le serveur ne repond pas sur $port (voir $serverLog)." -ForegroundColor Red; exit 1 }
Write-Host "     serveur OK." -ForegroundColor Green

Write-Host "2/3  Ouverture du tunnel Cloudflare..." -ForegroundColor Cyan
if (Test-Path $tunnelLog) { Remove-Item $tunnelLog -Force }
Start-Process -FilePath $cloudflared `
    -ArgumentList "tunnel","--url","http://127.0.0.1:$port","--logfile",$tunnelLog `
    -WindowStyle Hidden | Out-Null

Write-Host "3/3  Recherche de l'URL publique..." -ForegroundColor Cyan
$publicUrl = $null
for ($i = 0; $i -lt 40; $i++) {
    Start-Sleep -Milliseconds 500
    if (Test-Path $tunnelLog) {
        $m = Select-String -Path $tunnelLog -Pattern "https://[a-z0-9-]+\.trycloudflare\.com" -ErrorAction SilentlyContinue |
             Select-Object -First 1
        if ($m) { $publicUrl = $m.Matches[0].Value; break }
    }
}

Write-Host ""
if ($publicUrl) {
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host "  URL PUBLIQUE (a dicter a Malcom) :" -ForegroundColor Green
    Write-Host "     $publicUrl" -ForegroundColor White
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Identifiant : malcom.dorante   (mot de passe : voir PILOTE_ACCES_MALCOM.txt)"
    Write-Host "  L'URL change a CHAQUE relance de ce script. Laisse ce poste allume."
    Write-Host "  Logs : serveur -> $serverLog   tunnel -> $tunnelLog"
} else {
    Write-Host "URL Cloudflare pas encore visible. Regarde le log du tunnel :" -ForegroundColor Yellow
    Write-Host "   $tunnelLog"
}
