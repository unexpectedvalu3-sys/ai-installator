# KinéCotation — règles de CUMUL NGAP (anti-indu, volet n°2)

> 2026-07-22. Déclencheur : Enzo — « si le kiné fait plusieurs actes, l'app dit-elle qu'il ne peut pas
> les combiner ? c'est ça l'intérêt. » Constat : l'app **additionnait sans avertir** → total potentiellement
> illégal = l'indu qu'on promet d'éviter. ⚠️ **Sujet critique : une règle de cumul FAUSSE cause un indu.**
> Donc ici, on n'encode QUE le certain-sourcé ; le flou est marqué « à confirmer », jamais deviné.

---

## 1. La règle qui décide de tout — CONFIRMÉE

**On ne cote qu'UNE SEULE cotation de rééducation par séance.** Deux actes de rééducation ne se
cumulent pas.

> « Sauf exceptions prévues dans le texte, ces cotations ne sont pas cumulables. À chaque séance, une
> seule cotation s'applique donc, correspondant au traitement de la pathologie ou du territoire
> anatomique en cause. » — mémos NGAP masso-kiné (Assurance Maladie).

Sources : [mémo ameli M-Kiné](https://www.ameli.fr/sites/default/files/memo_m-kine_livret_a4_bat_web_13net.pdf) ·
[guide pratique NGAP masso-kiné AURA (jan. 2025)](https://actus-ps-74.cpam-haute-savoie.fr/sitepad-data/uploads/2025/01/GUIDE-PRATIQUE-DE-LA-NGAP-MASSO-KINESITHERAPIE_Assurance-Maladie-AURA_janvier-2025.pdf) ·
[NGAP officielle](https://sarthe.ordremk.fr/files/2019/10/NGAP-version-du-1er-septembre-2019.pdf)

**Corollaire produit essentiel** : plusieurs zones/territoires ne se codent PAS en additionnant deux
actes de zone — il existe des actes dédiés **« plusieurs territoires lésés » (article 1D, code TER)**
justement pour ça. Additionner deux actes de zone = surcotation.

**Exception = article 11B** : quand un cumul est permis, le 2ᵉ acte est coté à **50 %** de son
coefficient. Mais l'app ne l'applique PAS automatiquement (voir §4 : quand 11B s'applique reste à
cadrer précisément).

---

## 2. Ce qui SE cumule (catégories distinctes) — solide

Ces éléments ne sont pas des « actes de rééducation » concurrents : ils s'ajoutent.
- **Bilan diagnostic kinésithérapique (BDK, AMK)** — acte de diagnostic (chapitre I), facturable à des
  séances définies (1ʳᵉ, 30ᵉ, puis toutes les 20 ; neuro : 60ᵉ puis 50). Facturable dès la 1ʳᵉ séance
  dès qu'une rééducation est prescrite. [ameli — BDK](https://www.ameli.fr/masseur-kinesitherapeute/exercice-liberal/facturation-remuneration/tarifs-conventionnels/bilan-diagnostic-kinesitherapique).
  ⚠️ **À confirmer** : cumul BDK + séance de rééducation LE MÊME JOUR — les sources disent « sous
  certaines conditions » sans trancher net. À valider (kiné / ameli) avant d'en faire une règle dure.
- **Suppléments** (kinébalnéothérapie AMK 2,5/3,5 ; bandage multicouche RAV) — ce sont des
  « suppléments » par nature → cumulables avec l'acte de base. Conditions exactes à confirmer.
- **Déplacement** (IFD/IFS + IK) — indemnités accessoires, cumulables avec l'acte. **IFD et IFS ne se
  cumulent PAS entre elles** (déjà dans la base, `_note` déplacements).

---

## 3. Ce qui est fait dans l'app (2026-07-22) — garde-fou sur le CERTAIN uniquement

Alerte **« ⚠ Cumul à vérifier »** en tête de feuille dès que le panier contient **≥ 2 actes de
rééducation** (les actes du catalogue `actes` — repérés par `region != null` ; bilans/suppléments
`region == null` sont exclus, ils se cumulent). Le message :
- rappelle la règle (une seule cotation de rééducation par séance) ;
- pointe vers l'acte « plusieurs territoires » (art. 1D) comme codage correct du multi-zone ;
- signale que le total additionne à 100 % et est **à corriger** si le cumul n'est pas permis.

**On NE bloque PAS** (aide à la décision, le kiné valide) et **on ne recalcule PAS** le total (appliquer
le 11B à 50 % est une règle à confirmer — mieux vaut alerter que trancher faux). C'est le même principe
que l'alerte DAP.

---

## 4. Reste à confirmer (avant toute règle DURE) — action Enzo/kiné
- Cumul **BDK + séance** le même jour : oui/non/conditions.
- Périmètre exact de l'**article 11B** en kiné (dans quels cas un 2ᵉ acte est permis à 50 %).
- Cumul **rééducation + autre acte** distinct le même jour (ex. drainage lymphatique + rééducation).
- Conditions de cumul des **suppléments** (balnéo nécessite l'équipement ; bandage).
→ **Session dédiée avec Malcom** sur ses cas réels : c'est là qu'on figera les règles fines, comme pour
la sous-cotation. Le garde-fou §3 protège déjà du cas le plus courant et le plus grave (2 rééduc sommées).

---

## 5. Structure de données proposée (NON implémentée)
Quand les règles fines seront confirmées, les encoder dans `ngap_kine.json._meta` :
```
"_cumul": {
  "un_acte_reeduc_par_seance": true,
  "exception_11B_second_a_50pct": true,
  "cumulables_avec_acte": ["bilans", "supplements", "deplacements"],
  "non_cumulables_entre_elles": [["IFD","IFS"]],
  "a_confirmer": ["BDK+seance meme jour", "reeduc+drainage"]
}
```
Le moteur (Python `cotation_engine` + miroir JS) lirait ça au lieu de coder les règles en dur.
