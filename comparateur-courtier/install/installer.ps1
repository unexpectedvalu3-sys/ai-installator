# -*- coding: utf-8 -*-
# installer.ps1 — Installation du Comparateur Courtier pour les clients (Windows).
# Lancé par Installer.bat (double-clic). Étapes :
#   1) vérifie Python + Git
#   2) clone le dépôt (ou réutilise si déjà cloné)
#   3) crée le venv + installe les dépendances
#   4) demande les clés API + crée le compte courtier (mot de passe masqué)
#   5) génère le .env (avec hash du mot de passe — jamais stocké en clair)
#   6) crée un raccourci Bureau + lance l'app
#
# Re-lancé sur une install existante : met à jour (git pull + deps) sans
# réinitialiser le .env (les clés/compte sont conservés).

$ErrorActionPreference = "Stop"
$repo = "https://github.com/unexpectedvalu3-sys/ai-installator.git"
$subdir = "comparateur-courtier"
$installRoot = Join-Path $env:LOCALAPPDATA "ComparateurCourtier"
$cloneDir = Join-Path $installRoot "app"
$workDir = Join-Path $cloneDir $subdir

function Write-Step($m) { Write-Host "`n=== $m ===" -ForegroundColor Cyan }
function Write-Ok($m)   { Write-Host "  [OK] $m" -ForegroundColor Green }
function Write-Err($m)  { Write-Host "  [!] $m" -ForegroundColor Red }
function Read-Masked($prompt) {
    $val = ""
    Write-Host -NoNewline "$prompt : "
    while ($true) {
        $k = [System.Console]::ReadKey($true)
        if ($k.KeyChar -eq "`r" -or $k.KeyChar -eq "`n") { Write-Host ""; break }
        if ($k.Key -eq "Backspace" -and $val.Length -gt 0) { $val = $val.Substring(0,$val.Length-1); Write-Host -NoNewline "`b `b" }
        elseif ($k.Key -ne "Backspace" -and $k.KeyChar) { $val += $k.KeyChar; Write-Host -NoNewline "*" }
    }
    return $val
}

Write-Host "Installation du Comparateur Courtier" -ForegroundColor White

# --- 1) prérequis ---
Write-Step "Verification des prerequis"
$pyExe = $null
foreach ($cand in @("py","python","python3")) {
    try { $v = & $cand --version 2>$null; if ($LASTEXITCODE -eq 0 -and $v -match "Python") { $pyExe = $cand; break } } catch {}
}
if (-not $pyExe) {
    Write-Err "Python est introuvable. Installe Python 3.10+ depuis https://www.python.org/downloads/ (coche 'Add Python to PATH'), puis relance cet installeur."
    Read-Host "`nAppuie sur Entree pour fermer"; exit 1
}
Write-Ok "Python trouve : $(& $pyExe --version)"
try { $g = & git --version 2>$null; if ($LASTEXITCODE -eq 0) { Write-Ok "Git trouve : $g" } else { throw "no git" } }
catch {
    Write-Err "Git est introuvable. Installe Git depuis https://git-scm.com/download/win puis relance."
    Read-Host "`nAppuie sur Entree pour fermer"; exit 1
}

# --- 2) clone (ou pull si déjà présent) ---
Write-Step "Recuperation du logiciel"
if (Test-Path (Join-Path $workDir "app.py")) {
    Write-Host "  Installation existante detectee — mise a jour..."
    Push-Location $cloneDir
    & git pull --quiet --ff-only
    if ($LASTEXITCODE -ne 0) { Write-Err "git pull a echoue (on continue avec la version locale)" }
    Pop-Location
} else {
    New-Item -ItemType Directory -Force -Path $installRoot | Out-Null
    Write-Host "  Clonage depuis GitHub..."
    & git clone --quiet $repo $cloneDir
    if ($LASTEXITCODE -ne 0) { Write-Err "Clonage impossible. Verifie ta connexion Internet."; Read-Host "`nAppuie sur Entree pour fermer"; exit 1 }
}
Set-Location $workDir
Write-Ok "Code present dans $workDir"

# --- 3) venv + dépendances ---
Write-Step "Environnement Python"
$venv = Join-Path $workDir ".venv"
if (-not (Test-Path (Join-Path $venv "Scripts\python.exe"))) {
    Write-Host "  Creation de l'environnement virtuel..."
    & $pyExe -m venv $venv
    if ($LASTEXITCODE -ne 0) { Write-Err "echec venv"; Read-Host "`nAppuie sur Entree pour fermer"; exit 1 }
}
$py = Join-Path $venv "Scripts\python.exe"
Write-Host "  Installation des dependances (peut prendre 1-2 min)..."
& $py -m pip install --quiet --upgrade pip
& $py -m pip install --quiet -r requirements.txt
if ($LASTEXITCODE -ne 0) { Write-Err "echec installation dependances"; Read-Host "`nAppuie sur Entree pour fermer"; exit 1 }
Write-Ok "Dependances installees"

# --- 4) clés + compte (seulement si .env absent) ---
$envFile = Join-Path $workDir ".env"
if (Test-Path $envFile) {
    Write-Step "Configuration existante conservee"
    Write-Ok ".env deja present (cles et compte gardes). Supprime-le pour reconfigurer."
} else {
    Write-Step "Configuration — tes cles API"
    Write-Host "  Le comparateur a besoin de 2 cles (fournies avec ton dossier d'installation) :"
    $anth = Read-Host "  Colle ta cle ANTHROPIC_API_KEY"
    $or   = Read-Host "  Colle ta cle OPENROUTER_API_KEY"
    while (-not $anth.Trim()) { $anth = Read-Host "  ANTHROPIC_API_KEY (obligatoire)" }
    while (-not $or.Trim())   { $or   = Read-Host "  OPENROUTER_API_KEY (obligatoire)" }

    Write-Step "Creation de ton compte courtier"
    $user = Read-Host "  Identifiant (ton email)"
    while (-not $user.Trim()) { $user = Read-Host "  Identifiant (obligatoire)" }
    $pwd = Read-Masked "  Mot de passe (min 8 caracteres)"
    while ($pwd.Length -lt 8) { Write-Host "  Trop court."; $pwd = Read-Masked "  Mot de passe" }
    $pwd2 = Read-Masked "  Confirmation"
    while ($pwd -ne $pwd2) { Write-Host "  Les deux ne correspondent pas."; $pwd = Read-Masked "  Mot de passe"; $pwd2 = Read-Masked "  Confirmation" }

    # génère le hash via auth.hash_password (offline, jamais stocké en clair)
    $script = @"
import sys
sys.path.insert(0, r'$workDir')
import auth, secrets
print('HASH=' + auth.hash_password(r'$pwd'))
print('SECRET=' + secrets.token_urlsafe(48))
"@
    $tmp = Join-Path $env:TEMP "cc_gen_$PID.py"
    Set-Content -Path $tmp -Value $script -Encoding UTF8
    $out = & $py $tmp 2>&1
    Remove-Item $tmp -ErrorAction SilentlyContinue
    $hash = ($out | Where-Object { $_ -match "^HASH=" }).Split("=",2)[1]
    $secret = ($out | Where-Object { $_ -match "^SECRET=" }).Split("=",2)[1]
    if (-not $hash -or -not $secret) { Write-Err "echec generation auth"; Read-Host "`nAppuie sur Entree pour fermer"; exit 1 }

    $envContent = @"
ANTHROPIC_API_KEY=$($anth.Trim())
OPENROUTER_API_KEY=$($or.Trim())
LLM_MODEL=claude-sonnet-4-6
COMPARE_MODEL=z-ai/glm-5.2
APP_USER=$($user.Trim())
APP_PASSWORD_HASH=$hash
SECRET_KEY=$secret
COOKIE_INSECURE=1
"@
    Set-Content -Path $envFile -Value $envContent -Encoding UTF8
    Write-Ok "Compte cree : $($user.Trim())"
    Write-Host "  (Le mot de passe n'est PAS stocke en clair, seulement son hash.)" -ForegroundColor DarkGray
}

# --- 6) raccourcis Bureau + lanceur ---
Write-Step "Raccourcis"
$ws = New-Object -ComObject WScript.Shell
$bureau = [Environment]::GetFolderPath("Desktop")
$lnk = Join-Path $bureau "Comparateur Courtier.lnk"
$s = $ws.CreateShortcut($lnk)
$s.TargetPath = Join-Path $workDir "demarrer.bat"
$s.WorkingDirectory = $workDir
$s.IconLocation = Join-Path $workDir "install\app.ico"
if (-not (Test-Path $s.IconLocation)) { $s.IconLocation = "" }
$s.Description = "Lancer le Comparateur Courtier"
$s.Save()
Write-Ok "Raccourci cree sur le Bureau"

# raccourci "Mettre a jour"
$lnkUp = Join-Path $bureau "Comparateur — Mettre a jour.lnk"
$up = $ws.CreateShortcut($lnkUp)
$up.TargetPath = Join-Path $workDir "install\Mettre_a_jour.bat"
$up.WorkingDirectory = $workDir
$up.Description = "Telecharger la derniere mise a jour du Comparateur"
$up.Save()
Write-Ok "Raccourci 'Mettre a jour' cree sur le Bureau"

Write-Step "Termine !"
Write-Host "  L'application va demarrer. Un navigateur s'ouvrira sur http://localhost:8000"
Write-Host "  Identifiant : $($user.Trim())  (mot de passe que tu viens de choisir)" -ForegroundColor Yellow
Write-Host "  La fenetre noire doit rester ouverte pendant l'utilisation.`n" -ForegroundColor DarkGray

Start-Process -FilePath (Join-Path $workDir "demarrer.bat") -WorkingDirectory $workDir
Start-Sleep -Seconds 4
Start-Process "http://localhost:8000"
Write-Host "`nAppuie sur Entree pour fermer cette fenetre d'installation."
Read-Host
