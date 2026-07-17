# -*- coding: utf-8 -*-
"""Authentification par formulaire + session (cookie signe).

Reutilise le modele EPROUVE du comparateur-courtier (meme famille de code) :
UN compte, pas de base de donnees, identifiants en variables d'environnement.

  APP_USER            identifiant du kine (son email)
  APP_PASSWORD_HASH   hash PBKDF2 du mot de passe (genere par set_password.py)
  SECRET_KEY          cle aleatoire longue qui signe le cookie de session

Le mot de passe n'est JAMAIS stocke en clair ni connu de l'app : seul son hash
est en config. set_password.py produit ce hash localement (le kine tape son mot
de passe lui-meme). Ni Enzo ni l'assistant ne voient le mot de passe.

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

APP_USER = os.environ.get("APP_USER", "")
APP_PASSWORD_HASH = os.environ.get("APP_PASSWORD_HASH", "")
SECRET_KEY = os.environ.get("SECRET_KEY", "")

COOKIE_NAME = "kine_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 30     # 30 jours — connexion « boite mail »
# Cookie Secure par defaut (HTTPS en prod). COOKIE_INSECURE=1 pour le dev local
# en http:// (sinon le navigateur refuse le cookie et la connexion boucle).
COOKIE_SECURE = os.environ.get("COOKIE_INSECURE") != "1"

_serializer = URLSafeTimedSerializer(SECRET_KEY or "dev-insecure-key", salt="kine-session")


def configured():
    """True si l'app peut authentifier : identifiant + hash + cle de signature."""
    return bool(APP_USER and APP_PASSWORD_HASH and SECRET_KEY)


def hash_password(password, iterations=200_000):
    """Produit `pbkdf2$<iters>$<salt_b64>$<hash_b64>` pour APP_PASSWORD_HASH.
    Appele hors ligne par set_password.py — le mot de passe n'entre jamais ici en prod."""
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
    """Verifie identifiant + mot de passe en temps ~constant."""
    if not configured():
        return False
    user_ok = hmac.compare_digest((user or "").strip(), APP_USER)
    pwd_ok = _verify_password(password or "", APP_PASSWORD_HASH)
    return user_ok and pwd_ok


def make_session_token(user):
    return _serializer.dumps({"u": user})


def read_session_token(token):
    """Renvoie l'identifiant si le cookie est valide et non expire, sinon None."""
    try:
        data = _serializer.loads(token, max_age=SESSION_MAX_AGE)
        return data.get("u")
    except (BadSignature, SignatureExpired, Exception):
        return None
