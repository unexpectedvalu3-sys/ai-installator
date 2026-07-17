#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cree le compte du kine — A LANCER EN LOCAL, une seule fois.

    python set_password.py

Demande l'identifiant et le mot de passe (saisi masque), puis ecrit webapp/.env :

  APP_USER=...            l'email du kine
  APP_PASSWORD_HASH=...   hash PBKDF2 (le mot de passe n'est jamais stocke en clair)
  SECRET_KEY=...          genere aleatoirement (signe les cookies de session)
  MISTRAL_API_KEY=        A COLLER par Enzo (console Mistral) — pour l'OCR
  COOKIE_INSECURE=1       autorise le cookie en http:// local

Le mot de passe n'est jamais affiche ni transmis : seul son hash part dans .env.
SECRET_KEY est une cle de signature generee ici (ce n'est ni un mot de passe ni
une cle fournisseur) ; MISTRAL_API_KEY reste vide -> Enzo la colle lui-meme.
"""
import getpass
import secrets
from pathlib import Path

import auth

ENV = Path(__file__).resolve().parent / ".env"


def _lire_env():
    vals = {}
    if ENV.exists():
        for ligne in ENV.read_text(encoding="utf-8").splitlines():
            if "=" in ligne and not ligne.lstrip().startswith("#"):
                k, _, v = ligne.partition("=")
                vals[k.strip()] = v
    return vals


def main():
    print("Creation du compte kine\n" + "-" * 24)
    user = input("Identifiant (email) : ").strip()
    while not user:
        user = input("Identifiant (email) : ").strip()

    pwd = getpass.getpass("Mot de passe        : ")
    pwd2 = getpass.getpass("Confirmer           : ")
    if pwd != pwd2:
        print("\nLes mots de passe ne correspondent pas. Recommence.")
        return
    if len(pwd) < 10:
        print("\nMot de passe trop court (10 caracteres minimum — c'est un outil de sante).")
        return

    existant = _lire_env()
    conf = {
        "APP_USER": user,
        "APP_PASSWORD_HASH": auth.hash_password(pwd),
        # conserve une SECRET_KEY existante (sinon toutes les sessions sautent),
        # sinon en genere une nouvelle.
        "SECRET_KEY": existant.get("SECRET_KEY") or secrets.token_urlsafe(48),
        # conserve la cle Mistral si Enzo l'a deja collee, sinon placeholder vide
        "MISTRAL_API_KEY": existant.get("MISTRAL_API_KEY", ""),
        "COOKIE_INSECURE": existant.get("COOKIE_INSECURE", "1"),
    }
    lignes = [
        "# Config KineCotation — genere par set_password.py — NE PAS COMMITER",
        f"APP_USER={conf['APP_USER']}",
        f"APP_PASSWORD_HASH={conf['APP_PASSWORD_HASH']}",
        f"SECRET_KEY={conf['SECRET_KEY']}",
        "# Cle Mistral (OCR) : la creer sur https://console.mistral.ai puis la coller ici",
        f"MISTRAL_API_KEY={conf['MISTRAL_API_KEY']}",
        f"COOKIE_INSECURE={conf['COOKIE_INSECURE']}",
        "",
    ]
    ENV.write_text("\n".join(lignes), encoding="utf-8")
    print(f"\nOK  compte cree pour {user}  ->  {ENV}")
    if not conf["MISTRAL_API_KEY"]:
        print("A FAIRE : coller MISTRAL_API_KEY dans .env pour activer l'OCR (sans, l'app marche sans OCR).")
    print("Lancer :  python server.py   puis  http://127.0.0.1:8770")


if __name__ == "__main__":
    main()
