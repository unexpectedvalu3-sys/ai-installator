# -*- coding: utf-8 -*-
"""
Crée le workflow DEMO — Rappels Kiné dans n8n.
Flow: Manual Trigger → Lire Sheet → Parser/Filtrer → IF skip
  TRUE  → end
  FALSE → Email Gmail + SMS Twilio → MAJ Sheet rappel_envoye
"""
import json, requests

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NGQ5YjQ1NC05ZTZhLTQ3NmQtYTczMi1hNWNiYzFkNzAxOTIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZTQ2MmY4MzEtMDJhNS00YjU5LWE4MzctMGJhZmNkYjRmMTljIiwiaWF0IjoxNzgwNDkzMTM3LCJleHAiOjE3ODMwNTEyMDB9.jaAktbuoPW6IIAkm-sUdLQp3wDrSbhlpTM3JPkyFFQc"
BASE   = "http://localhost:5678/api/v1"
H      = {"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"}

SHEET_ID    = "1mvylh6MKh2RD8y6FtgyMXgMvfno_9iPOiwC6Osq6gaE"
SHEETS_CRED = {"id": "gEANv3fBenM1udse", "name": "Google Sheets account"}
GMAIL_CRED  = {"id": "87LqYKP4BqT9uKTY", "name": "Gmail account 2"}
TWILIO_CRED = {"id": "6jUa3m0DtieixSwP", "name": "Twilio Basic Auth"}
TWILIO_SID  = "AC33f3d945659595b4453b252c12633764"
TWILIO_FROM = "+16168798969"

# ── Code : parse + filtre demain ────────────────────────────────────────────
PARSER_CODE = r"""
const data = $input.first().json;
const values = data.values || [];
if (values.length < 2) return [{ json: { _skip: true } }];

const headers = values[0];
const rows = values.slice(1);
const tomorrow = new Date(Date.now() + 86400000).toISOString().slice(0, 10);

const results = [];
for (let i = 0; i < rows.length; i++) {
  const row = Object.fromEntries(headers.map((h, j) => [h, rows[i][j] || '']));
  if (row.date_rdv === tomorrow && row.rappel_envoye === '') {
    results.push({ json: { ...row, row_index: i + 2 } });
  }
}
return results.length > 0 ? results : [{ json: { _skip: true } }];
""".strip()

# ── Corps email Gmail ────────────────────────────────────────────────────────
EMAIL_SUBJECT = "=Rappel de votre rendez-vous demain — Cabinet " + "{{ $json.praticien }}"
EMAIL_BODY = """Bonjour {{ $json.prenom }},

Nous vous rappelons votre rendez-vous de kinésithérapie prévu demain le {{ $json.date_rdv }} à {{ $json.heure }} au cabinet de {{ $json.praticien }}.

En cas d'empêchement, merci de nous contacter dès que possible.

À demain,
{{ $json.praticien }}"""

# ── SMS Twilio ────────────────────────────────────────────────────────────────
SMS_BODY = "={{ 'Rappel RDV : ' + $json.prenom + ' ' + $json.nom + ', demain à ' + $json.heure + ' chez ' + $json.praticien + '. En cas d\\'empêchement, merci de contacter le cabinet.' }}"

nodes = [
  # 1. Manual Trigger
  {
    "id": "trigger-manual",
    "name": "Déclencher Démo",
    "type": "n8n-nodes-base.manualTrigger",
    "typeVersion": 1,
    "position": [240, 300],
    "parameters": {}
  },
  # 2. Lire sheet Demo_Kine
  {
    "id": "http-lire-sheet",
    "name": "Lire Patients Demo",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [460, 300],
    "credentials": {"googleSheetsOAuth2Api": SHEETS_CRED},
    "parameters": {
      "method": "GET",
      "url": f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/Demo_Kine",
      "authentication": "predefinedCredentialType",
      "nodeCredentialType": "googleSheetsOAuth2Api",
      "options": {}
    }
  },
  # 3. Parser + filtre RDV demain
  {
    "id": "code-parser",
    "name": "Filtrer RDV Demain",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [680, 300],
    "parameters": {"jsCode": PARSER_CODE}
  },
  # 4. IF _skip
  {
    "id": "if-skip",
    "name": "Patients à Rappeler ?",
    "type": "n8n-nodes-base.if",
    "typeVersion": 2,
    "position": [900, 300],
    "parameters": {
      "conditions": {
        "options": {"caseSensitive": True},
        "conditions": [{
          "leftValue": "={{ $json._skip }}",
          "rightValue": True,
          "operator": {"type": "boolean", "operation": "notEquals"}
        }]
      }
    }
  },
  # 5. Email Gmail
  {
    "id": "gmail-send",
    "name": "Envoyer Email Rappel",
    "type": "n8n-nodes-base.gmail",
    "typeVersion": 2.1,
    "position": [1120, 180],
    "credentials": {"gmailOAuth2": GMAIL_CRED},
    "parameters": {
      "operation": "send",
      "toList": "={{ $json.email }}",
      "subject": EMAIL_SUBJECT,
      "message": EMAIL_BODY,
      "options": {}
    }
  },
  # 6. SMS Twilio (HTTP Request avec Basic Auth)
  {
    "id": "http-sms",
    "name": "Envoyer SMS Rappel",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [1120, 380],
    "credentials": {"httpBasicAuth": TWILIO_CRED},
    "parameters": {
      "method": "POST",
      "url": f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json",
      "authentication": "genericCredentialType",
      "genericAuthType": "httpBasicAuth",
      "sendBody": True,
      "contentType": "form",
      "bodyParameters": {
        "parameters": [
          {"name": "To",   "value": "={{ $json.telephone }}"},
          {"name": "From", "value": TWILIO_FROM},
          {"name": "Body", "value": "={{ 'Rappel RDV : ' + $json.prenom + ' ' + $json.nom + ', demain à ' + $json.heure + ' chez ' + $json.praticien + '. En cas d\\'empêchement, merci de contacter le cabinet.' }}"}
        ]
      },
      "options": {}
    }
  },
  # 7. MAJ Sheet rappel_envoye
  {
    "id": "http-maj",
    "name": "MAJ Rappel Envoyé",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [1340, 280],
    "credentials": {"googleSheetsOAuth2Api": SHEETS_CRED},
    "parameters": {
      "method": "POST",
      "url": f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values:batchUpdate",
      "authentication": "predefinedCredentialType",
      "nodeCredentialType": "googleSheetsOAuth2Api",
      "sendBody": True,
      "contentType": "raw",
      "rawContentType": "application/json",
      "body": "={{ JSON.stringify({ data: [{ range: 'Demo_Kine!H' + $('Filtrer RDV Demain').item.json.row_index, values: [['OUI - ' + new Date().toISOString().slice(0,10)]] }], valueInputOption: 'USER_ENTERED' }) }}",
      "options": {}
    }
  },
]

connections = {
  "Déclencher Démo":       {"main": [[{"node": "Lire Patients Demo",    "type": "main", "index": 0}]]},
  "Lire Patients Demo":    {"main": [[{"node": "Filtrer RDV Demain",    "type": "main", "index": 0}]]},
  "Filtrer RDV Demain":    {"main": [[{"node": "Patients à Rappeler ?", "type": "main", "index": 0}]]},
  "Patients à Rappeler ?": {
    "main": [
      [{"node": "Envoyer Email Rappel", "type": "main", "index": 0},
       {"node": "Envoyer SMS Rappel",   "type": "main", "index": 0}],  # TRUE → email + SMS
      []  # FALSE → rien
    ]
  },
  "Envoyer Email Rappel":  {"main": [[{"node": "MAJ Rappel Envoyé", "type": "main", "index": 0}]]},
  "Envoyer SMS Rappel":    {"main": [[{"node": "MAJ Rappel Envoyé", "type": "main", "index": 0}]]},
}

workflow = {
  "name": "DEMO — Rappels Patients Kiné",
  "nodes": nodes,
  "connections": connections,
  "settings": {"executionOrder": "v1"},
  "staticData": None
}

r = requests.post(f"{BASE}/workflows", headers=H, json=workflow)
print("Status:", r.status_code)
d = r.json()
if r.status_code in (200, 201):
    print("Workflow créé !")
    print("ID:", d["id"])
    print("URL: http://localhost:5678/workflow/" + d["id"])
else:
    print("Erreur:", d.get("message", r.text[:300]))
