const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, LevelFormat
} = require('C:/Users/test/AppData/Roaming/npm/node_modules/docx');
const fs = require('fs');

// ─── Palette ───────────────────────────────────────────────────────────────
const BLUE     = "1F3864";   // header fonce
const MIDBLUE  = "2E75B6";   // titres sections
const LBLUE    = "D6E4F0";   // bg header tableau
const LLBLUE   = "EBF3FB";   // bg lignes paires
const WHITE    = "FFFFFF";
const ACCENT   = "C00000";   // rouge pour mots cles
const GREY     = "595959";   // texte secondaire
const LGREY    = "F2F2F2";   // bg section gris clair

// ─── Helpers ───────────────────────────────────────────────────────────────
const border = (color = "CCCCCC", size = 4) => ({
  style: BorderStyle.SINGLE, size, color
});
const cellBorders = (c = "CCCCCC") => ({
  top: border(c), bottom: border(c), left: border(c), right: border(c)
});
const noBorder = () => ({
  top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
  left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE }
});

function h(text, level = 1) {
  const sizes = { 1: 28, 2: 24, 3: 22 };
  const colors = { 1: BLUE, 2: MIDBLUE, 3: MIDBLUE };
  return new Paragraph({
    spacing: { before: level === 1 ? 280 : 200, after: 120 },
    border: level === 1 ? { bottom: border(MIDBLUE, 8) } : {},
    children: [new TextRun({
      text, bold: true, color: colors[level],
      size: sizes[level], font: "Arial"
    })]
  });
}

function p(runs, { spacing = {}, indent = {} } = {}) {
  const children = typeof runs === 'string'
    ? [new TextRun({ text: runs, font: "Arial", size: 20, color: "000000" })]
    : runs;
  return new Paragraph({ children, spacing: { after: 80, ...spacing }, indent });
}

function bold(text, color = "000000", size = 20) {
  return new TextRun({ text, bold: true, font: "Arial", size, color });
}
function normal(text, color = "000000", size = 20) {
  return new TextRun({ text, font: "Arial", size, color });
}
function colored(text, color, bold_ = false, size = 20) {
  return new TextRun({ text, bold: bold_, color, font: "Arial", size });
}

function gap(before = 100, after = 100) {
  return new Paragraph({ spacing: { before, after }, children: [] });
}

function bullet(text, indent = 360) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { after: 60 },
    indent: { left: indent },
    children: typeof text === 'string'
      ? [normal(text)]
      : text
  });
}

function tableCell(children, { bg = WHITE, w = 4680, bold_ = false, vAlign = VerticalAlign.CENTER, colspan = 1 } = {}) {
  return new TableCell({
    borders: cellBorders("CCCCCC"),
    width: { size: w, type: WidthType.DXA },
    shading: { fill: bg, type: ShadingType.CLEAR },
    margins: { top: 100, bottom: 100, left: 160, right: 160 },
    verticalAlign: vAlign,
    columnSpan: colspan,
    children: Array.isArray(children) ? children : [
      new Paragraph({ children: [new TextRun({ text: children, font: "Arial", size: 20, bold: bold_, color: "000000" })] })
    ]
  });
}

function headerCell(text, w = 4680) {
  return tableCell(text, { bg: LBLUE, w, bold_: true });
}

function sectionBox(label, children) {
  // Boite coloriee pour les pitchs secteur
  return [
    new Paragraph({
      spacing: { before: 160, after: 60 },
      children: [new TextRun({ text: `  ${label}`, bold: true, font: "Arial", size: 20, color: WHITE })],
      shading: { fill: MIDBLUE, type: ShadingType.CLEAR },
    }),
    ...children,
  ];
}

// ─── TABLES ────────────────────────────────────────────────────────────────

function tableObjections() {
  const rows_data = [
    ["« C'est combien ? »",
     "« Ça dépend de ce qu'on automatise — c'est pour ça que je propose la démo d'abord. Pour vous donner une idée : entre 500 et 2 000 € pour un premier workflow livré. Si ça vous fait gagner 6h/semaine, c'est rentabilisé en 3 semaines. »"],
    ["« J'ai pas le temps »",
     "« C'est exactement pour ça que vous m'appelez. La démo dure 20 minutes, je viens avec tout préparé — vous n'avez rien à faire en amont. »"],
    ["« On a déjà des logiciels »",
     "« Je ne remplace rien — je connecte ce que vous avez déjà. Vous gardez vos outils, j'automatise les tâches manuelles entre eux. »"],
    ["« L'IA c'est pas fiable »",
     "« C'est pour ça que je commence toujours par un seul workflow, sur un vrai cas chez vous, avec validation humaine à chaque étape. Vous voyez le résultat avant de décider quoi que ce soit. »"],
    ["« On est trop petits »",
     "« Au contraire — c'est les petites structures qui gagnent le plus. Une personne qui récupère 5h/semaine, c'est 20h/mois — l'équivalent d'un mi-temps sur les tâches répétitives. »"],
    ["« Je vais en parler à mon associé »",
     "« Bien sûr. Je peux envoyer un résumé d'une page ce soir ? Et si vous êtes disponibles tous les deux, on peut faire la démo ensemble. »"],
  ];
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2800, 6560],
    rows: [
      new TableRow({
        tableHeader: true,
        children: [headerCell("OBJECTION", 2800), headerCell("RÉPONSE", 6560)]
      }),
      ...rows_data.map((row, i) => new TableRow({
        children: [
          tableCell(row[0], { bg: i % 2 === 0 ? LGREY : WHITE, w: 2800, bold_: true }),
          tableCell(row[1], { bg: i % 2 === 0 ? LGREY : WHITE, w: 6560 }),
        ]
      }))
    ]
  });
}

function tableDemo() {
  const rows_data = [
    ["0–3 min", "Recadrage", "« Dans votre semaine, quelle tâche vous prend le plus de temps et que vous faites le moins ? » → écouter, noter"],
    ["3–8 min", "Démo live", "Lancer le workflow sur leur cas concret. Montrer en temps réel : input → résultat automatisé"],
    ["8–12 min", "Chiffrage ROI", "« Ce que vous venez de voir prenait combien de temps manuellement ? » → calcul ROI ensemble à voix haute"],
    ["12–16 min", "Scope élargi", "Proposer 2–3 autres automatisations possibles → montrer l'iceberg"],
    ["16–19 min", "Offre pilote", "1 workflow, livré en 5 jours, prix fixe. Pas d'abonnement, pas de surprise"],
    ["19–20 min", "Next step", "« Si on démarre la semaine prochaine, vous avez le workflow en prod dans 5 jours. On fait comment ? »"],
  ];
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [1200, 1800, 6360],
    rows: [
      new TableRow({
        tableHeader: true,
        children: [headerCell("TEMPS", 1200), headerCell("PHASE", 1800), headerCell("ACTION", 6360)]
      }),
      ...rows_data.map((row, i) => new TableRow({
        children: [
          tableCell(row[0], { bg: LBLUE, w: 1200, bold_: true }),
          tableCell(row[1], { bg: i % 2 === 0 ? LGREY : WHITE, w: 1800, bold_: true }),
          tableCell(row[2], { bg: i % 2 === 0 ? LGREY : WHITE, w: 6360 }),
        ]
      }))
    ]
  });
}

function tableOneLiners() {
  const data = [
    ["Kiné / Ostéo",    "« Je fais tourner votre cabinet pendant que vous soignez vos patients. »"],
    ["Comptable",       "« Vos documents arrivent tout seuls dans le bon dossier — vous validez, vous ne saisissez plus. »"],
    ["Plombier",        "« Votre devis part en 3 minutes, la relance part toute seule — vous faites plus de chantiers avec la même équipe. »"],
    ["Agence immo",     "« Votre CRM se remplit tout seul après chaque visite — fini les fins de journée à rattraper l'admin. »"],
  ];
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [1800, 7560],
    rows: [
      new TableRow({
        tableHeader: true,
        children: [headerCell("SECTEUR", 1800), headerCell("ONE-LINER À AVOIR EN TÊTE", 7560)]
      }),
      ...data.map((row, i) => new TableRow({
        children: [
          tableCell(row[0], { bg: i % 2 === 0 ? LGREY : WHITE, w: 1800, bold_: true }),
          tableCell(row[1], { bg: i % 2 === 0 ? LGREY : WHITE, w: 7560 }),
        ]
      }))
    ]
  });
}

function tableQualif() {
  const data = [
    ["« Qu'est-ce qui vous a parlé dans mon message ? »",     "Identifier le pain prioritaire"],
    ["« C'est vous qui gérez ça au quotidien, ou vous avez une équipe ? »", "Qualifier le décideur + taille"],
    ["« Vous utilisez quoi actuellement pour [le problème évoqué] ? »",      "Identifier l'existant"],
  ];
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [5200, 4160],
    rows: [
      new TableRow({
        tableHeader: true,
        children: [headerCell("QUESTION", 5200), headerCell("OBJECTIF", 4160)]
      }),
      ...data.map((row, i) => new TableRow({
        children: [
          tableCell(`"${row[0]}"`, { bg: i % 2 === 0 ? LGREY : WHITE, w: 5200 }),
          tableCell(row[1], { bg: i % 2 === 0 ? LGREY : WHITE, w: 4160, bold_: true }),
        ]
      }))
    ]
  });
}

// ─── DOCUMENT ──────────────────────────────────────────────────────────────
const doc = new Document({
  numbering: {
    config: [{
      reference: "bullets",
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: "•",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 560, hanging: 280 } } }
      }]
    }]
  },
  styles: {
    default: {
      document: { run: { font: "Arial", size: 20 } }
    }
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },  // A4
        margin: { top: 1000, right: 1000, bottom: 1000, left: 1000 }
      }
    },
    headers: {
      default: new Header({
        children: [
          new Paragraph({
            spacing: { after: 0 },
            border: { bottom: border(MIDBLUE, 10) },
            children: [
              new TextRun({ text: "FICHE APPEL ENTRANT  ·  AI Installator", bold: true, color: WHITE, font: "Arial", size: 22 }),
              new TextRun({ text: "\tunexpectedvalu3@gmail.com  |  Claude-Sonnet pipeline", font: "Arial", size: 18, color: "AAAAAA" }),
            ],
            shading: { fill: BLUE, type: ShadingType.CLEAR },
            tabStops: [{ type: "right", position: 9026 }],
          })
        ]
      })
    },
    children: [

      // ── 1. OUVERTURE ──────────────────────────────────────────────────
      h("1.  OUVERTURE (15 sec)", 1),
      new Paragraph({
        spacing: { after: 80 },
        shading: { fill: LGREY, type: ShadingType.CLEAR },
        border: { left: { style: BorderStyle.SINGLE, size: 16, color: ACCENT } },
        indent: { left: 240, right: 240 },
        children: [
          bold("« AI Installator, Enzo à l'appareil — bonjour ! »", ACCENT),
          normal("  *(laisser parler)*"),
        ]
      }),
      new Paragraph({
        spacing: { after: 80 },
        shading: { fill: LGREY, type: ShadingType.CLEAR },
        border: { left: { style: BorderStyle.SINGLE, size: 16, color: ACCENT } },
        indent: { left: 240, right: 240 },
        children: [
          normal("« Parfait, oui c'est bien moi qui vous ai écrit. Vous avez deux minutes ? »"),
        ]
      }),
      gap(60, 60),
      p([bold("⚠  Règle d'or : ", ACCENT), normal("ne pas pitcher tout de suite. D'abord écouter pourquoi ils ont rappelé.")]),

      // ── 2. QUALIFICATION ──────────────────────────────────────────────
      h("2.  QUALIFICATION (2–3 questions max)", 1),
      tableQualif(),

      // ── 3. PITCH 2 MIN ────────────────────────────────────────────────
      h("3.  PITCH 2 MIN — par secteur", 1),

      ...sectionBox("KINÉ / OSTÉO", [
        new Paragraph({
          spacing: { after: 80 }, indent: { left: 160 },
          children: [normal("« La plupart des cabinets perdent entre 5 et 8h par semaine sur les rappels patients, la confirmation de RDV, les relances no-show. Ce que je fais, c'est automatiser tout ça — le cabinet reçoit moins d'appels inutiles, le praticien ne touche plus à rien. J'ai mis ça en place pour un ami kiné, il a récupéré une demi-journée par semaine dès le premier mois. Ce que je vous propose : une démo de 20 minutes sur votre propre agenda — vous voyez exactement ce que ça donne chez vous, gratuitement, sans engagement. »")]
        })
      ]),
      gap(60, 0),
      ...sectionBox("COMPTABLE", [
        new Paragraph({
          spacing: { after: 80 }, indent: { left: 160 },
          children: [normal("« Le goulot d'étranglement classique dans un cabinet comptable, c'est la saisie : factures PDF, relevés bancaires, documents clients qui arrivent dans tous les sens. Ce que je fais, c'est automatiser la capture, le tri et l'intégration dans votre outil existant — sans changer vos logiciels. J'ai aidé un ami comptable à économiser plusieurs heures par semaine sur la saisie seule. 20 minutes de démo sur vos vrais documents, et vous voyez si c'est applicable chez vous. »")]
        })
      ]),
      gap(60, 0),
      ...sectionBox("PLOMBIER / ARTISAN", [
        new Paragraph({
          spacing: { after: 80 }, indent: { left: 160 },
          children: [normal("« Le truc qui coûte le plus cher dans une entreprise artisanale, c'est le temps passé à faire des devis à la main, à relancer les clients qui ne signent pas, à gérer les plannings. Je peux automatiser la génération de devis et les relances — résultat : moins de temps admin, plus de chantiers. J'ai aidé un ami artisan à réduire son temps admin de plusieurs heures par semaine. Démo 20 min, gratuit, sur votre activité réelle. »")]
        })
      ]),
      gap(60, 0),
      ...sectionBox("AGENCE IMMO", [
        new Paragraph({
          spacing: { after: 80 }, indent: { left: 160 },
          children: [normal("« En agence, le reporting, les relances acquéreurs, les comptes-rendus de visite — ça prend un temps fou. J'automatise ces workflows : les données remontent toutes seules dans votre CRM, les relances partent au bon moment, les rapports se génèrent. 20 minutes de démo sur vos propres process — vous voyez ce qui est automatisable dès cette semaine. »")]
        })
      ]),

      // ── 4. CTA ────────────────────────────────────────────────────────
      h("4.  FERMETURE / CTA", 1),
      new Paragraph({
        spacing: { after: 80 },
        shading: { fill: LGREY, type: ShadingType.CLEAR },
        border: { left: { style: BorderStyle.SINGLE, size: 16, color: MIDBLUE } },
        indent: { left: 240, right: 240 },
        children: [normal("« Ce que je vous propose c'est simple : on se prend 20 minutes cette semaine, je prépare une démonstration sur votre activité — pas une présentation PowerPoint, un vrai test en live. Vous avez un créneau ")]
          .concat([bold("jeudi ou vendredi", MIDBLUE), normal(" ? »")])
      }),
      gap(80, 0),
      p([bold("Si hésitation : ", GREY), normal("« C'est gratuit, sans engagement. Si au bout de 20 minutes vous ne voyez pas de valeur, on se dit au revoir sans problème. »")]),

      // ── 5. OBJECTIONS ─────────────────────────────────────────────────
      h("5.  OBJECTIONS", 1),
      tableObjections(),

      // ── 6. DÉMO 20 MIN ────────────────────────────────────────────────
      h("6.  STRUCTURE DÉMO 20 MIN", 1),
      tableDemo(),

      // ── 7. ONE-LINERS ─────────────────────────────────────────────────
      h("7.  ONE-LINERS PAR SECTEUR", 1),
      tableOneLiners(),

      // ── NOTE BAS ──────────────────────────────────────────────────────
      gap(200, 0),
      new Paragraph({
        spacing: { after: 0 },
        border: { top: border(MIDBLUE, 6) },
        children: [
          colored("À préparer avant prod : ", ACCENT, true, 18),
          normal("une démo prête par secteur (kiné / comptable / plombier / immo). Quand un prospect appelle, RDV dans les 48h max.", GREY, 18),
        ]
      }),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("C:/Users/test/Documents/Claude/Projects/ai-installator/Fiche_Appel_AI_Installator.docx", buf);
  console.log("OK — Fiche_Appel_AI_Installator.docx créé");
}).catch(e => { console.error("ERREUR:", e.message); process.exit(1); });
