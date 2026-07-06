# Protocole de benchmark OCR — ordonnances manuscrites

> Objectif : **chiffrer** le taux d'extraction de l'OCR sur de vraies ordonnances
> (manuscrites + tapées) → décision go/no-go de la feature OCR. On mesure, on ne débat pas.

---

## 0. ⚠️ RGPD — à lire AVANT de photographier

Une ordonnance = **donnée de santé**. L'image est envoyée à l'API Anthropic (sous-traitant).
Pour ce benchmark :

1. **Anonymiser chaque ordonnance AVANT la photo** : caviarder (feutre noir / bande) le **nom,
   prénom, date de naissance, NIR** du patient. On ne garde que le **contenu clinique**
   (pathologie, zone, nb séances, mentions). Le prescripteur peut rester.
2. **Pas de stockage cloud** des images. Travail local, dossier supprimé après le benchmark.
3. Pour la **production** (pas le benchmark) : hébergement **HDS** + DPA avec le fournisseur LLM
   obligatoires. Le benchmark sur images anonymisées ne vaut pas mise en production.

---

## 1. Échantillon

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
