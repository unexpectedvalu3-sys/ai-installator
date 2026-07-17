# KinéCotation — fournisseurs OCR pour ordonnances NOMINATIVES

> 2026-07-18. But : trouver un OCR qui permette d'envoyer des ordonnances **sans anonymiser**
> (donc données de santé identifiées) de façon LICITE. Le critère décisif n'est pas la qualité
> OCR, c'est le statut réglementaire : **HDS + non-rétention (ZDR) + DPA**, éditeur FR/UE.

---

## Le verdict en une phrase

**Aucun fournisseur ne coche tout (HDS-du-service + ZDR + API publique + prix) de façon confirmée
en self-service.** Le flux nominatif reste donc une démarche de **procurement + juridique**, comme
le contrat Mistral Enterprise — pas un interrupteur de code. Mais la recherche dégage un lead
crédible qui **réutilise l'OCR Mistral qu'on a déjà intégré**.

Piège à garder en tête partout : « **hébergé chez** un certifié HDS » ≠ « le **service** est certifié
HDS ». L'infra peut être HDS sans que l'API OCR le soit. À confirmer service par service.

---

## Le lead : Outscale + Mistral Document AI

**Outscale** (groupe Dassault) est certifié **SecNumCloud 3.2 + HDS** (infra), et propose la couche
**Mistral Document AI OCR** sur sa marketplace souveraine.
[outscale.com/secnumcloud-3-2](https://en.outscale.com/secnumcloud-3-2/) ·
[docs.mistral.ai OCR santé](https://docs.mistral.ai/resources/cookbooks/mistral-ocr-hcls-ocr_hcls)

Pourquoi c'est le meilleur candidat :
- **On garde Mistral OCR** (OCR 4 : bounding boxes, scores de confiance) → notre `prototype/llm.py`
  bascule dessus en **changeant l'endpoint**, pas en réécrivant. L'abstraction provider paie ici.
- Souveraineté française réelle (SecNumCloud, au-dessus de la simple région UE), meilleure posture
  que Mistral « La Plateforme » côté US-adjacent.

À confirmer AVANT de s'engager (les 3 questions décisives) :
1. Le **service OCR lui-même** est-il dans le périmètre du certificat HDS d'Outscale, ou seulement
   l'infra qui l'héberge ?
2. **Rétention** : l'offre packagée garantit-elle la non-rétention / non-réentraînement ?
3. **DPA art. 28** dédié + **prix** (aucune grille publique trouvée).

---

## Le backup : Docaposte

**Docaposte** (filiale La Poste), **certifié HDS** sur une partie de son offre (archivage SAE
confirmé), éditeur santé FR natif, avec une **API LAD/OCR** existante.
[docaposte.com HDS](https://www.docaposte.com/bibliotheque-de-contenu/cp-hds-docaposte.pdf) ·
[docaposte.com santé](https://www.docaposte.com/solutions/logiciels-metiers-et-services-numeriques-en-sante)

À confirmer : l'**API OCR/extraction** est-elle dans le périmètre HDS (pas seulement l'archivage) ?
Non-rétention ? Prix / SLA / adapté à un volume PME ? (Vente entreprise probable, pas self-service.)

---

## Écartés / à ne pas confondre

| Fournisseur | Pourquoi pas (pour l'instant) |
|---|---|
| **Scaleway Generative APIs** | **ZDR par défaut** (bon !) mais statut **HDS non confirmé** pour Generative APIs spécifiquement. À revérifier — pourrait devenir un bon candidat. |
| **OVHcloud AI Endpoints** | ZDR annoncé, mais **pas HDS** sur ce produit (demande client ouverte, nov. 2025). OVH est HDS ailleurs, pas ici. |
| **Lifen** | Certifié HDS, santé — mais **aucun endpoint OCR public** (outil interne à leur suite). Pas exploitable en API. |
| **Mindee**, **Koncile** | FR, API OCR publiques (Koncile a même une page « extraction ordonnance ») **mais HDS non prouvé** (Koncile : formulation ambiguë, pas de n° de certificat ; Mindee : pas HDS, hébergement EU/US au choix). |
| **Mistral « La Plateforme » (direct)** | HDS **non confirmé** en direct ; ZDR réservé à **Enterprise** (source tierce). C'est notre intégration actuelle — OK pour le test **anonymisé**, pas pour le nominatif. |
| **Azure / AWS / Google Document Intelligence** | US ; HDS France **non confirmé** par source officielle du fournisseur (seule une source tierce l'affirme). |

---

## Ce que ça change pour le projet

- **Rien ne débloque le flux nominatif aujourd'hui sans contrat.** Le message à Malcom reste :
  ordonnances **anonymisées** en test (cf. `06_PROVIDER_IA.md`, `09_HEBERGEMENT.md`).
- **Le travail technique est déjà fait** : l'abstraction `llm.py` rend le changement de fournisseur
  quasi trivial. Le blocage est côté contrat/juridique, chez toi.
- **Prochaine action utile** (à toi) : demander un devis + les réponses aux 3 questions décisives à
  **Outscale/Mistral** (lead) et **Docaposte** (backup). Je peux rédiger le mail de qualification
  fournisseur (les 3 questions + volume + besoin DPA) si tu veux.

## INCERTITUDES

- Périmètre HDS exact des services OCR (Outscale/Mistral, Docaposte) : **non confirmé** — c'est LA
  question à poser en direct.
- Aucun prix public trouvé pour les candidats santé (Outscale/Mistral packagé, Docaposte, Lifen).
- Statut HDS de Scaleway Generative APIs et OVHcloud AI Endpoints : en évolution, à resurveiller.
- Recherche = 10 requêtes web (agent Sonnet). Faits sourcés ; tout « non confirmé » l'est resté.
