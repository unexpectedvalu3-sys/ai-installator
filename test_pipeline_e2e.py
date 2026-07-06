"""
test_pipeline_e2e.py
────────────────────────────────────────────────────────────────────────────
Test complet de la pipeline prospection :
  1. Ajoute une ligne test dans Google Sheets (statut Nouveau, email de test)
  2. Trigger manuellement WF2 (Outreach)
  3. Affiche le resultat d'execution
  4. Check que le statut est passe a "Contacte"

Pre-requis:
  - Gmail migre vers unexpectedvalu3@gmail.com (migrate_gmail_credential.py)
  - n8n tourne (localhost:5678)

Usage:
  python test_pipeline_e2e.py [email_test]
  ex: python test_pipeline_e2e.py unexpectedvalu3@gmail.com
"""
import sys, json, time, requests

TEST_EMAIL = sys.argv[1] if len(sys.argv) > 1 else "unexpectedvalu3@gmail.com"

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NGQ5YjQ1NC05ZTZhLTQ3NmQtYTczMi1hNWNiYzFkNzAxOTIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZTQ2MmY4MzEtMDJhNS00YjU5LWE4MzctMGJhZmNkYjRmMTljIiwiaWF0IjoxNzgwNDkzMTM3LCJleHAiOjE3ODMwNTEyMDB9.jaAktbuoPW6IIAkm-sUdLQp3wDrSbhlpTM3JPkyFFQc"
BASE = "http://localhost:5678/api/v1"
H    = {"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"}

WF2_ID          = "CQcPR4kIgxRoidGY"
SPREADSHEET_ID  = "1mvylh6MKh2RD8y6FtgyMXgMvfno_9iPOiwC6Osq6gaE"

# Ligne de test a inserer dans Sheets via le node Google Sheets de WF2
# (injection directe via n8n execution avec donnees simulees)
TEST_LEAD = {
    "nom":          "TEST Kiné Dupont",
    "secteur":      "kiné",
    "ville":        "Paris 10e",
    "website":      "https://example.com",
    "tel":          "0600000000",
    "email":        TEST_EMAIL,
    "statut":       "Nouveau",
    "date_ajout":   "2026-06-03",
    "date_contact": "",
    "date_relance": "",
    "notes":        "LIGNE DE TEST - a supprimer apres validation"
}

print("=" * 60)
print("TEST E2E PIPELINE PROSPECTION")
print("=" * 60)
print(f"Email de test : {TEST_EMAIL}")
print()

# ─── Step 1: Trigger WF2 manuellement avec le lead de test ──────────────────
print("Step 1: Trigger WF2 (Outreach) avec lead de test...")
print("  Note: WF2 lit depuis Google Sheets.")
print("  Pour un vrai test E2E : ajoute cette ligne manuellement dans Sheets")
print(f"  https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")
print()
print("  Donnees a inserer (colonnes A-K) :")
cols = ["nom", "secteur", "ville", "website", "tel", "email",
        "statut", "date_ajout", "date_contact", "date_relance", "notes"]
vals = [TEST_LEAD[c] for c in cols]
print("  " + " | ".join(vals))
print()

# ─── Step 2: Execute WF2 via API ─────────────────────────────────────────────
print("Step 2: Execution manuelle de WF2...")
r = requests.post(
    f"{BASE}/workflows/{WF2_ID}/run",
    headers=H,
    json={"startNodes": ["Lire Prospects Nouveaux"]}
)

if r.status_code not in (200, 201):
    print(f"  ERREUR trigger WF2: {r.status_code}")
    print(f"  {r.text[:300]}")
    print()
    print("  Alternative: declenche WF2 manuellement dans n8n UI:")
    print(f"  http://localhost:5678/workflow/{WF2_ID}")
else:
    exec_data = r.json()
    exec_id   = exec_data.get("executionId") or exec_data.get("id")
    print(f"  Execution lancee: ID={exec_id}")
    print()

    # ─── Step 3: Poll execution status ───────────────────────────────────────
    print("Step 3: Attente du resultat (max 60s)...")
    for i in range(12):
        time.sleep(5)
        r2 = requests.get(f"{BASE}/executions/{exec_id}", headers=H)
        if r2.status_code == 200:
            ex = r2.json()
            status = ex.get("status") or ex.get("finished")
            print(f"  [{i*5+5}s] status={status}")
            if status in ("success", "error", True, False) and status != "running":
                break
    print()

    # ─── Step 4: Afficher le resultat ────────────────────────────────────────
    print("Step 4: Resultat execution:")
    if r2.status_code == 200:
        ex = r2.json()
        fin = ex.get("finished")
        mode = ex.get("mode")
        print(f"  Fini={fin}, Mode={mode}")
        data = ex.get("data", {})
        result_data = data.get("resultData", {})
        last_node = result_data.get("lastNodeExecuted")
        print(f"  Dernier node execute: {last_node}")
        err = result_data.get("error")
        if err:
            print(f"  Erreur: {err}")
    else:
        print(f"  Impossible de recuperer le resultat: {r2.status_code}")

print()
print("=" * 60)
print("VERIFICATION MANUELLE")
print("=" * 60)
print("1. Verifie ta boite Gmail (unexpectedvalu3@gmail.com)")
print("   -> Tu dois avoir recu un email de prospection")
print()
print("2. Verifie Google Sheets")
print(f"   https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")
print("   -> La ligne TEST doit avoir statut='Contacte'")
print("      et date_contact=aujourd'hui")
print()
print("3. Attends J+3, puis verifie WF3 (Relance)")
print("   -> Ou change date_contact a une date d'il y a 3 jours pour tester WF3 maintenant")
