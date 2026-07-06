# -*- coding: utf-8 -*-
"""
Met à jour la preuve sociale dans le prompt Claude de WF2
kiné : "cabinet de 4 personnes" -> "un ami kiné"
"""
import requests

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NGQ5YjQ1NC05ZTZhLTQ3NmQtYTczMi1hNWNiYzFkNzAxOTIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZTQ2MmY4MzEtMDJhNS00YjU5LWE4MzctMGJhZmNkYjRmMTljIiwiaWF0IjoxNzgwNDkzMTM3LCJleHAiOjE3ODMwNTEyMDB9.jaAktbuoPW6IIAkm-sUdLQp3wDrSbhlpTM3JPkyFFQc"
BASE = "http://localhost:5678/api/v1"
H = {"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"}

r = requests.get(f"{BASE}/workflows/CQcPR4kIgxRoidGY", headers=H)
wf = r.json()

for n in wf["nodes"]:
    if n["name"] == "Construire Prompt Claude":
        old = n["parameters"]["jsCode"]
        # Remplace l'exemple de preuve sociale générique par une mention honnête
        new = old.replace(
            'Preuve sociale courte (ex : "J\'ai aidé un cabinet de 4 personnes à économiser 8h/semaine")',
            'Preuve sociale courte — pour kiné/ostéo : utilise "J\'ai aidé un ami kiné à automatiser ses rappels, il a récupéré une demi-journée par semaine". Pour les autres secteurs : formule de façon neutre (ex: "Des professionnels que j\'accompagne gagnent en moyenne 6h par semaine sur ce type de tâche")'
        )
        n["parameters"]["jsCode"] = new
        print("Patché : Construire Prompt Claude")

payload = {
    "name": wf["name"], "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": wf.get("settings", {}),
    "staticData": wf.get("staticData")
}
r2 = requests.put(f"{BASE}/workflows/CQcPR4kIgxRoidGY", headers=H, json=payload)
print(f"PUT {r2.status_code}")
