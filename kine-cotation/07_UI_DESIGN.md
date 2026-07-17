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

### 3.6 Détails
- États vides utiles (`01 — Choisis une région…`) plutôt que du blanc.
- Copie **non directionnelle** (« Choisis une région, puis l'acte réalisé » et non « à gauche » :
  en mobile l'assistant est au-dessus).
- Mobile : la baseline marketing disparaît, **le badge barème reste** (c'est de la preuve).
- Feuille `sticky` en desktop, focus visibles, impression = la feuille seule.

---

## 4. Vérifications faites (pas des intentions)

- **Contraste** — 9 combinaisons testées, **toutes ≥ 4.5:1** (min. 5.99 : accent sur carte ; max. 17.04).
- **Non-régression** — les 22 IDs consommés par le JS sont présents après build.
- **Parcours réel en navigateur** — région → segmenté (`w_chir='oui'`, filtre 15→9) → acte → séance.
- **3 paliers DAP** sur l'arthroplastie du genou (seuil **26**) : séance 20 → `info`, 25 → `warn`, 30 → `danger`.
  *(Au passage : j'avais supposé un seuil de 16, c'était 26. Le moteur avait raison, pas moi.)*
- **Mobile 375×812** : une colonne, header sur une ligne, aucun débordement horizontal.

## 5. Reste à faire
- **Export du dossier de preuve** (fichier autonome, sérialisation canonique stable → hashable).
  C'est le delta produit de `05_REPOSITIONNEMENT_PREUVE.md` §6, et l'UI est prête à l'accueillir.
- Volume de séances dans le profil → projeter l'écart en €/an (le jour où le chiffre existe).
- Impression : vérifier sur une vraie imprimante, pas seulement en CSS.
