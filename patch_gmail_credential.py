import json, requests, sys

# API n8n
N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NGQ5YjQ1NC05ZTZhLTQ3NmQtYTczMi1hNWNiYzFkNzAxOTIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZTQ2MmY4MzEtMDJhNS00YjU5LWE4MzctMGJhZmNkYjRmMTljIiwiaWF0IjoxNzgwNDkzMTM3LCJleHAiOjE3ODMwNTEyMDB9.jaAktbuoPW6IIAkm-sUdLQp3wDrSbhlpTM3JPkyFFQc"
BASE = "http://localhost:5678/api/v1"
H = {"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"}

NEW_GMAIL_CRED = {"id": "O7TlhmxuwfxkA3ny", "name": "Gmail account 3"}

WF_IDS = {
    "WF2 - Outreach": "CQcPR4kIgxRoidGY",
    "WF3 - Relance":  "HT0tzw9eFpnuwwnL",
}

def patch_workflow(wf_name, wf_id):
    print(f"\n--- {wf_name} ({wf_id}) ---")

    r = requests.get(f"{BASE}/workflows/{wf_id}", headers=H)
    if r.status_code != 200:
        print(f"  ERREUR get: {r.status_code} {r.text[:200]}")
        return

    wf = r.json()
    nodes = wf.get("nodes", [])
    patched = 0

    for node in nodes:
        ntype = node.get("type", "")
        creds = node.get("credentials", {})

        # Patch node Gmail (type n8n-nodes-base.gmail)
        if "gmail" in ntype.lower():
            old = creds.get("gmailOAuth2", creds.get("googleOAuth2Api", {}))
            print(f"  Gmail node: {node['name']} | ancien cred: {old}")
            node["credentials"] = {"gmailOAuth2": NEW_GMAIL_CRED}
            patched += 1

    if patched == 0:
        print("  Aucun node Gmail trouve.")
        # Debug: lister tous les nodes
        for n in nodes:
            print(f"    node: {n.get('name')} | type: {n.get('type')}")
        return

    # PUT workflow
    payload = {
        "name": wf.get("name"),
        "nodes": nodes,
        "connections": wf.get("connections", {}),
        "settings": wf.get("settings", {"executionOrder": "v1"}),
        "staticData": wf.get("staticData"),
    }

    r2 = requests.put(f"{BASE}/workflows/{wf_id}", headers=H, json=payload)
    if r2.status_code == 200:
        print(f"  OK - {patched} node(s) patche(s) -> Gmail account 3 (contact.lumaaria@gmail.com)")
    else:
        print(f"  ERREUR put: {r2.status_code} {r2.text[:300]}")

for name, wid in WF_IDS.items():
    patch_workflow(name, wid)

print("\nDone.")
