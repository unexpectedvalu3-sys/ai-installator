# -*- coding: utf-8 -*-
"""
Remplace le SMS node par une requête Twilio avec rawBody expression
pour éviter le problème d'évaluation des bodyParameters form.
"""
import requests, json

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NGQ5YjQ1NC05ZTZhLTQ3NmQtYTczMi1hNWNiYzFkNzAxOTIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZTQ2MmY4MzEtMDJhNS00YjU5LWE4MzctMGJhZmNkYjRmMTljIiwiaWF0IjoxNzgwNDkzMTM3LCJleHAiOjE3ODMwNTEyMDB9.jaAktbuoPW6IIAkm-sUdLQp3wDrSbhlpTM3JPkyFFQc"
BASE = "http://localhost:5678/api/v1"
H = {"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"}

TWILIO_SID = "AC33f3d945659595b4453b252c12633764"
TWILIO_FROM = "+16168798969"

r = requests.get(f"{BASE}/workflows/XcbTX6R2UHCt5PyK", headers=H)
wf = r.json()

# Corps Twilio en raw URL-encoded — tout dans une seule expression
# On passe par le Code node (Filtrer RDV Demain) qui a déjà telephone et sms_body
TWILIO_BODY_EXPR = (
    "={{ 'To=' + encodeURIComponent($('Filtrer RDV Demain').item.json.telephone)"
    " + '&From=' + encodeURIComponent('" + TWILIO_FROM + "')"
    " + '&Body=' + encodeURIComponent($('Filtrer RDV Demain').item.json.sms_body) }}"
)

for n in wf["nodes"]:
    if n["name"] == "Envoyer SMS Rappel":
        n["parameters"] = {
            "method": "POST",
            "url": f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpBasicAuth",
            "sendBody": True,
            "contentType": "raw",
            "rawContentType": "application/x-www-form-urlencoded",
            "body": TWILIO_BODY_EXPR,
            "options": {}
        }
        print("SMS node - rawBody mode")
        print("Body expr:", TWILIO_BODY_EXPR[:100])

payload = {
    "name": wf["name"], "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": wf.get("settings", {}),
    "staticData": wf.get("staticData")
}
r2 = requests.put(f"{BASE}/workflows/XcbTX6R2UHCt5PyK", headers=H, json=payload)
print("PUT", r2.status_code)

# Vérifie
r3 = requests.get(f"{BASE}/workflows/XcbTX6R2UHCt5PyK", headers=H)
for n in r3.json()["nodes"]:
    if n["name"] == "Envoyer SMS Rappel":
        print("Stored body:", n["parameters"].get("body", "")[:120])
