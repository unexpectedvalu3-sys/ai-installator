# -*- coding: utf-8 -*-
"""Ajoute / met à jour un COMPTE dans le registre chiffré accounts.json.

    python make_account.py            -> lit keys.txt           (compte par défaut)
    python make_account.py sophie     -> lit clients/sophie.txt

Le profil doit contenir : APP_USER, APP_PASSWORD, ANTHROPIC_API_KEY,
OPENROUTER_API_KEY (+ LLM_MODEL / COMPARE_MODEL optionnels).

Après coup : commit + push accounts.json -> le compte marche IMMÉDIATEMENT sur
toutes les installs (le login récupère le registre en ligne). Plus besoin de
générer un installateur par client : un seul setup générique pour tout le monde.

Mot de passe : privilégier un mot de passe FORT (le registre est public ; c'est
lui qui protège les clés). Le script avertit s'il est faible.
"""
import sys
import json
from pathlib import Path

import accounts

BASE = Path(__file__).parent


def read_profile(client):
    p = (BASE / "clients" / f"{client}.txt") if client else (BASE / "keys.txt")
    if not p.exists():
        print(f"[!] Profil introuvable : {p.relative_to(BASE)}")
        sys.exit(1)
    cfg = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip()
    for k in ("APP_USER", "APP_PASSWORD", "ANTHROPIC_API_KEY", "OPENROUTER_API_KEY"):
        if not cfg.get(k):
            print(f"[!] {k} manquant (ou vide) dans {p.relative_to(BASE)}")
            sys.exit(1)
    return cfg


def main():
    client = sys.argv[1] if len(sys.argv) > 1 else None
    cfg = read_profile(client)
    user = cfg["APP_USER"].strip().lower()
    password = cfg["APP_PASSWORD"]
    if len(password) < 12 or password.lower() == password:
        print(f"[!] AVERTISSEMENT : mot de passe faible pour « {user} ». Le registre est public :")
        print("    un mot de passe long avec majuscules/chiffres protège bien mieux les clés API.")

    config = {k: cfg[k] for k in ("ANTHROPIC_API_KEY", "OPENROUTER_API_KEY") }
    config["LLM_MODEL"] = cfg.get("LLM_MODEL", "claude-sonnet-4-6")
    config["COMPARE_MODEL"] = cfg.get("COMPARE_MODEL", "z-ai/glm-5.2")
    config["display_name"] = cfg.get("DISPLAY_NAME", user)

    reg_path = BASE / "accounts.json"
    reg = {"accounts": {}}
    if reg_path.exists():
        try:
            reg = json.loads(reg_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    reg.setdefault("accounts", {})[user] = accounts.encrypt_entry(password, config)
    reg_path.write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"[OK] Compte « {user} » écrit dans accounts.json ({len(reg['accounts'])} compte(s)).")
    print("     Vérification déchiffrement :", "OK" if accounts.decrypt_entry(password, reg["accounts"][user]) else "ÉCHEC")
    print("     -> commit + push accounts.json pour activer le compte partout.")


if __name__ == "__main__":
    main()
