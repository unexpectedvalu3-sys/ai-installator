# 13 — Intégration VEGA (Epsilog / CGM)

> **But du document** : établir les FAITS (sources primaires, recherche web) sur ce que VEGA
> accepte en entrée/sortie, et en déduire l'échelle réaliste d'intégration pour KinéCotation.
> **Rappel de positionnement** : complément de VEGA, jamais concurrent (`00_PROJECT_PLAN.md` §4).
> Le frein d'adoption à lever = la **double saisie** (le kiné re-saisit dans VEGA la cotation
> décidée chez nous).
>
> **Méthode** : aucune donnée inventée. Chaque affirmation porte sa source, ou est marquée
> « non trouvé ». Recherche web uniquement, aucun contact commercial. Date : 2026-07-20.

---

## 0. Ce qu'est VEGA (cadrage)

- VEGA est édité par **Epsilog**, marque du groupe **CompuGroup Medical (CGM)**. Logiciel de
  gestion + télétransmission pour auxiliaires médicaux (IDEL, **kinés/MKDE**, orthophonistes,
  orthoptistes). ~50 000 utilisateurs revendiqués, éditeur depuis 1993.
  Source : [vega-logiciel.fr](https://www.vega-logiciel.fr/) ·
  [LinkedIn Epsilog-VEGA](https://fr.linkedin.com/company/epsilog-vega)
- La **facturation réelle (FSE, télétransmission SESAM-Vitale)** vit dans VEGA, application
  bureautique Windows propriétaire. C'est là que la cotation décidée chez nous doit être ressaisie.

---

## 1. API publique / programme partenaires / interfaçage éditeurs

**Verdict : aucune API publique française ni programme d'interfaçage éditeurs documenté pour VEGA. NON TROUVÉ.**

- **Pas d'API ni de portail développeur VEGA/Epsilog trouvé.** Aucune page « développeurs »,
  « API », « intégration éditeurs » sur vega-logiciel.fr ou epsilog.com dans les résultats.
  La page « collaboratif » ne mentionne **aucune** API ouverte ni programme partenaire tiers.
  Source : [vega-logiciel.fr/kinesitherapeute/collaboratif](https://www.vega-logiciel.fr/kinesitherapeute/collaboratif/)
- **CGM (maison mère) expose des API — mais dans le contexte US, pas VEGA France.** CGM publie
  des « publicly accessible APIs » et une FHIR API pour ses produits US (ex. CGM eMDs, CGM Aprima).
  Rien n'indique que ces API couvrent VEGA/Epsilog en France ni le flux de facturation kiné.
  Source : [CGM eMDs API Terms of Use](https://www.cgm.com/usa_en/products/electronic-health-records/other-ehrs/cgm-emds/cgm-emds-api-terms-of-use.html)
  → **à ne pas surinterpréter** : présomption d'API France = fausse tant que non confirmée par Epsilog.
- **Doctolib ↔ VEGA : pas d'intégration officielle.** Sur le forum Epsilog, la question d'une
  passerelle Doctolib est traitée comme « Doctolib en remplacement/à côté de VEGA », pas comme une
  intégration. Un mot de la direction VEGA évoquait (fil daté ~2018) « un projet similaire intégré
  à Véga à l'étude » — c.-à-d. **VEGA développe SON propre agenda, pas une passerelle tierce**.
  Des kinés utilisent Doctolib/Keldoc **en parallèle** (double saisie), faute d'intégration.
  Source : [forum.epsilog.com — « Doctolib ? »](https://forum.epsilog.com/viewtopic.php?t=16748)
- **Le seul « connecté » officiel = CLICKDOC PRO**, l'agenda en ligne… **également édité par CGM**.
  Synchronisation CLICKDOC ↔ VEGA « pour éviter la double saisie » de l'agenda. C'est une intégration
  **intra-groupe CGM**, pas une API ouverte à des tiers.
  Sources : [vega-logiciel.fr/kinesitherapeute/agenda](https://www.vega-logiciel.fr/kinesitherapeute/agenda/) ·
  [collaboratif](https://www.vega-logiciel.fr/kinesitherapeute/collaboratif/)

**Conséquence** : il n'existe pas, à ce jour et publiquement, de canal officiel pour **écrire**
une cotation/un acte dans VEGA depuis un logiciel tiers. La stratégie « on pousse la cotation
dans la FSE de VEGA par API » est **exclue** en l'état.

---

## 2. Formats d'import (patients, actes, agenda)

**Verdict : import documenté uniquement dans l'écosystème CGM (CLICKDOC → VEGA). Aucun format d'import public d'actes/cotations. NON TROUVÉ pour les actes.**

- **Import agenda** : la synchro CLICKDOC PRO ↔ VEGA existe (intra-CGM, cf. §1). Un tutoriel montre
  l'inverse — importer les patients **de VEGA vers CLICKDOCPRO**.
  Source : [YouTube — « Importer les patients de VEGA dans CLICKDOCPRO »](https://www.youtube.com/watch?v=OGL0ipOpPn8)
- **Import d'actes / de cotations depuis un tiers** : **NON TROUVÉ.** Rien n'indique que VEGA
  ingère un fichier d'actes/cotations produit par un logiciel externe. Le flux de facturation
  (choix de l'acte NGAP, création FSE) se fait dans l'interface VEGA.
- Signal des forums : les utilisateurs réclament de longue date un import/export « viable » de
  l'organiseur et des coordonnées — signe que **l'interop par fichier reste pauvre et non prioritaire**
  côté éditeur. Source : [forum.epsilog.com — export .csv organiseur](http://forum.epsilog.com/viewtopic.php?f=4&t=8595&vega=vega5)

---

## 3. Export patients (pour pré-remplir notre champ Patient)

**Verdict : OUI — export texte des patients confirmé et documenté. C'est le point d'accroche le plus solide.**

- VEGA exporte la **liste des patients** (bénéficiaires) vers un **fichier texte**. Procédure
  documentée par un concurrent (outil de migration Bilan Kiné) :
  **Outils → onglet Fichiers → Bénéficiaires → bouton « Editer » → « Coordonnées des patients »
  → « Autre action » → « Exportez vers un fichier texte »** → choix emplacement/nom.
  Source : [bilankine.fr — importer patients/prescripteurs depuis VEGA](https://bilankine.fr/comment-importer-vos-patients-prescripteurs-depuis-vega-vers-bilan-kine/)
- **Champs exportés** (d'après le forum Epsilog) : coordonnées administratives (nom, prénom,
  adresse, n° de sécu) + couverture sociale (médecin, caisse, mutuelle). Chemin alternatif :
  icône **LISTE → PATIENTS → petite main → « Editer la liste »**. Le format **« Texte » avec
  séparateur « ; »** est proposé pour faciliter l'import ailleurs (≈ CSV).
  Sources : [forum — Export de données VEGA](https://forum.epsilog.com/viewtopic.php?t=1495) ·
  [forum — Exportation fichier patient sous excel](https://forum.epsilog.com/viewtopic.php?t=2894)
- **Nature de l'export** : **manuel, à la demande, unidirectionnel (sortie seule)**. Pas d'API,
  pas de temps réel. Le kiné déclenche l'export ; nous consommons le fichier localement.
- **Le séparateur exact et la liste de colonnes complète ne sont pas figés** dans une doc officielle
  Epsilog trouvée (les champs ci-dessus viennent d'utilisateurs). **À confirmer** sur un export réel
  (celui de Malcom au pilote), pas à supposer.

---

## 4. Interop réglementaire (Ségur vague 2)

**Verdict : le paramédical (kinés) entre dans le périmètre Ségur vague 2, mais l'interop Ségur vise le MÉDICAL (documents de santé), PAS la facturation/cotation. Ne débloque pas l'écriture d'une cotation dans VEGA. Peut, à terme, offrir un export de données santé normalisé que nous pourrions lire.**

- **Nouveau couloir « Paramédical » (dont kinés) en vague 2.** Périmètre étendu à 3 nouveaux
  couloirs : sage-femme, chirurgien-dentiste, **paramédical**.
  Source : [esante.gouv.fr — Ségur vague 2 dispositifs et référencement](https://esante.gouv.fr/ens/segur-numerique-sante/vague-2)
- **Calendrier LGC ville/paramédical** : dépôt des demandes d'avance **avant le 16/12/2026**
  (référentiel DSR par dispositif). Source : [esante.gouv.fr — vague 2 / référencement](https://esante.gouv.fr/ens/segur-numerique-sante/vague-2/referencement)
- **5 services socles imposés au LGC** : INS qualifié · MSSanté (envoi **et** réception) ·
  Pro Santé Connect · DMP/Mon espace santé (consultation **et** alimentation). Plus : intégration
  des documents reçus par MSSanté, exigences d'ergonomie, et **« mise à disposition des données de
  santé sous un format lisible, exhaustif et exploitable »**.
  Source : [esante.gouv.fr — vague 2](https://esante.gouv.fr/ens/segur-numerique-sante/vague-2)
- **Limite structurante pour nous** : l'interop Ségur porte sur des **documents médicaux**
  (compte-rendus, INS, DMP, MSSanté) — **pas sur les actes de facturation NGAP ni les FSE**.
  Ségur **n'ouvre donc aucun canal pour injecter une cotation dans le circuit de facturation VEGA**.
- **Opportunité indirecte, à surveiller** : l'exigence « données de santé exploitables » **pourrait**
  imposer aux LGC paramédicaux un **export normalisé** (patients / prise en charge) que nous
  pourrions lire pour pré-remplir. **À vérifier dans le DSR paramédical** (non tranché ici) — le
  format et le périmètre exacts pour les kinés ne sont pas confirmés.
  Piste doc : [Avis de référencement SFP-LGC Va2 (PDF ANS)](https://esante.gouv.fr/sites/default/files/media/document/AF-SFP-LGC-Va2.pdf)

---

## 5. Échelle d'intégration — du plus solide au plus pragmatique

| # | Voie | Ce que ça fait | Dépendance VEGA | Effort | Risque / fragilité | Verdict |
|---|------|----------------|-----------------|--------|--------------------|---------|
| A | **API d'écriture dans VEGA (pousser la cotation/FSE)** | Éliminerait 100 % de la double saisie | API publique VEGA | — | **Bloqué** : aucune API publique trouvée (§1) | **Écarté** tant qu'Epsilog n'ouvre rien |
| B | **Export patients VEGA → pré-remplissage chez nous** | Le champ Patient est pré-rempli, l'utilisateur ne re-tape pas l'identité | Export texte manuel (existe, §3) | Faible | Faible : format à confirmer, pas de temps réel, manuel | **Recommandé** (accroche solide, sortie seule) |
| C | **Affichage côte à côte optimisé re-saisie** | Cotation affichée en gros, format « prêt à recopier » en < 5 s dans VEGA | Aucune | Très faible | Très faible : ne casse jamais, aucune dépendance éditeur | **Recommandé** (socle produit) |
| D | **Presse-papiers structuré (1 clic → coller dans VEGA)** | Copier la cotation formatée, coller dans le champ VEGA | Le champ VEGA cible doit accepter le collage | Faible-moyen | Moyen : dépend de l'ergonomie des champs VEGA (à tester réellement), gain partiel | **Utile SI testé OK** sur VEGA réel |
| E | **Assistant de saisie clavier / automation UI (RPA)** | Rejoue les frappes dans VEGA | Fenêtre VEGA au pixel/à l'ordre des champs | Élevé | **Élevé** : casse à chaque MAJ VEGA, support cauchemar, perçu comme « robot fragile » | **À déconseiller en produit** |
| F | **Interop Ségur (export santé normalisé)** | Lire les données patient/prise en charge via un futur export standardisé | Référencement Ségur paramédical de VEGA | Moyen | Moyen : dépend du DSR paramédical (non tranché), horizon 2026-2027, sortie seule (pas d'écriture cotation) | **À surveiller**, pas un pari pilote |

**Lecture d'ensemble** : aucune voie ne supprime totalement la re-saisie sans coopération d'Epsilog
(voie A). Le réalisme = **réduire la friction** (B + C, éventuellement D) plutôt que **supprimer**
la double saisie. E est un piège produit. F est un pari réglementaire à moyen terme.

---

## 6. Recommandation

### Stade pilote (Malcom)
- **Socle = voie C** (affichage côte à côte, cotation « prête à recopier » en < 5 s). Zéro dépendance,
  livrable immédiatement, ne casse jamais.
- **Ajouter voie B** si Malcom accepte un export patients depuis son VEGA : on récupère **son fichier
  texte réel**, on confirme séparateur + colonnes exacts (§3), on pré-remplit le champ Patient.
  C'est aussi la meilleure façon d'obtenir les **faits terrain** sur le format.
- **Tester voie D en conditions réelles** sur le VEGA de Malcom (le champ acte/cotation accepte-t-il
  un collage propre ?). Si oui → « 1 clic copier » ; si non → on s'en tient à C. **Ne pas promettre
  D avant le test.**
- **Ne pas faire E** (automation clavier), même en démo : ça crée une attente intenable.

### Produit (au-delà du pilote)
- Industrialiser B (un « import patients VEGA » propre, tolérant aux variantes de format) + C.
- **Surveiller le DSR Ségur paramédical** (voie F) : si un export santé normalisé devient obligatoire
  pour les LGC kiné (échéance dépôts 16/12/2026), il remplacerait avantageusement l'export texte ad hoc.
- Garder la porte A ouverte via un **contact Epsilog** (cf. §7) : c'est la seule voie qui tuerait la
  double saisie, mais elle ne dépend pas de nous.

**Message commercial honnête** : on ne « s'intègre pas dans VEGA » aujourd'hui ; on **réduit la
re-saisie à quelques secondes** et on **pré-remplit** ce qu'on peut légitimement lire (patients).
Toute promesse d'intégration profonde dépend d'Epsilog.

---

## 7. Questions à trancher uniquement avec Epsilog (action Enzo)

Ces points ne sont **pas résolubles par recherche web** — ils exigent un contact éditeur :

1. **API / interfaçage** : Epsilog expose-t-il une API (ou un connecteur partenaire) permettant à un
   tiers de **transmettre un acte/une cotation** dans VEGA (pré-remplir une FSE) ? Sous quelles
   conditions (contrat, certification, coût) ?
2. **Programme partenaires** : existe-t-il un programme d'interfaçage éditeurs (comme la logique
   CLICKDOC, mais ouvert aux tiers) ? Processus d'onboarding ?
3. **Formats d'import** : VEGA peut-il **importer** un fichier d'actes/patients produit par un tiers
   (spéc de format, exemple de fichier) ? Au-delà du seul écosystème CLICKDOC.
4. **Export patients** : le format texte est-il **stable et documenté** (séparateur, liste de colonnes,
   encodage) ? Y a-t-il un export plus riche/automatisable que le passage manuel par l'IHM ?
5. **Feuille de route Ségur vague 2 paramédical** : VEGA vise-t-il le référencement kiné, à quelle
   échéance, et le futur export « données de santé exploitables » sera-t-il consommable par un tiers ?
6. **Presse-papiers / collage** : les champs de saisie d'acte VEGA acceptent-ils un collage
   programmatique fiable (pour valider ou écarter la voie D) ?

---

### Annexe — sources principales
- vega-logiciel.fr : [accueil](https://www.vega-logiciel.fr/) ·
  [collaboratif](https://www.vega-logiciel.fr/kinesitherapeute/collaboratif/) ·
  [agenda](https://www.vega-logiciel.fr/kinesitherapeute/agenda/)
- Forum Epsilog : [Doctolib ?](https://forum.epsilog.com/viewtopic.php?t=16748) ·
  [Export de données VEGA](https://forum.epsilog.com/viewtopic.php?t=1495) ·
  [Export patient Excel](https://forum.epsilog.com/viewtopic.php?t=2894)
- [Bilan Kiné — migration depuis VEGA](https://bilankine.fr/comment-importer-vos-patients-prescripteurs-depuis-vega-vers-bilan-kine/)
- CGM : [eMDs API Terms of Use](https://www.cgm.com/usa_en/products/electronic-health-records/other-ehrs/cgm-emds/cgm-emds-api-terms-of-use.html)
- ANS Ségur vague 2 : [dispositifs/référencement](https://esante.gouv.fr/ens/segur-numerique-sante/vague-2) ·
  [référencement — calendrier](https://esante.gouv.fr/ens/segur-numerique-sante/vague-2/referencement) ·
  [Avis référencement SFP-LGC Va2 (PDF)](https://esante.gouv.fr/sites/default/files/media/document/AF-SFP-LGC-Va2.pdf)
