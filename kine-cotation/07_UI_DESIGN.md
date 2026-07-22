# KinéCotation — UI/UX : le système « L'Instrument »

> 2026-07-17. Brief d'Enzo : « la qualité du site vitrine 10K, mais en changeant le style et les couleurs ».
> Source : `webapp/build_webapp.py` (le HTML est **généré** — ne jamais éditer `kinecotation.html` à la main).

---

## 1. Ce qu'on prend au 10K, et ce qu'on refuse

Le 10K (`vitrines/vitrine-10k.html`) est une **vitrine** : on l'admire une fois. KinéCotation est un **outil** : un kiné l'ouvre vingt fois par jour, entre deux patients, souvent debout.

**On reprend la rigueur :**
- système de **jetons** (aucune valeur en dur), échelle d'espacement, durées et easing nommés ;
- palette **restreinte** : 2 neutres + 1 accent + 2 sémantiques, pas une couleur de plus ;
- **contrastes vérifiés** (script de contrôle, cf. §4) ;
- `prefers-reduced-motion` respecté.

**On refuse ses procédés de vitrine** — les reprendre serait hostile ici :
| Procédé 10K | Pourquoi pas |
|---|---|
| Preloader altimètre (3 s) | 3 s × 20/jour = du temps volé à un pro |
| Curseur custom | casse l'affordance dans un formulaire |
| Scène sticky scroll-scrubbée | on saisit, on ne scrolle pas pour la vue |
| CTA magnétiques | une cible qui fuit, c'est une cible ratée |
| Fraunces géant, marquee éditorial | de la place en moins pour la donnée |

> **La vitrine vend. Cet écran instrumente.**

---

## 2. L'écart de style, délibéré

| | Vitrine 10K | KinéCotation |
|---|---|---|
| Concept | **L'Ascension** (montagne, aspirationnel) | **L'Instrument** (précision, dense, calme) |
| Température | **chaude** — papier crème `#F5F1E9` | **froide** — ardoise `#F2F5F4` |
| Encre | bleue `#0C2438` | graphite à sous-ton vert `#0E1C19` |
| Accent | orange `#F07E26` | pétrole `#0B6E5F` |
| Typo | Fraunces (serif éditorial) + Instrument Sans | **IBM Plex Sans + IBM Plex Mono** |
| Motion | 160/340/620 ms, expressive | **120/220 ms**, utilitaire |

**Pourquoi Plex Mono, et pourquoi ce n'est pas décoratif :** les lettres-clés, coefficients et tarifs
sont des **données**, lues et comparées d'un coup d'œil des dizaines de fois par jour. Elles passent
en mono à **chiffres tabulaires** (`font-variant-numeric:tabular-nums`) → les colonnes s'alignent,
`8.11` et `8.1` se distinguent, les euros se comparent verticalement. C'est le seul choix
typographique du projet qui soit **fonctionnel avant d'être esthétique** — et il différencie
naturellement l'outil de la vitrine.

**Polices** : `webapp/assets/*.woff2` (IBM Plex, licence OFL, 55 Ko), inlinées en base64 au build.
Zéro requête réseau → cohérent avec le local-first : **rien ne sort du poste**, même pas une police.

---

## 3. Les décisions d'UX (le vrai travail)

### 3.1 Le n° de séance est promu
Il **pilote l'alerte DAP**, donc tout le cœur anti-indu. Il était dans un `<input>` de 70 px au fond
du tableau. Il est maintenant un contrôle identifié sous la ligne concernée.

### 3.2 Les alertes DAP passent en tête de feuille
Elles étaient en pied de page, après le total. C'est la **fonction de sécurité** du produit : `danger`
et `warn` s'affichent **au-dessus** du tableau ; seul `info` (rappel du référentiel) reste en aval.

### 3.3 La justification épingle le barème
**C'était le trou identifié dans `05_REPOSITIONNEMENT_PREUVE.md`.** Une preuve qui ne dit pas sous
quel barème elle a été produite ne vaut rien — et le barème a changé **trois fois en huit mois**.
La justification porte désormais : source SNMKR + version de base + valeur de lettre-clé + date.

### 3.4 Choix binaires en segmenté
`Opéré / Non opéré` et `Au référentiel / Hors référentiel` étaient des `<select>` : ouvrir, chercher,
choisir. Ce sont maintenant des segmentés — **un clic**. Re-cliquer désélectionne (retour au non-filtré).
Implémentés sur `<input type="hidden">` : **le JS existant lit toujours `.value`, rien n'a bougé côté logique.**

### 3.5 ⚠️ Anti-sous-cotation : fonction CONSTRUITE puis RETIRÉE
J'ai implémenté un contrôle « il existe un acte mieux coté dans cette région ». **Mesuré sur l'app réelle, il échoue deux fois :**

1. **Bruit** — dans une région les coefficients sont quasi identiques (tout `membre_inf` tient entre
   8,00 et 8,12 : **9 centimes**). L'alerte se déclenchait à chaque cotation pour un gain dérisoire et
   **désensibilisait à l'alerte DAP**. Une alerte qui crie tout le temps ne protège plus de rien.
2. **Danger** — les régions regroupent des actes cliniquement hétérogènes. Sur une atteinte
   radiculaire (`NMI 8.5`), le contrôle proposait `TER 16` **« +16,57 € »** — paralysie cérébrale de
   l'enfant. **Aucun rapport clinique.** C'est le comportement qui *provoque* un indu, dans un produit
   dont la promesse est la défendabilité.

> **Conclusion produit : l'outil ne peut pas détecter une sous-cotation** — il ignore ce qui a été
> cliniquement fait. Le chiffre de sous-cotation se mesure **avec le kiné** (ordonnances réelles :
> facturé vs défendable), jamais par heuristique logicielle.

**Remplacé par ce qui est sûr et utile** : un rappel, *en amont du choix*, quand un critère qui change
la cotation n'est pas renseigné. Vérifié : 14 actes non filtrés → **4** une fois les 2 critères
répondus. C'est **là**, en amont, que se joue la sous-cotation.

### 3.6 La date de la séance pilote le barème
Ajoutée en tête du parcours. **Ce n'est pas la date du jour** : une séance du 31/08 facturée le 05/09
se cote au barème du 31/08, et la justification doit attester **ce** barème-là. Changer la date
**recote tout le panier** (`recoter()`) — sinon une ligne ajoutée avant correction resterait figée au
mauvais barème. Le champ est resynchronisé à chaque appel : une date affichée en désaccord avec le
barème appliqué serait précisément l'incohérence silencieuse qui produit une preuve fausse
*(bug attrapé au test — la désynchronisation était réelle)*.
`min` = `applicable_depuis` ; une séance antérieure affiche un **refus de coter** au lieu d'un tarif.
Les paliers à venir ne sont annoncés que **pour la région affichée** (annoncer les 5 NMI à un kiné du
rachis, c'est du bruit).

### 3.6 bis « Prescrites » éditable (fallback OCR + flux manuel)
Le nombre de séances **prescrites** pilote l'alerte anticipée « DAP à prévoir ». Il n'était rempli
que par l'OCR (badge lecture seule) → en **flux manuel** ou si l'**OCR échoue sur ce champ**,
l'anticipation ne se déclenchait jamais. Le badge devient un **input éditable** (à côté de « Séance n° »),
pré-rempli par l'OCR, saisissable à la main sinon. `setPrescrites` miroir de `setSeance`.
**Piège résolu** : ces inputs vivent dans le tableau reconstruit à chaque frappe (`oninput → render`) →
le focus sautait après chaque chiffre. `render()` mémorise l'input actif (`data-fk`) et le restaure —
on peut taper « 30 » d'affilée. Vérifié : les 3 paliers d'alerte (prévoir/silence/requise), focus
préservé, mobile 375 (le conteneur `.seance` passe en `flex-wrap`).

### 3.7 Détails
- États vides utiles (`01 — Choisis une région…`) plutôt que du blanc.
- Copie **non directionnelle** (« Choisis une région, puis l'acte réalisé » et non « à gauche » :
  en mobile l'assistant est au-dessus).
- Mobile : la baseline marketing disparaît, **le badge barème reste** (c'est de la preuve).
- Feuille `sticky` en desktop, focus visibles, impression = la feuille seule.

### 3.8 Caviardage de l'ordonnance AVANT tout envoi (étape 00)
**Le problème.** L'ordonnance est une **donnée de santé**. L'ancien flux (`uploadOrdo`) envoyait le
fichier à `/api/ocr` **dès la sélection** — donc l'image nominative brute quittait le poste. Le
protocole benchmark (`benchmark/00_PROTOCOLE_BENCHMARK_OCR.md` §0) exige de caviarder nom / prénom /
date de naissance / NIR *avant la photo* ; en production, on ne peut pas compter là-dessus. On rend
donc le caviardage **structurel dans l'app** : les conditions du benchmark deviennent permanentes.

**Le flux (itération 2 — l'app masque toute seule).** Sélection d'une **image** (PNG/JPG/WebP) →
aperçu plein largeur dans un `<canvas>` → **détection locale** du bloc patient → l'aperçu apparaît
**déjà masqué** aux zones détectées → le kiné **vérifie d'un regard**, corrige au besoin (glisser pour
ajouter, « Annuler le dernier », « Tout effacer ») → bouton **« Analyser »** → et **seulement là**
l'image masquée part à `/api/ocr`. Le dessin manuel de la brique 1 reste **intact** : c'est le filet
de correction quand l'auto rate ou manque un bloc.

**Détection 100 % locale au navigateur (jamais de fuite).** La détection tourne dans le navigateur via
**tesseract.js** + le pack FR `tessdata_fast` (assets servis depuis `/static/tesseract/`, chargés
**paresseusement** à la 1ʳᵉ image, worker réutilisé ensuite). L'image **non masquée** ne sort jamais du
poste — **même pas vers notre backend** : la détection lit le canvas en mémoire, elle ne téléverse rien.
On repère les **libellés imprimés** (« Patient », « Nom », « Prénom », « Né(e) le », « NIR », « N° SS »…)
et on pré-pose un masque sur la **valeur à droite** du libellé (large à dessein : l'OCR photo est
approximatif, mieux vaut masquer trop que trop peu) ; on masque aussi tout **motif type NIR** (13-15
chiffres). Le prescripteur (RPPS 11 chiffres, « Dr … ») n'est **pas** une ancre → il reste visible.

**Pourquoi confirm-first, et pas silencieux.** Les masques auto **comptent** comme masques (le bouton
s'active), mais **l'envoi reste un geste explicite du kiné** — jamais d'auto-envoi. La donnée est de
santé : la machine propose, l'humain valide. Tant que le taux d'acceptation sans retouche n'est pas très
haut, on ne franchit pas le pas du tout-automatique.

**Métrique de confiance (pour décider un jour du tout-automatique).** Compteur `localStorage`
`kine_cav_stats {proposes, acceptes_sans_retouche}` (compteurs **seuls** — aucune donnée de santé),
incrémenté à chaque envoi où l'auto a proposé ≥ 1 masque ; « accepté sans retouche » = le kiné n'a ni
ajouté, ni annulé, ni tout effacé. Affiché discrètement dans **Mon profil** : « Caviardage auto : N/M
acceptés sans retouche ».

**Dégradation propre.** En `file://` (hors-ligne, `AUTO_OK=false`) ou si les assets ne chargent pas
(catch), on retombe **exactement** sur le flux manuel de la brique 1, avec la microcopie d'origine et
**zéro erreur console**. Si la détection tourne mais ne trouve **aucun** bloc (ordonnance manuscrite) :
microcopie « aucun bloc patient détecté — masque-le toi-même » + flux manuel.

**Pourquoi canvas et pas overlay CSS.** Les rectangles sont **gravés dans les pixels** (`fillRect`),
puis `canvas.toBlob()` → `FormData` (même endpoint, rien à changer côté serveur). Un overlay CSS
serait cosmétique : le fichier envoyé resterait nominatif. Ici, **le blob EST la version masquée**.

**Le principe non négociable, écrit dans le code.** L'image originale non masquée ne vit que dans
`ordoImg` (mémoire) et dans les pixels du canvas. **Aucun blob de l'original n'est jamais créé** :
`caviarderEtAnalyser()` est le seul producteur de blob, et il lit le canvas *après* gravure.

**Intuitivité (le critère de succès d'Enzo).**
- Geste universel (glisser = tracer un rectangle, comme un outil de capture), câblé en **souris ET
  tactile** (`mousedown/move/up` + `touchstart/move/end`, `touch-action:none` pour ne pas scroller).
- Microcopie au-dessus de l'aperçu : « Masque le **nom**, le **prénom** et la **date de naissance**…
  Le prescripteur peut rester. » (tutoiement, cohérent avec le reste).
- **Annuler le dernier masque** + **Tout effacer** (ghost). Pastille compteur (« 2 masques »). Pendant
  la détection (~1-3 s), état visible sur le canvas (voile + spinner « Détection du bloc patient… »).
- **Garde-fou** : **« Analyser »** est **désactivé tant qu'aucun masque n'est posé** (les masques
  auto-proposés comptent). Une case « Aucune info patient visible sur cette photo » débloque les cas
  déjà cadrés — **jamais** d'envoi silencieux non caviardé. Le bouton s'appelle « Analyser » (et non
  « Caviarder et analyser ») : avec l'auto-proposition, le caviardage est un **état visible** sur
  l'aperçu au-dessus, pas un geste à nommer.
- **PDF refusé** proprement (« prends l'ordonnance en photo ») : le canvas ne rend pas les PDF sans
  lib, et on ne veut pas d'échappatoire qui enverrait un fichier non masqué. `accept` limité aux images.

### 3.9 Champ « Patient » — local, jamais transmis
Un input **nom + prénom** dans l'en-tête de la feuille. Il alimente l'en-tête imprimé (« Patient : X »)
et la justification (« Feuille établie le … pour le patient X »). **Choix de conformité, pas un oubli
d'intégration** : la valeur vit dans l'état JS (`patient`), n'est envoyée à **aucun** endpoint et
n'est **pas** persistée en `localStorage` (une feuille = un patient ; « Vider » la réinitialise).
Microcopie discrète : « saisi localement, jamais transmis ». Le champ est **statique** (hors du bloc
que `render()` reconstruit) pour ne pas perdre le focus à chaque frappe ; le nom imprimé, lui, est
rendu dans `.fh` à partir de la variable. Le `patient_nom` que l'OCR pourrait renvoyer (vide dans le
flux caviardé) est **volontairement ignoré** : une lecture cloud ne doit jamais écraser la saisie locale.

> **Séparation des deux données de santé.** L'**image** part au cloud, mais **caviardée** ; l'**identité
> patient** est saisie localement et **ne quitte jamais le poste**. Aucune des deux ne circule en clair.

---

## 4. Vérifications faites (pas des intentions)

- **Contraste** — 9 combinaisons testées, **toutes ≥ 4.5:1** (min. 5.99 : accent sur carte ; max. 17.04).
  Éléments du caviardage/patient revérifiés : consigne 13.08, microcopie/`saisi localement` 4.57,
  compteur 8.23 (le panneau caviardage est passé sur fond `--card` — l'affordance est portée par la
  bordure accent gauche, pas par une teinte de fond qui aurait fait tomber la microcopie à 4.39).
- **Caviardage — le blob envoyé est bien masqué** (test navigateur, `fetch` intercepté sur
  `syn_01_ptg_genou.png`) : 2 masques souris → le blob capté, redessiné, a des pixels **noirs (0,0,0)**
  aux zones masquées et **préserve** le reste ; un seul `FormData` (champ `ordonnance`), **aucun blob de
  l'original**. Compteur, annuler, tout-effacer, garde-fou (bouton désactivé sans masque, case débloquante),
  refus PDF, geste **tactile** (`TouchEvent` réels) : tous vérifiés. Zéro erreur console.
- **Patient local** — apparaît dans l'en-tête + la justification, **survit** à un changement de date de
  séance, échappé (XSS), vidé par « Vider », et **absent de toute requête réseau** (le seul envoi est le
  blob image).
- **Non-régression** — les 22 IDs consommés par le JS sont présents après build.
- **Parcours réel en navigateur** — région → segmenté (`w_chir='oui'`, filtre 15→9) → acte → séance.
- **3 paliers DAP** sur l'arthroplastie du genou (seuil **26**) : séance 20 → `info`, 25 → `warn`, 30 → `danger`.
  *(Au passage : j'avais supposé un seuil de 16, c'était 26. Le moteur avait raison, pas moi.)*
- **Mobile 375×812** : une colonne, header sur une ligne, aucun débordement horizontal.
- **PWA installable** — manifest (icône monogramme « K » blanc sur pétrole `#0B6E5F`, coins arrondis + variante *maskable*), `theme-color` encre `#0E1C19`, service worker prudent (cache-first sur `/static/` public uniquement, réseau pour tout le reste). Vérifié en navigateur : SW actif au scope `/`, manifest 200 sans login, l'app reste gardée. Détail installation → `09_HEBERGEMENT.md`.

## 5. Reste à faire
- **Export du dossier de preuve** (fichier autonome, sérialisation canonique stable → hashable).
  C'est le delta produit de `05_REPOSITIONNEMENT_PREUVE.md` §6, et l'UI est prête à l'accueillir.
- Volume de séances dans le profil → projeter l'écart en €/an (le jour où le chiffre existe).
- Impression : vérifier sur une vraie imprimante, pas seulement en CSS.
