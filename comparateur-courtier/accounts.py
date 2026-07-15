# -*- coding: utf-8 -*-
"""Comptes « boîte mail » — registre chiffré, sans serveur.

Un SEUL installateur pour tous les clients : au login, l'app cherche le compte
dans un registre `accounts.json` où CHAQUE entrée (clés API + config du client)
est chiffrée avec une clé dérivée du mot de passe du client :

    PBKDF2-HMAC-SHA256 (1 000 000 itérations) -> AES-256-GCM

Le registre peut donc être publié (repo GitHub) : sans le bon mot de passe, une
entrée est indéchiffrable, et le tag GCM authentifie le déchiffrement (un mauvais
mot de passe échoue proprement -> c'est AUSSI la vérification du mot de passe).

Résolution du registre au login (le premier qui répond gagne) :
  1. le registre distant (repo GitHub, URL raw) — comptes à jour ;
  2. le cache local du dernier registre récupéré (usage hors-ligne) ;
  3. la copie embarquée dans l'exe au moment du build.

Ajout / modification d'un compte : `python make_account.py <nom>` puis commit+push.
"""
import os
import json
import base64
import hashlib
from pathlib import Path

BASE = Path(__file__).parent
DATA = Path(os.environ.get("DATA_DIR", BASE / "data"))

REGISTRY_URL = ("https://raw.githubusercontent.com/unexpectedvalu3-sys/"
                "ai-installator/main/comparateur-courtier/accounts.json")
KDF_ITERATIONS = 1_000_000

# Champs de config qu'une entrée déchiffrée applique à l'environnement.
CONFIG_KEYS = ("ANTHROPIC_API_KEY", "OPENROUTER_API_KEY", "LLM_MODEL", "COMPARE_MODEL")


def _b64e(b):
    return base64.b64encode(b).decode()


def _b64d(s):
    return base64.b64decode(s)


def derive_key(password, salt, iterations=KDF_ITERATIONS):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=32)


def encrypt_entry(password, config):
    """config (dict) -> entrée chiffrée à mettre dans accounts.json."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    import secrets
    salt = secrets.token_bytes(16)
    nonce = secrets.token_bytes(12)
    key = derive_key(password, salt)
    ct = AESGCM(key).encrypt(nonce, json.dumps(config, ensure_ascii=False).encode("utf-8"), None)
    return {"kdf": "pbkdf2-sha256", "iter": KDF_ITERATIONS,
            "salt": _b64e(salt), "nonce": _b64e(nonce), "data": _b64e(ct)}


def decrypt_entry(password, entry):
    """Renvoie la config (dict) si le mot de passe est bon, sinon None.
    Le tag AES-GCM garantit qu'un mauvais mot de passe ne peut pas 'réussir'."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    try:
        key = derive_key(password, _b64d(entry["salt"]), int(entry.get("iter", KDF_ITERATIONS)))
        pt = AESGCM(key).decrypt(_b64d(entry["nonce"]), _b64d(entry["data"]), None)
        return json.loads(pt.decode("utf-8"))
    except Exception:
        return None


def _load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return None


def _cache_path():
    return DATA / "accounts_cache.json"


def fetch_registry(timeout=6):
    """Registre : distant -> cache local -> copie embarquée. Jamais d'exception."""
    import urllib.request
    try:
        req = urllib.request.Request(REGISTRY_URL, headers={"User-Agent": "ComparateurCourtier"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            reg = json.loads(r.read().decode("utf-8"))
        if isinstance(reg, dict) and reg.get("accounts"):
            try:
                _cache_path().parent.mkdir(parents=True, exist_ok=True)
                _cache_path().write_text(json.dumps(reg, ensure_ascii=False), encoding="utf-8")
            except Exception:
                pass
            return reg
    except Exception:
        pass
    reg = _load_json(_cache_path())
    if isinstance(reg, dict) and reg.get("accounts"):
        return reg
    reg = _load_json(BASE / "accounts.json")   # copie embarquée au build
    if isinstance(reg, dict) and reg.get("accounts"):
        return reg
    return {"accounts": {}}


def login(user, password):
    """Tente le login « compte » : renvoie la config déchiffrée (dict) ou None.
    La casse de l'identifiant est ignorée ; les espaces autour aussi."""
    user = (user or "").strip().lower()
    if not user or not password:
        return None
    reg = fetch_registry()
    entry = (reg.get("accounts") or {}).get(user)
    if not entry:
        return None
    return decrypt_entry(password, entry)


def apply_config(config):
    """Applique la config du compte à l'environnement du process (les modules
    compare/llm lisent les clés via os.environ au moment de l'appel)."""
    for k in CONFIG_KEYS:
        v = config.get(k)
        if v:
            os.environ[k] = str(v)
