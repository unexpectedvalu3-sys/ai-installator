# -*- coding: utf-8 -*-
import json, requests

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NGQ5YjQ1NC05ZTZhLTQ3NmQtYTczMi1hNWNiYzFkNzAxOTIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZTQ2MmY4MzEtMDJhNS00YjU5LWE4MzctMGJhZmNkYjRmMTljIiwiaWF0IjoxNzgwNDkzMTM3LCJleHAiOjE3ODMwNTEyMDB9.jaAktbuoPW6IIAkm-sUdLQp3wDrSbhlpTM3JPkyFFQc"
BASE = "http://localhost:5678/api/v1"
H = {"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"}
SPREADSHEET_ID = "1mvylh6MKh2RD8y6FtgyMXgMvfno_9iPOiwC6Osq6gaE"
SHEETS_CRED = {"id": "gEANv3fBenM1udse", "name": "Google Sheets account"}

def make_http_update_node(node_id, node_name, position, col_value_pairs):
    """
    col_value_pairs: list of (col_letter, value_string)
    col G = statut, col I = date_contact, col J = date_relance
    """
    data_items = []
    for col, val in col_value_pairs:
        # Construit le range dynamique + la valeur
        data_items.append(
            '{"range": "Prospects!' + col + '{{ $json.row_index }}", "values": [["' + val + '"]]}'
        )
    body = '={{ JSON.stringify({ data: [' + ', '.join(data_items) + '], valueInputOption: "USER_ENTERED" }) }}'

    return {
        "id": node_id,
        "name": node_name,
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": position,
        "credentials": {"googleSheetsOAuth2Api": SHEETS_CRED},
        "parameters": {
            "method": "POST",
            "url": f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values:batchUpdate",
            "authentication": "predefinedCredentialType",
            "nodeCredentialType": "googleSheetsOAuth2Api",
            "sendBody": True,
            "contentType": "raw",
            "rawContentType": "application/json",
            "body": body,
            "options": {}
        }
    }

def replace_with_http(wf_id, old_name, new_id, new_name, col_val_pairs, prev_node, next_node=None):
    r = requests.get(f"{BASE}/workflows/{wf_id}", headers=H)
    wf = r.json()
    nodes, connections = wf["nodes"], wf["connections"]

    pos = next((n["position"] for n in nodes if n["name"] == old_name), [1680, 300])
    nodes = [n for n in nodes if n["name"] != old_name]
    connections.pop(old_name, None)

    new_node = make_http_update_node(new_id, new_name, pos, col_val_pairs)
    nodes.append(new_node)
    connections[prev_node] = {"main": [[{"node": new_name, "type": "main", "index": 0}]]}
    if next_node:
        connections[new_name] = {"main": [[{"node": next_node, "type": "main", "index": 0}]]}

    payload = {"name": wf["name"], "nodes": nodes, "connections": connections,
               "settings": wf.get("settings", {}), "staticData": wf.get("staticData")}
    r2 = requests.put(f"{BASE}/workflows/{wf_id}", headers=H, json=payload)
    print(f"  {wf['name']}: replaced '{old_name}' -> PUT {r2.status_code}")

# WF2
print("WF2: MAJ Statut Contacte")
replace_with_http(
    "CQcPR4kIgxRoidGY", "MAJ Statut Contacte",
    "http-update-contacte", "HTTP MAJ Contacte",
    [("G", "Contacté"), ("I", "={{ new Date().toISOString().slice(0,10) }}")],
    "Envoyer Email Gmail"
)

# WF3: RDV
print("WF3: MAJ Statut RDV Fixe")
replace_with_http(
    "HT0tzw9eFpnuwwnL", "MAJ Statut RDV Fixé",
    "http-update-rdv", "HTTP MAJ RDV Fixe",
    [("G", "RDV fixé")],
    "A Répondu ?"
)

# WF3: Relance
print("WF3: MAJ Statut Relance")
replace_with_http(
    "HT0tzw9eFpnuwwnL", "MAJ Statut Relance",
    "http-update-relance", "HTTP MAJ Relance",
    [("G", "Relancé"), ("J", "={{ new Date().toISOString().slice(0,10) }}")],
    "Envoyer Relance Gmail"
)

# WF1: fix sheetName
print("WF1: fix Ajouter dans Sheets")
r = requests.get(f"{BASE}/workflows/oDXLlTxQuktRbTpl", headers=H)
wf1 = r.json()
for n in wf1["nodes"]:
    if n["name"] == "Ajouter dans Sheets":
        n["parameters"]["sheetName"] = {"__rl": True, "value": "0", "mode": "id"}
        n["typeVersion"] = 4.1
payload = {"name": wf1["name"], "nodes": wf1["nodes"], "connections": wf1["connections"],
           "settings": wf1.get("settings", {}), "staticData": wf1.get("staticData")}
r2 = requests.put(f"{BASE}/workflows/oDXLlTxQuktRbTpl", headers=H, json=payload)
print(f"  WF1 Ajouter dans Sheets: PUT {r2.status_code}")
print("Done.")
