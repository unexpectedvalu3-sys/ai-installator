"""
Déchiffre le credential Google Sheets OAuth2 depuis la DB n8n,
puis ajoute une ligne test dans le Sheets CRM.
"""
import sqlite3, json, os, base64, requests
from Crypto.Cipher import AES

N8N_DIR = os.path.expanduser('~/.n8n')
DB_PATH  = os.path.join(N8N_DIR, 'database.sqlite')
ENC_KEY  = 'qiHNP04g4igdM98gN5YN1UOqc6t9cyDW'  # depuis ~/.n8n/config

SPREADSHEET_ID = '1mvylh6MKh2RD8y6FtgyMXgMvfno_9iPOiwC6Osq6gaE'

# ── Déchiffre la data n8n (format AES-256-CBC + CryptoJS "Salted__") ─────────
def decrypt_n8n(encrypted_b64: str, key: str) -> dict:
    raw = base64.b64decode(encrypted_b64)
    assert raw[:8] == b'Salted__', "Bad magic"
    salt      = raw[8:16]
    ciphertext = raw[16:]

    # CryptoJS EVP key derivation (MD5 x iterations)
    key_bytes = key.encode('utf-8')
    d = b''
    d_i = b''
    while len(d) < 48:  # 32 key + 16 iv
        import hashlib
        d_i = hashlib.md5(d_i + key_bytes + salt).digest()
        d += d_i
    aes_key = d[:32]
    aes_iv  = d[32:48]

    cipher  = AES.new(aes_key, AES.MODE_CBC, aes_iv)
    padded  = cipher.decrypt(ciphertext)
    # PKCS7 unpad
    pad_len = padded[-1]
    return json.loads(padded[:-pad_len].decode('utf-8'))

# ── Récupère le token du credential Google Sheets ────────────────────────────
conn = sqlite3.connect(DB_PATH)
cur  = conn.cursor()
cur.execute("SELECT id, name, data FROM credentials_entity WHERE type='googleSheetsOAuth2Api'")
row = cur.fetchone()
conn.close()

if not row:
    print("ERREUR: credential googleSheetsOAuth2Api non trouvé")
    exit(1)

print(f"Credential trouvé: {row[1]} ({row[0]})")
cred_data = decrypt_n8n(row[2], ENC_KEY)
print(f"Clés disponibles: {list(cred_data.keys())}")

token_data = cred_data.get('oauthTokenData', {})
access_token = token_data.get('access_token')

if not access_token:
    print("Pas d'access_token dans les données. Token data:", json.dumps(token_data, indent=2)[:300])
    exit(1)

print(f"Access token: {access_token[:30]}...")

# ── Ajoute la ligne test dans Sheets ─────────────────────────────────────────
row_values = [[
    'TEST Kiné Dupont', 'kiné', 'Paris 10e', 'https://example.com',
    '0600000000', 'unexpectedvalu3@gmail.com', 'Nouveau', '2026-06-03',
    '', '', 'LIGNE TEST - supprimer apres validation'
]]

resp = requests.post(
    f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/Prospects:append',
    params={'valueInputOption': 'USER_ENTERED'},
    headers={'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'},
    json={'values': row_values}
)

if resp.status_code == 200:
    data = resp.json()
    print(f"OK - Ligne ajoutée: {data.get('updates', {}).get('updatedRange')}")
else:
    print(f"ERREUR {resp.status_code}: {resp.text[:300]}")
