import json, requests

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NGQ5YjQ1NC05ZTZhLTQ3NmQtYTczMi1hNWNiYzFkNzAxOTIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZTQ2MmY4MzEtMDJhNS00YjU5LWE4MzctMGJhZmNkYjRmMTljIiwiaWF0IjoxNzgwNDkzMTM3LCJleHAiOjE3ODMwNTEyMDB9.jaAktbuoPW6IIAkm-sUdLQp3wDrSbhlpTM3JPkyFFQc"
BASE = "http://localhost:5678/api/v1"
H = {"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"}

GOOGLE_CRED  = {"id": "kCwgGnro1O8CvMjK", "name": "Google account"}
CLAUDE_CRED  = {"id": "HMF1JkG9k0moa4vO", "name": "Claude API Key"}
SERP_CRED    = {"id": "KO2v33eh3eV4wL1l", "name": "SerpAPI Key"}

# ── IMPORTANT : remplace par l'ID de ton Google Spreadsheet ──────────────────
# Crée un Sheets vide sur drive.google.com, copie l'ID dans l'URL
# Ex: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
SPREADSHEET_ID = "1mvylh6MKh2RD8y6FtgyMXgMvfno_9iPOiwC6Osq6gaE"
SHEET_NAME = "Prospects"

# ─────────────────────────────────────────────────────────────────────────────
# CODE NODES
# ─────────────────────────────────────────────────────────────────────────────

# WF1 — Lead Gen
CODE_GENERATE_QUERIES = r"""
const secteurs = [
  { secteur: "comptable", ville: "Paris", hook: "Vos assistants saisissent encore des factures PDF manuellement ?" },
  { secteur: "kiné",      ville: "Paris", hook: "Vous perdez du temps à rappeler les patients qui ne répondent pas ?" },
  { secteur: "plombier",  ville: "Paris", hook: "Vous faites encore vos devis à la main ?" },
  { secteur: "ostéopathe",ville: "Paris", hook: "Vous perdez du temps à rappeler les patients qui ne répondent pas ?" },
  { secteur: "agence immobilière", ville: "Paris", hook: "Votre reporting de la semaine se fait encore dans Excel ?" }
];
return secteurs.map(s => ({
  json: { query: s.secteur + " " + s.ville, secteur: s.secteur, ville: s.ville, hook: s.hook }
}));
"""

CODE_PARSE_LEADS = r"""
const items = $input.all();
const leads = [];
for (const item of items) {
  const results = item.json.local_results || item.json.organic_results || [];
  const secteur = item.json.search_parameters?.q?.split(' ')[0] || 'inconnu';
  for (const r of results.slice(0, 5)) {
    const email = r.website ? r.website.replace(/https?:\/\/(www\.)?/, '').split('/')[0] : null;
    leads.push({
      json: {
        nom:      r.title || r.name || 'Inconnu',
        secteur:  secteur,
        ville:    r.address || '',
        website:  r.website || r.link || '',
        tel:      r.phone || '',
        email:    '',
        statut:   'Nouveau',
        date_ajout: new Date().toISOString().slice(0, 10),
        date_contact: '',
        date_relance: '',
        notes:    ''
      }
    });
  }
}
return leads.length > 0 ? leads : [{ json: { _skip: true } }];
"""

# WF2 — Outreach
CODE_BUILD_EMAIL = r"""
const hooks = {
  "comptable":          "Vos assistants saisissent encore des factures PDF manuellement ?",
  "kiné":               "Vous perdez du temps à rappeler les patients qui ne répondent pas ?",
  "ostéopathe":         "Vous perdez du temps à rappeler les patients qui ne répondent pas ?",
  "plombier":           "Vous faites encore vos devis à la main ?",
  "agence immobilière": "Votre reporting de la semaine se fait encore dans Excel ?",
  "default":            "Vous avez des tâches répétitives qui pourraient être automatisées ?"
};
const row = $input.first().json;
const secteur = (row.secteur || 'default').toLowerCase();
const hook = hooks[secteur] || hooks['default'];
const nom = row.nom || 'là';
const prompt = `Tu es Enzo, consultant en automatisation IA pour PME françaises (AI Installator).
Rédige un email froid court et percutant pour prospecter ${nom}, un(e) ${secteur}.

Hook d'accroche : "${hook}"

Règles STRICTES :
- 5 lignes maximum
- Objet : accrocheur, personnalisé au secteur
- Corps : hook → preuve sociale courte (ex: "j'ai aidé un cabinet de 4 personnes à économiser 8h/semaine") → CTA (20 min, gratuit, sans engagement)
- Signature : Enzo — AI Installator
- Ton : direct, pro, pas vendeur
- PAS de lorem ipsum, PAS de placeholders entre crochets

Retourne UNIQUEMENT un JSON avec exactement ces 2 clés :
{"objet": "...", "corps": "..."}`;
return [{ json: { prompt, nom: row.nom, secteur: row.secteur, row_index: row.row_index } }];
"""

CODE_PARSE_EMAIL = r"""
const resp = $input.first().json;
const text = resp.content[0].text.trim();
let parsed;
try {
  const match = text.match(/\{[\s\S]*\}/);
  parsed = JSON.parse(match ? match[0] : text);
} catch(e) {
  parsed = { objet: "Automatiser vos tâches répétitives ?", corps: text };
}
const prev = $('Lire Prospects Nouveaux').item.json;
return [{ json: {
  objet:      parsed.objet,
  corps:      parsed.corps,
  nom:        prev.nom,
  secteur:    prev.secteur,
  email_dest: prev.email || '',
  row_index:  prev.row_index
}}];
"""

CODE_CLAUDE_BODY_OUTREACH = (
    "={{ JSON.stringify({"
    "  model: 'claude-sonnet-4-6',"
    "  max_tokens: 500,"
    "  messages: [{ role: 'user', content: $json.prompt }]"
    "}) }}"
)

# WF3 — Relance J+3
CODE_CHECK_RELANCE = r"""
const items = $input.all();
const today = new Date();
const toRelance = [];
for (const item of items) {
  const row = item.json;
  if (row.statut !== 'Contacté') continue;
  if (!row.date_contact) continue;
  const dc = new Date(row.date_contact);
  const diffDays = Math.floor((today - dc) / (1000 * 60 * 60 * 24));
  if (diffDays >= 3) {
    toRelance.push({ json: { ...row } });
  }
}
return toRelance.length > 0 ? toRelance : [{ json: { _skip: true } }];
"""

CODE_BUILD_RELANCE = r"""
const row = $input.first().json;
const nom = row.nom || '';
const secteur = row.secteur || '';
const corps = `Bonjour,\n\nJe me permets de revenir vers vous suite à mon email de la semaine dernière.\n\nBeaucoup de ${secteur}s que j'accompagne ne réalisent pas le temps qu'ils perdent sur des tâches répétitives — jusqu'à ce qu'on leur montre en live.\n\nJe peux vous faire une démo de 20 minutes, gratuite et sans engagement, sur un de vos vrais documents.\n\nVous avez un créneau cette semaine ?\n\nEnzo — AI Installator`;
return [{ json: {
  objet:      `Relance — automatisation pour ${secteur}`,
  corps,
  email_dest: row.email || '',
  nom,
  secteur,
  row_index:  row.row_index
}}];
"""

# ─────────────────────────────────────────────────────────────────────────────
# WORKFLOW 1 — LEAD GENERATION
# ─────────────────────────────────────────────────────────────────────────────

wf1 = {
    "name": "Prospection #1 — Lead Generation",
    "nodes": [
        {
            "id": "sticky-1",
            "name": "Note",
            "type": "n8n-nodes-base.stickyNote",
            "typeVersion": 1,
            "position": [-200, -200],
            "parameters": {
                "content": "## Prospection #1 — Lead Generation\n\n**Tourne chaque matin à 8h**\n\nScrape Google Maps via SerpAPI → filtre → ajoute dans Google Sheets\n\n⚠️ Remplace `SPREADSHEET_ID` dans le node Google Sheets",
                "height": 200, "width": 380, "color": 4
            }
        },
        {
            "id": "schedule-1",
            "name": "Chaque Matin 8h",
            "type": "n8n-nodes-base.scheduleTrigger",
            "typeVersion": 1.2,
            "position": [0, 300],
            "parameters": {
                "rule": {
                    "interval": [{"field": "hours", "hoursInterval": 24, "triggerAtHour": 8}]
                }
            }
        },
        {
            "id": "gen-queries",
            "name": "Générer Queries Secteurs",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [240, 300],
            "parameters": {"jsCode": CODE_GENERATE_QUERIES}
        },
        {
            "id": "serp-search",
            "name": "SerpAPI Google Maps",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [480, 300],
            "credentials": {"httpQueryAuth": SERP_CRED},
            "parameters": {
                "method": "GET",
                "url": "https://serpapi.com/search.json",
                "authentication": "genericCredentialType",
                "genericAuthType": "httpQueryAuth",
                "sendQuery": True,
                "queryParameters": {
                    "parameters": [
                        {"name": "engine", "value": "google_maps"},
                        {"name": "q",      "value": "={{ $json.query }}"},
                        {"name": "hl",     "value": "fr"},
                        {"name": "gl",     "value": "fr"}
                    ]
                }
            }
        },
        {
            "id": "parse-leads",
            "name": "Parser Leads",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [720, 300],
            "parameters": {"jsCode": CODE_PARSE_LEADS}
        },
        {
            "id": "filter-skip",
            "name": "Filtrer Vides",
            "type": "n8n-nodes-base.filter",
            "typeVersion": 2,
            "position": [960, 300],
            "parameters": {
                "conditions": {
                    "options": {"caseSensitive": True},
                    "conditions": [
                        {
                            "leftValue": "={{ $json._skip }}",
                            "rightValue": True,
                            "operator": {"type": "boolean", "operation": "notEquals"}
                        }
                    ]
                }
            }
        },
        {
            "id": "append-sheets",
            "name": "Ajouter dans Sheets",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4.5,
            "position": [1200, 300],
            "credentials": {"googleOAuth2Api": GOOGLE_CRED},
            "parameters": {
                "operation": "append",
                "documentId": {"__rl": True, "value": SPREADSHEET_ID, "mode": "id"},
                "sheetName": {"__rl": True, "value": SHEET_NAME, "mode": "name"},
                "columns": {
                    "mappingMode": "defineBelow",
                    "value": {
                        "nom":          "={{ $json.nom }}",
                        "secteur":      "={{ $json.secteur }}",
                        "ville":        "={{ $json.ville }}",
                        "website":      "={{ $json.website }}",
                        "tel":          "={{ $json.tel }}",
                        "email":        "={{ $json.email }}",
                        "statut":       "={{ $json.statut }}",
                        "date_ajout":   "={{ $json.date_ajout }}",
                        "date_contact": "",
                        "date_relance": "",
                        "notes":        ""
                    }
                },
                "options": {}
            }
        }
    ],
    "connections": {
        "Chaque Matin 8h":          {"main": [[{"node": "Générer Queries Secteurs", "type": "main", "index": 0}]]},
        "Générer Queries Secteurs": {"main": [[{"node": "SerpAPI Google Maps",      "type": "main", "index": 0}]]},
        "SerpAPI Google Maps":      {"main": [[{"node": "Parser Leads",             "type": "main", "index": 0}]]},
        "Parser Leads":             {"main": [[{"node": "Filtrer Vides",            "type": "main", "index": 0}]]},
        "Filtrer Vides":            {"main": [[{"node": "Ajouter dans Sheets",      "type": "main", "index": 0}]]}
    },
    "settings": {"executionOrder": "v1"}
}

# ─────────────────────────────────────────────────────────────────────────────
# WORKFLOW 2 — OUTREACH
# ─────────────────────────────────────────────────────────────────────────────

wf2 = {
    "name": "Prospection #2 — Outreach Email",
    "nodes": [
        {
            "id": "sticky-2",
            "name": "Note",
            "type": "n8n-nodes-base.stickyNote",
            "typeVersion": 1,
            "position": [-200, -200],
            "parameters": {
                "content": "## Prospection #2 — Outreach\n\n**Tourne chaque matin à 10h**\n\nLit les prospects 'Nouveau' dans Sheets → Claude génère email personnalisé → Gmail envoie → met à jour statut\n\n⚠️ Ajoute les emails dans la colonne `email` du Sheets avant l'envoi",
                "height": 220, "width": 420, "color": 3
            }
        },
        {
            "id": "schedule-2",
            "name": "Chaque Matin 10h",
            "type": "n8n-nodes-base.scheduleTrigger",
            "typeVersion": 1.2,
            "position": [0, 300],
            "parameters": {
                "rule": {
                    "interval": [{"field": "hours", "hoursInterval": 24, "triggerAtHour": 10}]
                }
            }
        },
        {
            "id": "read-prospects",
            "name": "Lire Prospects Nouveaux",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4.5,
            "position": [240, 300],
            "credentials": {"googleOAuth2Api": GOOGLE_CRED},
            "parameters": {
                "operation": "readRows",
                "documentId": {"__rl": True, "value": SPREADSHEET_ID, "mode": "id"},
                "sheetName": {"__rl": True, "value": SHEET_NAME, "mode": "name"},
                "filtersUI": {
                    "values": [
                        {"lookupColumn": "statut", "lookupValue": "Nouveau"}
                    ]
                },
                "options": {}
            }
        },
        {
            "id": "filter-email",
            "name": "Filtrer Avec Email",
            "type": "n8n-nodes-base.filter",
            "typeVersion": 2,
            "position": [480, 300],
            "parameters": {
                "conditions": {
                    "options": {"caseSensitive": True},
                    "conditions": [
                        {
                            "leftValue": "={{ $json.email }}",
                            "rightValue": "",
                            "operator": {"type": "string", "operation": "notEmpty"}
                        }
                    ]
                }
            }
        },
        {
            "id": "build-prompt",
            "name": "Construire Prompt Claude",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [720, 300],
            "parameters": {"jsCode": CODE_BUILD_EMAIL}
        },
        {
            "id": "claude-outreach",
            "name": "Claude Génère Email",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [960, 300],
            "credentials": {"httpHeaderAuth": CLAUDE_CRED},
            "parameters": {
                "method": "POST",
                "url": "https://api.anthropic.com/v1/messages",
                "authentication": "genericCredentialType",
                "genericAuthType": "httpHeaderAuth",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {"name": "anthropic-version", "value": "2023-06-01"},
                        {"name": "content-type",      "value": "application/json"}
                    ]
                },
                "sendBody": True,
                "contentType": "raw",
                "rawContentType": "application/json",
                "body": CODE_CLAUDE_BODY_OUTREACH
            }
        },
        {
            "id": "parse-email-resp",
            "name": "Parser Réponse Claude",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1200, 300],
            "parameters": {"jsCode": CODE_PARSE_EMAIL}
        },
        {
            "id": "send-gmail",
            "name": "Envoyer Email Gmail",
            "type": "n8n-nodes-base.gmail",
            "typeVersion": 2.1,
            "position": [1440, 300],
            "credentials": {"googleOAuth2Api": GOOGLE_CRED},
            "parameters": {
                "operation": "send",
                "sendTo": "={{ $json.email_dest }}",
                "subject": "={{ $json.objet }}",
                "emailType": "text",
                "message": "={{ $json.corps }}",
                "options": {}
            }
        },
        {
            "id": "update-statut",
            "name": "Mise à Jour Statut Contacté",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4.5,
            "position": [1680, 300],
            "credentials": {"googleOAuth2Api": GOOGLE_CRED},
            "parameters": {
                "operation": "update",
                "documentId": {"__rl": True, "value": SPREADSHEET_ID, "mode": "id"},
                "sheetName": {"__rl": True, "value": SHEET_NAME, "mode": "name"},
                "columns": {
                    "mappingMode": "defineBelow",
                    "value": {
                        "statut":        "Contacté",
                        "date_contact":  "={{ new Date().toISOString().slice(0,10) }}"
                    }
                },
                "matchingColumns": ["nom"],
                "options": {}
            }
        }
    ],
    "connections": {
        "Chaque Matin 10h":       {"main": [[{"node": "Lire Prospects Nouveaux",   "type": "main", "index": 0}]]},
        "Lire Prospects Nouveaux":{"main": [[{"node": "Filtrer Avec Email",         "type": "main", "index": 0}]]},
        "Filtrer Avec Email":     {"main": [[{"node": "Construire Prompt Claude",   "type": "main", "index": 0}]]},
        "Construire Prompt Claude":{"main":[[{"node": "Claude Génère Email",        "type": "main", "index": 0}]]},
        "Claude Génère Email":    {"main": [[{"node": "Parser Réponse Claude",      "type": "main", "index": 0}]]},
        "Parser Réponse Claude":  {"main": [[{"node": "Envoyer Email Gmail",        "type": "main", "index": 0}]]},
        "Envoyer Email Gmail":    {"main": [[{"node": "Mise à Jour Statut Contacté","type": "main", "index": 0}]]}
    },
    "settings": {"executionOrder": "v1"}
}

# ─────────────────────────────────────────────────────────────────────────────
# WORKFLOW 3 — RELANCE J+3
# ─────────────────────────────────────────────────────────────────────────────

CODE_CHECK_GMAIL_REPLY = r"""
const row = $input.first().json;
const emailDest = row.email || '';
if (!emailDest) return [{ json: { ...row, replied: false } }];
// On retourne le row pour que le node Gmail Search puisse chercher
return [{ json: { ...row, search_query: 'from:' + emailDest } }];
"""

CODE_EVAL_REPLY = r"""
const gmailData = $input.first().json;
const messages = gmailData.messages || [];
const prev = $('Vérifier Réponse Gmail').item?.json || {};
return [{ json: { ...prev, replied: messages.length > 0 } }];
"""

wf3 = {
    "name": "Prospection #3 — Relance J+3",
    "nodes": [
        {
            "id": "sticky-3",
            "name": "Note",
            "type": "n8n-nodes-base.stickyNote",
            "typeVersion": 1,
            "position": [-200, -200],
            "parameters": {
                "content": "## Prospection #3 — Relance J+3\n\n**Tourne chaque matin à 11h**\n\nLit prospects 'Contacté' depuis ≥3j → vérifie si réponse Gmail → \n- Répondu → statut 'RDV fixé'\n- Pas répondu → envoie relance → statut 'Relancé'",
                "height": 220, "width": 420, "color": 6
            }
        },
        {
            "id": "schedule-3",
            "name": "Chaque Matin 11h",
            "type": "n8n-nodes-base.scheduleTrigger",
            "typeVersion": 1.2,
            "position": [0, 300],
            "parameters": {
                "rule": {
                    "interval": [{"field": "hours", "hoursInterval": 24, "triggerAtHour": 11}]
                }
            }
        },
        {
            "id": "read-contactes",
            "name": "Lire Prospects Contactés",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4.5,
            "position": [240, 300],
            "credentials": {"googleOAuth2Api": GOOGLE_CRED},
            "parameters": {
                "operation": "readRows",
                "documentId": {"__rl": True, "value": SPREADSHEET_ID, "mode": "id"},
                "sheetName": {"__rl": True, "value": SHEET_NAME, "mode": "name"},
                "filtersUI": {
                    "values": [
                        {"lookupColumn": "statut", "lookupValue": "Contacté"}
                    ]
                },
                "options": {}
            }
        },
        {
            "id": "check-j3",
            "name": "Filtrer J+3",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [480, 300],
            "parameters": {"jsCode": CODE_CHECK_RELANCE}
        },
        {
            "id": "filter-skip-3",
            "name": "Filtrer Vides",
            "type": "n8n-nodes-base.filter",
            "typeVersion": 2,
            "position": [720, 300],
            "parameters": {
                "conditions": {
                    "options": {"caseSensitive": True},
                    "conditions": [
                        {
                            "leftValue": "={{ $json._skip }}",
                            "rightValue": True,
                            "operator": {"type": "boolean", "operation": "notEquals"}
                        }
                    ]
                }
            }
        },
        {
            "id": "check-reply-code",
            "name": "Vérifier Réponse Gmail",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [960, 300],
            "parameters": {"jsCode": CODE_CHECK_GMAIL_REPLY}
        },
        {
            "id": "gmail-search",
            "name": "Chercher Réponse Gmail",
            "type": "n8n-nodes-base.gmail",
            "typeVersion": 2.1,
            "position": [1200, 300],
            "credentials": {"googleOAuth2Api": GOOGLE_CRED},
            "parameters": {
                "operation": "getAll",
                "filters": {
                    "q": "={{ $json.search_query }}"
                },
                "returnAll": False,
                "limit": 1,
                "options": {}
            }
        },
        {
            "id": "eval-reply",
            "name": "A Répondu ?",
            "type": "n8n-nodes-base.if",
            "typeVersion": 2.2,
            "position": [1440, 300],
            "parameters": {
                "conditions": {
                    "options": {"caseSensitive": True},
                    "conditions": [
                        {
                            "leftValue": "={{ $json.id }}",
                            "rightValue": "",
                            "operator": {"type": "string", "operation": "notEmpty"}
                        }
                    ]
                }
            }
        },
        {
            "id": "update-rdv",
            "name": "Statut RDV Fixé",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4.5,
            "position": [1680, 160],
            "credentials": {"googleOAuth2Api": GOOGLE_CRED},
            "parameters": {
                "operation": "update",
                "documentId": {"__rl": True, "value": SPREADSHEET_ID, "mode": "id"},
                "sheetName": {"__rl": True, "value": SHEET_NAME, "mode": "name"},
                "columns": {
                    "mappingMode": "defineBelow",
                    "value": {"statut": "RDV fixé"}
                },
                "matchingColumns": ["nom"],
                "options": {}
            }
        },
        {
            "id": "build-relance",
            "name": "Construire Relance",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1680, 440],
            "parameters": {"jsCode": CODE_BUILD_RELANCE}
        },
        {
            "id": "send-relance",
            "name": "Envoyer Relance Gmail",
            "type": "n8n-nodes-base.gmail",
            "typeVersion": 2.1,
            "position": [1920, 440],
            "credentials": {"googleOAuth2Api": GOOGLE_CRED},
            "parameters": {
                "operation": "send",
                "sendTo": "={{ $json.email_dest }}",
                "subject": "={{ $json.objet }}",
                "emailType": "text",
                "message": "={{ $json.corps }}",
                "options": {}
            }
        },
        {
            "id": "update-relance",
            "name": "Statut Relancé",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4.5,
            "position": [2160, 440],
            "credentials": {"googleOAuth2Api": GOOGLE_CRED},
            "parameters": {
                "operation": "update",
                "documentId": {"__rl": True, "value": SPREADSHEET_ID, "mode": "id"},
                "sheetName": {"__rl": True, "value": SHEET_NAME, "mode": "name"},
                "columns": {
                    "mappingMode": "defineBelow",
                    "value": {
                        "statut":        "Relancé",
                        "date_relance":  "={{ new Date().toISOString().slice(0,10) }}"
                    }
                },
                "matchingColumns": ["nom"],
                "options": {}
            }
        }
    ],
    "connections": {
        "Chaque Matin 11h":        {"main": [[{"node": "Lire Prospects Contactés", "type": "main", "index": 0}]]},
        "Lire Prospects Contactés":{"main": [[{"node": "Filtrer J+3",              "type": "main", "index": 0}]]},
        "Filtrer J+3":             {"main": [[{"node": "Filtrer Vides",            "type": "main", "index": 0}]]},
        "Filtrer Vides":           {"main": [[{"node": "Vérifier Réponse Gmail",   "type": "main", "index": 0}]]},
        "Vérifier Réponse Gmail":  {"main": [[{"node": "Chercher Réponse Gmail",   "type": "main", "index": 0}]]},
        "Chercher Réponse Gmail":  {"main": [[{"node": "A Répondu ?",              "type": "main", "index": 0}]]},
        "A Répondu ?": {
            "main": [
                [{"node": "Statut RDV Fixé",    "type": "main", "index": 0}],
                [{"node": "Construire Relance",  "type": "main", "index": 0}]
            ]
        },
        "Construire Relance":      {"main": [[{"node": "Envoyer Relance Gmail",    "type": "main", "index": 0}]]},
        "Envoyer Relance Gmail":   {"main": [[{"node": "Statut Relancé",           "type": "main", "index": 0}]]}
    },
    "settings": {"executionOrder": "v1"}
}

# ─────────────────────────────────────────────────────────────────────────────
# DEPLOY
# ─────────────────────────────────────────────────────────────────────────────

for wf in [wf1, wf2, wf3]:
    r = requests.post(f"{BASE}/workflows", headers=H, json=wf)
    if r.status_code in (200, 201):
        data = r.json()
        print(f"OK {wf['name']}")
        print(f"   ID  : {data['id']}")
        print(f"   URL : http://localhost:5678/workflow/{data['id']}\n")
    else:
        print(f"ERREUR {wf['name']} — erreur {r.status_code}")
        print(json.dumps(r.json(), indent=2))

print("\nETAPE SUIVANTE :")
print("1. Crée un Google Sheets vide sur drive.google.com")
print("   Colonnes A→K : nom | secteur | ville | website | tel | email | statut | date_ajout | date_contact | date_relance | notes")
print("2. Copie l'ID depuis l'URL du Sheets")
print("3. Remplace 'TON_SPREADSHEET_ID_ICI' dans ce script et relance")
print("   (ou modifie directement les nodes Sheets dans n8n UI)")
print("\n4. Active les 3 workflows dans n8n (toggle ON)")
