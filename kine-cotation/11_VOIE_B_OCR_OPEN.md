# KinéCotation — Voie B : OCR open auto-hébergé sur GPU HDS

> 2026-07-18. Préparer la voie souveraine : un modèle OCR **open** tournant sur une **GPU dans le
> périmètre HDS** (Scaleway/Outscale). La donnée d'ordonnance **ne quitte jamais notre infra** →
> pas de sous-traitant tiers, rétention qu'on contrôle → **flux nominatif possible**. Voir `10_OCR_FOURNISSEURS.md`.
> Le seul inconnu : un modèle open lit-il le **manuscrit médical FR** aussi bien que Mistral OCR 4 ? → à benchmarker.

---

## 1. Candidats (licence = le point à ne pas rater)

Fait clé sourcé : sur du **manuscrit**, les OCR « traditionnels » (Tesseract, docTR, PaddleOCR, Surya)
**échouent** ; ce sont les **VLM** (modèles vision-langage) qui lisent l'écriture. On vise donc des VLM
servables via une API OpenAI-compatible (vLLM), sous licence **commerciale-compatible**.

| Modèle | Licence | Manuscrit FR | Servi vLLM | Verdict |
|---|---|---|---|---|
| **Qwen2.5-VL-7B / 32B** | **Apache 2.0** (7B & 32B) | Oui (VLM, extraction) | Oui (vllm>0.7.2) | **LEAD** — libre commercial, taille raisonnable |
| **Pixtral-12B** | **Apache 2.0** | Oui (VLM généraliste) | Oui | Bon — cohérence « famille Mistral » |
| **olmOCR / RolmOCR** (AllenAI) | Apache 2.0 (sur Qwen2-VL) | Oui — **spécialisé doc/manuscrit** | Oui | Fort candidat spécialisé OCR |
| GOT-OCR 2.0 | Apache 2.0 | Oui (manuscrit, tables, formules) | via serveur | À tester |
| Chandra 2 (Datalab) | code Apache 2.0 / poids **OpenRAIL-M** | Oui (90+ langues) | — | ⚠️ **gratuit < 2 M$ CA**, licence au-delà |
| Surya (Datalab) | GPL-3.0 + **RAIL-M** | Faible (OCR classique) | — | ⚠️ revenue-gated + faible manuscrit |
| docTR / PaddleOCR / Tesseract | Apache 2.0 / libre | **Faible (imprimé)** | — | Fallback **tapé** seulement |

- ⚠️ **Qwen2.5-VL-3B = recherche seulement** ; **72B** = licence commerciale au-delà de 100 M MAU. → rester **7B/32B**.
- ⚠️ **Surya / Chandra** sont *revenue-gated* (libres sous 2 M$ CA) : OK au départ, à re-checker à l'échelle.

**Shortlist à benchmarker** : Qwen2.5-VL-7B (lead), olmOCR (spécialisé), Pixtral-12B (famille Mistral).
Fallback imprimé si besoin : docTR/PaddleOCR. Baseline de référence : **Mistral OCR** (voie A).

Sources : [Qwen2.5-VL licences par taille](https://qwen.ai/blog?id=qwen2.5-vl) ·
[olmOCR AllenAI](https://olmocr.allenai.org/) ·
[comparatif OCR open 2026](https://modal.com/blog/8-top-open-source-ocr-models-compared)

---

## 2. Câblage technique — DÉJÀ FAIT

`prototype/llm.py` a un 3ᵉ provider **`selfhosted`** : appelle un endpoint **OpenAI-compatible**
(vLLM) via `KINE_LLM_BASE_URL`, sans dépendance ajoutée (urllib), format image objet OpenAI,
température 0, clé optionnelle (`KINE_LLM_API_KEY`), modèle surchargeable (`KINE_LLM_MODELE`).
Vérifié : requête bien formée en dry-run. **Basculer sur la voie B = variables d'env, pas de code.**

```
export KINE_LLM_PROVIDER=selfhosted
export KINE_LLM_BASE_URL=http://<gpu-hds>:8000/v1
export KINE_LLM_MODELE=Qwen/Qwen2.5-VL-7B-Instruct
```

---

## 3. Servir le modèle sur GPU HDS (esquisse)

1. **GPU Instance dans le périmètre HDS** (Scaleway : contrat HDS + support Business, périmètre
   confirmé = CPU/GPU Instances, Object/Block Storage, Bare Metal, VPC ; ou Outscale). Une L4/L40S
   suffit pour un 7B ; A100 pour 32B.
2. **vLLM** en serveur OpenAI-compatible :
   `python -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2.5-VL-7B-Instruct --port 8000`
3. Réseau **privé (VPC)** : l'endpoint n'est joignable que par notre backend, pas exposé au public.
4. `server.py` (OCR) → `llm._call_llm` → `selfhosted` → l'ordonnance va **de notre backend à notre
   GPU HDS**, et nulle part ailleurs. Rétention = ce qu'on décide (rien).

> On n'a **pas** à être soi-même certifié HDS : héberger sur une infra certifiée sous contrat HDS suffit.
> Reste à faire valider le montage par un juriste (posture projet : « diagnostic informatif »).

---

## 4. Benchmark — le harnais existe déjà

`benchmark/run_batch.py` passe par `ordonnance_ocr` → `llm._call_llm` : il benchmarke **n'importe quel
provider à iso-pipeline**. Donc comparer les candidats open à Mistral = changer une variable d'env,
sur les **mêmes ordonnances anonymisées** et les **mêmes métriques** (`benchmark/00_PROTOCOLE_BENCHMARK_OCR.md` :
champs critiques, bon acte top-1/3/5, alerte DAP, calibration confiance, **manuscrit vs tapé**).

```
KINE_LLM_PROVIDER=mistral    python benchmark/run_batch.py benchmark/ordonnances   # baseline (voie A)
KINE_LLM_PROVIDER=selfhosted KINE_LLM_BASE_URL=... KINE_LLM_MODELE=Qwen/Qwen2.5-VL-7B-Instruct \
                             python benchmark/run_batch.py benchmark/ordonnances   # candidat voie B
python benchmark/score.py benchmark/ordonnances
```

**Ce que le benchmark décide** : si un modèle open atteint le seuil du protocole (§4) sur le
**manuscrit** (le cas dur), la voie B est viable → souveraineté sans dépendre d'un tiers. Sinon : voie A
(Mistral souverain via Outscale + ZDR), ou OCR open réservé au **tapé** + saisie clic pour le manuscrit
(le produit tient quand même — l'OCR est un accélérateur, pas le moteur de valeur).

**Bloquant unique, comme toujours** : il faut les **vraies ordonnances anonymisées de Malcom**. Le
benchmark contient aujourd'hui 1 image synthétique. Sans échantillon réel, le choix voie A / voie B /
modèle se fait à l'aveugle.

---

## 5. Reste à faire
- Obtenir l'échantillon (15-20 ordonnances réelles anonymisées, manuscrites ET tapées).
- Monter une GPU HDS de test + vLLM (quelques heures ; coût GPU à l'heure, pas de contrat annuel pour tester).
- Benchmarker les 3 candidats vs Mistral ; trancher sur les chiffres.
- Prompt : les VLM open peuvent avoir besoin d'un prompt d'extraction plus explicite que Claude/Mistral
  (schéma JSON répété) — à ajuster dans `ordonnance_ocr.SYSTEME` si le taux de JSON valide est bas.
