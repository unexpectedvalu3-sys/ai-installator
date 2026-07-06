# KinéCotation — Copilote de cotation NGAP pour kinés

> Plan de projet — rédigé par le CEO (Claude) · v0.1 · 2026-06-27
> Sous-projet de **AI Installator** (agence IA automation PME).

---

## 1. Le pitch en une ligne

**Un copilote qui transforme « ordonnance + soins réalisés » en la cotation NGAP optimale ET défendable** — pour arrêter de sous-coter par peur de la CPAM.

---

## 2. Le problème (validé terrain par un kiné)

Depuis l'**avenant 7 (22 février 2024)**, la nomenclature kiné est passée à un système de **20 nouvelles lettres-clés** organisées par zone anatomique + contexte chirurgical + référentiel pathologie. Conséquence directe :

| Douleur | Mécanisme | Coût pour le kiné |
|---------|-----------|-------------------|
| **Sous-cotation défensive** | Le kiné code « au plus bas » par peur de l'indu | **Perte de CA récurrente** (manque à gagner à chaque séance) |
| **Indu / contrôle CPAM** | Mauvaise lettre-clé ou non-respect du référentiel | **Remboursement sur 3 ans + pénalité** (peut doubler la somme) |
| **Charge mentale** | Choisir la bonne lettre-clé à chaque facture | Temps perdu, stress, rejets de télétransmission |

**Le double bind** : coder haut = risque d'indu · coder bas = perte de revenu garantie. Aujourd'hui le kiné choisit la perte certaine pour éviter le risque. **On supprime le dilemme.**

---

## 3. Pourquoi c'est une vraie opportunité

- **Marché** : ~50 000 kinés libéraux en France, dont ~35 000 équipés VEGA.
- **Timing** : réforme récente (fév. 2024) → complexité fraîche, mal digérée, les habitudes ne sont pas prises.
- **Pain quantifiable** : on peut chiffrer le € récupéré ET le € de risque évité → ROI démontrable = argument de vente PME-friendly (cf. positionnement AI Installator « mener par la valeur »).
- **Design partner gratuit** : le kiné ami = validation domaine + 1er beta + cas de référence.

---

## 4. Positionnement — NE PAS attaquer VEGA de front

VEGA domine (35k/50k) sur la **facturation complète** (FSE, télétransmission, agenda, compta). Les concurrer = suicide.

**Notre wedge : une couche fine de DÉCISION, pas un logiciel de facturation.**
- VEGA fait de l'« aide à la saisie » mécanique (tu sais déjà quoi coter, il te le tape).
- Nous faisons de l'**aide à la décision** : *tu ne sais pas* quoi coter → l'arbre te guide → te donne la cotation max légale **+ la justification traçable** pour te défendre en cas de contrôle.

| | VEGA & co. | KinéCotation |
|---|---|---|
| Cœur | Facturation / FSE | **Décision de cotation** |
| Question résolue | « comment je transmets » | « **quoi coter, et pourquoi c'est défendable** » |
| Anti-indu | ❌ | ✅ justification générée par cotation |
| Anti-sous-cotation | ❌ | ✅ pousse vers le max légal |

> Stratégie : **complément**, pas remplaçant. À terme, intégration/export vers VEGA & co plutôt que concurrence.

---

## 5. MVP (le plus petit truc qui crée de la valeur)

**Arbre de décision interactif** qui prend en entrée :
1. Zone anatomique traitée (rachis / membre sup / membre inf / spécialité)
2. Opéré ou non (chirurgical C / médical M)
3. Pathologie dans le référentiel ou non (R / V)
4. Acte (séance de rééduc / bilan BDK / supplément)

Et sort :
- **La lettre-clé + coefficient** recommandés
- **Le nombre de séances autorisé** et si une **DAP** (demande d'accord préalable) est requise
- **Une justification rédigée** (traçabilité anti-indu) reliée à l'ordonnance
- Un **flag d'alerte** si l'ordonnance est incomplète/non conforme

Forme MVP : commencer en **CLI / script** (validation logique avec le kiné), puis web app légère.

**Hors scope MVP** : pas de FSE, pas de télétransmission, pas d'agenda. On reste sur la décision.

---

## 6. Architecture technique

```
[Ordonnance + soins] → [Arbre de décision] → [Moteur de cotation] → [Cotation + justif]
                              ↑
                    [Base de connaissance NGAP]  ← LE moat (données à jour, vérifiées)
```

- **Base de connaissance NGAP** (`knowledge_base/ngap_kine.json`) : lettres-clés, coefficients, règles séances/DAP. **C'est l'actif clé** — sa fraîcheur et sa justesse = la barrière à l'entrée.
- **Moteur** : Python pour le prototype (validation rapide), portage Ruby/n8n si industrialisation (stack maison AI Installator).
- **Couche LLM (Claude API)** : ✅ OCR ordonnance fait (`prototype/ordonnance_ocr.py`, `claude-opus-4-8` vision + structured output). **Principe de sécurité** : le LLM fait UNIQUEMENT la perception (extraire les faits cliniques) ; le moteur déterministe fait la cotation. Jamais de coefficient inventé par le LLM.

### Contraintes critiques (CEO must-know)
- ⚠️ **Données de santé** : ordonnances = données sensibles → si on stocke, **hébergement HDS** (Hébergeur de Données de Santé) obligatoire. MVP = **zéro stockage / traitement local** pour éviter ce coût au départ. Aligné avec l'ADN RGPD d'AI Installator (pack RGPD déjà livré = atout crédibilité).
- ⚠️ **Responsabilité** : outil d'**aide à la décision** — le kiné reste seul responsable de sa facturation. Disclaimer obligatoire. On ne « certifie » pas, on « recommande + justifie ».

---

## 7. Business model (hypothèses à tester)

- **Cible** : kiné libéral solo + petits cabinets.
- **Pricing** à valider : abonnement **15–30 €/mois/praticien** (vs. plusieurs centaines/milliers de € de sous-cotation annuelle récupérée → ROI évident).
- **Angle de vente** : « Récupère ta sous-cotation + sécurise-toi contre l'indu pour le prix d'un café par semaine. »
- **GTM** : design partner kiné → bouche-à-oreille ordre/CPTS/groupes Facebook kinés → contenu (la complexité NGAP = aimant SEO, cf. concurrents qui font du contenu là-dessus).

---

## 8. Roadmap

| Phase | Objectif | Livrable | Statut |
|-------|----------|----------|--------|
| **P0 — Recherche** | Maîtriser la NGAP 2024 | `01_RECHERCHE_NGAP.md` | ✅ fait |
| **P1 — Modélisation** | Arbre + base de connaissance | `02_decision_tree_v0.md` + `ngap_kine_v0.json` | ✅ squelette posé |
| **P2 — Prototype** | Moteur CLI qui guide la cotation | `prototype/cotation_engine.py` | ✅ v0 posée |
| **P3 — Validation domaine** | Session avec le kiné ami : valider règles + compléter coefficients vérifiés | À planifier | ⏳ besoin Enzo |
| **P4 — Données vérifiées** | 82 actes + coefficients + 14 référentiels HAS (seuils DAP) + déplacements IFS/IFD/IK — source SNMKR/ameli | `ngap_kine.json` + moteur facture | ✅ fait |
| **P5 — Web app légère** | Interface utilisable par un vrai kiné | App | ⏳ |
| **P6 — Pilote payant** | 1er cabinet en conditions réelles | Cas de référence | ⏳ |

---

## 9. Risques & parades

| Risque | Gravité | Parade |
|--------|---------|--------|
| Données NGAP fausses → mauvaise cotation → on cause un indu | 🔴 Critique | Sourcing 100 % officiel (ameli/avenant 7) + validation kiné + disclaimer responsabilité |
| HDS / RGPD si stockage santé | 🟠 | MVP local sans stockage ; HDS seulement à l'industrialisation |
| VEGA ajoute la même feature | 🟠 | Vitesse + focus + justification anti-indu (eux n'en font pas) |
| Réforme NGAP qui rebouge | 🟡 | Base de connaissance versionnée = facile à mettre à jour (= service récurrent vendable) |
| Adoption (kiné conservateur) | 🟡 | Design partner + preuve € récupéré chiffrée |

---

## 10. Prochaine action concrète (besoin Enzo)

**Organiser une session de 1 h avec le kiné ami** pour :
1. Valider la logique de l'arbre (`02_decision_tree_v0.md`).
2. Faire coter 5–10 ordonnances réelles à la main → comparer avec l'outil → mesurer l'écart de sous-cotation (= notre 1er chiffre de vente).
3. Récupérer les coefficients/règles exacts qu'il utilise au quotidien (compléter la KB).

> Tout le reste (compléter les données officielles, monter la web app) je peux le faire en autonomie une fois la logique validée.
