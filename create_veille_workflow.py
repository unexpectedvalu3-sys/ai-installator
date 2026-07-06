import json
import requests

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NGQ5YjQ1NC05ZTZhLTQ3NmQtYTczMi1hNWNiYzFkNzAxOTIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZTQ2MmY4MzEtMDJhNS00YjU5LWE4MzctMGJhZmNkYjRmMTljIiwiaWF0IjoxNzgwNDkzMTM3LCJleHAiOjE3ODMwNTEyMDB9.jaAktbuoPW6IIAkm-sUdLQp3wDrSbhlpTM3JPkyFFQc"
API_BASE = "http://localhost:5678/api/v1"
HEADERS = {"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"}

FORMAT_CODE = r"""
const allHits = [];
for (const item of $input.all()) {
  const hits = item.json.hits || [];
  for (const hit of hits) {
    allHits.push({
      title: hit.title || '',
      url: hit.url || ('https://news.ycombinator.com/item?id=' + hit.objectID),
      points: hit.points || 0,
      comments: hit.num_comments || 0,
      date: hit.created_at ? hit.created_at.slice(0, 10) : ''
    });
  }
}

const seen = new Set();
const unique = allHits.filter(h => {
  if (seen.has(h.url)) return false;
  seen.add(h.url);
  return h.title.length > 10;
});

unique.sort((a, b) => b.points - a.points);
const top = unique.slice(0, 30);

const formatted = top.map((h, i) =>
  (i+1) + '. [' + h.points + 'pts | ' + h.comments + 'cmts | ' + h.date + '] ' + h.title + '\n   ' + h.url
).join('\n\n');

return [{
  json: {
    stories_formatted: formatted,
    story_count: top.length,
    week_date: new Date().toLocaleDateString('fr-FR', {day:'2-digit', month:'2-digit', year:'numeric'})
  }
}];
"""

EXTRACT_CODE = r"""
const resp = $input.first().json;
const brief = resp.content[0].text;
const inTok = resp.usage ? resp.usage.input_tokens : 0;
const outTok = resp.usage ? resp.usage.output_tokens : 0;
return [{
  json: {
    brief: brief,
    subject: 'Veille IA — ' + new Date().toLocaleDateString('fr-FR'),
    tokens: inTok + ' in / ' + outTok + ' out',
    cost_usd: ((inTok * 0.00000025) + (outTok * 0.00000125)).toFixed(4)
  }
}];
"""

STICKY_NOTE = """## 📧 Ajouter l'envoi email

Connecter un nœud **Gmail** ou **Send Email** après "Extraire Brief" :
- **Subject** : `{{ $json.subject }}`
- **Body HTML** : `{{ $json.brief }}`
- **To** : `enz51prod@gmail.com`

## ⚙️ Config
Mettre ta clé Anthropic dans le nœud **Config API** (champ ANTHROPIC_KEY).

## 💰 Coût estimé
~$0.002 / brief (Claude Haiku)"""

workflow = {
    "name": "Veille Hebdo IA - AI Installator",
    "nodes": [
        {
            "id": "node-manual",
            "name": "Test Manuel",
            "type": "n8n-nodes-base.manualTrigger",
            "typeVersion": 1,
            "position": [120, 300],
            "parameters": {}
        },
        {
            "id": "node-schedule",
            "name": "Chaque Lundi 9h",
            "type": "n8n-nodes-base.scheduleTrigger",
            "typeVersion": 1.2,
            "position": [120, 500],
            "parameters": {
                "rule": {
                    "interval": [
                        {
                            "field": "cronExpression",
                            "expression": "0 9 * * 1"
                        }
                    ]
                }
            }
        },
        {
            "id": "node-config",
            "name": "Config API",
            "type": "n8n-nodes-base.set",
            "typeVersion": 3.4,
            "position": [340, 300],
            "parameters": {
                "mode": "manual",
                "assignments": {
                    "assignments": [
                        {
                            "id": "k-anthropic",
                            "name": "ANTHROPIC_KEY",
                            "value": "sk-ant-METTRE_CLE_ICI",
                            "type": "string"
                        }
                    ]
                }
            }
        },
        {
            "id": "node-hn-ia",
            "name": "HN IA Stories",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [580, 180],
            "parameters": {
                "method": "GET",
                "url": "https://hn.algolia.com/api/v1/search",
                "sendQuery": True,
                "queryParameters": {
                    "parameters": [
                        {
                            "name": "query",
                            "value": "AI LLM Claude GPT agents autonomous"
                        },
                        {
                            "name": "tags",
                            "value": "story"
                        },
                        {
                            "name": "numericFilters",
                            "value": "={{ 'created_at_i>' + Math.floor((Date.now() - 7*24*60*60*1000) / 1000) + ',points>5' }}"
                        },
                        {
                            "name": "hitsPerPage",
                            "value": "25"
                        }
                    ]
                }
            }
        },
        {
            "id": "node-hn-auto",
            "name": "HN Automation Stories",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [580, 420],
            "parameters": {
                "method": "GET",
                "url": "https://hn.algolia.com/api/v1/search",
                "sendQuery": True,
                "queryParameters": {
                    "parameters": [
                        {
                            "name": "query",
                            "value": "automation workflow n8n no-code startup SaaS launch"
                        },
                        {
                            "name": "tags",
                            "value": "story"
                        },
                        {
                            "name": "numericFilters",
                            "value": "={{ 'created_at_i>' + Math.floor((Date.now() - 7*24*60*60*1000) / 1000) + ',points>3' }}"
                        },
                        {
                            "name": "hitsPerPage",
                            "value": "20"
                        }
                    ]
                }
            }
        },
        {
            "id": "node-merge",
            "name": "Merge Stories",
            "type": "n8n-nodes-base.merge",
            "typeVersion": 3,
            "position": [820, 300],
            "parameters": {
                "mode": "append"
            }
        },
        {
            "id": "node-format",
            "name": "Format Stories",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1040, 300],
            "parameters": {
                "jsCode": FORMAT_CODE
            }
        },
        {
            "id": "node-claude",
            "name": "Claude Brief",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [1260, 300],
            "parameters": {
                "method": "POST",
                "url": "https://api.anthropic.com/v1/messages",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {
                            "name": "x-api-key",
                            "value": "={{ $('Config API').item.json.ANTHROPIC_KEY }}"
                        },
                        {
                            "name": "anthropic-version",
                            "value": "2023-06-01"
                        },
                        {
                            "name": "content-type",
                            "value": "application/json"
                        }
                    ]
                },
                "sendBody": True,
                "contentType": "raw",
                "rawContentType": "application/json",
                "body": "={{ JSON.stringify({ model: 'claude-haiku-4-5-20251001', max_tokens: 1500, messages: [{ role: 'user', content: \"Tu es l'analyste tech d'AI Installator, agence d'automatisation IA B2B pour PME françaises.\\n\\nStories HackerNews de la semaine (IA + Automation) :\\n\\n\" + $json.stories_formatted + \"\\n\\n---\\nGénère le brief hebdomadaire (markdown, français, chirurgical) :\\n\\n# VEILLE IA — \" + $json.week_date + \"\\n\\n## 🔥 Top 3 Signaux\\n(3 tendances/outils impactant la vente d'automatisation aux PME FR)\\n\\n## 💡 Opportunité Semaine\\n(1 angle business concret : nouveau besoin client, nouvel outil à revendre, concurrent)\\n\\n## ⚡ Actions 7 jours\\n(2-3 actions concrètes pour AI Installator)\\n\\n## ❌ Bruit à Ignorer\\n(1-2 hypes sans valeur réelle pour PME FR)\" }] }) }}"
            }
        },
        {
            "id": "node-extract",
            "name": "Extraire Brief",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1480, 300],
            "parameters": {
                "jsCode": EXTRACT_CODE
            }
        },
        {
            "id": "node-note",
            "name": "Note Instructions",
            "type": "n8n-nodes-base.stickyNote",
            "typeVersion": 1,
            "position": [1480, 60],
            "parameters": {
                "content": STICKY_NOTE,
                "height": 260,
                "width": 340,
                "color": 3
            }
        }
    ],
    "connections": {
        "Test Manuel": {
            "main": [
                [{"node": "Config API", "type": "main", "index": 0}]
            ]
        },
        "Chaque Lundi 9h": {
            "main": [
                [{"node": "Config API", "type": "main", "index": 0}]
            ]
        },
        "Config API": {
            "main": [
                [
                    {"node": "HN IA Stories", "type": "main", "index": 0},
                    {"node": "HN Automation Stories", "type": "main", "index": 0}
                ]
            ]
        },
        "HN IA Stories": {
            "main": [
                [{"node": "Merge Stories", "type": "main", "index": 0}]
            ]
        },
        "HN Automation Stories": {
            "main": [
                [{"node": "Merge Stories", "type": "main", "index": 1}]
            ]
        },
        "Merge Stories": {
            "main": [
                [{"node": "Format Stories", "type": "main", "index": 0}]
            ]
        },
        "Format Stories": {
            "main": [
                [{"node": "Claude Brief", "type": "main", "index": 0}]
            ]
        },
        "Claude Brief": {
            "main": [
                [{"node": "Extraire Brief", "type": "main", "index": 0}]
            ]
        }
    },
    "settings": {
        "executionOrder": "v1"
    }
}

resp = requests.post(
    f"{API_BASE}/workflows",
    headers=HEADERS,
    json=workflow
)

print(f"Status: {resp.status_code}")
result = resp.json()
if resp.status_code == 200 or resp.status_code == 201:
    wf_id = result.get("id")
    print(f"Workflow créé ! ID: {wf_id}")
    print(f"URL: http://localhost:5678/workflow/{wf_id}")
else:
    print("Erreur:")
    print(json.dumps(result, indent=2))
