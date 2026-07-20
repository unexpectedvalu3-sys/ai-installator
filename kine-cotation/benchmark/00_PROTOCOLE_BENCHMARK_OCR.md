# Protocole de benchmark OCR — ordonnances manuscrites

> Objectif : **chiffrer** le taux d'extraction de l'OCR sur de vraies ordonnances
> (manuscrites + tapées) → décision go/no-go de la feature OCR. On mesure, on ne débat pas.

---

## 0. ⚠️ RGPD — à lire AVANT de photographier

Une ordonnance = **donnée de santé**. L'image **sort du poste** vers le provider IA
(sous-traitant). C'est le SEUL endroit du produit où une donnée de santé circule —
le moteur, la KB et le dossier de preuve sont 100 % locaux et déterministes.

Pour ce benchmark :

1. **Anonymiser chaque ordonnance AVANT la photo** : caviarder (feutre noir / bande) le **nom,
   prénom, date de naissance, NIR** du patient. On ne garde que le **contenu clinique**
   (pathologie, zone, nb séances, mentions). Le prescripteur peut rester.
2. **Pas de stockage cloud** des images. Travail local, dossier supprimé après le benchmark.
3. **Provider** : par défaut **Mistral** (éditeur français, serveurs UE) — cf. `llm.py` et
   `06_PROVIDER_IA.md`. Le benchmark sur images **anonymisées** ne requiert pas de ZDR.

> ⚠️ **Corrigé le 2026-07-17** — l'ancienne rédaction disait « Pour la production : hébergement
> **HDS** + DPA obligatoires ». **Décision prise : architecture local-first** (le dossier de preuve
> reste chez le kiné → on n'héberge rien pour le compte d'un tiers → **l'HDS n'a pas d'objet**).
> Ce qu'il faut réellement pour la **production sur données réelles** :
> - **Mistral Enterprise + Zero Data Retention** (le ZDR n'est PAS sur l'offre standard) — sans
>   rétention, pas d'hébergement, donc pas d'HDS ;
> - **DPA art. 28** avec Mistral, et convention art. 28 avec le kiné ;
> - ⚠️ **« La Plateforme » n'est pas qualifiée HDS** à ce jour. Mistral héberge à Paris chez
>   Scaleway (certifié HDS), mais l'hébergeur certifié **ne transfère pas** sa qualification au
>   service — ne pas confondre les deux.
>
> Le benchmark sur images anonymisées ne vaut toujours pas mise en production.

---

## 0 bis. Sources de données de test (peut-on trouver des banques en ligne ?)

Un benchmark teste **deux axes distincts** — et une banque publique n'en couvre qu'un :
- **Axe 1 — lire le manuscrit FR** : le modèle déchiffre-t-il l'écriture cursive française ?
- **Axe 2 — extraction métier kiné** : zone / chirurgie / séances / pathologie + la cotation + la
  DAP qui en découlent. **Aucune banque publique ne couvre l'axe 2** (structure NGAP kiné FR).

| Source | Ce qu'elle teste | Licence / accès | Verdict |
|---|---|---|---|
| **Synthétique** (`prototype/make_test_ordonnance.py`) | Axe 2 **entier** + axe 1 sur le **tapé** + le prompt (JSON) | fictif, généré, **vérité terrain gratuite** | ✅ **à utiliser en 1er** (aucune donnée patient) |
| **RIMES** (Teklia/RIMES-2011-line, HF) | Axe 1 : **manuscrit FR** (courriers, pas ordonnances) | MIT, recherche | ✅ **1er filtre manuscrit** des modèles candidats |
| **`MMMuzammil/Medical_Prescription_Handwritten_Words`** (HF, 46 img : 36 mots + 10 chiffres) | Axe 1 **manuscrit médical**, **non-FR** (noms de médicaments EN), mots isolés | **MIT** | ✅ **2ᵉ filtre licite utilisé** (2026-07-20) → `benchmark/doctor_handwriting.py`, cf. `11_` §4 quater |
| Kaggle « Doctor's Handwritten Prescription BD » (4680 img) | Axe 1 manuscrit médical, **non-FR** | ouvert (Kaggle, auth requise) | 🟠 non testé (auth Kaggle) — miroirs HF sans licence explicite écartés (ligne rouge) |
| Kaggle « Doctor Handwriting Recognition » (Pakistan, 90 img) · HF `chinmays18`, `Technoculture` (ordonnances entières) | Axe 1, non-FR | ouvert / **licence absente sur HF** | 🔴 écartés : **pas de licence explicite** (ligne rouge) |
| **Ordonnances kiné FR (images)** | Axes 1+2 réels | **n'existe pas** en public | ❌ → vraies ordonnances anonymisées de Malcom |

> ⚠️ **Ligne rouge** : n'utiliser QUE des jeux de recherche sous licence. **Ne jamais scraper** de
> vraies ordonnances trouvées en ligne — ce sont des données de santé, même « publiques ».

**Séquence recommandée** : (1) **synthétique** maintenant → valide la chaîne extraction+cotation+DAP
et élimine les modèles au prompt fragile ; (2) **RIMES** → filtre l'aptitude au manuscrit FR des 3
candidats voie B (`11_VOIE_B_OCR_OPEN.md`) avant de payer du GPU ; (3) **vraies ordonnances
anonymisées de Malcom** → seul go/no-go réel (axes 1+2, écriture + métier).

### Jeu synthétique fourni
`python prototype/make_test_ordonnance.py` → **10 ordonnances** couvrant l'espace de décision (genou
PTG opéré, LCA, coiffe opérée, entorse, lombalgie, cervicalgie, hémiplégie, fracture avant-bras,
respiratoire, une **incomplète**) dans `benchmark/synthetiques/`, **avec `verite_terrain.csv`
auto-résolu contre la base** (acte_id + seuil DAP). Cohérence vérifiée (bon acte selon chirurgie,
bon seuil). **Limite assumée** : ce sont des ordonnances **tapées** (corps pseudo-manuscrit), pas de
la vraie écriture → l'axe 1 manuscrit reste pour RIMES + Malcom.

---

## 1. Échantillon (vraies ordonnances)

- **15 à 20 ordonnances réelles** fournies par le kiné design partner.
- **Variées** : manuscrites ET tapées, plusieurs pathologies/zones (rachis, genou, épaule,
  respiratoire…), avec et sans chirurgie, avec et sans nombre de séances explicite.
- Étiqueter chaque fichier `ordo_01.jpg`, `ordo_02.jpg`, … (le nom = l'`id`).
- Noter à part lesquelles sont **manuscrites** vs **tapées** (colonne `type` de la vérité terrain)
  → c'est LA segmentation qui répond à ta question.

---

## 2. Procédure

1. Mettre les images anonymisées dans un dossier, ex. `benchmark/ordonnances/`.
2. **Lancer l'extraction batch** :
   ```
   set ANTHROPIC_API_KEY=sk-ant-...      (ou $env: en PowerShell)
   python benchmark/run_batch.py benchmark/ordonnances
   ```
   → produit `predictions.csv`, `verite_terrain_modele.csv` (à remplir) et `catalogue_actes.csv`.
3. **Le kiné remplit la vérité terrain** : ouvrir `verite_terrain_modele.csv`, et pour chaque
   ordonnance indiquer ce qu'il **facturerait réellement** (chirurgie, nb séances, bilan, domicile,
   et l'`acte_id` correct lu dans `catalogue_actes.csv`). Enregistrer sous `verite_terrain.csv`.
4. **Scorer** :
   ```
   python benchmark/score.py benchmark/ordonnances
   ```
   → affiche le rapport + écrit `rapport_benchmark.csv`.

---

## 3. Ce qu'on mesure

| Métrique | Définition | Pourquoi |
|----------|------------|----------|
| **A. Champs critiques** | % exact sur `chirurgie`, `nb_seances`, `bilan`, `domicile` | Ces champs décident la cotation + la DAP |
| **B. Utilité cotation** | Le bon acte est-il dans le **top-1 / top-3 / top-5** des candidats ? | C'est la vraie valeur produit (gain de temps réel) |
| **C. Alerte DAP** | L'alerte DAP prédite = l'attendue ? | Le cœur anti-indu |
| **D. Calibration confiance** | Taux d'erreur quand `confiance=low` vs `high` | Si "low" prédit bien les ratés, le kiné sait quand se méfier |
| **E. Manuscrit vs tapé** | Toutes les métriques ci-dessus, **séparées** par type | **La réponse directe à la question du frein** |

---

## 4. Seuils go / no-go (proposés)

Lecture sur la **sous-population manuscrite** (le cas dur) :

| Résultat manuscrit | Décision |
|--------------------|----------|
| Champs critiques **≥ 80%** ET bon acte top-3 **≥ 80%** | ✅ OCR vend → on industrialise, communication "scanne et valide" |
| **60–80%** | 🟠 OCR en *assist* avec validation systématique ; communication prudente ("pré-remplissage") |
| **< 60%** | 🔴 OCR réservé au **tapé** ; saisie clic pour le manuscrit. **Le produit tient quand même** (catalogue + DAP + anti-indu intacts) |

> Rappel : même un OCR moyen ne casse pas le produit — le kiné valide toujours, et la cotation/DAP
> reste exacte. L'OCR est un **accélérateur**, pas le moteur de valeur.

**Bonus important** : une confiance bien calibrée (D) compte presque autant que l'accuracy. Un OCR à
70% mais qui *sait* quand il doute (et bascule sur l'arbre) est utilisable ; un OCR à 70% trop sûr de
lui ne l'est pas.

---

## 5. Sortie attendue

`rapport_benchmark.csv` + un récap console du type :

```
ÉCHANTILLON : 18 ordonnances (11 manuscrites, 7 tapées)
A. Champs critiques (exact) :  tapé 96%  |  manuscrit 78%
B. Bon acte top-3 :            tapé 100% |  manuscrit 82%
C. Alerte DAP correcte :       17/18
D. Calibration : erreurs sur confiance=low 4/5, sur high 1/13  → calibrée
→ Verdict : zone 60-80% manuscrit → OCR en assist + validation. Go prudent.
```
