# CLAUDE.md — AI Installator (Agence IA Automation, verticale courtage)

> Fichier projet. Le contrat global (identité, méthode, garde-fous, style) vit dans `C:\Users\test\CLAUDE.md`. Ici = **contexte agence + discipline + architecture + n8n-MCP**.

---

## 1. Contexte & positionnement
Agence d'**automatisation IA pour PME françaises** (marque mère **Lumaaria / AI Installator**). Stack : **Claude API + n8n + Ruby/Python**. Client cible : PME 5-50 salariés, ticket **500-3000€**.

**Verticale actée : courtage assurance** (pas de la « conformité IA vendue par la peur »).
- **Pourquoi mener par la valeur** : le Digital Omnibus (UE, 16/06/2026) a repoussé les obligations lourdes AI Act (Annexe III) du 02/08/2026 au **02/12/2027**. La conformité = argument **secondaire** ; la valeur (gain de temps, ROI chiffré) mène.
- **Pourquoi le courtage** : marché fragmenté, petits cabinets sans DSI, docs non structurés (terrain LLM idéal), commissions récurrentes (rétention), devoir de conseil DDA (douleur durable), souveraineté via stack local FR possible.
- **Posture légale** : pas d'agrément requis ; « diagnostic informatif, pas avis juridique » ; se couvrir contractuellement (convention sous-traitance art. 28).

Détail stratégie : `MEMORY/memory/agence-courtage-strategie.md`.

## 2. Sous-projets (verticales)
| Vertical | État | Mémoire |
|----------|------|---------|
| **Modul'R (tante, client pilote)** | App FastAPI déployée Railway, 3 outils (extraction CRM / comparateur mutuelle / fiche DDA) | `modulr-import-tante.md` |
| **KinéCotation** | Copilote NGAP, prototype + 82 actes + OCR + web app MVP | `kine-cotation-project.md` |
| **Artisan peintre** | Devis/facture, stade cadrage | `artisan-peintre-project.md` |
| **DocInvy** (SaaS proof) | Live, Render+Neon, Factur-X MINIMUM | `docinvy-infra.md` |

## 3. Discipline (risque n°1 = builder sans vendre)
- ~**50% discovery client** / ~35% appropriation de l'existant (pipeline, app) / ~15% admin-veille.
- **Une semaine sans avoir parlé à un courtier = une semaine de recul.**
- Sur l'app existante : comprendre assez pour **vendre / déployer / réparer sous pression**, pas réécrire de zéro. Décortiquer bloc par bloc, casser, réparer.

## 4. Architecture (patterns non négociables)
1. **Perception LLM / décision déterministe séparées** — le LLM extrait les faits (OCR, lecture devis), un moteur déterministe calcule (CSV Modul'R, cotation NGAP). Le LLM ne produit jamais un montant.
2. **Provider IA abstrait** (`_call_llm`) — basculable Mistral EU / local pour la prod RGPD.
3. **Dual-model par coût** — prose fine FR sur Claude (Sonnet/Opus) ; bulk pas cher sur **GLM 5.2** via OpenRouter (`z-ai/glm-5.2`, clé dans `.openclaw/.env`). ⚠️ modèle à raisonnement → `reasoning:{enabled:false}` sinon `content` vide.
4. **Fail-closed** — auth middleware sur toutes les routes ; entrée invalide → erreur propre (jamais 500 nu) ; secrets + PII exclus du repo (`.railwayignore`).
5. **RGPD by design** — pas d'IBAN ni de données de santé stockées ; métier santé → HDS si stockage → MVP local sans stockage.

## 5. Setup légal facturation
Pas de tampon obligatoire en France. Mentions requises : dénomination + forme juridique, SIREN/SIRET, RCS + greffe, TVA intra (si assujetti). **Statut d'Enzo (SASU vs EURL) pas encore tranché** → devis/factures génériques ou signaler le manque. Détail : `MEMORY/memory/ai-installator-legal-setup.md`.

## 6. Skills à privilégier
| Besoin | Skill |
|--------|-------|
| Analyse marché / nouveaux entrants | `/market-map` |
| Intelligence concurrentielle | `/competitive-radar` |
| Scorer une opportunité (ATOM) | `/opp-radar` |
| Prévisions marché 6-24 mois | `/trend-forecast` |
| Pitch client PME | `/b2b-pitch` |
| Stack / archi | `/code-velocity` |
| Recherche exhaustive | `/deep-research` |
| Brief hebdo marché IA | `/weekly-brief` |

---

## 7. n8n-MCP — System Prompt

Expert n8n automation via n8n-MCP tools. Rôle : concevoir, construire, valider des workflows avec précision maximale.

### Core Principles
1. **Silent Execution** — exécuter les tools sans commentaire, répondre APRÈS.
2. **Parallel Execution** — opérations indépendantes en parallèle.
3. **Templates First** — toujours vérifier les templates avant de partir de zéro.
4. **Multi-Level Validation** — `validate_node(minimal)` → `validate_node(full)` → `validate_workflow`.
5. **Never Trust Defaults** — les valeurs par défaut sont la source n°1 des échecs runtime. Configurer explicitement TOUS les paramètres qui pilotent le comportement d'un node.

### Workflow Process
1. **Start** : `tools_documentation()` pour les best practices.
2. **Template Discovery** (parallèle) : `search_templates` par metadata / task / node type / texte.
3. **Node Discovery** (si pas de template) : `search_nodes({query, includeExamples:true})`.
4. **Configuration** (parallèle) : `get_node({nodeType, detail:'standard'|'full', includeExamples:true})`.
5. **Validation** : `validate_node(minimal)` → `validate_node(full, profile:'runtime')` → fixer TOUTES les erreurs.
6. **Building** : templates d'abord (`get_template(id, {mode:'full'})`) · TOUS les params explicites · error handling · expressions `$json`, `$node["Name"].json`.
7. **Workflow Validation** : `validate_workflow` / `_connections` / `_expressions`.
8. **Deployment** : `n8n_create_workflow` → `n8n_validate_workflow({id})` → `n8n_test_workflow({workflowId})`.

### Warnings
- **Defaults FAILS** : `{resource:"message", operation:"post", text:"Hello"}` casse au runtime → tout expliciter (`select:"channel", channelId:"C123", …`).
- **IF multi-output** : `addConnection` avec `branch:"true"` / `branch:"false"`.

### Nodes les plus utilisés
`code` · `httpRequest` · `webhook` · `set` · `if` · `scheduleTrigger` · `@n8n/n8n-nodes-langchain.agent` · `googleSheets` · `@n8n/n8n-nodes-langchain.lmChatOpenAi` · `gmail`.

---

## Setup technique
- **n8n** : http://localhost:5678 · MCP `n8n-mcp` (stdio) · `NODE_FUNCTION_ALLOW_BUILTIN=fs,path`.
- **Claude API** : nouveau build → modèle le plus capable (Fable 5 / Opus 4.8 / Sonnet 5). Existant : extraction = Sonnet, tâches complexes = `claude-opus-4-8`.
- **Stack** : Ruby + n8n + Claude API. Clé Anthropic : `modulr-app/.env`.
- **Dernière réécriture** : 2026-07-09.
