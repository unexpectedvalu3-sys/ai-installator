# 15 — Intégration Maiia (Cegedim Santé)

> **But du document** : établir les FAITS (sources primaires, recherche web) sur ce que le
> logiciel « Maia » utilisé par Malcom accepte en entrée/sortie, et en déduire l'échelle
> réaliste d'intégration pour KinéCotation. Même méthode et même niveau d'exigence que
> `13_INTEGRATION_VEGA.md`.
>
> **Méthode** : aucune donnée inventée. Chaque affirmation porte sa source, ou est marquée
> « non trouvé ». Recherche web uniquement, aucun contact commercial. Date : 2026-07-22.

---

## 0. Désambiguïsation — quel « Maia » ?

**Verdict : « Maia » = Maiia (deux « i »), édité par Cegedim Santé (groupe Cegedim). Pour un
kiné libéral, le produit exact est « Maiia Kiné » (alias « Maiia Gestion Kiné »).**

- Éditeur et marque : **Cegedim Santé**, suite **Maiia** — agenda en ligne, téléconsultation,
  messagerie sécurisée, **et** un module métier dédié aux kinés (« Maiia Gestion » /
  « Maiia Kiné ») lancé fin 2020, ~6 000 kinés utilisateurs (~30 000 sur l'ensemble Cegedim).
  Sources : [Maiia Kiné — Cegedim Santé](https://www.cegedim-sante.com/solutions-sante-cegedim/solutions-web/maiia-kine/) ·
  [suite.maiia.com](https://suite.maiia.com/) (redirige vers [cegedim-sante.com/suite-maiia](https://www.cegedim-sante.com/suite-maiia/)) ·
  [news.maiia.com — lancement Maiia Gestion kinés](https://news.maiia.com/maiia-gestion-lancement-solution-organisation-cabinet-speciale-kines/actualites/)
- Périmètre fonctionnel confirmé pour les kinés : **agenda + bilan (BDK) + suivi patient +
  facturation (y compris en mobilité) + FSE**. Ce n'est donc **pas** un simple agenda/téléconsult
  couplé à un tiers pour la facturation — Maiia Kiné **facture lui-même** (§3).
  Source : [cegedim-sante.com/maiia-kine](https://www.cegedim-sante.com/solutions-sante-cegedim/solutions-web/maiia-kine/)
- **Piège d'homonymie identifié et écarté** : il existe une **autre société « Maiia »**
  (`maiia.cloud`), sans rapport, qui édite des logiciels métier pour **syndicats d'énergie et
  opérateurs de réseaux** (eau, assainissement, SIG). Une recherche sur « Maiia API ouvertes
  SIG/ERP/GED » remonte du contenu de **cette société énergie**, pas de la Maiia santé de
  Cegedim. **Ne pas confondre** : cette « API ouverte SIG/ERP/GED » ne concerne pas le produit
  utilisé par Malcom. Source du piège (à ignorer pour notre usage) : [maiia.cloud](https://www.maiia.cloud/).

**Ce document traite exclusivement de Maiia Kiné / Cegedim Santé.**

---

## 1. API publique / programme partenaires / interfaçage

**Verdict (MIS À JOUR 2026-07-22) : « Maiia Connect » est TRANCHÉ — ce n'est PAS un programme
d'interfaçage éditeurs tiers, c'est la messagerie sécurisée instantanée entre professionnels de
santé de Cegedim Santé (documents, chat, visio — équivalent MSSanté/WhatsApp pro). Aucune API
d'écriture (agenda, patients, actes) ouverte à des tiers n'a été trouvée nulle part pour Maiia.
Voir §1bis pour le détail des preuves. Le dossier se rapproche donc du verdict VEGA : pas d'API
d'écriture documentée pour un tiers.**

- Un centre d'aide dédié **« Maiia Connect »** existe (`connect.maiia.com` + catégorie Zendesk),
  preuve qu'un **concept de connecteur/partenariat** est officiellement nommé chez Cegedim
  Santé — contrairement à VEGA où rien de tel n'a été trouvé.
  Sources : [connect.maiia.com](https://connect.maiia.com/) ·
  [maiia.zendesk.com — catégorie Maiia Connect](https://maiia.zendesk.com/hc/fr/categories/360002453319-Maiia-Connect)
- ~~**Contenu exact NON TROUVÉ**~~ **RÉSOLU (§1bis)** : « Maiia Connect » est la messagerie
  sécurisée inter-professionnels de santé de Cegedim (chat, documents, visio) — PAS un
  programme d'interfaçage éditeurs tiers pour écrire agenda/patients/actes dans Maiia. Confirmé
  par 4 sources primaires indépendantes convergentes (page produit Cegedim, fiche Google Play,
  article de presse DSIH, documentation d'aide d'un AUTRE logiciel Cegedim — Crossway — qui
  intègre le même module « messagerie Maiia Connect »). Voir §1bis.
- **Aucune documentation développeur publique, aucune spec d'API (swagger/OpenAPI), aucun SDK
  ou wrapper GitHub/npm non officiel n'a été trouvé** pour une « API Maiia » ou « API Cegedim »
  d'écriture d'actes/facturation. Voir §1bis.

**Conséquence pour nous** : la piste A (API d'écriture via Maiia Connect) est **écartée** — même
verdict que VEGA sur ce point précis. Le seul signal restant est un poste de recrutement Cegedim
« Product Manager Interopérabilité » dont la mission est explicitement de transformer
l'interopérabilité maison en **« véritable plateforme d'intégration ouverte aux partenaires
externes »** (§1bis) : c'est un projet **en cours de construction**, pas un service existant
aujourd'hui — donc rien à promettre, mais un signal à surveiller (revérifier dans 6-12 mois).

---

## 1bis. Investigation approfondie Maiia Connect — preuves publiques (2026-07-22)

> Recherche complémentaire, sans accès au portail authentifié `connect.maiia.com` (login pro
> requis, jamais tenté). Objectif : reconstituer par des preuves publiques indirectes si
> « Maiia Connect » est une vraie API d'écriture pour éditeurs tiers ou autre chose. Recherches
> web uniquement (12 requêtes + 5 fetchs de pages), aucun contact commercial, aucune tentative de
> login.

### a) Ce que « Maiia Connect » EST réellement — 4 sources primaires convergentes

1. **Page produit officielle Cegedim Santé** : titre exact « Maiia Connect : messagerie
   sécurisée pour professionnels de santé » — citation verbatim relevée sur la page :
   *« La messagerie instantanée sécurisée qui vous connecte à tous les professionnels de santé
   en France »*, *« Un échange rapide et simple avec vos confrères »*. Fonctions listées : chat,
   messages vocaux/vidéo, partage de documents (compte-rendu, analyse, radio, ordonnance),
   gestion de tâches. Accès pro via `pro.maiia.com` avec authentification à deux facteurs.
   Source : [cegedim-sante.com/maiia-connect](https://www.cegedim-sante.com/solutions-sante-cegedim/solutions-web/maiia-connect/)
2. **Fiche Google Play de l'app** `com.cegedim.maiia.connect` : décrite comme application de
   **messagerie instantanée sécurisée et gratuite** pour professionnels de santé, utilisable
   seule ou couplée à l'appli Maiia Pro — aucune mention d'API, de webhook ou d'intégration
   logicielle tierce.
   Source : [play.google.com — Maiia Connect](https://play.google.com/store/apps/details?id=com.cegedim.maiia.connect)
3. **Article de presse spécialisée (DSIH, lancement du produit)** : « Cegedim Santé annonce le
   lancement de Maiia Connect, sa nouvelle **messagerie gratuite et instantanée** qui connecte
   tous les professionnels de santé » — confirme l'objet du produit dès son lancement (pas
   présenté comme un programme d'interfaçage éditeurs).
   Source : [dsih.fr — lancement Maiia Connect](https://dsih.fr/articles/4767/cegedim-sante-annonce-le-lancement-de-maiia-connect-sa-nouvelle-messagerie-gratuite-et-instantanee-qui-connecte-tous-les-professionnels-de-sante)
4. **Preuve croisée décisive — documentation d'aide d'un AUTRE logiciel Cegedim (Crossway)** :
   une page d'aide intitulée **« La messagerie Maiia Connect »** existe dans la doc en ligne de
   Crossway (autre LGC du groupe Cegedim, pas Maiia), ce qui prouve que « Maiia Connect » est un
   **module de messagerie transverse au groupe Cegedim**, packagé dans plusieurs de leurs propres
   logiciels métier — pas un service ouvert à des éditeurs tiers indépendants.
   Source : [cegedim-logiciels.com — La messagerie Maiia Connect (aide Crossway)](https://www.cegedim-logiciels.com/dyn/espace_client/Aide_en_ligne/crossway/24.03/webhelp/content/CW_Messageries_MaiiaConnect.html)

**→ Les 4 sources s'accordent sans exception : « Maiia Connect » = messagerie sécurisée
inter-professionnels de santé (proche de MSSanté), pas un canal d'écriture d'actes/cotations pour
un logiciel tiers.** Le nom de domaine `connect.maiia.com` correspond très probablement au portail
de connexion de cette messagerie (cohérent avec `pro.maiia.com` cité par Cegedim comme accès
professionnel), pas à un espace développeur.

### b) Recherche d'une API publique Maiia/Cegedim — négatif partout

- `developers.maiia.com`, `api.maiia.com` : **aucun résultat**, aucune doc développeur, aucune
  page swagger/OpenAPI trouvée pour Maiia.
- « Cegedim API » sur un agrégateur d'API tiers (apitracker.io) : liste bien une « Cegedim API »
  générique mais **sans aucune mention de Maiia, d'agenda santé ou de FSE/facturation**, et
  renvoie vers un PDF de référence daté de 2018 — signal d'une API ancienne/périmée ou hors
  sujet, pas une preuve d'API Maiia active.
  Source : [apitracker.io/a/cegedim-fr](https://apitracker.io/a/cegedim-fr)
- GitHub/npm : **aucun SDK ou wrapper non officiel** trouvé mentionnant une API Maiia ou Cegedim
  santé (recherches croisées « maiia api github », « cegedim api github »/sdk/wrapper) — un
  wrapper non officiel aurait pourtant suffi à prouver l'existence de l'API ; son absence totale
  est un indice supplémentaire (faible, mais cohérent) qu'il n'y a rien à wrapper.

### c) Offres d'emploi Cegedim — signal d'INTENTION, pas de service existant

- Une offre active (« Product Manager H/F », Boulogne-Billancourt) décrit la mission : accompagner
  **« la transformation de l'interopérabilité en une véritable plateforme d'intégration
  scalable, robuste et ouverte »**, avec profil attendu maîtrisant **API REST, webhooks,
  standards d'échange (FHIR/HL7 en plus)**, et un contexte explicite : *« l'interopérabilité est
  aujourd'hui un enjeu stratégique majeur : permettre aux produits de communiquer de façon fluide
  et ouvrir l'écosystème à des partenaires externes »*.
  Source : [careers.cegedim.com — Product Manager H/F](https://careers.cegedim.com/fr/annonce/4410853-product-manager-hf-92100-boulogne-billancourt)
- **Lecture correcte de ce signal** : Cegedim **n'a pas encore** de plateforme d'intégration
  ouverte aux tiers — l'offre dit vouloir la construire (« accompagner la transformation vers »).
  C'est donc une preuve supplémentaire, indirecte mais nette, que le service espéré (voie A)
  **n'existe pas aujourd'hui**, tout en indiquant une direction stratégique du groupe à surveiller
  à moyen terme (6-12 mois).
- Une offre distincte (alternance « Product manager interopérabilité et back-office ») confirme
  que le sujet interopérabilité est un axe RH actif chez Cegedim, sans plus de détail exploitable
  publiquement.
  Source : [careers.cegedim.com — alternance interopérabilité](https://careers.cegedim.com/fr/annonce/3683321-product-manager-interoperabilite-et-back-office-en-alternance-hf-92100-boulogne-billancourt)

### d) Écosystème Ségur / FHIR / MSSanté — interop clinique, pas facturation

- **Maiia Médecin** (pas Maiia Kiné) est référencé Ségur du numérique en santé vague 1, et en
  cours de référencement vague 2 : alimentation/consultation du **DMP**, qualification **INS**,
  génération de volets de synthèse structurés, ordonnance numérique, accès **MSSanté**.
  Source : [cegedim-sante.com — répondre aux exigences du Ségur](https://www.cegedim-sante.com/le-blog/logiciel-medical-repondre-aux-exigences-du-segur-du-numerique-en-sante/)
  et [maiia.zendesk.com — MSS Messagerie Sécurisée de Santé](https://maiia.zendesk.com/hc/fr/articles/4497778235026--MSS-Messagerie-S%C3%A9curis%C3%A9e-de-Sant%C3%A9)
- **Référencement Ségur équivalent pour Maiia Kiné spécifiquement : NON CONFIRMÉ** dans les
  résultats accessibles (les sources trouvées parlent de Maiia Médecin).
- Le Ségur porte sur l'interop **clinique** (DMP, MSSanté, INS) — **pas** sur un canal
  d'écriture de cotations/facturation pour des tiers. Même si Maiia expose un jour du FHIR côté
  Ségur, cela ne concernerait a priori que les documents de santé (volets, comptes-rendus), pas
  les actes NGAP/cotations. **Aucune API FHIR publique documentée pour Maiia n'a été trouvée.**

### e) Intégrateurs tiers annonçant une connexion à Maiia

- Le seul écosystème de partenaires confirmé publiquement est un réseau de **plus de 150
  télésecrétariats partenaires** (ex. Vocallz, cité comme partenaire historique) qui gèrent
  l'agenda Maiia pour le compte des praticiens — mais **aucune documentation technique publique**
  ne décrit comment (compte partagé classique dans l'interface web, très probablement, pas API).
  Sources : [telesecretariat.com — Télésecrétariat Maiia](https://www.telesecretariat.com/telesecretariat-maiia/) ·
  [secretariat-telephonique.tv — Location Agenda Maiia](https://secretariat-telephonique.tv/location-dagenda/agenda-maiia/)
- **Aucun éditeur logiciel tiers indépendant** (Doctolib, Keldoc, ou autre LGC hors groupe
  Cegedim) n'a été trouvé annonçant publiquement une intégration technique (API/webhook/FHIR)
  avec Maiia — cohérent avec l'absence de toute doc développeur publique.

### Verdict de la question décisive (§7 pt.1)

**Existe-t-il un moyen documenté, par un tiers, d'ÉCRIRE une cotation/un acte dans Maiia depuis
un logiciel externe ?** → **NON, à notre niveau de preuve actuel.** Aucune source publique
(officielle, presse, développeur, emploi, GitHub) ne documente une telle capacité. « Maiia
Connect », piste initialement ouverte, est maintenant **résolue et écartée** : c'est une
messagerie, pas une API d'écriture. Il reste une **hypothèse future non nulle** (poste
Interopérabilité en cours de recrutement chez Cegedim) mais **rien d'actionnable aujourd'hui**.
Niveau de preuve : **fort pour l'absence actuelle** (silence total et convergent sur 4+ angles de
recherche différents) ; **aucune preuve formelle d'un refus explicite de Cegedim** (nuance à
garder — ce n'est pas une déclaration éditeur « nous n'avons pas d'API », c'est une absence de
toute preuve positive après recherche large).

---

## 2. Formats d'import (patients, actes, agenda)

**Verdict : import CSV confirmé pour un cas précis (conventions mutuelles) ; aucun import de patients/actes en provenance d'un tiers n'a été trouvé. Investigation ciblée complémentaire menée le 2026-07-22, voir §2bis — confirme et détaille ce verdict.**

- **Import documenté** : dans Maiia Gestion Kiné, menu **Options ⚙ → CONVENTIONS MUTUELLES →
  Importer des conventions → Parcourir**, avec une contrainte de nommage de fichier
  (`C-nom...nom.csv`). C'est un import de **grille tarifaire mutuelle**, pas de patients ni d'actes.
  Source : [maiia.zendesk.com — La mutuelle sur Gestion Kiné](https://maiia.zendesk.com/hc/fr/articles/4402870410386-La-mutuelle-sur-Gestion-Kin%C3%A9)
- **Import de patients ou d'actes/cotations depuis un logiciel tiers : NON TROUVÉ.** Aucune
  page d'aide, FAQ ou forum ne mentionne la possibilité d'importer un fichier de patients ou
  d'actes produit en dehors de l'écosystème Cegedim.
- **Interopérabilité intra-écosystème uniquement** : la page produit mentionne une
  « interopérabilité avec les logiciels de gestion Cegedim Santé » et un export de données vers
  **Maiia Compta** depuis les logiciels cabinet du groupe (Maiia Kiné, Crossway, Médiclick, MLM).
  C'est un flux **interne à Cegedim**, pas un canal ouvert aux tiers — même logique que
  CLICKDOC↔VEGA chez Epsilog.
  Source : [cegedim-sante.com/suite-maiia](https://www.cegedim-sante.com/suite-maiia/)
- La synchronisation **Maiia Gestion ↔ Maiia Agenda** (évite la double saisie des dossiers
  patients) est également **intra-produit**, pas un mécanisme d'import externe.
  Source : [cegedim-sante.com/maiia-kine](https://www.cegedim-sante.com/solutions-sante-cegedim/solutions-web/maiia-kine/)

---

## 2bis. Capacités d'IMPORT — investigation ciblée (2026-07-22)

> Recherche complémentaire, focalisée exclusivement sur les capacités d'**import de fichier
> dans Maiia Kiné** (pas l'API — déjà tranchée §1/§1bis —, pas l'export — déjà couvert §4).
> Objectif produit : peut-on injecter dans Maiia, via un fichier qu'on génère, des actes/cotations
> (le graal — tuerait la double saisie), à défaut des patients, à défaut n'importe quel import
> structuré. Recherche web uniquement (11 requêtes + tentatives de fetch direct), aucun contact
> commercial, aucune tentative de login sur le portail authentifié.

### a) Import d'ACTES / cotations depuis un fichier tiers — NON TROUVÉ

- La page d'aide officielle dédiée à la saisie d'un acte s'intitule **« Saisir un acte, une
  cotation »** — le verbe employé est **« saisir »** (saisie manuelle dans l'interface), jamais
  « importer ». Aucune mention d'un import de fichier d'actes/cotations sur cette page ni ailleurs
  dans le centre d'aide Maiia, sur cegedim-sante.com, ni sur les chaînes vidéo officielles
  (YouTube/Facebook Maiia Kiné) consultées via recherche.
  Source : [maiia.zendesk.com — Saisir un acte, une cotation](https://maiia.zendesk.com/hc/fr/articles/10442014794770-Saisir-un-acte-une-cotation)
- **Import comptable / journal (piste dédiée à l'usage) : NON TROUVÉ non plus, et sens inverse à
  ce qu'on cherche.** La synchronisation « Maiia Compta ↔ Gestion Kiné » (menu Options →
  section Comptabilité → « Synchroniser », identifiant Compta à 6 chiffres) **génère
  automatiquement une écriture dans Maiia Compta pour chaque paiement reçu dans Gestion Kiné** —
  c'est un flux **interne à Cegedim** (Gestion Kiné → Compta), pas un import d'écritures ou
  d'actes produits par un logiciel tiers. Le concept de « journal » qui existe dans Maiia Compta
  (journal banque, journal caisse) sert à enregistrer les opérations internes, pas à recevoir un
  fichier externe.
  Sources : [maiia.zendesk.com — 4. Gérer les journaux et les comptes](https://maiia.zendesk.com/hc/fr/articles/4402864709394-4-G%C3%A9rer-les-journaux-et-les-comptes) ·
  synthèse de recherche référençant « Maiia Compta : exporter ses paiements ».
- **Formats standards d'échange d'actes (norme B2.R, FSE/SESAM-Vitale) : existent mais
  hors-sujet pour notre usage.** La norme B2.R encadre la télétransmission FSE enrichie vers les
  Organismes Concentrateurs Techniques (OCT, ex. Réseau Rééduc) ; SESAM-Vitale exige un agrément
  CNDA en tant que Logiciel de Gestion de Cabinet (LGC). Deux obstacles rédhibitoires pour nous :
  (1) c'est un canal de **télétransmission sortante** vers l'assurance maladie, pas un import
  entrant dans Maiia ; (2) il faudrait que KinéCotation devienne lui-même un LGC agréé CNDA, hors
  de portée pour un outil de pré-cotation. Mentionné pour être exhaustif, mais non actionnable.
  Source : [resopharma.fr — Télétransmission Kinésithérapeute / OCT (norme B2.R)](https://www.resopharma.fr/documents/normes/b2r_reeduc_sv140.pdf)

**Verdict (a) — ACTES/cotations : NON, non trouvé.** Aucun signal positif après recherche large
sur les canaux où une telle fonctionnalité se documenterait forcément si elle existait (centre
d'aide, page produit, tutoriels vidéo officiels). La page d'aide dédiée confirme au contraire,
par son vocabulaire même (« saisir »), que la saisie manuelle est le seul chemin documenté.

### b) Import de PATIENTS en masse depuis un fichier tiers — NON TROUVÉ

- La page d'aide officielle s'intitule **« Créer, modifier un patient »** (au singulier) — cohérent
  avec une création unitaire dans l'interface, pas avec un import de liste. Aucune mention d'un
  import de fichier patients (CSV/Excel) trouvée sur cette page ni ailleurs.
  Source : [maiia.zendesk.com — Créer, modifier un patient](https://maiia.zendesk.com/hc/fr/articles/21273874050706-Cr%C3%A9er-modifier-un-patient)
  (⚠️ contenu détaillé non accessible en lecture directe — 403 — conclusion basée sur le titre et
  les extraits indexés par le moteur de recherche, pas sur une lecture intégrale de la page.)
- **Migration vers Maiia : un SERVICE annoncé, pas un format d'import self-service documenté.**
  Cegedim Santé promet « Migration, installation et formation incluses » lors de l'onboarding —
  formule marketing générique, sans détail technique (aucun format de fichier, aucune procédure
  self-service publiée). Un article tiers confirme que la migration logicielle est un vrai sujet
  dans le secteur kiné (plusieurs éditeurs — Topaze, Milo, Doctolib — annoncent un accompagnement
  migration gratuit) mais **aucune source ne documente la mécanique technique côté Maiia**
  (import de fichier normé vs ressaisie manuelle assistée par un humain côté Cegedim). Le signal
  penche vers un accompagnement **humain/service** lors de l'onboarding plutôt qu'un import de
  fichier ouvert et documenté publiquement.
  Sources : [cegedim-sante.com/services-maiia](https://www.cegedim-sante.com/services-maiia/) ·
  [topaze.com — changer facilement de logiciel kiné](https://www.topaze.com/blog/actualite-kines/changer-facilement-de-logiciel-kine-pour-une-migration-sans-stress/)
- **Seul import de fichier confirmé reste celui déjà identifié en §2** : les grilles tarifaires
  mutuelles (`C-nom...nom.csv`, menu Conventions mutuelles) — hors sujet patients/actes.
- **Signal indirect, sens inverse** : un service tiers pour kinés (« Gustave », agenda connecté)
  annonce pouvoir reprendre patients/rendez-vous **depuis** Maiia (parmi d'autres logiciels
  sources) — c'est un flux **sortant** de Maiia exploité par ce tiers (mécanisme non détaillé
  publiquement, probablement scraping/export assisté), pas une preuve d'import **dans** Maiia
  depuis un fichier tiers. Mentionné par honnêteté, mais ne change pas le verdict.
  Source : [services.gustave.app](https://services.gustave.app/)

**Verdict (b) — PATIENTS : NON, non trouvé au sens d'un import self-service documenté.** La
migration existe comme service d'onboarding accompagné, pas comme format de fichier public que
nous pourrions générer nous-mêmes.

### c) Bonus hors mission stricte — indice sur les colonnes de l'export §4

Les extraits indexés par le moteur de recherche pour la page « Liste de patients, séances, actes »
(bloquée en lecture directe, 403 — cf. §4) laissent apparaître un format CSV avec des colonnes
plausibles : *Date de séance, Patient (avec date de naissance), Traitement, Cotation, Date de
facture, Numéro de facture, Date de règlement, Montant*. **⚠️ Provient d'un extrait de moteur de
recherche, pas d'une lecture directe de la page (toujours 403 lors de cette investigation) — à
considérer comme un indice fort mais NON confirmé formellement.** Cohérent avec le §4 existant :
à vérifier avec un export réel de Malcom avant de bâtir dessus.

### Verdict global de la mission ciblée (2026-07-22)

**(a) Import ACTES/cotations : NON TROUVÉ.** **(b) Import PATIENTS en masse : NON TROUVÉ**
(seule la migration-service existe, sans format documenté). Aucun changement à la stratégie
§5/§6 : voie A (import actes) reste écartée, voie B (export CSV → pré-remplissage) reste la
meilleure piste côté patients, à qualifier avec un export réel de Malcom.

---

## 3. Agrément SESAM-Vitale / FSE — Maiia facture-t-il lui-même ?

**Verdict : OUI, sources éditeur convergentes indiquent que Maiia Kiné génère et télétransmet lui-même les FSE. Confirmation officielle sur la liste CNDA non effectuée (à vérifier).**

- L'éditeur annonce une **« génération automatique des feuilles de soins électroniques (FSE) »**
  et un **« processus fluide et conforme pour une transmission rapide et sécurisée des FSE »**,
  avec facturation possible **en mobilité, au domicile du patient**.
  Source : [cegedim-sante.com/maiia-kine](https://www.cegedim-sante.com/solutions-sante-cegedim/solutions-web/maiia-kine/)
- Maiia propose son propre **« Lecteur SESAM-Vitale »** (lecture carte Vitale + carte CPS), ce
  qui n'aurait pas de sens si Maiia n'était qu'un agenda découplé de la facturation.
  Source : [maiia.zendesk.com — Logiciel lecteur de cartes SESAM-Vitale](https://maiia.zendesk.com/hc/fr/articles/12279783304466--Logiciel-lecteur-de-cartes-SESAM-vitale)
- Maiia Kiné est cité comme éligible au **FAMI** (Fonds d'Aide à la Modernisation de l'Offre de
  Soins), dispositif réservé à des logiciels de facturation/gestion de cabinet reconnus — signal
  cohérent avec un statut de LGC facturant, pas de simple agenda.
  Source : synthèse de recherche web, cf. page éditeur ci-dessus (métrique reprise de plusieurs
  articles secondaires — **à recouper** avec la liste officielle FAMI si besoin de certitude totale).
- **Non vérifié directement** : je n'ai pas confirmé la présence de « Maiia » sur la liste
  officielle des logiciels agréés CNDA (`cnda.ameli.fr` → Consulter les logiciels → Prestataires
  de Soins), cette consultation nécessitant une recherche interactive sur le site. **NON TROUVÉ
  au sens strict d'une preuve CNDA nominative** — mais le faisceau de preuves éditeur (FSE auto,
  lecteur SESAM-Vitale propre, facturation mobilité) rend la conclusion « Maiia facture et
  télétransmet lui-même » **hautement probable**, à la différence d'un logiciel purement agenda.
  Source à consulter pour trancher : [cnda.ameli.fr](https://cnda.ameli.fr/)

**Conséquence** : comme pour VEGA, la double saisie a lieu **dans Maiia lui-même** (l'acte/la
cotation décidée chez nous doit être re-saisie dans l'écran de facturation Maiia) — ce n'est pas
un problème contourné par un autre logiciel de facturation tiers.

---

## 4. Export patients / séances / actes (pour pré-remplir notre champ Patient)

**Verdict : export CSV confirmé et documenté par l'éditeur — probablement plus riche et plus « propre » que l'export texte de VEGA, mais colonnes exactes non vérifiées (accès article bloqué).**

- Une page d'aide officielle intitulée **« Liste de patients, séances, actes »** existe et décrit
  un export : bouton **« Télécharger justificatif » → « Export CSV »**, ouverture native dans
  Excel. C'est un **CSV structuré** (pas un simple texte à séparateur ad hoc comme VEGA).
  Source : [maiia.zendesk.com — Liste de patients, séances, actes](https://maiia.zendesk.com/hc/fr/articles/27375623944338-Liste-de-patients-s%C3%A9ances-actes)
  (⚠️ contenu détaillé de l'article **non accessible** lors de cette recherche — 403 en lecture
  automatisée ; le titre et le chapô confirment l'existence de la fonctionnalité, pas le détail
  des colonnes).
- Export CSV également confirmé pour les **factures** (« Export CSV des factures sélectionnées »,
  fichier `Export_facture` au format xls dans le dossier Téléchargements).
  Source : [maiia.zendesk.com — Facture : imprimer, supprimer, exporter](https://maiia.zendesk.com/hc/fr/articles/4402878709522-Facture-imprimer-supprimer-exporter)
- **Nature de l'export** : manuel, à la demande, depuis l'interface web Maiia — pas d'API, pas de
  temps réel, mêmes limites que l'export VEGA.
- **Colonnes exactes, encodage, granularité (patient seul vs patient+séance+acte dans un même
  fichier) : NON CONFIRMÉS** dans le détail. **À vérifier sur un export réel de Malcom** au
  pilote — exactement la même réserve que pour VEGA §3.

---

## 5. Échelle d'intégration — du plus solide au plus pragmatique

| # | Voie | Ce que ça fait | Dépendance Maiia | Effort | Risque / fragilité | Verdict |
|---|------|----------------|-------------------|--------|---------------------|---------|
| A | **API d'écriture dans Maiia via « Maiia Connect »** | Éliminerait la double saisie si le programme permettait d'écrire un acte/une cotation | « Maiia Connect » = messagerie, **pas** une API d'écriture (§1bis, résolu 2026-07-22) | — | — | **Écartée** : aucune API d'écriture tiers documentée nulle part (même verdict que VEGA sur ce point) |
| B | **Export patients/séances/actes CSV → pré-remplissage chez nous** | Pré-remplit le champ Patient (et potentiellement séances/actes) | Export CSV manuel (existe, §4) | Faible | Faible : colonnes exactes à confirmer, pas de temps réel | **Recommandé** (accroche solide, sortie seule, format CSV a priori plus propre que VEGA) |
| C | **Affichage côte à côte optimisé re-saisie** | Cotation affichée « prête à recopier » en < 5 s dans l'écran de facturation Maiia | Aucune | Très faible | Très faible : ne casse jamais | **Recommandé** (socle produit, identique à VEGA) |
| D | **Presse-papiers structuré (1 clic → coller dans Maiia)** | Copier la cotation formatée, coller dans le champ acte Maiia | Le champ Maiia cible doit accepter le collage (web, donc a priori standard HTML) | Faible-moyen | Moyen : à tester réellement sur l'interface web Maiia de Malcom | **Utile SI testé OK** — probabilité de succès plus élevée que sur VEGA (Windows natif) car interface web |
| E | **Import de conventions mutuelles détourné pour d'autres usages** | — | — | — | **Hors sujet** : ce canal (§2) ne concerne que les grilles tarifaires mutuelle, pas les patients/actes | **Écarté** |
| F | **Assistant de saisie clavier / automation UI (RPA)** | Rejoue les frappes dans l'interface web Maiia | Structure de la page web Maiia | Élevé | **Élevé** : casse à chaque mise à jour d'interface, fragile | **À déconseiller en produit** (identique à VEGA) |

**Lecture d'ensemble (mise à jour 2026-07-22)** : la situation Maiia est **légèrement plus
favorable** que VEGA sur un point concret désormais confirmé — l'export patients/actes est un
**vrai CSV documenté** plutôt qu'un export texte artisanal (point B). Le point autrefois ouvert
(« Maiia Connect », voie A) est maintenant **résolu et écarté** : c'est une messagerie
inter-professionnels, pas un programme d'interfaçage tiers (§1bis) — Maiia rejoint donc VEGA sur
l'absence d'API d'écriture, mais reste en avance sur la qualité de l'export de sortie.

---

## 6. Recommandation

### Stade pilote (Malcom)
- **Socle = voie C** (affichage côte à côte, cotation prête à recopier). Zéro dépendance,
  livrable immédiatement.
- **Ajouter voie B dès que possible** : demander à Malcom un export réel « Liste de
  patients/séances/actes » (CSV) depuis son Maiia Kiné, pour confirmer les colonnes exactes et
  bâtir le pré-remplissage du champ Patient. C'est la voie la plus solide et la plus rapide à
  qualifier.
- **Tester voie D en conditions réelles** sur l'interface web de Malcom : les champs d'acte
  Maiia acceptent-ils un collage propre ? Le fait que Maiia soit une appli web (pas un exécutable
  Windows comme VEGA) rend cette hypothèse plus probable, mais **ne pas promettre avant test**.
- **Voie A écartée (§1bis)** : « Maiia Connect » est confirmé comme messagerie inter-pro, pas un
  programme d'interfaçage tiers — ne plus le présenter comme piste ouverte en interne ou au client.
- **Ne pas faire F** (automation clavier), pour les mêmes raisons que VEGA.

### Produit (au-delà du pilote)
- Industrialiser B (import CSV patients/séances/actes Maiia, tolérant aux variantes de colonnes).
- Voie A : ne plus investir de temps de recherche dessus tant que Cegedim n'a pas concrétisé sa
  « plateforme d'intégration ouverte » évoquée dans son offre d'emploi Product Manager
  Interopérabilité (§1bis-c) — à re-vérifier dans 6-12 mois, pas avant.
- Garder l'hypothèse D vivante si le test de collage sur l'interface web est concluant.

**Message commercial honnête** : identique à VEGA — pas d'« intégration Maiia » aujourd'hui,
mais une **réduction de la re-saisie** via l'affichage optimisé et, potentiellement, un
pré-remplissage patients dès que l'export CSV réel est en main. L'écriture directe dans Maiia via
« Maiia Connect » n'est **pas** une option (§1bis) — ne pas la promettre.

---

## 7. Questions à trancher uniquement avec Cegedim / Maiia (action Enzo)

1. ~~**Maiia Connect** : que couvre exactement ce programme ?~~ **RÉPONDU par recherche publique
   (§1bis, 2026-07-22)** : c'est la messagerie sécurisée inter-professionnels de santé, pas un
   programme d'interfaçage éditeurs tiers. Question résiduelle éventuelle si contact éditeur :
   Cegedim a-t-il un calendrier pour la « plateforme d'intégration ouverte » mentionnée dans son
   offre d'emploi Product Manager Interopérabilité ?
2. **Export patients/séances/actes CSV** : structure exacte (colonnes, encodage, granularité —
   un export patients seul est-il possible séparément des séances/actes) ? Peut-on l'automatiser
   (export programmé, plutôt que clic manuel) ?
3. **Agrément SESAM-Vitale** : confirmation formelle que Maiia Kiné est agréé CNDA en tant que LGC
   facturant (pas seulement déclaratif éditeur) — vérifiable normalement sur `cnda.ameli.fr`, à
   faire ou à faire confirmer par l'éditeur.
4. **Import** : Maiia peut-il importer un fichier d'actes/cotations produit par un tiers (au-delà
   du seul import de convention mutuelle) ?
5. **Collage dans les champs de saisie d'acte** : le champ acte de l'interface web Maiia
   accepte-t-il un collage programmatique fiable (pour valider ou écarter la voie D) ?

---

## 8. Comparaison rapide avec VEGA (13_INTEGRATION_VEGA.md)

VEGA : dossier API totalement fermé, export patients en texte artisanal non normalisé. Maiia
(mis à jour 2026-07-22) : même absence confirmée d'API d'écriture pour un tiers — « Maiia
Connect » a été vérifié et écarté (c'est une messagerie, §1bis), rejoignant le verdict VEGA sur ce
point — mais Maiia garde un avantage réel avec un export CSV structuré et documenté par l'éditeur,
à confirmer sur le terrain avec Malcom.

---

### Annexe — sources principales
- Éditeur / produit : [cegedim-sante.com/maiia-kine](https://www.cegedim-sante.com/solutions-sante-cegedim/solutions-web/maiia-kine/) ·
  [cegedim-sante.com/suite-maiia](https://www.cegedim-sante.com/suite-maiia/) ·
  [suite.maiia.com](https://suite.maiia.com/) ·
  [news.maiia.com — lancement Maiia Gestion kinés](https://news.maiia.com/maiia-gestion-lancement-solution-organisation-cabinet-speciale-kines/actualites/)
- Maiia Connect : [connect.maiia.com](https://connect.maiia.com/) ·
  [Zendesk — catégorie Maiia Connect](https://maiia.zendesk.com/hc/fr/categories/360002453319-Maiia-Connect) ·
  [cegedim-sante.com — Maiia Connect, messagerie sécurisée](https://www.cegedim-sante.com/solutions-sante-cegedim/solutions-web/maiia-connect/) ·
  [Google Play — Maiia Connect](https://play.google.com/store/apps/details?id=com.cegedim.maiia.connect) ·
  [DSIH — lancement Maiia Connect](https://dsih.fr/articles/4767/cegedim-sante-annonce-le-lancement-de-maiia-connect-sa-nouvelle-messagerie-gratuite-et-instantanee-qui-connecte-tous-les-professionnels-de-sante) ·
  [cegedim-logiciels.com — messagerie Maiia Connect (aide Crossway)](https://www.cegedim-logiciels.com/dyn/espace_client/Aide_en_ligne/crossway/24.03/webhelp/content/CW_Messageries_MaiiaConnect.html)
- Absence d'API publique : [apitracker.io/a/cegedim-fr](https://apitracker.io/a/cegedim-fr)
- Signal RH Cegedim (intention future, pas service existant) :
  [careers.cegedim.com — Product Manager H/F](https://careers.cegedim.com/fr/annonce/4410853-product-manager-hf-92100-boulogne-billancourt) ·
  [careers.cegedim.com — alternance interopérabilité](https://careers.cegedim.com/fr/annonce/3683321-product-manager-interoperabilite-et-back-office-en-alternance-hf-92100-boulogne-billancourt)
- Ségur / interop clinique (Maiia Médecin) :
  [cegedim-sante.com — répondre aux exigences du Ségur](https://www.cegedim-sante.com/le-blog/logiciel-medical-repondre-aux-exigences-du-segur-du-numerique-en-sante/) ·
  [maiia.zendesk.com — MSS Messagerie Sécurisée de Santé](https://maiia.zendesk.com/hc/fr/articles/4497778235026--MSS-Messagerie-S%C3%A9curis%C3%A9e-de-Sant%C3%A9)
- Réseau télésecrétariat partenaire (agenda, pas API) :
  [telesecretariat.com — Télésecrétariat Maiia](https://www.telesecretariat.com/telesecretariat-maiia/) ·
  [secretariat-telephonique.tv — Location Agenda Maiia](https://secretariat-telephonique.tv/location-dagenda/agenda-maiia/)
- Centre d'aide Maiia : [Liste de patients, séances, actes](https://maiia.zendesk.com/hc/fr/articles/27375623944338-Liste-de-patients-s%C3%A9ances-actes) ·
  [Facture : imprimer, supprimer, exporter](https://maiia.zendesk.com/hc/fr/articles/4402878709522-Facture-imprimer-supprimer-exporter) ·
  [La mutuelle sur Gestion Kiné](https://maiia.zendesk.com/hc/fr/articles/4402870410386-La-mutuelle-sur-Gestion-Kin%C3%A9) ·
  [Logiciel lecteur de cartes SESAM-Vitale](https://maiia.zendesk.com/hc/fr/articles/12279783304466--Logiciel-lecteur-de-cartes-SESAM-vitale)
- Homonyme écarté (secteur énergie, sans rapport) : [maiia.cloud](https://www.maiia.cloud/)
- CNDA (à consulter pour confirmation formelle non faite ici) : [cnda.ameli.fr](https://cnda.ameli.fr/)
- Investigation IMPORT ciblée (§2bis, 2026-07-22) : [maiia.zendesk.com — Saisir un acte, une cotation](https://maiia.zendesk.com/hc/fr/articles/10442014794770-Saisir-un-acte-une-cotation) ·
  [maiia.zendesk.com — Créer, modifier un patient](https://maiia.zendesk.com/hc/fr/articles/21273874050706-Cr%C3%A9er-modifier-un-patient) ·
  [maiia.zendesk.com — 4. Gérer les journaux et les comptes](https://maiia.zendesk.com/hc/fr/articles/4402864709394-4-G%C3%A9rer-les-journaux-et-les-comptes) ·
  [cegedim-sante.com/services-maiia](https://www.cegedim-sante.com/services-maiia/) ·
  [topaze.com — changer facilement de logiciel kiné](https://www.topaze.com/blog/actualite-kines/changer-facilement-de-logiciel-kine-pour-une-migration-sans-stress/) ·
  [resopharma.fr — norme B2.R télétransmission kiné](https://www.resopharma.fr/documents/normes/b2r_reeduc_sv140.pdf) ·
  [services.gustave.app](https://services.gustave.app/)
