# Support de démo — KinéCotation (RDV kiné design partner)

> Objectif du RDV : valider l'outil, **chiffrer la sous-cotation récupérée**, enrôler le kiné comme design partner. Durée cible : 20-25 min.

---

## 0. Setup (2 min avant le RDV)

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."          # clé dispo dans modulr-app/.env
cd C:\Users\test\Documents\Claude\Projects\ai-installator\kine-cotation\webapp
python server.py                                # → http://localhost:8770
```
Ouvre `http://localhost:8770` dans le navigateur. **Remplis ton profil une fois** (onglet « Mon profil ») — ou utilise les coordonnées du kiné s'il est là, effet « c'est déjà à ton nom ».

Cas de démo prêts (dossier `prototype/`) :
- `test_ordonnance.png` → **PTG genou, 30 séances** → déclenche l'alerte DAP (le cas qui vend).
- `ordo_lombalgie.png` → **lombalgie, 10 séances** → cas « normal » sans alerte (contraste).

---

## 1. Ouverture — la douleur (30 s, à dire)

> « Aujourd'hui tu sous-cotes par sécurité pour éviter l'indu de la CPAM. Résultat : tu perds du CA à chaque séance, ET tu n'es jamais sûr d'être en règle. Je te montre un outil qui supprime ce dilemme : il te donne la cotation **maximale légale** ET la **justification** pour te défendre, en 20 secondes. »

---

## 2. Démo en 3 actes

### Acte 1 — L'arbre de décision (le cœur) · 3 min
1. Onglet **Cotation**. Région → **Membre inférieur**.
2. Opéré ? → **Oui**. Référentiel ? → **Oui**.
3. Clique **RIC 8.12 — Après arthroplastie du genou (PTG)**.
4. Dans la ligne, saisis **n° séance : 30**.
5. 👉 **Le money shot** : l'alerte rouge **« DAP REQUISE — dès la 26ᵉ »** s'affiche.
   > « Là, sans cet outil, soit tu factures et tu prends un indu sur 3 ans, soit tu sous-cotes. Lui, il te le dit avant. »
6. Clique **+ Bilan (BDK)** → choisis le 10.7. Coche **À domicile**, 15 km.
7. Montre la **feuille de soins** : total, à ton en-tête, avec la **justification anti-indu** prête à archiver.

### Acte 2 — L'OCR : scanner l'ordonnance · 3 min
1. Clique **Importer une ordonnance** → choisis `test_ordonnance.png`.
2. 👉 Le panneau **« Ordonnance lue »** apparaît : patient, pathologie, **30 séances**, domicile, bilan, confiance.
3. Clique l'acte proposé **RIC 8.12** → la feuille se remplit, domicile auto-coché, **DAP déclenchée sans rien retaper**.
   > « Tu photographies, tu valides. C'est tout. »
4. (Honnêteté) : « Sur du manuscrit bien gribouillé, on validera le taux ensemble — mais même si l'OCR doute, l'arbre marche au clic. »

### Acte 3 — La personnalisation + le PDF · 1 min
1. Onglet **Mon profil** : montre que nom, RPPS, n° de facturation, conventionnement sont stockés.
2. Reviens, **Imprimer / PDF** → la feuille sort à son en-tête, prête à classer/donner.

---

## 3. Le money shot chiffré (le plus important) · 5 min

> Sors une feuille blanche. Demande-lui de **coter à la main 3 de ses ordonnances récentes**, comme il le fait au quotidien. Puis refais-les dans l'outil. **Note les écarts.**

| Ordonnance | Sa cotation | Cotation outil | Écart |
|-----------|-------------|----------------|-------|
| 1 | … | … | +… € |
| 2 | … | … | +… € |
| 3 | … | … | +… € |

→ **Écart moyen × nb séances/an = le manque à gagner annuel.** C'est ton argument de vente n°1 et son ROI personnel.

---

## 4. Objections / FAQ (préparées)

| Il dit… | Tu réponds… |
|---------|-------------|
| « L'écriture des médecins est illisible » | « L'OCR est un accélérateur, pas le moteur. S'il rate, tu cliques 4 réponses. Et on va mesurer le vrai taux ensemble sur tes ordos. » |
| « J'ai déjà VEGA » | « On ne remplace pas VEGA. Lui transmet ta FSE ; nous on te dit **quoi coter** et on te couvre sur l'indu — ce qu'il ne fait pas. Complément. » |
| « C'est légal de coter plus ? » | « On ne cote pas *plus*, on cote *juste* — la cotation que la NGAP autorise pour l'acte réellement fait. La sous-cotation, c'est toi qui te pénalises. » |
| « Et mes données patients ? » | « Pour la prod : hébergement HDS + tu restes responsable. Le profil et les ordos restent sur ton poste en l'état actuel. » |
| « C'est toi qui factures à ma place ? » | « Non. C'est une **aide à la décision** + un justificatif. Tu valides et tu restes responsable — c'est écrit sur chaque feuille. » |

---

## 5. Le call-to-action

> « Je cherche **un kiné design partner** pour caler l'outil sur le terrain. En échange : tu l'utilises gratuitement, tu me donnes 15-20 ordonnances (anonymisées) pour mesurer l'OCR, et tu deviens mon cas de référence. Deal ? »

**Ce que tu repars avec, idéalement :**
1. Les **3 écarts de sous-cotation chiffrés** (= la preuve ROI).
2. Une **pile d'ordonnances réelles** (dont manuscrites) → lancer le [benchmark OCR](benchmark/00_PROTOCOLE_BENCHMARK_OCR.md).
3. Sa **liste de cas tordus** au quotidien (cumuls, cas limites) → backlog produit.
