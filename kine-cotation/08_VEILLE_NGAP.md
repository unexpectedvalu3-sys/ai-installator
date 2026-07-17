# KinéCotation — Veille NGAP & releases

> 2026-07-17. Demande d'Enzo : « il faudrait que ça check la dernière release de la db
> et qu'on fasse des release auto si jamais il y a du changement ».

---

## 1. Le partage — et pourquoi je ne suis la demande qu'à moitié

| Étape | Qui | Pourquoi |
|---|---|---|
| **Détecter** un nouveau tableau SNMKR | 🤖 **auto** (lundi 06:00 UTC) | Aucun risque. Le barème a bougé 3× en 8 mois : personne ne peut surveiller ça à la main. |
| **Mettre à jour `ngap_kine.json`** | 👤 **Enzo** | ⛔ **Jamais automatique.** Voir §2. |
| **Builder + publier l'app** | 🤖 **auto** (sur le commit de la base) | Le déclencheur est **ta validation** → tout automatiser est sûr. Zéro corvée entre « la base est juste » et « le kiné a la bonne version ». |

**Tu as raison sur la release, pas sur la mise à jour de la base.**

## 2. Pourquoi la base ne se met JAMAIS à jour toute seule

`00_PROJECT_PLAN.md` §9 classe en risque **🔴 critique** : « données NGAP fausses → mauvaise
cotation → **on cause un indu** ». Une chaîne scrape-PDF → release automatique pousserait des
coefficients non vérifiés chez tous les kinés — **et la justification générée les attesterait**.
On ne se contenterait pas de faire perdre de l'argent : on signerait l'erreur.

Le diff automatique est fiable sur ce qu'il lit (couverture mesurée : **91/91 triplets**), mais il
ne lit que `(code, coefficient, tarif)`. **Il ne voit pas** : à quel acte rattacher un triplet (il y
a plusieurs `TER`, plusieurs `NMI` — et `NMI 11,01` est à la fois la valeur *actuelle* de la
paraplégie et la valeur *future* de l'atteinte périphérique multiple) ; les actes ajoutés ou
supprimés ; les libellés remaniés ; les seuils DAP ; les référentiels HAS ; les champs éditoriaux
(article, région, chirurgie, référentiel). **Ce sont des jugements humains.**

> Le veilleur lève l'alarme et montre l'écart. Enzo tranche.

## 3. Le veilleur a payé dès son premier run

`tools/check_ngap_release.py` a trouvé, contre le tableau v19, **deux écarts que ma vérification à
la main du matin (v1.1) avait manqués** :

1. **🔴 Bug de lettre-clé** — « Affection du coude ou de l'avant-bras **non opérée** » était codée
   **`VSC`** (le code de l'acte *opéré*) au lieu de **`VSM`**. Tarif identique (17,88 €) → **invisible
   à un diff de tarifs**. Mais une mauvaise lettre-clé, c'est un rejet de télétransmission ou un indu.
   Détectée parce que le diff indexe sur `(code, coefficient)`, pas sur le tarif.
2. **Le 01/09 touche 5 actes, pas 1** — j'en avais encodé un seul. Les cinq NMI neuro prennent
   +1 point : para/tétraplégie 11,01→12,01 · déficiences 2 membres+ 10→11 · myopathie 10,99→11,99 ·
   encéphalopathie 11→12 · atteinte périphérique multiple 10,01→11,01.

→ **Base v1.2 : 91/91 triplets réconciliés avec le tableau officiel.** Vérifié par machine, plus par mon œil.

## 4. Les pièces

- **`tools/check_ngap_release.py`** — lit la page SNMKR, prend le PDF le plus récent, compare à
  `_meta.source_url`, et si drift : télécharge, extrait (poppler `pdftotext -layout`), diffe, rapporte.
  Sorties : `0` à jour · `2` drift · `1` erreur. `--json` pour la CI.
  Les cotations **futures** (`_paliers`) sont incluses dans la comparaison — sinon les 5 NMI du 01/09
  seraient signalées « absentes de la base » à chaque passage : **une fausse alarme permanente
  apprend à ignorer l'outil**, et c'est l'alerte DAP qui en meurt.
- **`.github/workflows/ngap-watch.yml`** — lundi 06:00 UTC. Drift → ouvre (ou commente) une issue
  avec le diff. Ne touche à rien.
- **`.github/workflows/kine-release.yml`** — sur push touchant la base → build + release
  `kine-v<version>` avec `kinecotation.html`.
  **Garde-fou** : si l'app n'embarque pas la version de la base, **le build casse**. Une app qui
  porterait un vieux barème produirait une justification qui atteste le mauvais barème — le pire
  échec possible pour un produit dont la promesse est la preuve.

## 5. Reste à faire

- **Diffuser au kiné** : la release GitHub existe, mais l'app ne va pas encore la chercher.
  Rebrancher le mécanisme déjà éprouvé du comparateur (GitHub Releases + cache local + repli
  embarqué) — cf. [[comparateur-courtier-app]].
- ~~Le moteur ne gère pas les cotations datées~~ → **fait (base v1.3)**. `_futur` (une marche)
  remplacé par `_paliers` (liste). Le moteur Python et l'app résolvent le palier **à la date de la
  séance**, avec parité vérifiée sur 25 combinaisons. `_meta.applicable_depuis` ajouté : la base
  n'ayant pas d'historique avant le 28/05/2026, coter une séance antérieure est **refusé** plutôt
  que de rendre un barème faux que la justification attesterait.
- ~~Confirmer l'année du « 01/09 »~~ → **fait : 2026, source primaire.** Avenant 7 §C (arrêté du
  21/08/2023, [JORFTEXT000047995983](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000047995983)) :
  « *Les dispositions du présent C s'appliquent à compter du 1er septembre 2026* », visant les actes de
  l'**article 4** dont le **coefficient est 10 ou 11**, revalorisés d'**un point** → correspond exactement
  aux 5 actes encodés.
- ⚠️ **Mais la date est doublement conditionnelle** (base v1.4, paliers marqués `conditionnel`) :
  (a) « sous réserve d'une modification préalable de la liste des actes » (art. L. 162-1-7) ;
  (b) exposée au **comité d'alerte ONDAM** — précédent : juin 2025 a gelé les revalorisations de juillet
  2025, ce qui est la raison d'être de l'avenant 8. Avis 2026-1 (20/04) écarte le dépassement sérieux ;
  avis 2026-2 (25/06) « n'écarte pas le risque » et appelle à annuler les mises en réserve — formulation
  de **vigilance**, pas le constat de « risque sérieux » qui déclenche l'alerte. **Lecture d'après presse,
  avis non lu (paywall)** → à re-vérifier avant le 01/09. Si alerte : report au **01/01/2027**.
### Échéances connues, volontairement PAS dans la base (`_meta._a_surveiller`, v1.5)

Le veilleur les rappelle **à chaque passage** avec le décompte des jours — sinon une note dort dans un
JSON que personne ne relit et l'échéance passe.

**1. Bilan de repérage de la fragilité — AMK 10 (22,10 €), au 01/09/2026** ✅ *vérifié au livret officiel
de l'Ordre MK (p.6)* : « *personnes âgées de **70 ans ou plus*** […] nouvel acte au **chapitre I des actes
de diagnostic** du titre XIV […] **coté AMK 10**. Cet acte est réalisé **sur prescription médicale ou à
l'initiative du masseur-kinésithérapeute** […]. Le **compte rendu** doit être adressé au **médecin
traitant** […]. Ces dispositions s'appliquent à compter du **1er septembre 2026 sous réserve d'une
modification préalable de la liste des actes** (art. L. 162-1-7). »

> ⚠️ **Trois erreurs de presse que j'avais rapportées, corrigées par le livret** : l'acte n'est **pas**
> réservé à l'exercice coordonné (ESP/ESS/CDS/MSP) et n'est **pas** limité à 8 séances — ces conditions
> appartiennent à la section **accès direct**, un dispositif différent. Et la FAQ SNMKR annonce le
> *1er juillet 2026* : **périmée**, le livret dit 1er septembre.

**2. +0,3 point au 01/07/2027 sur ~12 lettres-clés** (RAM, RAO, RSC, RSM, RIC, RIM, VIM, VIC, VSM, VSC,
DRA, APM — ex-AMS 7,5, soit **le gros du catalogue**). *Trouvé dans le livret p.5* : « *0,9 point en
2 étapes : +0,6 au 1er juillet 2025 ; +0,3 au 1er juillet 2027* » (le +0,6 a été gelé par l'alerte ONDAM
puis appliqué au 01/01/2026 — il est déjà dans les coefficients actuels). Personne ne l'avait vu.

**Pourquoi on ne les ajoute pas maintenant** — les deux sont **absents du tableau SNMKR v19**, notre
source unique. Pour le bilan fragilité, cette absence à 6 semaines de l'échéance est en soi
l'information : la modification de la LAP n'a pas eu lieu. Les ajouter briserait la réconciliation
**91/91** et créerait une **fausse alarme permanente** du veilleur — ce qui apprend à ignorer l'outil, et
c'est l'alerte DAP qui en meurt. On attend que le SNMKR publie : le veilleur les verra apparaître en
« absent de la base ». **On ne devance pas la source.**

- Le veilleur ne surveille que le SNMKR. Un avenant paraît d'abord au **JO** — une veille Légifrance
  donnerait de l'avance, mais le tableau SNMKR reste la source de la base.

> **Risque asymétrique, et c'est ce qui dicte le design** : appliquer un palier qui n'entre pas en vigueur
> → le kiné **surcote → indu** ; l'ignorer à tort → il sous-cote (perte, sans risque légal). Dans un produit
> dont la promesse est la défendabilité, la faute à ne pas causer est la première. Le moteur et l'app
> **affichent une réserve** au lieu de changer le tarif en silence.
