# KinéCotation — Repositionnement : de la décision à la preuve

> 2026-07-17. Suite de `04_ETUDE_MARCHE_FACTURATION.md`. Remplace la section 4 de `00_PROJECT_PLAN.md`.

---

## 1. Pourquoi le wedge « décision » est mort

Le plan v0.1 oppose VEGA (« aide à la saisie mécanique ») à KinéCotation (« aide à la décision »). Cette opposition ne tient plus : **le calcul de la lettre-clé est déjà une commodité gratuite** — appli FFMKR « Ma cotation Kiné », ngap-kine.fr, rhomboid.fr, gudule.co, module Milo. Le syndicat de la cible le distribue lui-même.

On ne vend pas 20 €/mois ce qu'un syndicat donne. **Il faut descendre d'un cran dans la chaîne de valeur.**

---

## 2. La vraie question sans réponse

Les simulateurs répondent à : *« combien vaut cet acte ? »*
Personne ne répond à : **« dans 3 ans, comment tu prouves que tu avais le droit ? »**

C'est ça, le produit.

### Ce qu'est réellement une procédure d'indu
La CPAM repère un profil atypique dans les données de facturation (volume, distribution des cotations vs pairs), notifie l'indu, et **c'est au kiné de produire les pièces** : ordonnance, bilans (BDK), traçabilité des séances, DAP ou accord tacite. Prescription **3 ans**, point de départ = date de **mandatement** (pas de facturation) — donc la fenêtre réelle est plus longue que 3 ans après la séance.

Le kiné ne perd pas parce qu'il a mal coté. **Il perd parce que, 3 ans après, il ne peut pas reconstituer pourquoi il a coté ainsi.** L'ordonnance est perdue, le bilan n'a jamais été rédigé, le seuil du référentiel n'est documenté nulle part.

→ Le produit = **constituer, au moment de la séance, le dossier qui sera réclamé 3 ans plus tard.**

Ce n'est pas un paragraphe de prose générée. C'est une **pièce datée** qui relie :
`ordonnance (OCR) → faits cliniques extraits → règle NGAP appliquée (version datée de la KB) → cotation retenue`

---

## 3. Le vrai moat — et le plan se trompait sur sa nature

`00_PROJECT_PLAN.md` §6 dit : la base de connaissance est le moat parce que sa **fraîcheur** est une barrière à l'entrée. **Faux** : la fraîcheur est une commodité (le SNMKR publie le tableau gratuitement, on l'a récupéré en une requête).

Le vrai moat : **la KB versionnée est ce qui rend la justification défendable dans le temps.** Pour défendre en 2029 une séance de 2026, il faut prouver *quelle nomenclature était en vigueur ce jour-là*.

Et ce n'est pas théorique — on vient de le vérifier en direct sur notre propre base :

| Date | Événement |
|---|---|
| 01/01/2026 | tarifs avenant 7 (tableau SNMKR **v15a** — la source de notre KB v1.0) |
| 28/05/2026 | avenant 8 : TER 9,49→9,79 · TER 9,51→9,81 · APM 9,50→9,80 (tableau **v19**) |
| 01/09/2026 | NMI 10,01→11,01 (atteinte périphérique multi-membres) — **à venir dans 6 semaines** |

**Trois barèmes différents en 8 mois. Le SNMKR est passé de v15a à v19 — 4 versions — en 7 mois.**

Une justification qui n'épingle pas la version de la KB ne vaut rien. Et **personne ne peut fabriquer ça rétroactivement** : un concurrent qui démarre en 2027 ne pourra jamais produire la preuve d'une séance de 2026. **Le moat est temporel, il se constitue en avançant, et il ne se rattrape pas.** Chaque mois d'avance est un mois qu'un concurrent ne peut pas racheter.

C'est la première barrière à l'entrée réelle du projet. Elle justifie de démarrer **maintenant** plutôt que « quand le produit sera mûr ».

### Pourquoi les gratuits ne peuvent pas suivre
Les simulateurs sont **sans état** : ils disent le coefficient du jour, ils n'enregistrent pas que tu as demandé, sur quels faits, sous quelle version. Leur métier c'est le service adhérent, pas la responsabilité. **Un syndicat n'assumera jamais ta cotation** — et nous non plus (disclaimer « aide à la décision » maintenu). Mais nous, on produit la pièce que **le kiné** signe.

---

## 4. ⚠️ Le conflit d'architecture — TRANCHÉ le 2026-07-17

> **Décisions d'Enzo** : **local-first** (pas d'HDS) · **OCR conservé** · **provider Mistral (FR/UE)**.
> Modèle IA local écarté (aucune garantie sur la machine du kiné). Détail + état RGPD + reste à
> faire : **`06_PROVIDER_IA.md`**. L'abstraction provider (`prototype/llm.py`) est implémentée.
>
> Deux corrections à ce qui suit :
> - Le « **bloquant** » est **levé**. L'HDS n'est pas une architecture à pré-décider, c'est une
>   infrastructure qui se loue plus tard. Seule contrainte à tenir maintenant : **le dossier de
>   preuve doit être un fichier autonome à sérialisation canonique stable** (donc hashable). Ça
>   garde l'option HDS ouverte à coût nul.
> - **Le local-first ne suffit pas au RGPD** tant que l'OCR envoie l'ordonnance à une API. C'est
>   le seul endroit où une donnée de santé circule — et c'était le problème le plus urgent, pas le
>   stockage. Traité par le provider FR/UE ; production = Mistral Enterprise + ZDR + DPA.

### Le raisonnement d'origine

La preuve suppose du **stockage durable**. Le plan §6 dit « MVP = zéro stockage » précisément pour éviter l'**HDS**. **Les deux sont incompatibles.**

**Résolution : local-first.** L'HDS s'impose à l'hébergement de données de santé **pour le compte d'un tiers**. Si le dossier de preuve reste **sur la machine du kiné** — il est son propre responsable de traitement, on n'héberge rien — **l'HDS ne s'applique pas.**

Conséquences :
- Le dossier de preuve est un fichier local (chez le kiné), jamais chez nous.
- On ne voit jamais une donnée de santé → RGPD trivial, argument de vente en soi.
- Coût HDS = 0. Cohérent avec l'ADN RGPD de l'agence.
- **Contrainte produit** : pas de SaaS multi-tenant classique. App locale, ou web app qui n'écrit que dans le navigateur/disque du kiné. Ça oriente toute la techno — **à trancher avant d'écrire la P5**.

**Ne pas survendre le juridique** : un horodatage réellement *opposable* (eIDAS qualifié) est un service payant. On dit **« traçable et daté »**, pas « opposable ». Honnêteté du claim : ça ne fait pas gagner un contentieux automatiquement — **ça permet de répondre dans les délais avec un dossier cohérent au lieu de capituler.** C'est déjà énorme par rapport à l'état de l'art (rien).

---

## 5. Le piège doctrinal — et sa sortie

**Tension à nommer** : le CLAUDE.md de l'agence interdit explicitement « la conformité vendue par la peur » et impose que « la valeur mène ». Or le wedge défendable (la preuve) **est exactement un produit de peur**. Et la peur se vend mal ici : la probabilité perçue d'un contrôle est ≈ 0 tant qu'il n'a pas eu lieu.

**Sortie — et c'est le cœur du repositionnement :**

> Le kiné sous-cote **parce que coter juste fait peur**. Supprime la peur → il cote juste → il gagne plus.
> **La preuve n'est pas une assurance. C'est la permission d'arrêter de perdre de l'argent.**

- On **vend** la récupération (valeur, upside, conforme à la doctrine agence).
- On **livre** la preuve (ce qui rend la récupération sûre à activer).

Accroche : **« Cote au juste tarif, avec la preuve derrière. »**
La preuve est l'*activateur*, le € est le *pitch*. Le double bind de `00_PROJECT_PLAN.md` §2 est enfin résolu par le produit et pas seulement décrit.

---

## 6. Conséquence sur le MVP — bonne nouvelle

L'arbre de décision devient **de la plomberie, pas le produit**. Le produit, c'est le dossier.

| Brique | État |
|---|---|
| OCR ordonnance (`ordonnance_ocr.py`) | ✅ existe |
| Moteur déterministe (`cotation_engine.py`) | ✅ existe |
| KB versionnée + datée | ✅ v1.1, recalée v19 aujourd'hui |
| **Export « dossier de cotation » daté + version KB épinglée** | ❌ **à faire — c'est le delta** |
| Stockage local | ❌ à cadrer (cf. §4) |

**Le delta est petit.** Le gros (perception LLM + décision déterministe) est déjà là. Il manque la sérialisation d'une pièce justificative — quelques jours, pas un trimestre. Le pattern archi « LLM perçoit / moteur décide » (CLAUDE.md §4.1) devient d'ailleurs un **argument de vente** : le montant n'est jamais inventé par une IA, il est calculé par une règle traçable. C'est exactement ce qu'il faut pouvoir dire en contrôle.

---

## 7. Ce qui reste bloquant

**Le chiffre de sous-cotation n'existe nulle part** (cf. `04` §6 : recherche dédiée, rien — ni donnée publique, ni syndicale). Le pitch « récupération » n'a donc **aucun chiffre**. Il ne peut venir que du terrain.

Bonne nouvelle : la KB est désormais juste, donc **la session kiné devient une machine à produire ce chiffre** :
> 5-10 ordonnances réelles → cotation du kiné vs cotation moteur → delta €/séance × volume annuel = **le seul chiffre de vente du projet.**

Ce n'est plus une validation de logique. C'est **la production de l'actif commercial manquant.**

### Hook de prise de contact (coût zéro, aucune donnée client)
> « Ton logiciel est-il bien passé à l'avenant 8 du 28 mai ? TER 9,49 est devenu 9,79. Et le 1er septembre, NMI 10,01 passe à 11,01. »

Ça ne prétend rien sur ses pertes (les éditeurs poussent normalement les MAJ — **ne pas affirmer qu'il perd 0,66 €/séance**), mais ça prouve la compétence en une phrase et ça ouvre la conversation sur le terrain exact du produit. Utilisable dès demain, sans produit fini.

---

## 8. Décisions à prendre (Enzo)

1. **Valider le repositionnement** décision → preuve. Si oui, réécrire `00_PROJECT_PLAN.md` §4, §6 et §7.
2. **Trancher le local-first** (§4) — ça détermine toute la techno de la P5. Bloquant.
3. **Caler la session kiné** — priorité n°1, c'est la seule source du chiffre de vente.
4. **Rééduca Paris 17-19/09/2026** — seule fenêtre GTM de l'année, dans 2 mois. Y aller ou pas, à décider vite.
5. **FFMKR = concurrent sur le calcul, partenaire possible sur la preuve** (un syndicat veut du service adhérent, pas de la responsabilité). À explorer une fois le repositionnement acté.
