"""
migrate_gmail_credential.py
────────────────────────────────────────────────────────────────────────────
Usage:
  1. Va dans n8n UI : http://localhost:5678/credentials/new
     - Type : Gmail OAuth2
     - Connecte-toi avec unexpectedvalu3@gmail.com
     - Sauvegarde → copie l'ID depuis l'URL ou la liste credentials
  2. Lance ce script avec l'ID en argument :
       python migrate_gmail_credential.py <NOUVEAU_CREDENTIAL_ID>
  3. Il update WF2 + WF3 automatiquement.
"""
import sys, json, requests

if len(sys.argv) < 2:
    print("Usage: python migrate_gmail_credential.py <NOUVEAU_CREDENTIAL_ID>")
    print()
    print("Etape 1: Cree le credential dans n8n UI:")
    print("  http://localhost:5678/credentials/new")
    print("  Type: Gmail OAuth2")
    print("  Compte: unexpectedvalu3@gmail.com")
    print()
    print("Etape 2: Copie l'ID depuis la liste credentials:")
    print("  http://localhost:5678/credentials")
    sys.exit(0)

NEW_CRED_ID   = sys.argv[1]
NEW_CRED_NAME = "Gmail unexpectedvalu3"

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NGQ5YjQ1NC05ZTZhLTQ3NmQtYTczMi1hNWNiYzFkNzAxOTIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZTQ2MmY4MzEtMDJhNS00YjU5LWE4MzctMGJhZmNkYjRmMTljIiwiaWF0IjoxNzgwNDkzMTM3LCJleHAiOjE3ODMwNTEyMDB9.jaAktbuoPW6IIAkm-sUdLQp3wDrSbhlpTM3JPkyFFQc"
BASE = "http://localhost:5678/api/v1"
H    = {"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"}

NEW_CRED = {"id": NEW_CRED_ID, "name": NEW_CRED_NAME}

WF_IDS = {
    "WF2 - Outreach":   "CQcPR4kIgxRoidGY",
    "WF3 - Relance J+3":"HT0tzw9eFpnuwwnL",
}

def update_gmail_cred_in_workflow(wf_name, wf_id):
    r = requests.get(f"{BASE}/workflows/{wf_id}", headers=H)
    r.raise_for_status()
    wf = r.json()

    updated = 0
    for node in wf["nodes"]:
        creds = node.get("credentials", {})
        if "gmailOAuth2" in creds:
            old = creds["gmailOAuth2"]["id"]
            creds["gmailOAuth2"] = NEW_CRED
            print(f"  [{wf_name}] Node '{node['name']}': {old} -> {NEW_CRED_ID}")
            updated += 1

    if updated == 0:
        print(f"  [{wf_name}] Aucun node Gmail trouve")
        return

    payload = {
        "name":        wf["name"],
        "nodes":       wf["nodes"],
        "connections": wf["connections"],
        "settings":    wf.get("settings", {}),
        "staticData":  wf.get("staticData"),
    }
    r2 = requests.put(f"{BASE}/workflows/{wf_id}", headers=H, json=payload)
    if r2.status_code in (200, 201):
        print(f"  [{wf_name}] OK - {updated} node(s) mis a jour")
    else:
        print(f"  [{wf_name}] ERREUR {r2.status_code}: {r2.text[:200]}")

print(f"Migration Gmail -> {NEW_CRED_ID} ({NEW_CRED_NAME})")
print()
for name, wf_id in WF_IDS.items():
    update_gmail_cred_in_workflow(name, wf_id)

print()
print("Done. Teste la pipeline avec test_pipeline_e2e.py")
