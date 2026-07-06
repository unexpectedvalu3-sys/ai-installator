# -*- coding: utf-8 -*-
"""
Reset la ligne demo avant chaque presentation client.
- Remet rappel_envoye a vide (sinon le filtre skip Marie)
- Met la date RDV a demain
- Met le telephone du prospect (modifie la variable TELEPHONE_PROSPECT)
"""
import sqlite3, json, base64, os, requests
from Crypto.Cipher import AES
import hashlib
from datetime import date, timedelta

# ← CHANGE ICI le numero du prospect avant la demo
TELEPHONE_PROSPECT = "+33787739910"

DB = os.path.expanduser("~/.n8n/database.sqlite")
EK = "qiHNP04g4igdM98gN5YN1UOqc6t9cyDW"

def evp(p, s):
    d, d_i = b"", b""
    while len(d) < 48:
        d_i = hashlib.md5(d_i + p + s).digest()
        d += d_i
    return d[:32], d[32:48]

def dec(s):
    raw = base64.b64decode(s)
    k, iv = evp(EK.encode(), raw[8:16])
    dc = AES.new(k, AES.MODE_CBC, iv).decrypt(raw[16:])
    return json.loads(dc[:-dc[-1]])

conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT data FROM credentials_entity WHERE id = 'gEANv3fBenM1udse'")
cred = dec(cur.fetchone()[0])
conn.close()

r = requests.post("https://oauth2.googleapis.com/token", data={
    "client_id": cred["clientId"], "client_secret": cred["clientSecret"],
    "refresh_token": cred["oauthTokenData"]["refresh_token"], "grant_type": "refresh_token"
})
token = r.json()["access_token"]
SHEET_ID = "1mvylh6MKh2RD8y6FtgyMXgMvfno_9iPOiwC6Osq6gaE"
hdrs = {"Authorization": f"Bearer {token}"}

tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")

# Met a jour : telephone + date_rdv demain + reset rappel_envoye
r2 = requests.put(
    f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/Demo_Kine!C2:H2",
    headers=hdrs, params={"valueInputOption": "USER_ENTERED"},
    json={"values": [[TELEPHONE_PROSPECT, "unexpectedvalu3@gmail.com", tomorrow, "10h00", "Dr. Mercier", ""]]}
)
print(f"Reset OK ({r2.status_code}) - RDV demain {tomorrow} - Tel {TELEPHONE_PROSPECT}")
