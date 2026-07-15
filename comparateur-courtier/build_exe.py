# -*- coding: utf-8 -*-
"""Build du Comparateur Courtier : .exe (PyInstaller) + setup.exe (Inno Setup).

Usage (depuis le venv du projet) :
    .venv\\Scripts\\python build_exe.py

Produit dans dist\\ :
  - ComparateurCourtier.exe   (~43 Mo) — l'app autonome (sans Python)
  - setup_ComparateurCourtier.exe (~44 Mo) — l'installateur pour les clients

Pour pousser une mise à jour aux clients :
  1. Modifier le code
  2. Relancer ce script
  3. Créer un GitHub Release (tag v1.x.x) avec ComparateurCourtier.exe en asset
  4. Les clients cliquent « Vérifier les mises à jour » dans le tray icon
"""
import subprocess, sys, shutil, os, secrets, base64, hashlib
from pathlib import Path

BASE = Path(__file__).parent
EXE_NAME = "ComparateurCourtier"
ISCC = r"C:\Users\admin\AppData\Local\Programs\Inno Setup 6\ISCC.exe"
APP_VERSION = "1.0.9"   # incrémenter à chaque build + release


def _gen_hash(password):
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return "pbkdf2$200000${}${}".format(
        base64.b64encode(salt).decode(), base64.b64encode(dk).decode())


def _build_embedded_config(client=None):
    """Génère embedded_config.py (compilé dans l'exe) à partir d'un profil client.

    - `python build_exe.py`         -> lit keys.txt (compte par défaut)
    - `python build_exe.py sophie`  -> lit clients/sophie.txt (un compte par client)

    Chaque profil contient les clés API + identifiants + mot de passe (haché ici).
    Au 1er lancement, run_local.py écrit un .env à partir de ces valeurs. Les
    fichiers de profil (keys.txt et clients/*.txt) sont gitignore : jamais commités."""
    keys_file = (BASE / "clients" / f"{client}.txt") if client else (BASE / "keys.txt")
    if not keys_file.exists():
        print(f"[!] Profil introuvable : {keys_file.relative_to(BASE)}. Crée-le avec :")
        print("    ANTHROPIC_API_KEY=sk-ant-...")
        print("    OPENROUTER_API_KEY=sk-or-...")
        print("    APP_USER=<identifiant>")
        print("    APP_PASSWORD=<mot de passe>")
        sys.exit(1)
    cfg = {}
    for line in keys_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip()
    required = ["ANTHROPIC_API_KEY", "OPENROUTER_API_KEY", "APP_USER", "APP_PASSWORD"]
    for k in required:
        if not cfg.get(k):
            print(f"[!] {k} manquant (ou vide) dans {keys_file.relative_to(BASE)}"); sys.exit(1)
    pwd_hash = _gen_hash(cfg["APP_PASSWORD"])
    lines = [
        f'APP_VERSION = {APP_VERSION!r}',
        f'ANTHROPIC_API_KEY = {cfg["ANTHROPIC_API_KEY"]!r}',
        f'OPENROUTER_API_KEY = {cfg["OPENROUTER_API_KEY"]!r}',
        f'LLM_MODEL = {cfg.get("LLM_MODEL", "claude-sonnet-4-6")!r}',
        f'COMPARE_MODEL = {cfg.get("COMPARE_MODEL", "z-ai/glm-5.2")!r}',
        f'APP_USER = {cfg["APP_USER"]!r}',
        f'APP_PASSWORD_HASH = {pwd_hash!r}',
        '# Lignes écrites dans .env au 1er lancement (run_local.py ajoute SECRET_KEY + COOKIE_INSECURE)',
        'LINES = [',
        f'    "ANTHROPIC_API_KEY=" + ANTHROPIC_API_KEY,',
        f'    "OPENROUTER_API_KEY=" + OPENROUTER_API_KEY,',
        f'    "LLM_MODEL=" + LLM_MODEL,',
        f'    "COMPARE_MODEL=" + COMPARE_MODEL,',
        f'    "APP_USER=" + APP_USER,',
        f'    "APP_PASSWORD_HASH=" + APP_PASSWORD_HASH,',
        ']',
    ]
    out = BASE / "embedded_config.py"
    out.write_text("# -*- coding: utf-8 -*-\n# AUTO-GÉNÉRÉ par build_exe.py — NE PAS COMMITTER.\n"
                   "# Clés + identifiants embarqués dans l'exe.\n\n"
                   + "\n".join(lines) + "\n", encoding="utf-8")
    print(f"[OK] embedded_config.py généré (identifiant: {cfg['APP_USER']})")
    return out


# --- 0) Génère embedded_config.py ---
# Profil client optionnel en argument : `python build_exe.py sophie` -> clients/sophie.txt
_client = sys.argv[1] if len(sys.argv) > 1 else None
print(f"=== 0/2 Génération embedded_config.py ({_client or 'keys.txt'}) ===")
_build_embedded_config(_client)

# --- 1) Build PyInstaller (.exe) ---
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
    "--collect-all", "pdfplumber",
    "--collect-all", "pdfminer.six",
    "--collect-all", "openpyxl",
    "--collect-all", "anthropic",
    "--collect-all", "pydantic",
    "--collect-all", "pydantic_core",   # embarque _pydantic_core.pyd (sinon crash au démarrage)
    "--hidden-import", "uvicorn.logging",
    "--hidden-import", "uvicorn.protocols.http.auto",
    "--hidden-import", "uvicorn.protocols.websockets.auto",
    "--hidden-import", "uvicorn.lifespan.on",
    "--hidden-import", "uvicorn.lifespan.off",
    "--hidden-import", "pystray._win32",
    "--hidden-import", "PIL._tkinter_finder",
    "run_local.py",
]
print("=== 1/2 Build PyInstaller (.exe) ===")
r = subprocess.run(cmd, cwd=str(BASE))
if r.returncode != 0:
    print("[!] Build exe échoué."); sys.exit(1)
exe = BASE / "dist" / f"{EXE_NAME}.exe"
print(f"\n[OK] {exe.name} : {exe.stat().st_size / 1024 / 1024:.1f} Mo")

# --- 2) Build Inno Setup (setup.exe) ---
# Génère l'icône .ico depuis mascotte.png (si pas déjà fait ou obsolète)
ico = BASE / "static" / "mascotte.ico"
png = BASE / "static" / "mascotte.png"
if not ico.exists() or ico.stat().st_mtime < png.stat().st_mtime:
    from PIL import Image
    Image.open(png).save(str(ico), format="ICO",
                         sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])
    print("[OK] mascotte.ico regénéré")

iss = BASE / "ComparateurCourtier.iss"
print(f"\n=== 2/2 Build Inno Setup (setup.exe) ===")
r = subprocess.run([ISCC, str(iss)], cwd=str(BASE))
if r.returncode != 0:
    print("[!] Build setup.exe échoué."); sys.exit(1)
setup = BASE / "dist" / "setup_ComparateurCourtier.exe"
print(f"\n[OK] {setup.name} : {setup.stat().st_size / 1024 / 1024:.1f} Mo")
print(f"\n=== Terminé ===")
print(f"  App         : {exe}")
print(f"  Installateur: {setup}")
print(f"\nPour mettre à jour les clients :")
print(f"  1. Créer un GitHub Release (tag v1.x.x) avec ComparateurCourtier.exe en asset")
print(f"  2. Les clients cliquent « Vérifier les mises à jour » dans le tray icon")
