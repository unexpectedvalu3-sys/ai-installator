# -*- coding: utf-8 -*-
"""Registre MULTI-COMPTES pour l'app hebergee.

Difference avec le comparateur (exe) : ici la cle Mistral vit COTE SERVEUR et est
partagee -> aucune cle a livrer par compte. Une entree = juste {user, hash}.
Et on ne PUBLIE PAS les hash (outil de sante) : le registre n'est jamais commite.

Source du registre (le premier qui repond gagne) :
  1. env KINE_ACCOUNTS  (JSON) — pour l'hebergement (colle dans le dashboard de l'hote) ;
  2. fichier local accounts.json (gitignore) — pour le dev / un serveur avec disque.

Format : {"comptes": [{"user": "malcom.dorante", "password_hash": "pbkdf2$..."}]}

Ajouter/modifier un compte : `python make_account.py`.
"""
import json
import os
from pathlib import Path

import auth

ICI = Path(__file__).resolve().parent
ACCOUNTS_FILE = Path(os.environ.get("KINE_ACCOUNTS_FILE", ICI / "accounts.json"))


def _normaliser(reg):
    """Accepte {"comptes":[...]} ou une liste brute ; rend une liste de comptes."""
    if isinstance(reg, dict):
        reg = reg.get("comptes") or reg.get("accounts") or []
    return [c for c in reg if isinstance(c, dict) and c.get("user") and c.get("password_hash")]


def charger():
    """Registre : env KINE_ACCOUNTS -> fichier local. Jamais d'exception."""
    brut = os.environ.get("KINE_ACCOUNTS", "").strip()
    if brut:
        try:
            return _normaliser(json.loads(brut))
        except Exception:
            pass
    try:
        return _normaliser(json.loads(ACCOUNTS_FILE.read_text(encoding="utf-8")))
    except Exception:
        return []


def has_any():
    return bool(charger())


def _trouver(comptes, user):
    cible = (user or "").strip().lower()
    for c in comptes:
        if c["user"].strip().lower() == cible:
            return c
    return None


def check(user, password):
    """Vrai si (user, password) correspond a un compte du registre. Temps ~constant :
    on verifie toujours un hash, meme si l'utilisateur n'existe pas."""
    comptes = charger()
    c = _trouver(comptes, user)
    stored = c["password_hash"] if c else "pbkdf2$200000$AAAA$AAAA"  # leurre anti-timing
    ok = auth._verify_password(password or "", stored)
    return bool(c) and ok


def upsert(path, user, password_hash):
    """Ajoute ou remplace un compte dans le fichier registre (usage make_account.py)."""
    try:
        comptes = _normaliser(json.loads(Path(path).read_text(encoding="utf-8")))
    except Exception:
        comptes = []
    comptes = [c for c in comptes if c["user"].strip().lower() != user.strip().lower()]
    comptes.append({"user": user, "password_hash": password_hash})
    comptes.sort(key=lambda c: c["user"].lower())
    Path(path).write_text(json.dumps({"comptes": comptes}, ensure_ascii=False, indent=2),
                          encoding="utf-8")
    return comptes
