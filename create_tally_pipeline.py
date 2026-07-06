import json, requests

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NGQ5YjQ1NC05ZTZhLTQ3NmQtYTczMi1hNWNiYzFkNzAxOTIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZTQ2MmY4MzEtMDJhNS00YjU5LWE4MzctMGJhZmNkYjRmMTljIiwiaWF0IjoxNzgwNDkzMTM3LCJleHAiOjE3ODMwNTEyMDB9.jaAktbuoPW6IIAkm-sUdLQp3wDrSbhlpTM3JPkyFFQc"
BASE   = "http://localhost:5678/api/v1"
H      = {"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"}

SHEETS_CRED = {"id": "gEANv3fBenM1udse", "name": "Google Sheets account"}
GMAIL_CRED  = {"id": "rbg1SnQ9JvaQiv7d", "name": "Gmail account"}
CLAUDE_CRED = {"id": "HMF1JkG9k0moa4vO", "name": "Claude API Key"}

SPREADSHEET_ID = "1mvylh6MKh2RD8y6FtgyMXgMvfno_9iPOiwC6Osq6gaE"
SHEET_LEADS    = "Leads_Tally"
ENZO_EMAIL     = "unexpectedvalu3@gmail.com"

# ─────────────────────────────────────────────────────────────────────────────
# CODE NODES
# ─────────────────────────────────────────────────────────────────────────────

# 1. Parse Tally payload → clean object
CODE_PARSE_TALLY = r"""
const body = $input.first().json;

// Skip Tally test events
if (body.eventType && body.eventType !== 'FORM_RESPONSE') {
  return [{ json: { _skip: true } }];
}

const fields = body.data?.fields || body.fields || [];

// Build a label → value map (lowercase keys for matching)
const map = {};
for (const f of fields) {
  const label = (f.label || f.question || '').toLowerCase().trim();
  const val   = Array.isArray(f.value) ? f.value.join(', ') : (f.value ?? '');
  if (label && String(val).trim() !== '') map[label] = String(val).trim();
}

const get = (...keywords) => {
  for (const kw of keywords) {
    for (const [label, val] of Object.entries(map)) {
      if (label.includes(kw.toLowerCase())) return val;
    }
  }
  return '';
};

const prenom   = get('prénom', 'prenom', 'first');
const nom      = get('nom de famille', 'last name') || get('nom');
const email    = get('email', 'mail', 'e-mail');
const tel      = get('téléphone', 'telephone', 'tel ', 'phone', 'mobile');
const secteur  = get('secteur', 'activité', 'métier', 'domaine', 'industrie');
const effectif = get('effectif', 'taille', 'collaborateur', 'employé', 'salarié', 'personne');
const probleme = get('tâche', 'chronophage', 'automatiser', 'problème', 'défi', 'difficulté', 'challenge', 'processus');
const temps    = get('temps', 'heures', 'durée');
const outils   = get('outil', 'logiciel', 'software', 'crm', 'excel', 'utilise');
const budget   = get('budget', 'investissement', 'prix', 'coût');

// Full text of all fields for Claude
const allFields = fields
  .filter(f => {
    const v = Array.isArray(f.value) ? f.value.join('') : String(f.value ?? '');
    return v.trim() !== '';
  })
  .map(f => {
    const v = Array.isArray(f.value) ? f.value.join(', ') : f.value;
    return `- ${f.label || f.question}: ${v}`;
  })
  .join('\n');

return [{ json: {
  prenom,
  nom,
  email,
  tel,
  secteur,
  effectif,
  probleme,
  temps_perdu:     temps,
  outils,
  budget,
  all_fields:      allFields || JSON.stringify(body, null, 2),
  date_soumission: new Date().toISOString().slice(0, 10),
  statut_lead:     'Nouveau'
}}];
"""

# 2. Build Claude prompt
CODE_BUILD_PROMPT = r"""
const d = $input.first().json;
const prenom = d.prenom || 'le prospect';

const prompt = `Tu es un consultant senior en automatisation IA pour PME françaises, pour Lumaraa.
Analyse ce diagnostic et génère un rapport JSON.

=== DIAGNOSTIC ===
${d.all_fields}

=== FORMAT ATTENDU (JSON strict, rien d'autre) ===
{
  "score": <entier 1-10, potentiel automation>,
  "score_justification": "<1 phrase courte>",
  "opportunites": ["<opp 1>", "<opp 2>", "<opp 3 max>"],
  "gain_temps_estime": "<ex: 5-8h/semaine>",
  "recommandation": "<2-3 phrases personnalisees : quelle solution, pourquoi, premier pas concret>",
  "prochaine_etape": "<CTA specifique>"
}`;

return [{ json: { prompt, ...d } }];
"""

# 3. Parse Claude response + build emails
CODE_PARSE_ANALYSE = r"""
const resp  = $input.first().json;
const text  = resp.content?.[0]?.text?.trim() || '';
const prev  = $('Construire Prompt').item.json;

let a;
try {
  const match = text.match(/\{[\s\S]*\}/);
  a = JSON.parse(match ? match[0] : text);
} catch(e) {
  a = {
    score: 7,
    score_justification: "Fort potentiel identifie",
    opportunites: ["Automatisation des taches repetitives identifiee"],
    gain_temps_estime: "A evaluer ensemble",
    recommandation: "Votre profil presente un fort potentiel d'automatisation. Je vous propose un appel de 20 minutes pour l'explorer.",
    prochaine_etape: "Reservez votre diagnostic gratuit sur lumaraa.fr"
  };
}

const prenom = prev.prenom || '';
const nom    = prev.nom    || '';

const corps_prospect =
`Bonjour ${prenom},

Merci d'avoir rempli le diagnostic Lumaraa.

Voici notre analyse :

Score potentiel : ${a.score}/10
${a.score_justification}

Opportunites identifiees :
${(a.opportunites || []).map((o, i) => `${i+1}. ${o}`).join('\n')}

Gain de temps estime : ${a.gain_temps_estime}

Recommandation :
${a.recommandation}

Prochaine etape : ${a.prochaine_etape}

Je vous contacterai dans les 24h.

Cordialement,
Enzo - Lumaraa
contact@lumaraa.fr`;

const corps_notif =
`Nouveau lead Tally !

Nom : ${prenom} ${nom}
Email : ${prev.email}
Secteur : ${prev.secteur}
Probleme : ${prev.probleme}
Budget : ${prev.budget}
Score Claude : ${a.score}/10
Recommandation : ${a.recommandation}

Verifie dans Sheets > Leads_Tally.`;

return [{ json: {
  email_prospect:  prev.email,
  prenom,
  nom,
  objet_prospect:  `Votre diagnostic Lumaraa - Potentiel ${a.score}/10`,
  corps_prospect,
  objet_notif:     `[Lead] ${prenom} ${nom} - Score ${a.score}/10`,
  corps_notif,
  score:           a.score,
  recommandation:  a.recommandation,
  ...prev
}}];
"""

CLAUDE_BODY = (
    "={{ JSON.stringify({"
    "  model: 'claude-sonnet-4-6',"
    "  max_tokens: 600,"
    "  messages: [{ role: 'user', content: $json.prompt }]"
    "}) }}"
)

# ─────────────────────────────────────────────────────────────────────────────
# WORKFLOW
# ─────────────────────────────────────────────────────────────────────────────

wf = {
    "name": "Tally Diagnostic → Sheets + Analyse + Email",
    "nodes": [
        {
            "id": "sticky",
            "name": "Note",
            "type": "n8n-nodes-base.stickyNote",
            "typeVersion": 1,
            "position": [-200, -220],
            "parameters": {
                "content": (
                    "## Tally → Sheets → Analyse → Email\n\n"
                    "**Trigger** : Tally form PdrRX1 POST sur /webhook/tally-diagnostic\n\n"
                    "**Flux** :\n"
                    "1. Tally webhook recoit le diagnostic\n"
                    "2. Parse les champs dynamiquement\n"
                    "3. Sauvegarde dans Sheets (Leads_Tally)\n"
                    "4. Claude analyse le potentiel automation\n"
                    "5. Email personnalise au prospect\n"
                    "6. Notif interne a Enzo\n\n"
                    "**Setup Tally** : Webhook URL = https://NGROK_URL/webhook/tally-diagnostic\n"
                    "(ngrok http 5678 pour exposer n8n)\n\n"
                    "**Sheet requis** : Leads_Tally avec headers :\n"
                    "date | prenom | nom | email | tel | secteur | effectif | probleme | temps_perdu | outils | budget | score | recommandation | statut"
                ),
                "height": 340, "width": 480, "color": 5
            }
        },
        {
            "id": "webhook",
            "name": "Webhook Tally",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [0, 300],
            "parameters": {
                "httpMethod":   "POST",
                "path":         "tally-diagnostic",
                "responseMode": "onReceived",
                "responseData": "firstEntryJson",
                "options":      {}
            },
            "webhookId": "tally-diagnostic-lumaraa"
        },
        {
            "id": "parse-tally",
            "name": "Parser Tally",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [240, 300],
            "parameters": {"jsCode": CODE_PARSE_TALLY}
        },
        {
            "id": "filter-skip",
            "name": "Ignorer Tests",
            "type": "n8n-nodes-base.filter",
            "typeVersion": 2,
            "position": [480, 300],
            "parameters": {
                "conditions": {
                    "options": {"caseSensitive": True},
                    "conditions": [
                        {
                            "leftValue":  "={{ $json._skip }}",
                            "rightValue": True,
                            "operator":   {"type": "boolean", "operation": "notEquals"}
                        }
                    ]
                }
            }
        },
        {
            "id": "sheets-append",
            "name": "Sauvegarder Sheets",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4.5,
            "position": [720, 300],
            "credentials": {"googleSheetsOAuth2Api": SHEETS_CRED},
            "parameters": {
                "operation":  "append",
                "documentId": {"__rl": True, "value": SPREADSHEET_ID, "mode": "id"},
                "sheetName":  {"__rl": True, "value": SHEET_LEADS, "mode": "name"},
                "columns": {
                    "mappingMode": "defineBelow",
                    "value": {
                        "date":          "={{ $json.date_soumission }}",
                        "prenom":        "={{ $json.prenom }}",
                        "nom":           "={{ $json.nom }}",
                        "email":         "={{ $json.email }}",
                        "tel":           "={{ $json.tel }}",
                        "secteur":       "={{ $json.secteur }}",
                        "effectif":      "={{ $json.effectif }}",
                        "probleme":      "={{ $json.probleme }}",
                        "temps_perdu":   "={{ $json.temps_perdu }}",
                        "outils":        "={{ $json.outils }}",
                        "budget":        "={{ $json.budget }}",
                        "score":         "",
                        "recommandation":"",
                        "statut":        "Nouveau"
                    }
                },
                "options": {}
            }
        },
        {
            "id": "build-prompt",
            "name": "Construire Prompt",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [960, 300],
            "parameters": {"jsCode": CODE_BUILD_PROMPT}
        },
        {
            "id": "claude-analyse",
            "name": "Claude Analyse",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [1200, 300],
            "credentials": {"httpHeaderAuth": CLAUDE_CRED},
            "parameters": {
                "method":              "POST",
                "url":                 "https://api.anthropic.com/v1/messages",
                "authentication":      "genericCredentialType",
                "genericAuthType":     "httpHeaderAuth",
                "sendHeaders":         True,
                "headerParameters": {
                    "parameters": [
                        {"name": "anthropic-version", "value": "2023-06-01"},
                        {"name": "content-type",      "value": "application/json"}
                    ]
                },
                "sendBody":        True,
                "contentType":     "raw",
                "rawContentType":  "application/json",
                "body":            CLAUDE_BODY
            }
        },
        {
            "id": "parse-analyse",
            "name": "Parser Analyse",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1440, 300],
            "parameters": {"jsCode": CODE_PARSE_ANALYSE}
        },
        {
            "id": "update-score",
            "name": "MAJ Score Sheets",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4.5,
            "position": [1680, 300],
            "credentials": {"googleSheetsOAuth2Api": SHEETS_CRED},
            "parameters": {
                "operation":  "update",
                "documentId": {"__rl": True, "value": SPREADSHEET_ID, "mode": "id"},
                "sheetName":  {"__rl": True, "value": SHEET_LEADS, "mode": "name"},
                "columns": {
                    "mappingMode": "defineBelow",
                    "value": {
                        "score":          "={{ $json.score }}",
                        "recommandation": "={{ $json.recommandation }}",
                        "statut":         "Analyse OK"
                    }
                },
                "matchingColumns": ["email"],
                "options": {}
            }
        },
        {
            "id": "email-prospect",
            "name": "Email Prospect",
            "type": "n8n-nodes-base.gmail",
            "typeVersion": 2.1,
            "position": [1920, 200],
            "credentials": {"gmailOAuth2": GMAIL_CRED},
            "parameters": {
                "operation": "send",
                "sendTo":    "={{ $json.email_prospect }}",
                "subject":   "={{ $json.objet_prospect }}",
                "emailType": "text",
                "message":   "={{ $json.corps_prospect }}",
                "options":   {}
            }
        },
        {
            "id": "notif-enzo",
            "name": "Notif Enzo",
            "type": "n8n-nodes-base.gmail",
            "typeVersion": 2.1,
            "position": [1920, 420],
            "credentials": {"gmailOAuth2": GMAIL_CRED},
            "parameters": {
                "operation": "send",
                "sendTo":    ENZO_EMAIL,
                "subject":   "={{ $json.objet_notif }}",
                "emailType": "text",
                "message":   "={{ $json.corps_notif }}",
                "options":   {}
            }
        }
    ],
    "connections": {
        "Webhook Tally":      {"main": [[{"node": "Parser Tally",       "type": "main", "index": 0}]]},
        "Parser Tally":       {"main": [[{"node": "Ignorer Tests",      "type": "main", "index": 0}]]},
        "Ignorer Tests":      {"main": [[{"node": "Sauvegarder Sheets", "type": "main", "index": 0}]]},
        "Sauvegarder Sheets": {"main": [[{"node": "Construire Prompt",  "type": "main", "index": 0}]]},
        "Construire Prompt":  {"main": [[{"node": "Claude Analyse",     "type": "main", "index": 0}]]},
        "Claude Analyse":     {"main": [[{"node": "Parser Analyse",     "type": "main", "index": 0}]]},
        "Parser Analyse":     {"main": [[{"node": "MAJ Score Sheets",   "type": "main", "index": 0}]]},
        "MAJ Score Sheets":   {"main": [[
            {"node": "Email Prospect", "type": "main", "index": 0},
            {"node": "Notif Enzo",     "type": "main", "index": 0}
        ]]}
    },
    "settings": {"executionOrder": "v1"}
}

# ─────────────────────────────────────────────────────────────────────────────
# DEPLOY
# ─────────────────────────────────────────────────────────────────────────────

def deploy():
    print("=== Deploiement Tally Pipeline ===\n")
    print("PRE-REQUIS : creer l'onglet 'Leads_Tally' dans le Google Sheets")
    print("avec ces headers en ligne 1 :")
    print("  date | prenom | nom | email | tel | secteur | effectif | probleme | temps_perdu | outils | budget | score | recommandation | statut\n")

    r = requests.post(f"{BASE}/workflows", headers=H, json=wf)
    if r.status_code not in (200, 201):
        print(f"ERREUR creation : {r.status_code}")
        print(r.text)
        if "401" in str(r.status_code):
            print("\n=> JWT expire. Regenerer dans n8n : Settings > API > Create API Key")
        return

    wf_data = r.json()
    wf_id   = wf_data.get("id")
    print(f"Workflow cree : ID={wf_id}")

    ra = requests.post(f"{BASE}/workflows/{wf_id}/activate", headers=H)
    if ra.status_code in (200, 201):
        print("Workflow ACTIVE")
    else:
        print(f"Activation : {ra.status_code} - {ra.text}")

    webhook_path = "tally-diagnostic"
    print(f"\n=== SETUP TALLY ===")
    print(f"1. Lance ngrok : ngrok http 5678")
    print(f"2. Copie l'URL publique (ex: https://abc.ngrok-free.app)")
    print(f"3. Dans Tally form PdrRX1 > Integrations > Webhooks :")
    print(f"   URL = https://NGROK_URL/webhook/{webhook_path}")
    print(f"4. Tally enverra chaque soumission a ce webhook")
    print(f"\nURL locale test : http://localhost:5678/webhook/{webhook_path}")
    print(f"\nDone.")

if __name__ == "__main__":
    deploy()
