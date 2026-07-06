"""
Fix WF2: remplace filtersUI (incompatible) par readAll + Code node pour filtrer.
Aussi fix WF3 Lire Prospects Contactés pour la même raison.
"""
import json, requests

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NGQ5YjQ1NC05ZTZhLTQ3NmQtYTczMi1hNWNiYzFkNzAxOTIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZTQ2MmY4MzEtMDJhNS00YjU5LWE4MzctMGJhZmNkYjRmMTljIiwiaWF0IjoxNzgwNDkzMTM3LCJleHAiOjE3ODMwNTEyMDB9.jaAktbuoPW6IIAkm-sUdLQp3wDrSbhlpTM3JPkyFFQc"
BASE = "http://localhost:5678/api/v1"
H = {"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"}

SPREADSHEET_ID = "1mvylh6MKh2RD8y6FtgyMXgMvfno_9iPOiwC6Osq6gaE"
SHEETS_CRED = {"id": "gEANv3fBenM1udse", "name": "Google Sheets account"}

def fix_workflow(wf_id, read_node_name, filter_statut, filter_code_name, filter_code_id, next_node_name):
    """
    Patch un workflow qui a un node Sheets avec filtersUI :
    - Vide filtersUI -> lit toutes les lignes
    - Insère un Code node après qui filtre par statut
    """
    r = requests.get(f"{BASE}/workflows/{wf_id}", headers=H)
    r.raise_for_status()
    wf = r.json()
    nodes = wf["nodes"]
    connections = wf["connections"]

    # ── 1. Fix le node Sheets : supprime filtersUI ──────────────────────────
    for n in nodes:
        if n["name"] == read_node_name:
            params = n["parameters"]
            # Supprime filtersUI, garde le reste
            params.pop("filtersUI", None)
            params.pop("filters", None)
            # Lit TOUTES les lignes (pas de filtre côté Sheets)
            params["options"] = {"returnAll": True}
            # Ajoute row_index dans la sortie
            print(f"  Fixed node: {read_node_name}")

    # ── 2. Vérifie si le Code node de filtre existe déjà ────────────────────
    if any(n["name"] == filter_code_name for n in nodes):
        print(f"  Code node {filter_code_name} déjà présent")
        return

    # ── 3. Trouve la position du read node pour placer le code node après ───
    read_pos = next((n["position"] for n in nodes if n["name"] == read_node_name), [240, 300])
    code_pos = [read_pos[0] + 240, read_pos[1]]

    # Décale les nodes suivants pour faire de la place
    for n in nodes:
        if n["position"][0] >= code_pos[0] and n["name"] != read_node_name:
            n["position"][0] += 240

    # ── 4. Code node de filtre ───────────────────────────────────────────────
    filter_code = f"""
const items = $input.all();
const filtered = [];
for (let i = 0; i < items.length; i++) {{
  const row = items[i].json;
  if (row.statut === '{filter_statut}') {{
    filtered.push({{ json: {{ ...row, row_index: i + 2 }} }});
  }}
}}
return filtered.length > 0 ? filtered : [{{ json: {{ _skip: true }} }}];
"""
    code_node = {
        "id": filter_code_id,
        "name": filter_code_name,
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": code_pos,
        "parameters": {"jsCode": filter_code.strip()}
    }
    nodes.append(code_node)

    # ── 5. Update connections ────────────────────────────────────────────────
    # read_node_name -> code_node -> next_node_name
    connections[read_node_name] = {"main": [[{"node": filter_code_name, "type": "main", "index": 0}]]}
    connections[filter_code_name] = {"main": [[{"node": next_node_name, "type": "main", "index": 0}]]}
    print(f"  Added filter code node: {filter_code_name}")

    # ── 6. PUT ───────────────────────────────────────────────────────────────
    payload = {
        "name": wf["name"],
        "nodes": nodes,
        "connections": connections,
        "settings": wf.get("settings", {}),
        "staticData": wf.get("staticData"),
    }
    r2 = requests.put(f"{BASE}/workflows/{wf_id}", headers=H, json=payload)
    if r2.status_code in (200, 201):
        print(f"  OK — {wf['name']} mis à jour")
    else:
        print(f"  ERREUR {r2.status_code}: {r2.text[:200]}")

# WF2 — Outreach : filtre "Nouveau"
print("=== Fix WF2 ===")
fix_workflow(
    wf_id          = "CQcPR4kIgxRoidGY",
    read_node_name = "Lire Prospects Nouveaux",
    filter_statut  = "Nouveau",
    filter_code_name = "Filtrer Statut Nouveau",
    filter_code_id = "filter-nouveau",
    next_node_name = "Filtrer Avec Email"
)

# WF3 — Relance : filtre "Contacté"
print("=== Fix WF3 ===")
fix_workflow(
    wf_id          = "HT0tzw9eFpnuwwnL",
    read_node_name = "Lire Prospects Contactés",
    filter_statut  = "Contacté",
    filter_code_name = "Filtrer Statut Contacté",
    filter_code_id = "filter-contacte",
    next_node_name = "Filtrer J+3"
)
