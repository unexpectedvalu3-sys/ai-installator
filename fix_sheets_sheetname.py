"""
Fix le sheetName mode="name" -> mode="id" (gid=0) pour éviter l'appel API de résolution.
Aussi retire returnAll de options (pas supporté là).
Applique à WF2 (Lire Prospects Nouveaux) et WF3 (Lire Prospects Contactés).
"""
import json, requests

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NGQ5YjQ1NC05ZTZhLTQ3NmQtYTczMi1hNWNiYzFkNzAxOTIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZTQ2MmY4MzEtMDJhNS00YjU5LWE4MzctMGJhZmNkYjRmMTljIiwiaWF0IjoxNzgwNDkzMTM3LCJleHAiOjE3ODMwNTEyMDB9.jaAktbuoPW6IIAkm-sUdLQp3wDrSbhlpTM3JPkyFFQc"
BASE = "http://localhost:5678/api/v1"
H = {"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"}

NODES_TO_FIX = [
    ("CQcPR4kIgxRoidGY", "Lire Prospects Nouveaux"),
    ("HT0tzw9eFpnuwwnL", "Lire Prospects Contactés"),
]

for wf_id, node_name in NODES_TO_FIX:
    r = requests.get(f"{BASE}/workflows/{wf_id}", headers=H)
    r.raise_for_status()
    wf = r.json()

    for n in wf["nodes"]:
        if n["name"] == node_name:
            p = n["parameters"]
            # Fix sheetName: mode=name -> mode=id (gid 0 = première feuille)
            p["sheetName"] = {"__rl": True, "value": "gid=0", "mode": "id"}
            # Retire returnAll de options (paramètre top-level pour certaines versions)
            p.pop("options", None)
            p["options"] = {}
            print(f"  Fixed {node_name} in {wf['name']}")

    payload = {
        "name": wf["name"], "nodes": wf["nodes"],
        "connections": wf["connections"],
        "settings": wf.get("settings", {}),
        "staticData": wf.get("staticData"),
    }
    r2 = requests.put(f"{BASE}/workflows/{wf_id}", headers=H, json=payload)
    if r2.status_code in (200, 201):
        print(f"  OK - {wf['name']} updated")
    else:
        print(f"  ERREUR {r2.status_code}: {r2.text[:150]}")
