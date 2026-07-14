# -*- coding: utf-8 -*-
# update.ps1 — Mettre a jour le Comparateur Courtier (lancé par Mettre_a_jour.bat).
#   1) git pull (telecharge la derniere version depuis GitHub)
#   2) pip install -r requirements.txt (nouvelles dependances)
#   3) relance l'app si elle tournait

$ErrorActionPreference = "Stop"
chcp 65001 > $null

# retrouve le dossier d'installation : là où vit ce .bat (install/) + parent = workDir
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$workDir = Split-Path -Parent $scriptDir
$cloneDir = Split-Path -Parent $workDir
Set-Location $cloneDir

function W($m){ Write-Host "`n=== $m ===" -ForegroundColor Cyan }
function Ok($m){ Write-Host "  [OK] $m" -ForegroundColor Green }
function Err($m){ Write-Host "  [!] $m" -ForegroundColor Red }

W "Arret de l'application si elle tourne"
Get-Process python,uvicorn -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -like "*$workDir*" -or $_.Path -like "*ComparateurCourtier*"
} | ForEach-Object { Write-Host "  Arret de $($_.Id)"; Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue }
Ok "fait"

W "Telechargement de la mise a jour"
& git pull --quiet --ff-only
if ($LASTEXITCODE -eq 0) { Ok "code a jour" }
else {
    Err "git pull a echoue. Si tu as modifie des fichiers locaux, lance 'git stash' puis reessaie."
    Read-Host "`nAppuie sur Entree pour fermer"; exit 1
}

W "Mise a jour des dependances"
$py = Join-Path $workDir ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { Err "venv introuvable — relance Installer.bat"; Read-Host "`nEntree pour fermer"; exit 1 }
& $py -m pip install --quiet --upgrade pip
& $py -m pip install --quiet -r (Join-Path $workDir "requirements.txt")
if ($LASTEXITCODE -ne 0) { Err "echec dependances"; Read-Host "`nEntree pour fermer"; exit 1 }
Ok "dependances a jour"

W "Relance"
Start-Process -FilePath (Join-Path $workDir "demarrer.bat") -WorkingDirectory $workDir
Start-Sleep -Seconds 3
Start-Process "http://localhost:8000"
Ok "application relancee"
Write-Host "`nMise a jour terminee. Tu peux fermer cette fenetre.`n" -ForegroundColor Green
Start-Sleep -Seconds 3
