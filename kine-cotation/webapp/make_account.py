#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ajoute (ou remplace) un compte kine — A LANCER EN LOCAL.

    python make_account.py

Relance-le autant de fois que de kines : le registre est MULTI-COMPTES.
Demande l'identifiant et le mot de passe (saisi masque), ecrit webapp/accounts.json
et s'assure qu'une SECRET_KEY existe dans webapp/.env.

Le mot de passe n'est jamais affiche ni stocke en clair : seul son hash PBKDF2 va
au registre. accounts.json est gitignore (les hash ne sont PAS publies).

Pour un HEBERGEMENT : le script imprime KINE_ACCOUNTS et SECRET_KEY a coller dans
le dashboard de l'hote (rien ne vit dans un fichier commite).
"""
import getpass
import json
import secrets
from pathlib import Path

import accounts
import auth

ICI = Path(__file__).resolve().parent
ENV = ICI / ".env"
REG = ICI / "accounts.json"


def _secret_key():
    """Reutilise la SECRET_KEY de .env si presente (sinon les sessions sautent),
    sinon en cree une et l'ecrit dans .env."""
    if ENV.exists():
        for ligne in ENV.read_text(encoding="utf-8").splitlines():
            if ligne.startswith("SECRET_KEY=") and ligne[11:].strip():
                return ligne[11:].strip()
    key = secrets.token_urlsafe(48)
    lignes = []
    if ENV.exists():
        lignes = [l for l in ENV.read_text(encoding="utf-8").splitlines()
                  if not l.startswith("SECRET_KEY=")]
    else:
        lignes = ["# Config KineCotation — NE PAS COMMITER", "COOKIE_INSECURE=1"]
    lignes.append(f"SECRET_KEY={key}")
    ENV.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    return key


def main():
    print("Ajout d'un compte kine (multi-comptes)\n" + "-" * 38)
    user = input("Identifiant (ex. malcom.dorante) : ").strip()
    while not user:
        user = input("Identifiant (ex. malcom.dorante) : ").strip()

    pwd = getpass.getpass("Mot de passe        : ")
    pwd2 = getpass.getpass("Confirmer           : ")
    if pwd != pwd2:
        print("\nLes mots de passe ne correspondent pas. Recommence.")
        return
    if len(pwd) < 10:
        print("\nMot de passe trop court (10 caracteres minimum — outil de sante).")
        return

    comptes = accounts.upsert(REG, user, auth.hash_password(pwd))
    key = _secret_key()

    print(f"\nOK  compte '{user}' enregistre  ->  {REG}")
    print(f"    {len(comptes)} compte(s) au registre : {', '.join(c['user'] for c in comptes)}")
    print("\n--- POUR UN HEBERGEMENT : colle ces variables dans le dashboard de l'hote ---")
    print("KINE_ACCOUNTS=" + json.dumps({"comptes": comptes}, ensure_ascii=False))
    print(f"SECRET_KEY={key}")
    print("MISTRAL_API_KEY=<coller la cle Mistral>   (OCR ; sans elle l'app marche sans OCR)")
    print("HOST=0.0.0.0")
    print("# NE PAS mettre COOKIE_INSECURE en prod (HTTPS -> cookie Secure).")
    print("---------------------------------------------------------------------------")
    print("\nEn local : python server.py  puis  http://127.0.0.1:8770")


if __name__ == "__main__":
    main()
