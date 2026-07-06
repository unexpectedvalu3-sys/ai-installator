import json, requests

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NGQ5YjQ1NC05ZTZhLTQ3NmQtYTczMi1hNWNiYzFkNzAxOTIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZTQ2MmY4MzEtMDJhNS00YjU5LWE4MzctMGJhZmNkYjRmMTljIiwiaWF0IjoxNzgwNDkzMTM3LCJleHAiOjE3ODMwNTEyMDB9.jaAktbuoPW6IIAkm-sUdLQp3wDrSbhlpTM3JPkyFFQc"
BASE = "http://localhost:5678/api/v1"
H = {"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"}
WF_ID = "XsmDaLc80jrax7SK"

# ─── 1. GET workflow ────────────────────────────────────────────────────────────
wf = requests.get(f"{BASE}/workflows/{WF_ID}", headers=H).json()
nodes = wf["nodes"]

# ─── 2. Nouveau code "Formater Markdown" → produit du binaire ──────────────────
FORMAT_MD_V2 = r"""
const resp    = $input.first().json;
const brief   = resp.content[0].text;
const sujet   = $('Form Trigger').item.json['Sujet de recherche'];
const date    = new Date().toLocaleDateString('fr-FR', {day:'2-digit', month:'2-digit', year:'numeric'});
const dateIso = new Date().toISOString().slice(0, 10);
const inTok   = resp.usage?.input_tokens  || 0;
const outTok  = resp.usage?.output_tokens || 0;

const report  = `# Rapport : ${sujet}

**Date :** ${date}
**Modele :** claude-sonnet-4-6
**Tokens :** ${inTok} in / ${outTok} out (~$${((inTok*0.000003)+(outTok*0.000015)).toFixed(4)})

---

${brief}
`;

const safeSubj   = sujet.slice(0, 30).replace(/[^\w\s-]/g, '').trim().replace(/\s+/g, '_');
const filename   = 'research_' + dateIso + '_' + safeSubj + '.md';
const filePath   = 'C:/Users/test/Documents/Claude/Projects/ai-installator/research/' + filename;
const binaryData = await $helpers.prepareBinaryData(Buffer.from(report, 'utf8'), filename, 'text/markdown');

return [{ json: { file_path: filePath, sujet, date_iso: dateIso }, binary: { data: binaryData } }];
"""

# ─── 3. Patcher les nodes ───────────────────────────────────────────────────────
for node in nodes:
    if node["name"] == "Formater Markdown":
        node["parameters"]["jsCode"] = FORMAT_MD_V2
        print("Patched: Formater Markdown")

    elif node["name"] == "Ecrire Fichier" or node["name"] == "Écrire Fichier":
        # Remplacer le Code node par readWriteFile
        node["type"]        = "n8n-nodes-base.readWriteFile"
        node["typeVersion"] = 1
        node["parameters"]  = {
            "operation":        "write",
            "fileName":         "={{ $json.file_path }}",
            "dataPropertyName": "data",
            "options":          {}
        }
        print("Patched: Ecrire Fichier -> readWriteFile")

# ─── 4. PUT workflow ────────────────────────────────────────────────────────────
settings = wf.get("settings", {})
# n8n API v1 ne veut que executionOrder dans settings
clean_settings = {}
if "executionOrder" in settings:
    clean_settings["executionOrder"] = settings["executionOrder"]

payload = {
    "name":        wf["name"],
    "nodes":       nodes,
    "connections": wf["connections"],
    "settings":    clean_settings
}
r = requests.put(f"{BASE}/workflows/{WF_ID}", headers=H, json=payload)
if r.status_code in (200, 201):
    print(f"Workflow mis a jour — ID: {r.json()['id']}")
    print(f"URL: http://localhost:5678/workflow/{WF_ID}")
else:
    print(f"Erreur {r.status_code}:")
    print(json.dumps(r.json(), indent=2))
