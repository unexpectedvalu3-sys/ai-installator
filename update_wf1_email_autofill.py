"""
Update WF1 — Lead Generation: ajoute 2 nodes pour extraire l'email depuis le website
Structure après update:
  Filtrer Vides -> Fetch Website -> Extraire Email -> Ajouter dans Sheets
"""
import json, requests

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NGQ5YjQ1NC05ZTZhLTQ3NmQtYTczMi1hNWNiYzFkNzAxOTIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZTQ2MmY4MzEtMDJhNS00YjU5LWE4MzctMGJhZmNkYjRmMTljIiwiaWF0IjoxNzgwNDkzMTM3LCJleHAiOjE3ODMwNTEyMDB9.jaAktbuoPW6IIAkm-sUdLQp3wDrSbhlpTM3JPkyFFQc"
BASE   = "http://localhost:5678/api/v1"
WF1_ID = "oDXLlTxQuktRbTpl"
H = {"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"}

# ─── GET current workflow ───────────────────────────────────────────────────
r = requests.get(f"{BASE}/workflows/{WF1_ID}", headers=H)
r.raise_for_status()
wf = r.json()

nodes = wf["nodes"]
connections = wf["connections"]

# ─── Shift "Ajouter dans Sheets" 480px to the right ─────────────────────────
for n in nodes:
    if n["name"] == "Ajouter dans Sheets":
        n["position"] = [1680, 300]
        break

# ─── New node 1: Fetch Website ───────────────────────────────────────────────
# - httpRequest GET sur le website du prospect
# - continueOnFail=true : si timeout/404/no website → continue avec corps vide
# - responseFormat text pour avoir le HTML brut
node_fetch = {
    "id": "fetch-website",
    "name": "Fetch Website",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [1200, 300],
    "continueOnFail": True,
    "parameters": {
        "method": "GET",
        "url": "={{ $json.website && $json.website.startsWith('http') ? $json.website : 'https://httpstat.us/204' }}",
        "options": {
            "response": {
                "response": {
                    "responseFormat": "text"
                }
            },
            "timeout": 5000
        }
    }
}

# ─── New node 2: Extraire Email ──────────────────────────────────────────────
# - Code node runOnceForEachItem
# - regex sur le HTML pour extraire mailto:
# - merge avec les données originales du lead (depuis Filtrer Vides)
CODE_EXTRACT = r"""
const html = ($input.item.json.body || $input.item.json.data || $input.item.json.error || '').toString();
const lead = $('Filtrer Vides').item.json;

// Cherche mailto: dans le HTML
const m = html.match(/mailto:([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})/i);
const email = m ? m[1].toLowerCase() : '';

return { json: { ...lead, email } };
"""

node_extract = {
    "id": "extract-email",
    "name": "Extraire Email",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1440, 300],
    "parameters": {
        "jsCode": CODE_EXTRACT,
        "mode": "runOnceForEachItem"
    }
}

# ─── Ajouter les 2 nouveaux nodes ────────────────────────────────────────────
nodes.append(node_fetch)
nodes.append(node_extract)

# ─── Update connections ────────────────────────────────────────────────────────
# Avant : Filtrer Vides -> Ajouter dans Sheets
# Apres : Filtrer Vides -> Fetch Website -> Extraire Email -> Ajouter dans Sheets

connections["Filtrer Vides"] = {
    "main": [[{"node": "Fetch Website", "type": "main", "index": 0}]]
}
connections["Fetch Website"] = {
    "main": [[{"node": "Extraire Email", "type": "main", "index": 0}]]
}
connections["Extraire Email"] = {
    "main": [[{"node": "Ajouter dans Sheets", "type": "main", "index": 0}]]
}

wf["nodes"] = nodes
wf["connections"] = connections

# ─── PUT updated workflow (only allowed fields) ───────────────────────────────
payload = {
    "name":        wf["name"],
    "nodes":       wf["nodes"],
    "connections": wf["connections"],
    "settings":    wf.get("settings", {}),
    "staticData":  wf.get("staticData"),
}
r2 = requests.put(f"{BASE}/workflows/{WF1_ID}", headers=H, json=payload)
if r2.status_code in (200, 201):
    print("OK — WF1 mis a jour avec email auto-fill")
    print("Nouveaux nodes : Fetch Website + Extraire Email")
    print(f"  Filtrer Vides -> Fetch Website -> Extraire Email -> Ajouter dans Sheets")
else:
    print(f"ERREUR {r2.status_code}")
    print(json.dumps(r2.json(), indent=2))
