# Recherche — NGAP Kiné 2024 (Avenant 7)

> Synthèse domaine pour KinéCotation · 2026-06-27 · sources en bas.

---

## 1. La réforme (ce qui a tout compliqué)

- **Entrée en vigueur : 22 février 2024**, via l'**avenant 7** à la convention nationale des masseurs-kinésithérapeutes.
- **80 nouveaux actes** ajoutés à la NGAP.
- **20 nouvelles lettres-clés** classant les actes par **région du corps** + **contexte chirurgical** + **référentiel pathologie**.
- Possibilité (sous conditions) de facturer **2 séances le même jour** depuis fév. 2024.

## 2. La logique des lettres-clés (cœur de l'arbre de décision)

**Règle mnémotechnique (structure du code) :**
- **1ʳᵉ position** → domaine / pathologie
- **2ᵉ position** → zone anatomique : **S** = membre supérieur · **I** = membre inférieur
- **3ᵉ position** → prise en charge : **C** = chirurgie · **M** = médicale
- **R** = dans le **référentiel** pathologie · **V** = **hors référentiel** (variable)

### Tableau des lettres-clés

| Code | Domaine | Zone | Chir/Méd | Référentiel |
|------|---------|------|----------|-------------|
| **RAM** | Rachis non opéré | Rachis | Médical | — |
| **RAO** | Rachis opéré | Rachis | Chirurgical | — |
| **DRA** | Déviation du rachis | Rachis | — | — |
| **RSM** | Membre supérieur non opéré | Sup | Médical | Oui (R) |
| **RSC** | Membre supérieur opéré | Sup | Chirurgical | Oui (R) |
| **VSM** | Membre supérieur non opéré | Sup | Médical | Non (hors réf.) |
| **VSC** | Membre supérieur opéré | Sup | Chirurgical | Non (hors réf.) |
| **RIM** | Membre inférieur non opéré | Inf | Médical | Oui (R) |
| **RIC** | Membre inférieur opéré | Inf | Chirurgical | Oui (R) |
| **VIM** | Membre inférieur non opéré | Inf | Médical | Non (hors réf.) |
| **VIC** | Membre inférieur opéré | Inf | Chirurgical | Non (hors réf.) |
| **ARL** | Affections respiratoires, maxillo-faciales et ORL | — | — | — |
| **NMI** | Affections neuromusculaires / rhumatismales inflammatoires | — | — | — |
| **RAV** | Affections vasculaires | — | — | — |
| **AMP** | Amputations | — | — | — |
| **RPE** | Déambulation personne âgée | — | — | — |
| **TER** | Pathologies sur 2+ territoires | Multi | — | — |
| **RAB** | Rééducation abdominale et périnéo-sphinctérienne | — | — | — |
| **RPB** | Patients brûlés | — | — | — |
| **PLL** | Soins palliatifs | — | — | — |

> ⚠️ **À sourcer officiellement** : les **coefficients** (valeur du multiplicateur) de chaque lettre-clé et le **nombre de séances** associé au référentiel. Non figés ici pour ne pas induire de fausse cotation.

## 3. Le BDK (Bilan Diagnostic Kinésithérapique)

- **Obligatoire depuis 1996**, sur prescription médicale ; pose le diagnostic kiné + objectifs de soins.
- **Coté en AMK** (lettre-clé maintenue pour les bilans) :
  - **10,7 AMK** : rééducation/réadaptation fonctionnelle — pour 1 à 10 séances, à la 30ᵉ séance, puis toutes les 20 séances.
  - **10,8 AMK** : affections neurologiques et musculaires — pour 1 à 10 séances, à la 60ᵉ séance, puis toutes les 50 séances.
- **N'a pas besoin d'être inscrit sur l'ordonnance** pour être facturé (le kiné peut le réaliser même sans mention « bilan »).
- C'est **le seul document officiel prouvant la prise en charge** → pièce maîtresse de défense en cas de contrôle.

## 4. Valeur des lettres-clés

- **Tarif = Coefficient × Valeur de la lettre-clé.**
- Valeur de base ≈ **2,21 € métropole** / **2,43 € DROM**. *(à reconfirmer officiellement par lettre-clé)*

## 5. Référentiel pathologie, séances & DAP

- Le **nombre de séances** et l'article dépendent du **diagnostic posé au BDK**.
- **~20 pathologies** ont un nombre de séances pré-défini ; au-delà → **DAP (Demande d'Accord Préalable)** obligatoire pour ajouter des séances.
- Lettres en **R** = pathologie inscrite au référentiel (cadre séances défini) ; en **V** = hors référentiel.

## 6. Le risque : indu & contrôle CPAM (= la peur qui fait sous-coter)

- **Indu** = somme versée à tort, récupérée par la CPAM. Les **erreurs de cotation sont la 1ʳᵉ source d'indus** chez les kinés.
- Conséquences : **remboursement estimé sur les 3 dernières années + pénalité** pouvant **doubler** la somme.
- Causes : complexité NGAP, mauvaise interprétation des codes, non-respect des protocoles/référentiel.
- Une **ordonnance incomplète/non conforme** → rejet de facturation ou demande de justification au contrôle.

➡️ **Insight produit** : la justification documentée (BDK + traçabilité de la cotation) est le bouclier. Notre outil doit **générer cette justification** à chaque recommandation.

## 7. Concurrence

- **VEGA** : leader (35 000 / 50 000 kinés). Logiciel complet (FSE, télétransmission, agenda, compta, BDK) avec « aide à la saisie » des cotations. → on ne le concurrence PAS, on complète (cf. plan §4).
- Topaze, Milo, Maddie, Cofidoc, Fyzéa : contenu/édito + logiciels gestion. Beaucoup de **contenu SEO sur la complexité NGAP** = signal de demande + canal d'acquisition.

---

## Sources

- [La nomenclature des actes de kinésithérapie — ameli.fr](https://www.ameli.fr/masseur-kinesitherapeute/exercice-liberal/facturation-remuneration/nouvelle-nomenclature)
- [Bilan diagnostic kinésithérapique (BDK) — ameli.fr](https://www.ameli.fr/masseur-kinesitherapeute/exercice-liberal/facturation-remuneration/tarifs-conventionnels/bilan-diagnostic-kinesitherapique)
- [Nomenclature NGAP kinés 2026 — Cofidoc](https://cofidoc.fr/nomenclature-ngap-kines-ce-quil-faut-savoir/)
- [NGAP Kiné : cotation des actes — VEGA](https://www.vega-logiciel.fr/kinesitherapeute/ngap/)
- [Guide pratique NGAP masso-kinésithérapie — Assurance Maladie AURA (PDF, janv. 2025)](https://actus-ps-74.cpam-haute-savoie.fr/sitepad-data/uploads/2025/01/GUIDE-PRATIQUE-DE-LA-NGAP-MASSO-KINESITHERAPIE_Assurance-Maladie-AURA_janvier-2025.pdf)
- [Avenant n°7 à la convention nationale (PDF)](https://gard.ordremk.fr/files/2024/11/CVL_Livret-avenant-7-kine-web_VF.pdf)
- [Cotation NGAP Kiné guide pratique — Blog Rééduca](https://blog.salonreeduca.com/cotation-ngap-kine-le-guide-pratique-2024/)
- [Indus CPAM kiné — Milo](https://www.milo-kine.fr/blog/installation-gestion-activite/facturation/indus-cpam/)
- [Contrôle d'activité & indus CPAM kiné — ValTB Avocats](https://www.valtb-avocats.com/indus-cpam-kine/)

> ⚠️ **À faire en P4** : remplacer les valeurs « à sourcer » par les coefficients/séances exacts depuis l'**avenant 7** et le **guide pratique CPAM AURA** (PDF officiels ci-dessus).
