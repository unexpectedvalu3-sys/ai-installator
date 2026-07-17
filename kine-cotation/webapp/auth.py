# -*- coding: utf-8 -*-
"""Authentification par formulaire + session (cookie signe).

MULTI-COMPTES : les identifiants vivent dans un registre (accounts.py) — plusieurs
kines, chacun son mot de passe. Ce module ne garde que la crypto commune (hash,
verif, jeton de session) et la cle de signature :

  SECRET_KEY          cle aleatoire longue qui signe le cookie de session

Le mot de passe n'est JAMAIS stocke en clair : seul son hash PBKDF2 est au
registre. make_account.py produit ce hash localement (le kine tape son mot de
passe lui-meme). Ni Enzo ni l'assistant ne voient le mot de passe.

POURQUOI UN LOGIN SUR UN OUTIL LOCAL-FIRST ?
La cotation, la DAP, le dossier de preuve et le profil sont 100% locaux (chez le
kine) : ils n'ont AUCUN secret a proteger, c'est de la logique NGAP publique. Le
login gagne sa place sur deux choses seulement :
  1. controle d'acces (ce sera un produit ; on veut savoir qui l'utilise) ;
  2. l'OCR : la cle Mistral vit cote serveur, jamais dans le navigateur ni dans
     un fichier que le kine pourrait fuiter. Le login garde l'endpoint /api/ocr.

Fail-closed : si la config est incomplete, l'app ne sert rien (503).
"""
import os
import hmac
import base64
import hashlib
import secrets

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

SECRET_KEY = os.environ.get("SECRET_KEY", "")

COOKIE_NAME = "kine_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 30     # 30 jours — connexion « boite mail »
# Cookie Secure par defaut (HTTPS en prod). COOKIE_INSECURE=1 pour le dev local
# en http:// (sinon le navigateur refuse le cookie et la connexion boucle).
COOKIE_SECURE = os.environ.get("COOKIE_INSECURE") != "1"

_serializer = URLSafeTimedSerializer(SECRET_KEY or "dev-insecure-key", salt="kine-session")


def configured():
    """True si l'app peut authentifier : une cle de signature ET au moins un compte
    dans le registre (accounts.py). Sinon fail-closed (503), l'app ne sert rien."""
    import accounts
    return bool(SECRET_KEY and accounts.has_any())


def hash_password(password, iterations=200_000):
    """Produit `pbkdf2$<iters>$<salt_b64>$<hash_b64>` a mettre au registre.
    Appele hors ligne par make_account.py — le mot de passe n'entre jamais ici en prod."""
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return "pbkdf2${}${}${}".format(
        iterations, base64.b64encode(salt).decode(), base64.b64encode(dk).decode())


def _verify_password(password, stored):
    try:
        algo, iters, salt_b64, hash_b64 = stored.split("$")
        if algo != "pbkdf2":
            return False
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iters))
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False


def check_credentials(user, password):
    """Verifie (identifiant, mot de passe) contre le registre MULTI-COMPTES."""
    if not SECRET_KEY:
        return False
    import accounts
    return accounts.check(user, password)


def make_session_token(user):
    return _serializer.dumps({"u": user})


def read_session_token(token):
    """Renvoie l'identifiant si le cookie est valide et non expire, sinon None."""
    try:
        data = _serializer.loads(token, max_age=SESSION_MAX_AGE)
        return data.get("u")
    except (BadSignature, SignatureExpired, Exception):
        return None
