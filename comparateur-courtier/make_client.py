# -*- coding: utf-8 -*-
"""Génère l'installateur d'UN client — rapide, SANS rebuild PyInstaller.

    python make_client.py            -> lit keys.txt           -> dist/setup_courtier.exe
    python make_client.py sophie     -> lit clients/sophie.txt -> dist/setup_sophie.exe

Prérequis : l'exe générique doit exister (python build_exe.py). Cet exe, sans aucun
secret, est empaqueté avec un petit .env client (clés API + identifiants) que
l'installateur dépose à côté de l'exe. Ajouter/mettre à jour un client = ~10 s.
"""
import subprocess, sys, secrets, base64, hashlib
from pathlib import Path

from version import APP_VERSION

BASE = Path(__file__).parent
ISCC = r"C:\Users\admin\AppData\Local\Programs\Inno Setup 6\ISCC.exe"


def _hash_password(password, iterations=200_000):
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return "pbkdf2$200000${}${}".format(
        base64.b64encode(salt).decode(), base64.b64encode(dk).decode())


def _read_profile(client):
    keys_file = (BASE / "clients" / f"{client}.txt") if client else (BASE / "keys.txt")
    if not keys_file.exists():
        print(f"[!] Profil introuvable : {keys_file.relative_to(BASE)}")
        sys.exit(1)
    cfg = {}
    for line in keys_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip()
    for k in ("ANTHROPIC_API_KEY", "OPENROUTER_API_KEY", "APP_USER", "APP_PASSWORD"):
        if not cfg.get(k):
            print(f"[!] {k} manquant (ou vide) dans {keys_file.relative_to(BASE)}")
            sys.exit(1)
    return cfg


def main():
    client = sys.argv[1] if len(sys.argv) > 1 else None
    exe = BASE / "dist" / "ComparateurCourtier.exe"
    if not exe.exists():
        print("[!] dist/ComparateurCourtier.exe absent. Lance d'abord : python build_exe.py")
        sys.exit(1)

    cfg = _read_profile(client)
    name = client or (cfg["APP_USER"] or "courtier")

    # .env client déposé à côté de l'exe par l'installateur. Le SECRET_KEY n'est PAS
    # mis ici : run_local.py l'ajoute au 1er lancement (unique par install).
    env_lines = [
        f"ANTHROPIC_API_KEY={cfg['ANTHROPIC_API_KEY']}",
        f"OPENROUTER_API_KEY={cfg['OPENROUTER_API_KEY']}",
        f"LLM_MODEL={cfg.get('LLM_MODEL', 'claude-sonnet-4-6')}",
        f"COMPARE_MODEL={cfg.get('COMPARE_MODEL', 'z-ai/glm-5.2')}",
        f"APP_USER={cfg['APP_USER']}",
        f"APP_PASSWORD_HASH={_hash_password(cfg['APP_PASSWORD'])}",
        "COOKIE_INSECURE=1",
    ]
    env_path = BASE / "dist" / "_client.env"
    env_path.write_text("\n".join(env_lines) + "\n", encoding="utf-8")

    print(f"=== Installateur client « {name} » (v{APP_VERSION}) ===")
    r = subprocess.run([
        ISCC,
        f"/DClientName={name}",
        f"/DAppVersion={APP_VERSION}",
        f"/DClientEnv={env_path}",
        str(BASE / "ComparateurCourtier.iss"),
    ], cwd=str(BASE))
    try:
        env_path.unlink()   # ne pas laisser traîner le .env avec les secrets
    except Exception:
        pass
    if r.returncode != 0:
        print("[!] Build installateur échoué."); sys.exit(1)

    setup = BASE / "dist" / f"setup_{name}.exe"
    print(f"\n[OK] {setup.name} : {setup.stat().st_size / 1024 / 1024:.1f} Mo")
    print(f"     Identifiant : {cfg['APP_USER']}  (mot de passe : celui du profil)")


if __name__ == "__main__":
    main()
