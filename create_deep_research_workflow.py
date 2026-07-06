import json, requests

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NGQ5YjQ1NC05ZTZhLTQ3NmQtYTczMi1hNWNiYzFkNzAxOTIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZTQ2MmY4MzEtMDJhNS00YjU5LWE4MzctMGJhZmNkYjRmMTljIiwiaWF0IjoxNzgwNDkzMTM3LCJleHAiOjE3ODMwNTEyMDB9.jaAktbuoPW6IIAkm-sUdLQp3wDrSbhlpTM3JPkyFFQc"
BASE = "http://localhost:5678/api/v1"
H = {"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"}

# ─── 1. CREDENTIALS ────────────────────────────────────────────────────────────
def create_credential(name, ctype, data):
    r = requests.post(f"{BASE}/credentials", headers=H, json={"name": name, "type": ctype, "data": data})
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Credential error: {r.text}")
    return r.json()

serp  = create_credential("SerpAPI Key",    "httpQueryAuth",  {"name": "api_key",  "value": "VOTRE_CLE_SERPAPI_ICI",  "allowedDomains": ""})
claude = create_credential("Claude API Key", "httpHeaderAuth", {"name": "x-api-key", "value": "VOTRE_CLE_CLAUDE_ICI", "allowedDomains": ""})
print(f"Credentials créés — SerpAPI: {serp['id']}  Claude: {claude['id']}")

# ─── 2. CODE STRINGS ───────────────────────────────────────────────────────────
GENERATE_QUERIES = r"""
const sujet = $input.first().json['Sujet de recherche'];
return [
  { json: { query: sujet + ' marché France PME 2025 2026',              sujet } },
  { json: { query: sujet + ' concurrents acteurs principaux France',    sujet } },
  { json: { query: sujet + ' tendances opportunités émergentes IA',     sujet } }
];
"""

AGGREGATE = r"""
const items = $input.all();
let text = '';
for (const item of items) {
  const results = item.json.organic_results || [];
  const q = item.json.search_parameters?.q || '?';
  text += '\n\n### Query: "' + q + '"\n\n';
  for (const r of results.slice(0, 5)) {
    text += '**' + (r.title || 'Sans titre') + '**\n';
    text += (r.snippet || '') + '\n';
    text += 'URL: ' + (r.link || '') + '\n\n';
  }
}
const sujet = $('Form Trigger').item.json['Sujet de recherche'];
return [{ json: { research_text: text, sujet } }];
"""

FORMAT_MD = r"""
const resp  = $input.first().json;
const brief = resp.content[0].text;
const sujet = $('Form Trigger').item.json['Sujet de recherche'];
const date  = new Date().toLocaleDateString('fr-FR', {day:'2-digit', month:'2-digit', year:'numeric'});
const inTok  = resp.usage?.input_tokens  || 0;
const outTok = resp.usage?.output_tokens || 0;
const report = `# Rapport : ${sujet}

**Date :** ${date}
**Modèle :** claude-sonnet-4-6
**Tokens :** ${inTok} in / ${outTok} out (~$${((inTok*0.000003)+(outTok*0.000015)).toFixed(4)})

---

${brief}
`;
return [{ json: { report_content: report, sujet, date_iso: new Date().toISOString().slice(0,10) } }];
"""

WRITE_FILE = r"""
const fs   = require('fs');
const path = require('path');
const data      = $input.first().json;
const content   = data.report_content;
const sujet     = data.sujet;
const dateStr   = data.date_iso;
const safeSubj  = sujet.slice(0,30).replace(/[^\w\sÀ-ž-]/g,'').trim().replace(/\s+/g,'_');
const dir       = 'C:/Users/test/Documents/Claude/Projects/ai-installator/research';
if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
const filename  = path.join(dir, 'research_' + dateStr + '_' + safeSubj + '.md');
fs.writeFileSync(filename, content, 'utf8');
return [{ json: { success: true, file_path: filename, bytes: Buffer.byteLength(content,'utf8') } }];
"""

CLAUDE_BODY_EXPR = (
    "={{ JSON.stringify({"
    "  model: 'claude-sonnet-4-6',"
    "  max_tokens: 3000,"
    "  system: \"Tu es un expert analyste marché IA pour PME françaises. Tu génères des rapports de recherche structurés, précis et actionnables avec scoring ATOM (/25). Réponds UNIQUEMENT en Markdown bien formaté.\","
    "  messages: [{"
    "    role: 'user',"
    "    content: \"Sujet : \" + $json.sujet + \"\\n\\nRésultats de recherche web :\\n\" + $json.research_text"
    "      + \"\\n\\n---\\nGénère un rapport Markdown complet avec exactement ces sections :\\n\""
    "      + \"\\n## TL;DR\\n(3 bullets max)\\n\""
    "      + \"\\n## Analyse Marché\\n(état, taille, dynamiques)\\n\""
    "      + \"\\n## Concurrents\\n(tableau Nom | Position | Forces | Faiblesses)\\n\""
    "      + \"\\n## Opportunités Non Exploitées\\n(top 3 avec justification)\\n\""
    "      + \"\\n## Score ATOM /25\\n| Critère | Note /5 | Justification |\\n|---------|---------|---------------|\\n| Attractivité | | |\\n| Timing | | |\\n| Originalité | | |\\n| Monétisation | | |\\n| **TOTAL** | **/25** | |\\n\""
    "      + \"\\n## Action Cette Semaine\\n(1 action concrète pour AI Installator)\""
    "  }]"
    "}) }}"
)

STICKY = """## 🔬 Deep Research — AI Installator

### Utilisation
1. Copier l'URL du **Form Trigger** (bouton ▶ dans le nœud)
2. Saisir un sujet de recherche
3. Le rapport `.md` est généré dans `research/`

### ⚙️ Config obligatoire
- **SerpAPI Key** → Settings > Credentials > "SerpAPI Key" > remplacer la valeur
  (compte gratuit : 100 recherches/mois — serpapi.com)
- **Claude API Key** → Settings > Credentials > "Claude API Key" > remplacer la valeur

### 💰 Coût / rapport
- SerpAPI : 3 crédits (~0.03$ sur plan payant)
- Claude Sonnet : ~0.02-0.05$

### 📁 Output
`research/research_YYYY-MM-DD_sujet.md`"""

# ─── 3. WORKFLOW ───────────────────────────────────────────────────────────────
workflow = {
    "name": "Deep Research - AI Installator",
    "nodes": [
        {
            "id": "note-main",
            "name": "Note Instructions",
            "type": "n8n-nodes-base.stickyNote",
            "typeVersion": 1,
            "position": [-60, -240],
            "parameters": {"content": STICKY, "height": 340, "width": 420, "color": 4}
        },
        {
            "id": "form-trigger",
            "name": "Form Trigger",
            "type": "n8n-nodes-base.formTrigger",
            "typeVersion": 2.2,
            "position": [120, 300],
            "webhookId": "deep-research-form",
            "parameters": {
                "formTitle": "Deep Research AI Installator",
                "formDescription": "Générer un rapport de recherche structuré avec scoring ATOM",
                "formFields": {
                    "values": [
                        {
                            "fieldLabel": "Sujet de recherche",
                            "fieldType": "text",
                            "requiredField": True,
                            "placeholder": "Ex: automatisation IA pour PME françaises"
                        }
                    ]
                },
                "options": {}
            }
        },
        {
            "id": "gen-queries",
            "name": "Générer 3 Queries",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [360, 300],
            "parameters": {"jsCode": GENERATE_QUERIES}
        },
        {
            "id": "serp-request",
            "name": "SerpAPI Search",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [600, 300],
            "credentials": {"httpQueryAuth": {"id": serp["id"], "name": serp["name"]}},
            "parameters": {
                "method": "GET",
                "url": "https://serpapi.com/search.json",
                "authentication": "genericCredentialType",
                "genericAuthType": "httpQueryAuth",
                "sendQuery": True,
                "queryParameters": {
                    "parameters": [
                        {"name": "q",   "value": "={{ $json.query }}"},
                        {"name": "num", "value": "5"},
                        {"name": "hl",  "value": "fr"},
                        {"name": "gl",  "value": "fr"}
                    ]
                }
            }
        },
        {
            "id": "aggregate",
            "name": "Agréger Résultats",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [840, 300],
            "parameters": {"jsCode": AGGREGATE}
        },
        {
            "id": "claude-request",
            "name": "Claude API",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [1080, 300],
            "credentials": {"httpHeaderAuth": {"id": claude["id"], "name": claude["name"]}},
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
                "body": CLAUDE_BODY_EXPR
            }
        },
        {
            "id": "format-md",
            "name": "Formater Markdown",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1320, 300],
            "parameters": {"jsCode": FORMAT_MD}
        },
        {
            "id": "write-file",
            "name": "Écrire Fichier",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1560, 300],
            "parameters": {"jsCode": WRITE_FILE}
        }
    ],
    "connections": {
        "Form Trigger":       {"main": [[{"node": "Générer 3 Queries",   "type": "main", "index": 0}]]},
        "Générer 3 Queries":  {"main": [[{"node": "SerpAPI Search",       "type": "main", "index": 0}]]},
        "SerpAPI Search":     {"main": [[{"node": "Agréger Résultats",    "type": "main", "index": 0}]]},
        "Agréger Résultats":  {"main": [[{"node": "Claude API",           "type": "main", "index": 0}]]},
        "Claude API":         {"main": [[{"node": "Formater Markdown",    "type": "main", "index": 0}]]},
        "Formater Markdown":  {"main": [[{"node": "Écrire Fichier",       "type": "main", "index": 0}]]}
    },
    "settings": {"executionOrder": "v1"}
}

r = requests.post(f"{BASE}/workflows", headers=H, json=workflow)
if r.status_code in (200, 201):
    wf = r.json()
    print(f"\n✅ Workflow créé — ID: {wf['id']}")
    print(f"   URL: http://localhost:5678/workflow/{wf['id']}")
else:
    print(f"\n❌ Erreur {r.status_code}:")
    print(json.dumps(r.json(), indent=2))
