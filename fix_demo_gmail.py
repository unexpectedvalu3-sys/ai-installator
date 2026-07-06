# -*- coding: utf-8 -*-
import requests, json

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NGQ5YjQ1NC05ZTZhLTQ3NmQtYTczMi1hNWNiYzFkNzAxOTIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZTQ2MmY4MzEtMDJhNS00YjU5LWE4MzctMGJhZmNkYjRmMTljIiwiaWF0IjoxNzgwNDkzMTM3LCJleHAiOjE3ODMwNTEyMDB9.jaAktbuoPW6IIAkm-sUdLQp3wDrSbhlpTM3JPkyFFQc"
BASE = "http://localhost:5678/api/v1"
H = {"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"}

r = requests.get(f"{BASE}/workflows/XcbTX6R2UHCt5PyK", headers=H)
wf = r.json()

for n in wf["nodes"]:
    if n["name"] == "Envoyer Email Rappel":
        n["parameters"] = {
            "operation": "send",
            "sendTo": "={{ $json.email }}",
            "subject": "={{ $json.email_subject }}",
            "emailType": "text",
            "message": "={{ $json.email_body }}",
            "options": {}
        }
        print("Gmail patched:", n["parameters"]["sendTo"])

    if n["name"] == "Envoyer SMS Rappel":
        params = n["parameters"]
        for p in params.get("bodyParameters", {}).get("parameters", []):
            if p["name"] == "Body":
                p["value"] = "={{ $json.sms_body }}"
                print("SMS body patched:", p["value"])
            if p["name"] == "To":
                p["value"] = "={{ $json.telephone }}"
                print("SMS to patched:", p["value"])

    if n["name"] == "MAJ Rappel Envoyé":
        # Vérifie que row_index vient bien de Filtrer RDV Demain
        body = n["parameters"].get("body", "")
        print("MAJ body:", body[:100])

payload = {
    "name": wf["name"], "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": wf.get("settings", {}),
    "staticData": wf.get("staticData")
}
r2 = requests.put(f"{BASE}/workflows/XcbTX6R2UHCt5PyK", headers=H, json=payload)
print("PUT", r2.status_code)

# Vérification
r3 = requests.get(f"{BASE}/workflows/XcbTX6R2UHCt5PyK", headers=H)
wf2 = r3.json()
for n in wf2["nodes"]:
    if n["name"] == "Envoyer Email Rappel":
        print("Stored sendTo:", n["parameters"]["sendTo"])
