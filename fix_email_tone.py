# -*- coding: utf-8 -*-
"""
Patch WF2 'Construire Prompt Claude' + WF3 'Construire Relance' :
- Emails formels avec "Bonjour,"
- Signature "Cordialement,\nEnzo — AI Installator"
- Ton pro courtois (pas familier, pas vendeur criard)
"""
import json, requests

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NGQ5YjQ1NC05ZTZhLTQ3NmQtYTczMi1hNWNiYzFkNzAxOTIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZTQ2MmY4MzEtMDJhNS00YjU5LWE4MzctMGJhZmNkYjRmMTljIiwiaWF0IjoxNzgwNDkzMTM3LCJleHAiOjE3ODMwNTEyMDB9.jaAktbuoPW6IIAkm-sUdLQp3wDrSbhlpTM3JPkyFFQc"
BASE = "http://localhost:5678/api/v1"
H = {"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"}

# ─── WF2 : nouveau prompt Claude (email formel) ──────────────────────────────
WF2_PROMPT_CODE = r'''const hooks = {
  "comptable":          "Vos assistants saisissent encore des factures PDF manuellement ?",
  "kiné":               "Vous perdez du temps à rappeler les patients qui ne répondent pas ?",
  "ostéopathe":         "Vous perdez du temps à rappeler les patients qui ne répondent pas ?",
  "plombier":           "Vous faites encore vos devis à la main ?",
  "agence immobilière": "Votre reporting de la semaine se fait encore dans Excel ?",
  "default":            "Vous avez des tâches répétitives qui pourraient être automatisées ?"
};
const row = $input.first().json;
const secteur = (row.secteur || 'default').toLowerCase();
const hook = hooks[secteur] || hooks["default"];
const nom = row.nom || "";

const prompt = `Tu es Enzo, consultant en automatisation IA pour PME françaises (AI Installator).
Rédige un email de prospection professionnel et courtois pour ${nom}, un(e) ${secteur}.

Hook d'accroche : "${hook}"

Règles STRICTES :
- Commence TOUJOURS par "Bonjour,"
- 6 lignes maximum (corps uniquement, sans compter la signature)
- Objet : accrocheur, personnalisé au secteur, sans point d'exclamation
- Corps :
    1. "Bonjour,"
    2. Hook ou question d'accroche (une phrase)
    3. Preuve sociale courte (ex : "J'ai aidé un cabinet de 4 personnes à économiser 8h/semaine")
    4. CTA : proposition d'un échange de 20 minutes, gratuit et sans engagement
- Termine par la signature exacte : "Cordialement,\nEnzo — AI Installator"
- Ton : professionnel, direct, courtois — jamais familier, jamais criard
- PAS de lorem ipsum, PAS de mots entre [crochets]

Retourne UNIQUEMENT un JSON valide avec exactement ces 2 clés :
{"objet": "...", "corps": "..."}
Le champ "corps" doit inclure "Bonjour," au début et "Cordialement,\nEnzo — AI Installator" à la fin.`;

return [{ json: { prompt, nom: row.nom, secteur: row.secteur, row_index: row.row_index } }];'''

# ─── WF3 : relance formelle ──────────────────────────────────────────────────
WF3_RELANCE_CODE = r'''const row = $input.first().json;
const nom = row.nom || '';
const secteur = row.secteur || '';

const corps = `Bonjour,

Je me permets de revenir vers vous suite à mon message de la semaine dernière.

De nombreux professionnels du secteur ${secteur} que j'accompagne ne réalisent le temps perdu sur des tâches répétitives qu'après une démonstration concrète sur leurs propres documents.

Je vous propose un échange de 20 minutes, sans engagement et entièrement gratuit, pour vous montrer ce qui est automatisable dans votre activité.

Seriez-vous disponible cette semaine ?

Cordialement,
Enzo — AI Installator`;

return [{ json: {
  objet:      `Suite à mon précédent message — automatisation pour votre cabinet ${secteur}`,
  corps,
  email_dest: row.email || '',
  nom,
  secteur,
  row_index:  row.row_index
}}];'''

def patch_node_code(wf_id, node_name, new_code):
    r = requests.get(f"{BASE}/workflows/{wf_id}", headers=H)
    r.raise_for_status()
    wf = r.json()

    found = False
    for n in wf["nodes"]:
        if n["name"] == node_name:
            n["parameters"]["jsCode"] = new_code
            found = True
            print(f"  Patched: {node_name}")

    if not found:
        print(f"  ⚠ Node '{node_name}' non trouvé dans {wf['name']}")
        return

    payload = {
        "name": wf["name"],
        "nodes": wf["nodes"],
        "connections": wf["connections"],
        "settings": wf.get("settings", {}),
        "staticData": wf.get("staticData")
    }
    r2 = requests.put(f"{BASE}/workflows/{wf_id}", headers=H, json=payload)
    print(f"  PUT {r2.status_code} — {wf['name']}")
    if r2.status_code not in (200, 201):
        print(f"  Erreur: {r2.text[:200]}")

print("=== WF2 — Patch prompt email formel ===")
patch_node_code("CQcPR4kIgxRoidGY", "Construire Prompt Claude", WF2_PROMPT_CODE)

print("\n=== WF3 — Patch relance formelle ===")
patch_node_code("HT0tzw9eFpnuwwnL", "Construire Relance", WF3_RELANCE_CODE)

print("\nDone.")
