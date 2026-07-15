# -*- coding: utf-8 -*-
"""Build de l'exe GÉNÉRIQUE du Comparateur Courtier (PyInstaller).

L'exe ne contient AUCUN secret : la config (clés API + identifiants) est déposée
par l'installateur dans un .env à côté de l'exe. Un seul exe sert tous les clients.

Workflow :
    python build_exe.py            -> dist/ComparateurCourtier.exe  (exe générique, ~2 min)
    python make_client.py sophie   -> dist/setup_sophie.exe         (installateur client, ~10 s)

Pour publier une mise à jour :
    1. Bumper version.py
    2. python build_exe.py
    3. gh release create vX.Y.Z dist/ComparateurCourtier.exe --title ... --notes ...
       (l'exe étant générique, l'asset public ne contient aucun secret)
"""
import subprocess, sys, shutil
from pathlib import Path

from version import APP_VERSION

BASE = Path(__file__).parent
EXE_NAME = "ComparateurCourtier"


def _make_ico():
    """Génère static/mascotte.ico depuis mascotte.png (pour l'icône de l'installateur)."""
    ico = BASE / "static" / "mascotte.ico"
    png = BASE / "static" / "mascotte.png"
    if png.exists() and (not ico.exists() or ico.stat().st_mtime < png.stat().st_mtime):
        from PIL import Image
        Image.open(png).save(str(ico), format="ICO",
                             sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
        print("[OK] mascotte.ico régénéré")


print(f"=== Build exe générique — version {APP_VERSION} ===")
for d in ("build", "dist"):
    p = BASE / d
    if p.exists():
        shutil.rmtree(p)

cmd = [
    sys.executable, "-m", "PyInstaller",
    "--onefile", "--windowed",
    "--name", EXE_NAME,
    "--icon", str(BASE / "static" / "mascotte.png"),
    "--add-data", f"static{';'}static",
    "--add-data", f"accounts.json{';'}.",   # copie embarquée du registre de comptes (fallback hors-ligne)
    "--hidden-import", "version",
    "--collect-all", "pdfplumber",
    "--collect-all", "pdfminer.six",
    "--collect-all", "openpyxl",
    "--collect-all", "anthropic",
    "--collect-all", "pydantic",
    "--collect-all", "pydantic_core",   # embarque _pydantic_core.pyd (sinon crash au démarrage)
    "--collect-all", "PIL",             # embarque _imaging.pyd
    "--hidden-import", "uvicorn.logging",
    "--hidden-import", "uvicorn.protocols.http.auto",
    "--hidden-import", "uvicorn.protocols.websockets.auto",
    "--hidden-import", "uvicorn.lifespan.on",
    "--hidden-import", "uvicorn.lifespan.off",
    "--hidden-import", "pystray._win32",
    "--hidden-import", "PIL._tkinter_finder",
    "run_local.py",
]
r = subprocess.run(cmd, cwd=str(BASE))
if r.returncode != 0:
    print("[!] Build exe échoué."); sys.exit(1)

exe = BASE / "dist" / f"{EXE_NAME}.exe"
print(f"\n[OK] {exe.name} : {exe.stat().st_size / 1024 / 1024:.1f} Mo (générique, sans secret)")

_make_ico()

# --- Installateur UNIVERSEL (v1.2 : connexion par compte, plus de .env client) ---
ISCC = r"C:\Users\admin\AppData\Local\Programs\Inno Setup 6\ISCC.exe"
print("\n=== Installateur universel (setup_ComparateurCourtier.exe) ===")
r = subprocess.run([ISCC, f"/DAppVersion={APP_VERSION}", str(BASE / "ComparateurCourtier.iss")], cwd=str(BASE))
if r.returncode != 0:
    print("[!] Build installateur échoué."); sys.exit(1)
setup = BASE / "dist" / "setup_ComparateurCourtier.exe"
print(f"[OK] {setup.name} : {setup.stat().st_size / 1024 / 1024:.1f} Mo")

print("\n=== Terminé ===")
print(f"  Exe générique         : {exe}")
print(f"  Installateur universel: {setup}  (le MÊME pour tous les clients)")
print("  Ajouter un compte     :  python make_account.py <nom>  puis commit+push accounts.json")
