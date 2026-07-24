# KinéCotation — Coût OCR ordonnances NOMINATIVES : chiffrage « le moins cher »

> 2026-07-20. Suite de `10_OCR_FOURNISSEURS.md` (les deux voies conformes) et `11_VOIE_B_OCR_OPEN.md`
> (benchmark Qwen). Objectif : **le coût mensuel le plus bas** pour traiter des ordonnances nominatives
> licitement, sur un usage pilote réaliste.
>
> **Hypothèse de charge** : 1-5 kinés · **20-100 ordonnances/jour ouvré** (~440 à 2 200 pages/mois sur 22 j) ·
> latence ≤ 30 s/image · dispo **heures ouvrées** (pas de 24/7 requis).
>
> ⚠️ Chaque chiffre est sourcé par une grille **publique**. Quand le prix n'est pas public, c'est écrit
> « non public » — c'est une donnée en soi (pas d'estimation inventée). Devis/contact commercial exclus.

---

## 0. Rappel du cadre (ne pas re-trancher ici)

- La **certification HDS certifie l'HÉBERGEMENT, pas l'inférence IA**. La bonne question : la donnée
  est-elle hébergée sur une infra HDS + le service retient/entraîne-t-il dessus ? (cf. `10_`).
- **Voie A (managée)** : OCR cloud avec contrat **ZDR + infra HDS** (Outscale/Mistral souverain).
- **Voie B (auto-hébergée)** : VLM open (Qwen2.5-VL-7B) sur **GPU dans le périmètre HDS** d'un cloud FR.

---

## 1. VOIE B — GPU dans le périmètre HDS

### 1.1 Quel GPU ? Le moins cher qui fait tourner un VLM 7B (~15 Go VRAM)

Un Qwen2.5-VL-7B en inférence tient sur **une L4 (24 Go VRAM)** — le plus petit/moins cher GPU data-center
proposé par les hébergeurs HDS FR. Pas besoin de L40S (48 Go) ni A100 pour le 7B ; la L40S ne sert que si
on monte au 32B. **La L4 est donc le plancher matériel.**

### 1.2 Prix GPU (grilles publiques)

| Hébergeur | Instance | GPU / VRAM | Prix/heure | Prix/mois 24-7 (~730 h) | Source |
|---|---|---|---|---|---|
| **Scaleway** | L4-1-24G (PAR-1) | 1× L4 / 24 Go | **0,79 €** | ~575 € | [pricing/gpu](https://www.scaleway.com/en/pricing/gpu/) |
| **OVHcloud** | L4-90 | 1× L4 / 24 Go | **0,75 €** | **540 €** (forfait mensuel) | [pcr.cloud-mercato L4-90](https://pcr.cloud-mercato.com/providers/ovh/flavors/L4-90) |
| Scaleway | L40S-1-48G (PAR-2) | 1× L40S / 48 Go | 1,40 €* | ~1 022 € | [pricing/gpu](https://www.scaleway.com/en/pricing/gpu/) |
| OVHcloud | L40S | 1× L40S / 48 Go | ~1,69 $ | — | [gputracker](https://gputracker.dev/provider/ovhcloud) |
| **Outscale** (Dassault) | GPU / LLMaaS | non listé | **non public** (sur devis) | non public | [outscale/pricing](https://en.outscale.com/pricing/) · [LLMaaS](https://en.outscale.com/llmaas-by-outscale/) |

\* prix Scaleway affiché en USD sur certaines pages, ~1,40 $ ≈ 1,30 € ; retenir la L4 de toute façon.

**OVHcloud L4-90 = le GPU le moins cher (0,75 €/h, plafond mensuel 540 €).** Scaleway juste derrière
(0,79 €/h). Outscale ne publie pas ses tarifs GPU → non chiffrable sans devis.

### 1.3 Le coût qui domine tout : le **contrat HDS + plan de support obligatoire**

Chez les deux hébergeurs, héberger de la donnée de santé **impose un plan de support payant** (+ signature
d'un contrat/addendum HDS, sans prix séparé publié). Ce **plancher fixe** pèse plus lourd que le GPU au
volume pilote.

| Hébergeur | Plan support min. requis HDS | Prix | Source |
|---|---|---|---|
| **Scaleway** | **Business** (ou Enterprise) | **max(250 €/mois ; 10 % de la conso)** | [support plans](https://www.scaleway.com/en/docs/account/reference-content/understanding-support-plans/) · [HDS](https://www.scaleway.com/fr/security-and-resilience/hds/) |
| Scaleway | Enterprise | max(990 €/mois ; 20 %) | idem |
| **OVHcloud** | **Business** (ou Enterprise) | **à partir de ~300 $/mois** (10 % de la facture, plancher ~300 $ ≈ 275 €) | [support levels](https://www.ovhcloud.com/en/support-levels/plans/) · [HDS OVH](https://www.ovhcloud.com/en/compliance/hds/) |
| OVHcloud | Enterprise | à partir de ~5 850 $/mois (30 %) | idem |

- **Périmètre HDS confirmé** : Scaleway → « CPU **& GPU Instances**, Block/Object Storage, Elastic Metal, VPC »
  ([HDS Scaleway](https://www.scaleway.com/fr/security-and-resilience/hds/)). OVHcloud → « Public Cloud
  **Instances** » (les GPU sont des Public Cloud Instances ; sous-flavor à confirmer au contrat)
  ([doc HDS OVH](https://raw.githubusercontent.com/ovh/docs/develop/pages/account_and_service_management/account_information/hds_certification/guide.en-sg.md)).
- Le support est facturé **au % de la conso avec un plancher** : au volume pilote la conso GPU est faible,
  donc c'est **le plancher (250 €/275 €) qui s'applique**, pas le %.
- **Un seul plan de support couvre TOUTES les ressources HDS du compte** → ajouter la VM applicative en
  périmètre HDS n'ajoute **pas** de coût de support, seulement le prix de la VM.

### 1.4 Deux scénarios d'allumage GPU (facturation à l'heure)

| Scénario | Heures/mois | GPU L4 (OVH 0,75 €/h) | + Support Business | **Total Voie B** |
|---|---|---|---|---|
| **GPU 10 h/j ouvrés** (~220 h) | 220 | 165 € | ~275 € | **~440 €/mois** |
| **GPU 24/7** | 730 | 540 € (forfait) | ~275 € | **~815 €/mois** |

(Scaleway équivalent : 10 h/j = 174 € GPU + 250 € = **~425 €/mois** ; 24/7 = 575 € + 250 € = **~825 €/mois**.)

→ **Éteindre la GPU hors heures ouvrées fait tomber la facture GPU de ~65 %.** Le pilote n'a pas besoin de
24/7 : **~425-440 €/mois** est le vrai plancher Voie B, dont **~250-275 € de support incompressible**.

### 1.5 La VM applicative (déjà nécessaire) — deux hypothèses de transit

L'app web tourne déjà sur une petite VM (~10-40 €/mois, ex. instance CPU Scaleway/OVH).

- **Hypothèse a — l'image ne transite pas en clair par le backend** (upload direct navigateur → GPU HDS,
  ou chiffré de bout en bout) : la VM applicative peut rester **hors HDS** → aucun surcoût.
- **Hypothèse b — l'image de santé transite en clair par le backend** : cette VM doit **elle aussi être en
  périmètre HDS** → +10-40 €/mois pour la VM (le support Business est déjà payé, cf. 1.3). Négligeable.

→ Impact ≤ 40 €/mois quoi qu'il arrive. **À câbler idéalement en hypothèse (a)** pour minimiser le périmètre.

---

## 2. VOIE A — OCR managé ZDR/HDS

| Offre | Conforme nominatif ? | Prix | Source |
|---|---|---|---|
| **Mistral OCR standard** (`mistral-ocr-4`, La Plateforme) | ❌ (ni HDS ni ZDR par défaut, cf. `10_`) | **4 $ / 1 000 pages** (= 0,004 $/page) · Document AI 5 $/1 000 | [mistral.ai/pricing/api](https://mistral.ai/pricing/api) |
| **Mistral Enterprise** (ZDR dédié) | ✅ par contrat | **non public** | [mistral.ai/pricing](https://mistral.ai/pricing) |
| **Outscale LLMaaS + Mistral souverain** (SecNumCloud + HDS) | ✅ (précédent PulseLife) | **non public** (sur devis) | [LLMaaS by Outscale](https://en.outscale.com/llmaas-by-outscale/) |
| **Docaposte** (santé, HDS via Arkhineo) | HDS oui, mais pas d'API OCR self-service santé | **non public** | [docaposte certifications](https://www.docaposte.com/en/our-certifications) |

**Le seul chiffre public de la Voie A est l'OCR Mistral standard NON conforme : 0,004 $/page.**
Il sert d'**ancre d'ordre de grandeur** : au volume pilote (100 ord/j × 22 j ≈ 2 200 pages/mois),
l'OCR pur coûte **~8,80 $/mois (~8 €)**. Autrement dit : le calcul OCR lui-même est quasi gratuit ;
**tout ce qu'on paierait en plus dans une offre conforme = le prix de la souveraineté/ZDR/HDS**
(contrat Enterprise ou LLMaaS souverain), et **ce prix-là n'est pas public**.

→ **Voie A conforme = non chiffrable sans devis.** On sait que ça existe (PulseLife tourne sous ZDR
Outscale/Mistral) mais ni Mistral Enterprise ni Outscale LLMaaS ne publient de grille.

---

## 3. Point de bascule Voie A ↔ Voie B

Comme les prix Voie A conformes sont non publics, le croisement exact en euros **n'est pas calculable**.
Mais la **structure de coût** tranche déjà :

- **Voie B** = un **coût fixe** ~425-440 €/mois (GPU 10 h/j + support), **quasi indépendant du volume**
  jusqu'à saturation de la L4. Or une L4 traite un 7B à ~10 s/image (benchmark `11_`) → ~360 img/h →
  **~79 000 images/mois** à 220 h. Le pilote (≤ 2 200/mois) est **35× sous la capacité** : le coût/ordonnance
  Voie B baisse mécaniquement avec le volume.
- **Voie A conforme** = probablement **à l'usage** (par page) + éventuel **minimum de plateforme**. Si elle
  est facturée près du tarif standard (0,004 $/page) sans gros minimum, alors au volume pilote elle coûte
  **quelques dizaines d'euros/mois** — **bien moins que le plancher fixe de la Voie B**.

**Croisement théorique** (contre un prix cloud conforme hypothétique *p* €/page, sans minimum) :
plancher Voie B 440 € ÷ *p*. À *p* = 0,004 € → bascule vers **~110 000 pages/mois** (~50× le pilote).

→ **Traduction** :
- **À l'échelle pilote, la Voie A managée est moins chère** — *si* un contrat souverain à l'usage existe
  **sans minimum mensuel lourd**. L'inconnue qui peut tout inverser = **le minimum du contrat souverain**
  (s'il impose, disons, un forfait > 440 €/mois, la Voie B repasse devant immédiatement).
- **La Voie B gagne sur le prix** seulement à **fort volume** (dizaines de milliers de pages/mois) **ou** si
  le contrat souverain a un gros minimum. Son intérêt au pilote n'est **pas le prix** mais la **souveraineté**
  (aucun tiers ne voit la donnée), la **prévisibilité** (coût fixe) et l'**indépendance** (pas de ZDR d'un
  tiers à auditer).

### 3.1 L'option HYBRIDE change le calcul (et c'est probablement le vrai gagnant)

Qwen local sur la **machine du cabinet** (RTX 4070 d'Enzo : **gratuit**, déjà benchmarké dans `11_`) pour
le **tapé** (quasi-parité cloud sur l'extraction) + **cloud conforme uniquement pour le manuscrit**
(où Qwen local décroche : CER 4,5 % vs ~1 %) :

- On **supprime le plancher GPU HDS de 425-440 €/mois** : le tapé est traité **on-premise**, gratuit,
  la donnée ne quitte pas le cabinet.
- Seules les **ordonnances manuscrites** partent au cloud conforme → volume cloud réduit → facture à l'usage
  encore plus petite.
- **Résultat probable = la config la moins chère de toutes** : ~0 € d'infra + une petite facture d'OCR
  cloud conforme pour la fraction manuscrite.
- ⚠️ **Nuance juridique** : traiter en local sur la machine du praticien **déplace** la question HDS —
  un traitement local sur le poste du professionnel de santé n'est *a priori* pas de « l'hébergement par un
  tiers », donc hors périmètre HDS ; **à faire valider par un juriste** (cf. §4). Ne pas re-trancher ici.

---

## 4. Verdict : le moins cher

**Classement par coût mensuel croissant, au volume pilote (≤ 2 200 pages/mois) :**

| # | Configuration | Coût mensuel | Conforme nominatif | Réserve |
|---|---|---|---|---|
| 🥇 | **Hybride** : Qwen local (tapé, gratuit) + cloud conforme pour le manuscrit | **~0 € infra + facture usage manuscrit** (non chiffrable : prix conforme non public) | oui, sous réserve juridique du « local = hors HDS » | prix cloud conforme non public ; validation juriste du montage local |
| 🥈 | **Voie A managée** : Outscale/Mistral souverain ZDR (usage) | **non public** — potentiellement quelques dizaines €/mois *si pas de gros minimum* | oui (précédent PulseLife) | **prix + minimum non publics** = risque n°1 du chiffrage |
| 🥉 | **Voie B** : GPU L4 OVH/Scaleway **10 h/j ouvrés** + support Business | **~425-440 €/mois** (+ ≤ 40 € VM si transit backend) | oui (souveraineté maximale) | plancher fixe, dont ~250-275 € de support incompressible |
| — | Voie B GPU **24/7** | ~815-825 €/mois | oui | inutile pour un pilote (pas besoin de 24/7) |

**En clair :**
- **Le moins cher chiffrable et 100 % maîtrisé = la Voie B à ~425-440 €/mois** (GPU L4 allumée aux heures
  ouvrées + support Business), OVHcloud L4-90 étant le GPU le moins cher (0,75 €/h).
- **Potentiellement moins cher encore = l'hybride** (Qwen local tapé + cloud manuscrit) et **la Voie A
  managée à l'usage** — mais **les deux dépendent d'un prix conforme non public** (Outscale/Mistral) ; on ne
  peut pas l'affirmer sans devis.
- **Le poste qui domine la Voie B n'est pas le GPU (~165 €) mais le support HDS obligatoire (~250-275 €).**
  C'est le vrai plancher de la souveraineté auto-hébergée.

---

## 5. Incertitudes (documentées, à ne pas re-trancher)

- **Juridique** : HDS certifie l'**hébergement**, pas l'inférence ; la question du **transit** de la donnée
  (backend en clair ? local sur poste = hors HDS ?) et le montage global **restent à valider par un juriste**
  (posture projet : « diagnostic informatif », cf. `10_`/`11_`). Non re-tranché ici.
- **Prix Voie A conforme non publics** : Mistral Enterprise, Outscale LLMaaS, Docaposte → **pas de grille**,
  donc point de bascule non calculable et classement #1/#2 non départageable sans devis.
- **Périmètre GPU OVH sous HDS** : « Public Cloud Instances » certifiées ; le sous-flavor GPU spécifiquement
  à confirmer au contrat HDS (Scaleway, lui, liste explicitement « GPU Instances »).
- **Précision manuscrit** (cf. `11_`) : Qwen local ~4,5 % CER sur RIMES *propre* — chutera sur du gribouillis
  médical ; le go/no-go Voie B / hybride se joue sur les **vraies ordonnances de Malcom**, pas encore obtenues.
