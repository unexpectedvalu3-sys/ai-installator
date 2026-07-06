# Arbre de décision — Cotation NGAP v0

> Logique à VALIDER avec le kiné design partner (P3). Coefficients/séances marqués `?` = à sourcer (P4).

```
ENTRÉE : ordonnance + soins réalisés à la séance
│
├─ Q0. L'acte est-il un BILAN (BDK) ?
│     └─ OUI → AMK 10,7 (rééduc/réadapt) ou AMK 10,8 (neuro/musculaire)
│              + rappel : facturable même sans mention "bilan" sur l'ordo
│              → STOP (cotation bilan)
│
├─ Q1. ZONE anatomique principale traitée ?
│     ├─ Rachis ───────────────► Q2a
│     ├─ Membre supérieur ─────► Q2b
│     ├─ Membre inférieur ─────► Q2b
│     └─ Spécialité (ORL/resp, neuro, vasculaire, périnée,
│        amputation, brûlé, palliatif, gériatrie, multi-territoires)
│                              ──► Q3 (lettre-clé dédiée directe)
│
├─ Q2a. RACHIS : opéré ? déviation ?
│     ├─ Déviation du rachis ──► DRA
│     ├─ Opéré ───────────────► RAO
│     └─ Non opéré ───────────► RAM
│
├─ Q2b. MEMBRE (sup/inf) : opéré ? dans le référentiel pathologie ?
│     │   position2 : S=supérieur, I=inférieur
│     │   position3 : C=chirurgical, M=médical
│     │   préfixe   : R=référentiel, V=hors référentiel
│     ├─ Sup + chir + référentiel ──► RSC
│     ├─ Sup + méd  + référentiel ──► RSM
│     ├─ Sup + chir + hors réf.   ──► VSC
│     ├─ Sup + méd  + hors réf.   ──► VSM
│     ├─ Inf + chir + référentiel ──► RIC
│     ├─ Inf + méd  + référentiel ──► RIM
│     ├─ Inf + chir + hors réf.   ──► VIC
│     └─ Inf + méd  + hors réf.   ──► VIM
│
├─ Q3. SPÉCIALITÉS (lettre-clé directe)
│     ├─ Respiratoire / maxillo-facial / ORL ──► ARL
│     ├─ Neuromusculaire / rhumatismal inflam. ► NMI
│     ├─ Vasculaire ──────────────────────────► RAV
│     ├─ Amputation ──────────────────────────► AMP
│     ├─ Déambulation personne âgée ──────────► RPE
│     ├─ 2+ territoires ──────────────────────► TER
│     ├─ Abdo / périnéo-sphinctérien ─────────► RAB
│     ├─ Brûlures ────────────────────────────► RPB
│     └─ Soins palliatifs ────────────────────► PLL
│
├─ Q4. RÉFÉRENTIEL & SÉANCES
│     ├─ Pathologie dans le référentiel ?
│     │     └─ nombre de séances cadré (?) → si dépassement → DAP requise
│     └─ Hors référentiel → cadre séances (?) → DAP selon cas
│
└─ SORTIE :
      • Lettre-clé + coefficient (?)
      • Nb séances autorisé + DAP oui/non
      • JUSTIFICATION rédigée (zone + chir/méd + référentiel + lien ordonnance)  ← anti-indu
      • ALERTES : ordonnance incomplète ? cohérence soins↔prescription ?
```

## Points à trancher avec le kiné (P3)
1. Quand `R` (référentiel) vs `V` (hors réf.) — quelle est la liste exacte des pathologies du référentiel ?
2. Coefficients réels par lettre-clé (métropole/DROM).
3. Règles de cumul (2 séances/jour, suppléments, IFD/IK déplacements).
4. Cas limites : poly-pathologie → TER vs cotation principale ?
