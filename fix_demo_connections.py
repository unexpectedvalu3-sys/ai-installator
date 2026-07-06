# -*- coding: utf-8 -*-
"""
Fix la pipeline démo :
Email et SMS en série (Email -> SMS) au lieu de parallèle.
SMS référence $('Filtrer RDV Demain').item.json pour avoir les données patient.
"""
import requests, json

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NGQ5YjQ1NC05ZTZhLTQ3NmQtYTczMi1hNWNiYzFkNzAxOTIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZTQ2MmY4MzEtMDJhNS00YjU5LWE4MzctMGJhZmNkYjRmMTljIiwiaWF0IjoxNzgwNDkzMTM3LCJleHAiOjE3ODMwNTEyMDB9.jaAktbuoPW6IIAkm-sUdLQp3wDrSbhlpTM3JPkyFFQc"
BASE = "http://localhost:5678/api/v1"
H = {"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"}

TWILIO_SID = "AC33f3d945659595b4453b252c12633764"
TWILIO_FROM = "+16168798969"

r = requests.get(f"{BASE}/workflows/XcbTX6R2UHCt5PyK", headers=H)
wf = r.json()

# Connexions : Email -> SMS -> MAJ (en série)
wf["connections"] = {
    "Déclencher Démo":        {"main": [[{"node": "Lire Patients Demo",    "type": "main", "index": 0}]]},
    "Lire Patients Demo":     {"main": [[{"node": "Filtrer RDV Demain",    "type": "main", "index": 0}]]},
    "Filtrer RDV Demain":     {"main": [[{"node": "Patients à Rappeler ?", "type": "main", "index": 0}]]},
    "Patients à Rappeler ?":  {"main": [
        [{"node": "Envoyer Email Rappel", "type": "main", "index": 0}],  # TRUE
        []                                                                # FALSE
    ]},
    "Envoyer Email Rappel":   {"main": [[{"node": "Envoyer SMS Rappel",  "type": "main", "index": 0}]]},
    "Envoyer SMS Rappel":     {"main": [[{"node": "MAJ Rappel Envoyé",   "type": "main", "index": 0}]]},
}

# SMS node : référence Filtrer RDV Demain pour les données patient
for n in wf["nodes"]:
    if n["name"] == "Envoyer SMS Rappel":
        n["parameters"] = {
            "method": "POST",
            "url": f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpBasicAuth",
            "sendBody": True,
            "contentType": "form",
            "bodyParameters": {
                "parameters": [
                    {"name": "To",   "value": "={{ $('Filtrer RDV Demain').item.json.telephone }}"},
                    {"name": "From", "value": TWILIO_FROM},
                    {"name": "Body", "value": "={{ $('Filtrer RDV Demain').item.json.sms_body }}"}
                ]
            },
            "options": {}
        }
        print("SMS node updated — référence Filtrer RDV Demain")

    # MAJ sheet : référence aussi Filtrer RDV Demain pour row_index
    if n["name"] == "MAJ Rappel Envoyé":
        SHEET_ID = "1mvylh6MKh2RD8y6FtgyMXgMvfno_9iPOiwC6Osq6gaE"
        SHEETS_CRED = {"id": "gEANv3fBenM1udse", "name": "Google Sheets account"}
        n["parameters"]["body"] = "={{ JSON.stringify({ data: [{ range: 'Demo_Kine!H' + $('Filtrer RDV Demain').item.json.row_index, values: [['OUI - ' + new Date().toISOString().slice(0,10)]] }], valueInputOption: 'USER_ENTERED' }) }}"
        print("MAJ node updated")

payload = {
    "name": wf["name"], "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": wf.get("settings", {}),
    "staticData": wf.get("staticData")
}
r2 = requests.put(f"{BASE}/workflows/XcbTX6R2UHCt5PyK", headers=H, json=payload)
print("PUT", r2.status_code)
