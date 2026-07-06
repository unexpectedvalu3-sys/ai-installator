# Playbook Prospection PME — AI Installator

## Cibles prioritaires (par ordre de facilité de closing)

| Priorité | Secteur | Douleur principale | Ticket visé |
|----------|---------|-------------------|-------------|
| 🥇 | Artisans / BTP | Devis + relances manuelles | 500-800€ |
| 🥇 | Professions libérales (kiné, vétérinaire, ostéo) | Emails/rappels patients | 500-800€ |
| 🥈 | Cabinet comptable | Saisie factures PDF | 800-1500€ |
| 🥈 | PME commerce local | SAV email répétitif | 800-1500€ |
| 🥉 | Agence immo | Suivi prospects + reporting | 1000-2000€ |

---

## Où trouver les cibles (sources)

1. **Google Maps** → taper "comptable [ville]", "kiné [ville]", "plombier [ville]" → récupérer email/tel
2. **LinkedIn** → recherche "gérant" + secteur + ville → DM direct
3. **Pages Jaunes** → scraping manuel ou outil (liste email + tel)
4. **Réseau personnel** → toujours le plus chaud, closer en premier
5. **Facebook groupes** → groupes "entrepreneurs [région]", "artisans [ville]"

---

## Message d'approche (à adapter par canal)

### LinkedIn DM (version courte)
```
Bonjour [Prénom],

Je travaille avec des [secteur] comme vous pour automatiser
les tâches répétitives — [exemple concret : saisie de factures, 
emails clients, relances devis].

J'ai récemment aidé un client à économiser 6h/semaine sur ce type de tâche.

Vous avez 20 minutes cette semaine pour voir si c'est applicable 
chez vous ? C'est gratuit, sans engagement.

Enzo
```

### Email froid (version directe)
```
Objet : Automatiser [tâche spécifique] chez [Entreprise] ?

Bonjour [Prénom],

En regardant votre activité, j'imagine que vous passez du temps sur 
[douleur spécifique au secteur].

Je suis spécialisé dans l'automatisation de ce type de tâche pour les 
[secteur] — résultat livré en 5 jours, RGPD inclus.

Un exemple concret : [cas client anonymisé — ex: "un cabinet comptable 
de 4 personnes a récupéré 8h/semaine sur la saisie de factures"].

Vous avez 20 minutes cette semaine pour un audit gratuit ?

Enzo — AI Installator
[téléphone]
```

### Message WhatsApp / SMS (si contact direct)
```
Bonjour [Prénom], c'est Enzo. 
Je fais de l'automatisation IA pour les [secteur].
Je peux vous faire économiser plusieurs heures par semaine sur [tâche].
Démo gratuite 20 min cette semaine ?
```

---

## Hooks par secteur (première phrase d'accroche)

| Secteur | Hook |
|---------|------|
| **Artisan BTP** | "Vous faites encore vos devis à la main ?" |
| **Comptable** | "Vos assistants saisissent encore des factures PDF manuellement ?" |
| **Kiné / Ostéo** | "Vous perdez du temps à rappeler les patients qui ne répondent pas ?" |
| **Commerce** | "Vous répondez aux mêmes questions clients par email chaque jour ?" |
| **Agence immo** | "Votre reporting de la semaine se fait encore dans Excel ?" |

---

## La démo live (ce qui signe le contrat)

**Règle d'or : ne jamais vendre avec des slides. Vendre en live.**

### Protocole démo (20 minutes)
```
0-5 min  → Écoute : "Quelle est la tâche qui vous prend le plus de temps ?"
5-10 min → Demo : prends UN de leurs vrais documents (facture, email type)
           → Lance le workflow devant eux → résultat en 30 secondes
10-15 min → ROI : "Combien d'heures ça vous prendrait manuellement ?"
            → Calcule le retour : X heures × taux horaire = Y€/mois économisés
15-20 min → Offre : propose le Quick Win (500-800€) ou Pack Core (1500-3000€)
```

### Ce qu'il faut préparer avant la démo
- [ ] Workflow de base prêt (extraction facture PDF → Google Sheets)
- [ ] Workflow email → classification + draft réponse
- [ ] Clé API Claude opérationnelle
- [ ] n8n lancé sur localhost:5678
- [ ] 1 PDF de facture générique pour demo si pas de doc client dispo

---

## Gestion des objections

| Objection | Réponse |
|-----------|---------|
| **"C'est trop cher"** | "Le forfait de base c'est 800€. Si vous gagnez 5h/semaine à 20€/h c'est 400€/mois. Rentabilisé en 2 mois." |
| **"On n'a pas le temps de s'en occuper"** | "Vous me donnez 2h pour comprendre votre process. Je livre en 5 jours. Vous ne touchez à rien." |
| **"On a déjà essayé des outils, ça n'a pas marché"** | "Les outils génériques ne comprennent pas vos documents. Moi je construis spécifiquement pour vous." |
| **"Et le RGPD ?"** | "Je livre avec la documentation RGPD incluse. Vos données ne quittent pas votre système." |
| **"Je dois en parler à mon associé"** | "Pas de problème — je peux refaire la démo avec lui présent. Quand est-il dispo ?" |
| **"On verra plus tard"** | "Je comprends. Juste pour info : j'ai 2 créneaux libres cette semaine pour démarrer. Après je suis complet." |

---

## Offres à proposer

### Quick Win — 500-800€ (entry)
- 1 workflow automatisé sur leur pain #1
- Livraison : 5 jours ouvrés
- Inclus : formation 30 min + doc RGPD
- Objectif : prouver le ROI → ouvrir vers retainer

### Pack Core — 1500-3000€
- 3 workflows custom
- Connexion à leurs outils existants (Gmail, Drive, Sheets)
- Formation équipe 1h
- Doc RGPD complète
- 1 mois de support inclus

### Retainer mensuel — 400-800€/mois
- Maintenance + ajustements workflows
- 1 nouveau workflow/mois
- Support prioritaire
- À proposer systématiquement après Quick Win

---

## Suivi prospection (tracker)

Tenir à jour un Google Sheets ou Notion avec :

| Prospect | Secteur | Canal | Statut | Prochaine action | Date |
|----------|---------|-------|--------|-----------------|------|
| | | | | | |

**Statuts :** Contacté → RDV fixé → Démo faite → Offre envoyée → Signé → Retainer

---

## Règles de base

1. **10 contacts/jour minimum** les 2 premières semaines
2. **Relance à J+3** si pas de réponse (1 seule relance)
3. **Jamais d'argumentaire long** — hook court + question ouverte
4. **Démo sur vrai document client** > slides > argumentaire
5. **Toujours proposer le retainer** après signature du Quick Win
6. **1 cas client chiffré dès le 2ème client** → utiliser dans toutes les communications
