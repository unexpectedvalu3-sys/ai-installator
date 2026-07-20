# KinéCotation — Provider IA : décision, état RGPD, ce qui reste à faire

> 2026-07-17. Décisions d'Enzo : **architecture local-first** + **OCR conservé** + **provider FR/UE**.
> Applique CLAUDE.md §4.1 (perception/décision séparées) et §4.2 (provider abstrait).

> **MàJ 2026-07-20 (pilote).** Pour la mise en ligne pilote de Malcom, l'OCR tourne sur **Claude
> Sonnet** (`KINE_LLM_PROVIDER=anthropic`, `KINE_LLM_MODELE=claude-sonnet-5`), via la **clé Anthropic
> déjà en main** (mutualisée avec Modul'R) — aucune clé Mistral à créer. La nuance **US est assumée
> pour le pilote** parce que l'image part **caviardée structurellement** (l'identité patient ne quitte
> jamais le poste du kiné). La **cible souveraineté FR/UE pour la production reste inchangée** :
> provider Mistral (défaut) ou VOIE B auto-hébergée. Le provider abstrait (§4.2 / `llm.py`) rend cette
> bascule triviale.

---

## 1. Les décisions prises

| Question | Décision | Pourquoi |
|---|---|---|
| Stockage du dossier de preuve | **Local** (chez le kiné) | On n'héberge rien pour le compte d'un tiers → **l'HDS n'a pas d'objet**. Coût 0. |
| Certification HDS | **Non** | Prématuré : des mois + des dizaines de k€, pré-revenu, et ça ne règle pas la jambe LLM. Option non perdue (cf. §5). |
| Modèle IA local (sur le poste du kiné) | **Écarté** | Aucune garantie que la machine d'un kiné (portable bureautique, sans GPU) le fasse tourner. Install + téléchargement multi-Go + support à distance = la facture déjà payée sur l'exe du comparateur. |
| OCR dans le produit | **Conservé** | Choix d'Enzo. (Note : le protocole benchmark §4 rappelle que le produit tient même sans OCR — c'est un accélérateur, pas le moteur de valeur.) |
| Provider | **Mistral par défaut** (éditeur français, serveurs UE) | Seule option qui donne la qualité **et** la souveraineté FR. |

**Conséquence à assumer** : l'ordonnance **sort du cabinet**. Le discours de vente n'est plus
« rien ne quitte votre cabinet » mais **« vos données restent en France, chez un acteur français »**.
C'est le seul endroit du produit où une donnée de santé circule — moteur, KB et dossier de preuve
sont 100 % locaux et déterministes.

> **MàJ 2026-07-20** — l'app **caviarde l'image AVANT envoi** (masquage nom/prénom/date de naissance/NIR
> sur canvas dans l'étape « 00 Ordonnance » ; seule la version masquée part au provider — cf.
> `07_UI_DESIGN.md` §3.8). L'identité patient, elle, est saisie localement et **ne quitte jamais le poste**.
> Ça durcit l'argument souveraineté mais **ne remplace pas** la validation juriste (Enterprise + ZDR + DPA).
>
> **MàJ 2026-07-20 (itér. 2)** — le caviardage est désormais **auto-proposé** : une détection OCR
> **100 % locale au navigateur** (tesseract.js + pack FR `tessdata_fast`, servis depuis `/static/tesseract/`)
> repère le bloc patient et pré-pose les masques ; l'image non masquée ne sort **même pas vers notre
> backend**. Le kiné valide d'un geste (« Analyser »). C'est un **2ᵉ modèle OCR, purement local**, distinct
> du provider cloud (Mistral) qui, lui, ne reçoit que l'image déjà masquée.

---

## 2. Ce qui a été implémenté

- **`prototype/llm.py`** — la couche provider abstraite qu'imposait CLAUDE.md §4.2 et qui n'avait
  jamais été appliquée ici. Un seul point de bascule, aucun nom de fournisseur ailleurs.
  - `KINE_LLM_PROVIDER` = `mistral` (défaut) | `anthropic` · `KINE_LLM_MODELE` (surcharge)
  - Fail-closed : clé absente ou provider inconnu → erreur explicite, jamais un plantage nu.
  - `python prototype/llm.py` → affiche provider / modèle / état de la clé.
- **`prototype/ordonnance_ocr.py`** — le couplage `anthropic.Anthropic()` (ligne 112) et le
  `MODELE = "claude-opus-4-8"` en dur (ligne 41) ont disparu. Passe par `llm._call_llm`.
- **`benchmark/run_batch.py`** — hérite de l'abstraction, permet de comparer deux providers
  **à iso-pipeline** :
  ```
  KINE_LLM_PROVIDER=mistral   python run_batch.py ordonnances
  KINE_LLM_PROVIDER=anthropic python run_batch.py ordonnances
  ```
- **`requirements.txt`** — ~~`mistralai`~~ **retiré** (2026-07-18) : le SDK s'installe corrompu sur la
  machine d'Enzo (Defender). Mistral est appelé via son **API OpenAI-compatible en HTTP direct**
  (`llm._post_openai_compat`, `https://api.mistral.ai/v1`), partagé avec le provider `selfhosted`.

Vérifié : tout compile, la chaîne s'importe, la bascule des deux providers fonctionne, l'erreur
clé-manquante est propre.

---

## 3. ⚠️ État RGPD réel (vérifié le 2026-07-17 — à re-vérifier avant prod)

| Fait | Source | Impact |
|---|---|---|
| **« La Plateforme » (cloud Mistral) n'est PAS qualifiée HDS** | recherche web 17/07/2026 | Bloquant si on stocke de la donnée de santé chez eux. |
| Mistral héberge à **Paris chez Scaleway**, lui **certifié HDS** | idem | ⚠️ **Piège** : l'hébergeur certifié **ne transfère pas** sa qualification au service. Ne pas confondre (même conflation que « faire un HDS »). |
| **Zero Data Retention réservé à l'abonnement Enterprise** | idem | C'est le ZDR qui porte l'argument « pas de rétention → pas d'hébergement → HDS sans objet ». **Pas dispo sur l'offre standard.** |
| DPA Mistral existe | [legal.mistral.ai](https://legal.mistral.ai/terms/data-processing-addendum) | À signer pour la prod. |

**Ce que ça donne concrètement :**
- ✅ **Benchmark maintenant** : ordonnances **anonymisées** (protocole §0.1 : caviarder nom,
  prénom, date de naissance, NIR) → pas besoin de ZDR. **Rien ne bloque.**
- 🔴 **Production sur données réelles** : **Mistral Enterprise + ZDR + DPA art. 28** obligatoires,
  plus une convention art. 28 avec le kiné (on devient son sous-traitant dès qu'on fournit l'accès
  au LLM — cf. le modèle `accounts.json` du comparateur qui livre nos clés au client).

> Je raisonne, je ne rends pas un avis juridique (posture agence : « diagnostic informatif »).
> Le montage Enterprise/ZDR/HDS se fait valider par un avocat avant le premier patient réel.

---

## 4. Questions techniques ouvertes

   *(MàJ 2026-07-18 : défaut Mistral = `mistral-medium-latest` — `pixtral-*` n'existe pas sur le
   compte testé. Mistral medium a fait chirurgie 100 % au 1er benchmark, cf. `11_VOIE_B_OCR_OPEN.md`.)*
1. **modèle Mistral chat vs `mistral-ocr-latest` / OCR 4.** J'ai câblé le modèle vision
   en un appel, pour rester **à iso-pipeline avec Claude** (image → JSON structuré) et rendre le
   benchmark comparable. Mais **OCR 4 sort des scores de confiance en ligne** — or le protocole §4
   dit qu'une confiance calibrée « compte presque autant que l'accuracy » (métrique D). Un pipeline
   en 2 temps (`client.ocr.process` → texte + confiance → modèle texte → schéma) est peut-être
   meilleur. **À trancher par le benchmark, pas par le débat.**
2. **PDF non supporté côté Mistral** dans `llm.py` (le chat vision attend une image) → erreur
   explicite. Contournement : convertir en PNG (poppler est installé), ou passer par l'endpoint OCR.
3. **Fallback** : que fait le produit si l'API est indisponible ? Aujourd'hui : erreur. L'arbre de
   décision manuel reste le chemin de secours — à câbler dans l'UI.

---

## 5. Ce qui reste à faire (par Enzo)

1. **Créer la clé Mistral** sur <https://console.mistral.ai> → `set MISTRAL_API_KEY=...`
   *(je ne crée jamais de clé API ni ne saisis de secret — garde-fou agence.)*
2. **Fournir des ordonnances réelles anonymisées** (15-20, manuscrites ET tapées) : le benchmark
   contient aujourd'hui **1 image, tapée, synthétique** — c'est un smoke test, pas une mesure.
   Sans ça, le choix du provider se fait à l'aveugle.
3. Le jour d'un vrai patient : **contrat Enterprise + ZDR + DPA**.

**L'option HDS n'est pas perdue** : tant que le dossier de preuve est un fichier autonome à
sérialisation canonique stable, on peut passer au centralisé chez un hébergeur HDS plus tard sans
rien redessiner. C'est la seule contrainte de design à tenir dès maintenant.

Voir `05_REPOSITIONNEMENT_PREUVE.md` §4 et `benchmark/00_PROTOCOLE_BENCHMARK_OCR.md` §0.
