# -*- coding: utf-8 -*-
"""
Simule le nouveau prompt email sur 3 secteurs différents
pour valider avant mise en prod.
"""
import sqlite3, json, base64, os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import hashlib, requests

DB = os.path.expanduser("~/.n8n/database.sqlite")
ENCRYPTION_KEY = "qiHNP04g4igdM98gN5YN1UOqc6t9cyDW"

def evp_derive(password: bytes, salt: bytes):
    d, d_i = b"", b""
    while len(d) < 48:
        d_i = hashlib.md5(d_i + password + salt).digest()
        d += d_i
    return d[:32], d[32:48]

def decrypt_n8n(encrypted_str: str) -> dict:
    raw = base64.b64decode(encrypted_str)
    assert raw[:8] == b"Salted__"
    salt = raw[8:16]
    data = raw[16:]
    key, iv = evp_derive(ENCRYPTION_KEY.encode(), salt)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    dec = cipher.decrypt(data)
    pad = dec[-1]
    dec = dec[:-pad]
    return json.loads(dec.decode("utf-8"))

# Récupère la clé Claude depuis n8n
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT data FROM credentials_entity WHERE id = 'HMF1JkG9k0moa4vO'")
row = cur.fetchone()
conn.close()

cred = decrypt_n8n(row[0])
api_key = cred.get("value", "")
print(f"Claude API key: {api_key[:20]}...")

# Nouveau prompt (copie du WF2)
def build_prompt(nom, secteur):
    hooks = {
        "comptable":          "Vos assistants saisissent encore des factures PDF manuellement ?",
        "kiné":               "Vous perdez du temps à rappeler les patients qui ne répondent pas ?",
        "ostéopathe":         "Vous perdez du temps à rappeler les patients qui ne répondent pas ?",
        "plombier":           "Vous faites encore vos devis à la main ?",
        "agence immobilière": "Votre reporting de la semaine se fait encore dans Excel ?",
        "default":            "Vous avez des tâches répétitives qui pourraient être automatisées ?"
    }
    hook = hooks.get(secteur.lower(), hooks["default"])
    return f"""Tu es Enzo, consultant en automatisation IA pour PME françaises (AI Installator).
Rédige un email de prospection professionnel et courtois pour {nom}, un(e) {secteur}.

Hook d'accroche : "{hook}"

Règles STRICTES :
- Commence TOUJOURS par "Bonjour,"
- 6 lignes maximum (corps uniquement, sans compter la signature)
- Objet : accrocheur, personnalisé au secteur, sans point d'exclamation
- Corps :
    1. "Bonjour,"
    2. Hook ou question d'accroche (une phrase)
    3. Preuve sociale courte (ex : "J'ai aidé un cabinet de 4 personnes à économiser 8h/semaine")
    4. CTA : proposition d'un échange de 20 minutes, gratuit et sans engagement
- Termine par la signature exacte : "Cordialement,\\nEnzo — AI Installator"
- Ton : professionnel, direct, courtois — jamais familier, jamais criard
- PAS de lorem ipsum, PAS de mots entre [crochets]

Retourne UNIQUEMENT un JSON valide avec exactement ces 2 clés :
{{"objet": "...", "corps": "..."}}
Le champ "corps" doit inclure "Bonjour," au début et "Cordialement,\\nEnzo — AI Installator" à la fin."""

def call_claude(prompt):
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    text = r.json()["content"][0]["text"].strip()
    import re
    m = re.search(r'\{[\s\S]*\}', text)
    return json.loads(m.group(0)) if m else {"raw": text}

# Test sur 3 secteurs
tests = [
    ("Cabinet Romain Kiné", "kiné"),
    ("Dupont Expertise Comptable", "comptable"),
    ("Plomberie Moreau & Fils", "plombier"),
]

print("\n" + "="*60)
for nom, secteur in tests:
    print(f"\n[{secteur.upper()}] — {nom}")
    print("-"*60)
    result = call_claude(build_prompt(nom, secteur))
    print(f"OBJET : {result.get('objet', '?')}")
    print(f"\nCORPS :\n{result.get('corps', result.get('raw', '?'))}")
    print("="*60)

print("\nValidation OK ? Lance demain à 8h.")
