# -*- coding: utf-8 -*-
"""Authentification par formulaire + session (cookie signé).

Modèle : UN déploiement par courtier -> un seul compte, pas de base de données.
Les identifiants vivent en variables d'environnement :

  APP_USER            identifiant du courtier (ex. son email)
  APP_PASSWORD_HASH   hash PBKDF2 du mot de passe (généré par set_password.py)
  SECRET_KEY          clé aléatoire longue qui signe le cookie de session

Le mot de passe n'est JAMAIS stocké en clair ni connu de l'app : seul son hash
est en config. `set_password.py` produit ce hash localement (le courtier tape
son mot de passe lui-même).

Fail-closed : si la config est incomplète, l'app ne sert rien (503).
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

COOKIE_NAME = "courtier_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 30     # 30 jours — connexion « boîte mail »
# Cookie Secure par défaut (HTTPS en prod). Mettre COOKIE_INSECURE=1 pour le dev
# local en http:// (sinon le navigateur refuse le cookie et la connexion boucle).
COOKIE_SECURE = os.environ.get("COOKIE_INSECURE") != "1"

_serializer = URLSafeTimedSerializer(SECRET_KEY or "dev-insecure-key", salt="courtier-session")


def configured():
    """True si l'app peut signer des sessions. Les identifiants eux-mêmes viennent
    soit du registre de comptes (accounts.py — mode « boîte mail »), soit du .env
    historique (APP_USER/APP_PASSWORD_HASH — installs d'avant la v1.2)."""
    return bool(SECRET_KEY)


def legacy_available():
    """True si un compte « historique » (.env posé par un ancien installateur)
    est présent — conservé pour la rétro-compatibilité des installs existantes."""
    return bool(APP_USER and APP_PASSWORD_HASH)


def hash_password(password, iterations=200_000):
    """Produit une chaîne `pbkdf2$<iters>$<salt_b64>$<hash_b64>` à mettre dans
    APP_PASSWORD_HASH. Utilisé hors ligne par set_password.py."""
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
    """Vérifie identifiant + mot de passe en temps constant (autant que possible)."""
    if not configured():
        return False
    user_ok = hmac.compare_digest((user or "").strip(), APP_USER)
    pwd_ok = _verify_password(password or "", APP_PASSWORD_HASH)
    return user_ok and pwd_ok


def make_session_token(user):
    return _serializer.dumps({"u": user})


def read_session_token(token):
    """Renvoie l'identifiant si le cookie est valide et non expiré, sinon None."""
    try:
        data = _serializer.loads(token, max_age=SESSION_MAX_AGE)
        return data.get("u")
    except (BadSignature, SignatureExpired, Exception):
        return None
