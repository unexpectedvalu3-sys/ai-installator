# -*- coding: utf-8 -*-
"""Génère la config d'authentification du courtier — À LANCER EN LOCAL.

    python set_password.py

Le script demande l'identifiant et le mot de passe (saisi masqué), puis affiche
les trois variables d'environnement à coller dans la config du déploiement :

  APP_USER, APP_PASSWORD_HASH, SECRET_KEY

Le mot de passe n'est jamais affiché ni stocké : seul son hash PBKDF2 est produit.
"""
import getpass
import secrets

import auth


def main():
    print("Configuration du compte courtier\n" + "-" * 34)
    user = input("Identifiant (email) : ").strip()
    while not user:
        user = input("Identifiant (email) : ").strip()

    pwd = getpass.getpass("Mot de passe        : ")
    pwd2 = getpass.getpass("Confirmer           : ")
    if pwd != pwd2:
        print("\nLes mots de passe ne correspondent pas. Recommence.")
        return
    if len(pwd) < 8:
        print("\nMot de passe trop court (8 caractères minimum).")
        return

    hashed = auth.hash_password(pwd)
    secret = secrets.token_urlsafe(48)

    print("\nÀ mettre dans la config du déploiement (variables d'environnement) :\n")
    print(f"APP_USER={user}")
    print(f"APP_PASSWORD_HASH={hashed}")
    print(f"SECRET_KEY={secret}")
    print("\nGarde SECRET_KEY secrète et stable : la changer déconnecte les sessions en cours.")


if __name__ == "__main__":
    main()
