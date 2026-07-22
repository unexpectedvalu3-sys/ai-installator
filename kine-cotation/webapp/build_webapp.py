#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genere l'app web autonome KineCotation a partir de la base officielle.

Source unique : ../knowledge_base/ngap_kine.json -> injecte dans le template HTML.
Polices : assets/*.woff2 -> inlinees en base64 (fichier unique, zero requete reseau,
          coherent avec l'architecture local-first : rien ne sort du poste).
Sortie  : kinecotation.html (un seul fichier, a ouvrir dans un navigateur).

    python build_webapp.py

Design : concept « L'INSTRUMENT » — cf. 07_UI_DESIGN.md.
  La vitrine 10K vend (chaud, editorial, Fraunces, papier/encre/orange).
  Cet ecran instrumente (froid, dense, Plex Sans + Plex Mono, ardoise/petrole).
  On reprend la RIGUEUR du 10K (systeme de jetons, echelle d'espacement, motion
  disciplinee, contraste verifie) mais AUCUN de ses procedes de vitrine
  (preloader, curseur custom, scroll-scrub, CTA magnetiques) : cet outil est
  utilise vingt fois par jour entre deux patients, pas admire une fois.
"""

import base64
import json
from pathlib import Path

ICI = Path(__file__).resolve().parent
KB = json.loads((ICI.parent / "knowledge_base" / "ngap_kine.json").read_text(encoding="utf-8"))


def _font(nom: str) -> str:
    return base64.b64encode((ICI / "assets" / nom).read_bytes()).decode()


FONTS = f"""
@font-face{{font-family:'Plex';font-weight:400;font-style:normal;font-display:swap;
  src:url(data:font/woff2;base64,{_font('plex-sans-400.woff2')}) format('woff2')}}
@font-face{{font-family:'Plex';font-weight:600;font-style:normal;font-display:swap;
  src:url(data:font/woff2;base64,{_font('plex-sans-600.woff2')}) format('woff2')}}
@font-face{{font-family:'PlexMono';font-weight:500;font-style:normal;font-display:swap;
  src:url(data:font/woff2;base64,{_font('plex-mono-500.woff2')}) format('woff2')}}
"""

TEMPLATE = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>KinéCotation — cotation NGAP défendable</title>
<style>
__FONTS__

/* ============================================================
   JETONS — concept « L'instrument »
   Ecart delibere avec la vitrine 10K : elle est CHAUDE (papier creme
   #F5F1E9 / encre bleue #0C2438 / orange #F07E26, Fraunces editorial).
   Ici tout est FROID : ardoise, encre graphite-vert, accent petrole.
   Contrastes AA verifies au build (voir 07_UI_DESIGN.md).
   ============================================================ */
:root{
  /* surfaces — froides, la ou le 10K est creme */
  --paper:#F2F5F4; --paper-2:#E7ECEA; --card:#FBFCFC;
  /* encre — graphite a sous-ton vert (10K : bleu) */
  --ink:#0E1C19; --ink-2:#1C332E; --ink-soft:rgba(14,28,25,.60); --ink-faint:rgba(14,28,25,.42);
  --line:rgba(14,28,25,.13); --line-strong:rgba(14,28,25,.28);
  --on-ink:#EAF1EE; --on-ink-muted:rgba(234,241,238,.62); --on-ink-line:rgba(234,241,238,.16);
  /* accent petrole = interactif ET « defendable » (un seul accent, comme le 10K) */
  --accent:#0B6E5F; --accent-deep:#084F44; --accent-bright:#11A08A;
  --accent-wash:rgba(11,110,95,.08); --accent-line:rgba(11,110,95,.32);
  /* semantiques — distinctes de l'accent, jamais decoratives */
  --warn:#8A4B00; --warn-wash:#FCF3E6; --warn-line:rgba(138,75,0,.30);
  --danger:#96261B; --danger-wash:#FBEDEB; --danger-line:rgba(150,38,27,.30);
  /* echelle d'espacement (meme discipline que le 10K) */
  --sp-1:4px; --sp-2:8px; --sp-3:12px; --sp-4:16px; --sp-5:24px; --sp-6:32px; --sp-7:48px;
  /* motion — sobre : un outil, pas une vitrine */
  --dur-1:120ms; --dur-2:220ms; --ease:cubic-bezier(.22,.61,.21,1);
  --radius:10px;
  --sans:'Plex',-apple-system,Segoe UI,Roboto,sans-serif;
  --mono:'PlexMono',ui-monospace,SFMono-Regular,Consolas,monospace;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
  font-size:14px;line-height:1.5;-webkit-font-smoothing:antialiased}
/* les CHIFFRES sont des donnees : mono tabulaire, alignes, comparables d'un coup d'oeil */
.num,.ftab td.r,.tot span:last-child,.c{font-family:var(--mono);font-variant-numeric:tabular-nums}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:4px}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}

/* ---------- header ---------- */
header{background:var(--ink);color:var(--on-ink);padding:var(--sp-3) var(--sp-5);
  display:flex;align-items:center;gap:var(--sp-4);flex-wrap:wrap}
header h1{font-size:16px;margin:0;font-weight:600;letter-spacing:-.01em}
header .sub{color:var(--on-ink-muted);font-size:12.5px}
/* la version du bareme est une info de PREUVE, pas un detail : elle est dans le chrome */
.bareme{font-family:var(--mono);font-size:11px;color:var(--on-ink-muted);
  border:1px solid var(--on-ink-line);border-radius:999px;padding:3px 9px;white-space:nowrap}
nav{margin-left:auto;display:flex;gap:var(--sp-1);background:rgba(234,241,238,.07);
  padding:3px;border-radius:8px}
nav{flex:none}
nav button{background:transparent;color:var(--on-ink-muted);border:0;padding:7px 14px;
  border-radius:6px;cursor:pointer;font:inherit;font-size:13px;white-space:nowrap;
  transition:all var(--dur-1) var(--ease)}
nav button:hover{color:var(--on-ink)}
nav button.on{background:var(--on-ink);color:var(--ink);font-weight:600}
nav a#nav-out{color:var(--on-ink-muted);text-decoration:none;font-size:13px;padding:7px 14px;
  border-radius:6px;transition:color var(--dur-1) var(--ease)}
nav a#nav-out:hover{color:var(--on-ink)}
/* mobile : le header ne doit pas manger l'ecran. La baseline est du marketing,
   le barème est de la preuve -> on sacrifie la baseline, on garde le barème.
   En mode servi (http) un 3e item (Déconnexion) apparait dans le nav : titre +
   barème + 3 items ne tiennent pas sur 375px. On autorise donc le header à wrapper
   -> le nav (pastille compacte) passe sur sa propre ligne, aligné à droite, sans
   jamais élargir le document. Le barème reste lisible sur la 1re ligne. */
@media(max-width:640px){
  header{padding:var(--sp-3) var(--sp-4);gap:var(--sp-2);flex-wrap:wrap}
  header .sub{display:none}
  header h1{font-size:15px}
  .bareme{font-size:10px;padding:2px 7px;overflow:hidden;text-overflow:ellipsis}
  nav button{padding:6px 10px;font-size:12px}
}

/* ---------- layout ---------- */
main{max-width:1140px;margin:var(--sp-5) auto var(--sp-7);padding:0 var(--sp-4);
  display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:var(--sp-4);align-items:start}
@media(max-width:900px){main{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:var(--sp-5)}
.card h2{margin:0 0 var(--sp-4);font-size:11px;text-transform:uppercase;letter-spacing:.09em;
  color:var(--ink-faint);font-weight:600}
.sticky{position:sticky;top:var(--sp-4)}
@media(max-width:900px){.sticky{position:static}}

/* ---------- etapes ---------- */
.step{margin-bottom:var(--sp-4)}
/* date de seance : en tete, compacte — elle pilote le bareme mais ne doit pas
   voler la vedette au parcours de cotation */
.dateline{display:flex;align-items:center;gap:var(--sp-3);padding-bottom:var(--sp-4);
  border-bottom:1px solid var(--line)}
.dateline label{margin:0;font-weight:600;color:var(--ink);white-space:nowrap}
.dateline input{width:auto;font-family:var(--mono);font-size:13px}
.lbl{display:flex;align-items:center;gap:var(--sp-2);font-size:13px;font-weight:600;margin-bottom:var(--sp-2)}
.idx{font-family:var(--mono);font-size:10px;color:var(--accent);border:1px solid var(--accent-line);
  border-radius:4px;padding:1px 5px;font-weight:500}
label{display:block;font-size:12.5px;color:var(--ink-soft);margin:var(--sp-3) 0 var(--sp-1)}
input,select{width:100%;padding:9px 11px;border:1px solid var(--line-strong);border-radius:7px;
  font:inherit;font-size:13.5px;background:var(--card);color:var(--ink);
  transition:border-color var(--dur-1) var(--ease),box-shadow var(--dur-1) var(--ease)}
input:hover,select:hover{border-color:var(--ink-faint)}
input:focus,select:focus{outline:0;border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-wash)}
.row{display:flex;gap:var(--sp-3)}.row>*{flex:1;min-width:0}
.chk{display:flex;align-items:center;gap:var(--sp-2);margin-top:var(--sp-3)}
.chk input{width:auto;accent-color:var(--accent)}
.chk label{margin:0}

/* segmente : un choix binaire = UN clic, pas trois (select -> ouvrir -> choisir) */
.seg{display:flex;gap:var(--sp-1);background:var(--paper-2);padding:3px;border-radius:8px}
.seg button{flex:1;background:transparent;border:0;padding:8px 10px;border-radius:6px;cursor:pointer;
  font:inherit;font-size:13px;color:var(--ink-soft);transition:all var(--dur-1) var(--ease)}
.seg button:hover{color:var(--ink)}
.seg button.on{background:var(--card);color:var(--accent-deep);font-weight:600;
  box-shadow:0 1px 2px rgba(14,28,25,.10)}

/* ---------- liste d'actes ---------- */
.actes{display:flex;flex-direction:column;gap:var(--sp-1);max-height:280px;overflow:auto;
  margin-top:var(--sp-2);padding-right:2px}
.acte{display:flex;justify-content:space-between;align-items:baseline;gap:var(--sp-3);
  border:1px solid var(--line);border-left:2px solid transparent;border-radius:7px;
  padding:9px 11px;cursor:pointer;font-size:13px;background:var(--card);text-align:left;
  transition:border-color var(--dur-1) var(--ease),background var(--dur-1) var(--ease)}
.acte:hover{border-color:var(--accent-line);border-left-color:var(--accent);background:var(--accent-wash)}
.acte .c{font-weight:500;color:var(--accent-deep);white-space:nowrap}
.acte .lib{color:var(--ink-soft)}
.acte .t{white-space:nowrap;font-family:var(--mono);font-variant-numeric:tabular-nums;color:var(--ink)}

/* ---------- feuille ---------- */
#feuille{background:var(--card);border-radius:var(--radius)}
.fh{display:flex;justify-content:space-between;gap:var(--sp-4);
  border-bottom:2px solid var(--ink);padding-bottom:var(--sp-3);margin-bottom:var(--sp-3)}
.fh .n{font-weight:600;font-size:15px}
.ftab{width:100%;border-collapse:collapse;font-size:13px}
.ftab th{text-align:left;padding:6px 4px;font-size:10px;text-transform:uppercase;
  letter-spacing:.07em;color:var(--ink-faint);border-bottom:1px solid var(--line-strong)}
.ftab td{text-align:left;padding:9px 4px;border-bottom:1px solid var(--line);vertical-align:top}
.ftab td.r{text-align:right;white-space:nowrap}
.ftab tbody tr{animation:in var(--dur-2) var(--ease)}
@keyframes in{from{opacity:0;transform:translateY(-3px)}to{opacity:1;transform:none}}
.tot{display:flex;justify-content:space-between;align-items:baseline;font-weight:600;
  font-size:17px;margin-top:var(--sp-3);padding-top:var(--sp-3);border-top:2px solid var(--ink)}
.x{color:var(--ink-faint);cursor:pointer;padding:0 4px;transition:color var(--dur-1) var(--ease)}
.x:hover{color:var(--danger)}

/* n° de seance ET nb prescrites : ils PILOTENT l'alerte DAP -> promus, editables.
   'Prescrites' = saisissable a la main quand l'OCR echoue ou en flux manuel. */
.seance{display:inline-flex;align-items:center;gap:6px 8px;flex-wrap:wrap;margin-top:6px;
  padding:4px 8px;background:var(--paper-2);border:1px solid var(--line);border-radius:6px}
.seance span{font-size:11px;color:var(--ink-soft)}
.seance input{width:56px;padding:3px 6px;font-family:var(--mono);font-size:12.5px;text-align:center}

/* ---------- alertes ---------- */
.alert{border-radius:7px;padding:10px 12px;font-size:12.5px;margin-top:var(--sp-2);
  border:1px solid;border-left-width:3px}
.alert.danger{background:var(--danger-wash);color:var(--danger);border-color:var(--danger-line)}
.alert.warn{background:var(--warn-wash);color:var(--warn);border-color:var(--warn-line)}
.alert.info{background:var(--accent-wash);color:var(--accent-deep);border-color:var(--accent-line)}
.alert b{font-weight:600}

/* ---------- divers ---------- */
button.act{background:var(--accent);color:#fff;border:0;padding:10px 16px;border-radius:7px;
  cursor:pointer;font:inherit;font-size:13.5px;font-weight:600;
  transition:background var(--dur-1) var(--ease),transform var(--dur-1) var(--ease)}
button.act:hover{background:var(--accent-deep)}
button.act:active{transform:translateY(1px)}
button.ghost{background:var(--paper-2);color:var(--ink)}
button.ghost:hover{background:var(--line);color:var(--ink)}
.pill{display:inline-block;background:var(--accent-wash);color:var(--accent-deep);
  border-radius:999px;padding:3px 10px;font-size:11.5px;font-weight:600}
.muted{color:var(--ink-soft);font-size:12px}
.empty{text-align:center;padding:var(--sp-6) var(--sp-4);color:var(--ink-faint);font-size:13px}
.empty .big{font-family:var(--mono);font-size:22px;color:var(--line-strong);display:block;margin-bottom:var(--sp-2)}
.justif{font-size:11.5px;color:var(--ink-soft);margin-top:var(--sp-4);
  border:1px dashed var(--line-strong);border-radius:7px;padding:var(--sp-3);background:var(--paper)}
.justif b{color:var(--ink)}
.justif .src{font-family:var(--mono);font-size:10.5px;color:var(--ink-faint);
  margin-top:var(--sp-2);padding-top:var(--sp-2);border-top:1px solid var(--line)}
hr.sep{border:0;border-top:1px solid var(--line);margin:var(--sp-4) 0}
.hidden{display:none}
.file{border:1px dashed var(--line-strong);border-radius:7px;padding:var(--sp-3);background:var(--paper)}
.file input{border:0;background:transparent;padding:0;font-size:12.5px}

/* ---------- caviardage de l'ordonnance (etape 00) ----------
   L'image d'ordonnance est une donnee de SANTE. Le geste de masquage se fait
   ICI, en local, sur un canvas : seule la version aux pixels noircis quittera le
   poste (cf. caviarderEtAnalyser). Le geste = glisser (souris OU doigt), comme
   un outil de capture d'ecran — universel, rien a apprendre. */
/* fond carte (le plus clair) pour que la microcopie mutee passe AA ; l'affordance
   « zone d'action » est portee par la bordure accent gauche, pas par une teinte de
   fond qui abaisserait le contraste du texte. */
.cav{margin-top:var(--sp-3);border:1px solid var(--accent-line);border-left:3px solid var(--accent);
  background:var(--card);border-radius:8px;padding:var(--sp-3)}
.cav .hint{font-size:12.5px;color:var(--ink-2);margin-bottom:var(--sp-2)}
.cav .hint b{color:var(--ink)}
.cavwrap{position:relative;border:1px solid var(--line-strong);border-radius:6px;overflow:hidden;
  background:var(--paper-2);line-height:0}
/* touch-action:none -> le glissement dessine, il ne fait pas defiler la page (mobile). */
#ordoCanvas{display:block;max-width:100%;height:auto;cursor:crosshair;touch-action:none}
.cavbar{display:flex;align-items:center;gap:var(--sp-2);flex-wrap:wrap;margin-top:var(--sp-2)}
.cavbar .grow{flex:1}
.act.mini{padding:6px 10px;font-size:12px}
.cavcount{font-family:var(--mono);font-variant-numeric:tabular-nums}
.cavnote{font-size:11px;color:var(--ink-soft);margin-top:var(--sp-2)}
button.act:disabled{background:var(--line-strong);color:var(--on-ink-muted);cursor:not-allowed}
button.act:disabled:hover{background:var(--line-strong)}
/* overlay « Détection du bloc patient… » : l'app masque toute seule, le kiné
   valide d'un regard. Pendant l'OCR local (1-3 s) l'aperçu est voilé + spinner. */
.cavov{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:var(--sp-2);
  background:rgba(14,28,25,.58);color:var(--on-ink);font-size:12.5px;text-align:center;
  padding:var(--sp-3);line-height:1.35}
.cavov .sp{width:15px;height:15px;border:2px solid var(--on-ink-line);border-top-color:var(--on-ink);
  border-radius:50%;animation:cavspin .8s linear infinite;flex:none}
@keyframes cavspin{to{transform:rotate(360deg)}}

/* ---------- champ patient (en-tete de la feuille, STRICTEMENT local) ----------
   La valeur ne quitte jamais le poste : ni reseau, ni localStorage (une feuille =
   un patient). Cf. setPatient / reset. */
.patientbox{display:flex;align-items:center;gap:var(--sp-2);flex-wrap:wrap;
  padding-bottom:var(--sp-3);margin-bottom:var(--sp-3);border-bottom:1px solid var(--line)}
.patientbox label{margin:0;font-weight:600;color:var(--ink);white-space:nowrap;font-size:13px}
.patientbox input{flex:1;min-width:140px;width:auto;font-size:13.5px}
.patientbox .local{font-size:11px;color:var(--ink-soft);white-space:nowrap}

/* ---------- impression : la feuille seule ---------- */
@media print{
  header,nav,#tab-cotation .builder,.noprint{display:none!important}
  body{background:#fff;font-size:11pt}
  main{display:block;max-width:none;margin:0;padding:0}
  .card{border:0;padding:0}
  .justif{background:#fff}
  .sticky{position:static}
}
</style>
</head>
<body>
<header>
  <h1>KinéCotation</h1>
  <span class="sub">cote au juste tarif, avec la preuve derrière</span>
  <span class="bareme" id="bareme"></span>
  <nav>
    <button id="nav-cot" class="on" onclick="show('cotation')">Cotation</button>
    <button id="nav-prof" onclick="show('profil')">Mon profil</button>
    <a id="nav-out" href="/logout" style="display:none">Déconnexion</a>
  </nav>
</header>

<main id="tab-profil" class="hidden">
  <div class="card">
    <h2>Profil praticien</h2>
    <p class="muted">Saisi une fois. Apparaît en en-tête de chaque feuille. <b>Stocké localement sur ce poste</b> — rien n'est envoyé.</p>
    <label>Nom et prénom</label><input id="p_nom" placeholder="Claire DUBOIS">
    <label>Qualité</label><input id="p_qual" value="Masseur-Kinésithérapeute D.E.">
    <div class="row"><div><label>N° RPPS</label><input id="p_rpps" placeholder="10101010101"></div>
      <div><label>N° de facturation (AM)</label><input id="p_amf" placeholder="691234567"></div></div>
    <label>Adresse du cabinet</label><input id="p_adr" placeholder="12 rue des Lilas">
    <div class="row"><div><label>Code postal / Ville</label><input id="p_cpv" placeholder="69003 LYON"></div>
      <div><label>Téléphone</label><input id="p_tel" placeholder="04 78 00 00 00"></div></div>
    <label>Email</label><input id="p_mail" placeholder="cabinet@exemple.fr">
    <label>Conventionnement / secteur</label><input id="p_conv" placeholder="Conventionné secteur 1">
    <div class="chk"><input type="checkbox" id="p_drom"><label>Exercice en DROM-COM (lettre-clé 2,43 € au lieu de 2,21 €)</label></div>
    <p style="margin-top:var(--sp-5)"><button class="act" onclick="saveProfil()">Enregistrer</button>
      <span id="psaved" class="pill" style="display:none">✓ enregistré</span></p>
    <hr class="sep">
    <!-- Métrique de confiance du caviardage auto (compteurs seuls, AUCUNE donnée de
         santé). Sert à décider un jour du tout-automatique : tant que le taux
         d'acceptation sans retouche n'est pas très haut, on garde la validation. -->
    <p class="muted" id="cavStats" style="font-size:11.5px;margin:0"></p>
  </div>
  <div class="card">
    <h2>Aperçu en-tête</h2>
    <div id="profilApercu"></div>
  </div>
</main>

<main id="tab-cotation">
  <div class="card builder">
    <h2>Construire la cotation</h2>

    <!-- La date de la SEANCE pilote le bareme (pas la date du jour) : une seance du
         31/08 facturee le 05/09 se cote au bareme du 31/08. Elle est donc en tete. -->
    <div class="step dateline">
      <label for="w_date">Date de la séance</label>
      <input id="w_date" type="date" onchange="setDateSeance(this.value)">
    </div>

    <div class="step">
      <div class="lbl"><span class="idx">00</span> Ordonnance (optionnel)</div>
      <!-- Images seules : le caviardage se fait sur canvas, qui ne rend pas les PDF
           sans lib. PDF selectionne -> message propre (voir onOrdoFile). -->
      <div class="file"><input id="ordoFile" type="file" accept="image/png,image/jpeg,image/webp" onchange="onOrdoFile(this)"></div>
      <div id="ocrPanel"></div>
    </div>

    <hr class="sep">

    <div class="step">
      <div class="lbl"><span class="idx">01</span> Région / type d'affection</div>
      <select id="w_region" onchange="onRegion()"></select>
    </div>

    <div id="w_chir_wrap" class="step hidden">
      <div class="lbl"><span class="idx">02</span> Acte post-chirurgical ?</div>
      <input type="hidden" id="w_chir" value="">
      <div class="seg" data-for="w_chir">
        <button type="button" data-v="oui">Opéré</button>
        <button type="button" data-v="non">Non opéré</button>
      </div>
    </div>

    <div id="w_ref_wrap" class="step hidden">
      <div class="lbl"><span class="idx">03</span> Pathologie au référentiel HAS ?</div>
      <input type="hidden" id="w_ref" value="">
      <div class="seg" data-for="w_ref">
        <button type="button" data-v="oui">Au référentiel</button>
        <button type="button" data-v="non">Hors référentiel</button>
      </div>
    </div>

    <div class="step">
      <div class="lbl"><span class="idx">04</span> Acte réalisé</div>
      <div id="criteres"></div>
      <div id="w_actes" class="actes"></div>
    </div>

    <hr class="sep">
    <div class="row noprint">
      <button class="act ghost" onclick="openPicker('bilan')">+ Bilan (BDK)</button>
      <button class="act ghost" onclick="openPicker('supp')">+ Supplément</button>
    </div>
    <div id="picker"></div>
    <div class="chk"><input type="checkbox" id="w_dom" onchange="onDom()"><label>Séance à domicile (déplacement)</label></div>
    <div id="w_dom_wrap" class="hidden row" style="margin-top:var(--sp-2)">
      <div><label>Distance facturable (km)</label><input id="w_km" type="number" min="0" value="0" oninput="render()"></div>
      <div><label>Terrain</label><select id="w_terrain" onchange="render()"><option value="plaine">Plaine</option><option value="montagne">Montagne</option><option value="pied_ski">À pied / ski</option></select></div>
    </div>
  </div>

  <div class="card sticky">
    <h2 class="noprint">Feuille de soins</h2>
    <!-- Patient : saisi LOCALEMENT. Champ statique (jamais reconstruit par render())
         pour ne pas perdre le focus a chaque frappe. La valeur alimente l'en-tete
         imprime (« Patient : X », rendu dans .fh) et la justification. Elle ne part
         a AUCUN endpoint et n'est PAS persistee (une feuille = un patient). -->
    <div class="patientbox noprint">
      <label for="f_patient">Patient</label>
      <input id="f_patient" placeholder="Nom et prénom du patient" oninput="setPatient(this.value)"
        autocomplete="off">
      <span class="local">saisi localement, jamais transmis</span>
    </div>
    <div id="feuille"></div>
    <p class="noprint" style="margin-top:var(--sp-4);display:flex;gap:var(--sp-2);flex-wrap:wrap">
      <button class="act" onclick="window.print()">Imprimer / PDF</button>
      <!-- Copier pour VEGA : la double saisie est le frein n°1 (cf. 13_INTEGRATION_VEGA
           voie C/D). Pas d'API VEGA -> presse-papiers optimise pour la re-saisie. Le
           texte NE contient JAMAIS le nom du patient (un presse-papiers peut fuiter). -->
      <button class="act ghost" id="btnVega" onclick="copierVega(this)"
        title="Copie un bloc texte compact de la cotation, prêt à recopier dans VEGA (sans le nom du patient)">Copier la cotation</button>
      <button class="act ghost" onclick="reset()">Vider</button>
    </p>
  </div>
</main>

<script>
const KB = __CATALOGUE_JSON__;
const REGIONS = [
 ['rachis','Rachis (lombalgie, cervicalgie, dorsal…)'],
 ['membre_sup','Membre supérieur (épaule, coude, poignet, main)'],
 ['membre_inf','Membre inférieur (hanche, genou, cheville, pied)'],
 ['multi_territoires','Plusieurs membres / territoires'],
 ['neuro_musculaire','Neurologique / musculaire'],
 ['rhumato_inflammatoire','Rhumatisme inflammatoire'],
 ['respiratoire','Respiratoire'],
 ['maxillo_orl','Maxillo-faciale / ORL'],
 ['vasculaire','Vasculaire / lymphœdème'],
 ['abdo_perineo','Abdominale / périnéale'],
 ['geriatrie','Déambulation sujet âgé'],
 ['amputation','Amputation'],
 ['brulures','Brûlures'],
 ['palliatif','Soins palliatifs'],
];
let profil = JSON.parse(localStorage.getItem('kine_profil')||'{}');
let panier = [];      // {code,coef,tarif,libelle,article,referentiel,chirurgie,seance,region}
// Identite du patient — CHOIX DE CONFORMITE, ne pas « ameliorer » en l'envoyant au
// serveur : elle vit uniquement ici, en memoire, jamais transmise ni persistee.
let patient = '';
const esc = s => String(s==null?'':s).replace(/[&<>"]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

// ---- helpers cotation (miroir du moteur Python) ----
const lettre = ()=> profil.drom ? KB._meta.valeur_lettre_cle_eur.drom : KB._meta.valeur_lettre_cle_eur.metropole;
const tarif = c => Math.round(c*lettre()*100)/100;
const eur = n => n.toFixed(2).replace('.',',')+' €';

// ---- cotations datees (miroir de cotation_engine.acte_a_la_date) ----
// La NGAP bouge par PALIERS (01/01/2026, 28/05/2026, 01/09/2026). La date qui fait
// foi est celle DE LA SEANCE, jamais « aujourd'hui » : une seance du 31/08 facturee
// le 05/09 se cote au bareme du 31/08 — et la justification doit attester CE bareme.
const isoAujourdhui = ()=>{const d=new Date(); return new Date(d.getTime()-d.getTimezoneOffset()*60000).toISOString().slice(0,10);};
let dateSeance = isoAujourdhui();

function acteALaDate(a, d){
  let r={coefficient:a.coefficient, tarif_metropole:a.tarif_metropole, palier:null, conditionnel:false, condition:null};
  (a._paliers||[]).slice().sort((x,y)=>x.a_partir_du<y.a_partir_du?-1:1)
    .forEach(p=>{ if(d>=p.a_partir_du) r={coefficient:p.coefficient, tarif_metropole:p.tarif_metropole,
      palier:p.a_partir_du, conditionnel:!!p.conditionnel, condition:p.condition||null}; });
  return r;
}
const frDate = d => d.split('-').reverse().join('/');
// La base n'a PAS d'historique avant applicable_depuis : coter avant, ce serait
// produire un bareme faux QUE LA JUSTIFICATION ATTESTERAIT. On refuse.
const dateHorsPerimetre = d => !!(KB._meta.applicable_depuis && d < KB._meta.applicable_depuis);
const actesRegion = r => KB.actes.filter(a=>a.region===r);
const trouverRef = a => KB.referentiels.find(r=>a.libelle.toLowerCase().includes(r.match_libelle));
// ATTENTION — deux quantites DIFFERENTES, a ne jamais confondre :
//   seance     = a quelle seance on en est aujourd'hui (saisi par le kine)
//   prescrites = combien le medecin en a prescrit (lu sur l'ordonnance par l'OCR)
// Les confondre faisait crier « DAP REQUISE — Or seance n°30 » des la 1re seance
// d'une ordonnance de 30 seances (bug corrige le 2026-07-17). Une fausse alerte
// dans la fonction de securite = le kine n'y croit plus, et l'anti-indu meurt.
function alerteDap(ref,seance,prescrites){
  const seuil=ref.dap_des_seance;
  let b=`Référentiel HAS : ${ref.situation} → ${ref.seances_avant_dap?('1 à '+ref.seances_avant_dap):'0'} séance(s), DAP dès la ${seuil}ᵉ.`;
  if(ref.note) b+=` (${ref.note})`;
  if(seance!=null && seance>=seuil) return {lvl:'danger',msg:'<b>⚠ DAP REQUISE</b> — '+b+` Or séance n°${seance}.`};
  if(seance!=null && seance===seuil-1) return {lvl:'warn',msg:'<b>Avant-dernière séance sans DAP</b> — anticiper. '+b};
  // Anticipation : ce que l'OCR permet vraiment. L'ordonnance depasse le seuil ->
  // le kine SAIT des la 1re seance qu'une DAP tombera. Ce n'est pas une alerte, c'est
  // un plan de charge.
  if(seance==null && prescrites!=null && prescrites>=seuil)
    return {lvl:'warn',msg:`<b>DAP à prévoir</b> — l'ordonnance prescrit <span class="num">${prescrites}</span> séances `
      +`et la DAP tombe dès la <span class="num">${seuil}ᵉ</span>. Anticipe le bilan. `+b};
  return {lvl:'info',msg:b};
}
function ligneDeplacement(km,terrain){
  const d=KB.deplacements, art=panier[0]?panier[0].article:'';
  const ifs = d.articles_IFS.includes(String(art));
  const base = ifs ? d.IFS_eur : d.IFD_eur;
  const bareme = profil.drom ? d.IK_drom : d.IK_metropole;
  const ik = Math.round((km*(bareme[terrain]||0))*100)/100;
  const lib = (ifs?'Indemnité forfaitaire de déplacement spécifique':'Indemnité forfaitaire de déplacement')
            + (km?` + IK ${km} km ${terrain} (${eur(ik)})`:'');
  return {code:ifs?'IFS':'IFD',coef:'—',tarif:Math.round((base+ik)*100)/100,libelle:lib,article:'—',referentiel:false,chirurgie:false};
}

// ---- navigation ----
function show(t){
  document.getElementById('tab-cotation').classList.toggle('hidden',t!=='cotation');
  document.getElementById('tab-profil').classList.toggle('hidden',t!=='profil');
  document.getElementById('nav-cot').classList.toggle('on',t==='cotation');
  document.getElementById('nav-prof').classList.toggle('on',t==='profil');
  if(t==='profil'){ loadProfilForm(); renderCavStats(); }
}
// Métrique de confiance du caviardage auto — lue depuis localStorage (compteurs
// seuls). Affichée discrètement dans le profil : « N/M acceptés sans retouche ».
function renderCavStats(){
  const el=document.getElementById('cavStats'); if(!el) return;
  let s={}; try{ s=JSON.parse(localStorage.getItem('kine_cav_stats')||'{}'); }catch(e){}
  const p=s.proposes||0, a=s.acceptes_sans_retouche||0;
  el.innerHTML = p
    ? ('Caviardage auto : <b>'+a+' / '+p+'</b> acceptés sans retouche.')
    : 'Caviardage auto : aucune proposition mesurée pour l\'instant.';
}
function bumpCavStats(accepteSansRetouche){
  let s={}; try{ s=JSON.parse(localStorage.getItem('kine_cav_stats')||'{}'); }catch(e){}
  s.proposes=(s.proposes||0)+1;
  if(accepteSansRetouche) s.acceptes_sans_retouche=(s.acceptes_sans_retouche||0)+1;
  try{ localStorage.setItem('kine_cav_stats',JSON.stringify(s)); }catch(e){}
}

// ---- profil ----
const PF=['nom','qual','rpps','amf','adr','cpv','tel','mail','conv'];
function loadProfilForm(){PF.forEach(k=>{const e=document.getElementById('p_'+k); if(e&&profil[k]!=null)e.value=profil[k];});
  document.getElementById('p_drom').checked=!!profil.drom; renderProfilApercu();}
function saveProfil(){PF.forEach(k=>profil[k]=document.getElementById('p_'+k).value.trim());
  profil.drom=document.getElementById('p_drom').checked;
  localStorage.setItem('kine_profil',JSON.stringify(profil));
  const s=document.getElementById('psaved');s.style.display='inline-block';setTimeout(()=>s.style.display='none',1500);
  renderProfilApercu(); render();}
function enteteHTML(){
  if(!profil.nom) return '<div class="muted">Renseigne ton profil (onglet « Mon profil ») pour personnaliser l\'en-tête.</div>';
  return `<div class="n">${profil.nom||''}</div><div class="muted">${profil.qual||''}</div>
    <div class="muted">${profil.adr||''} ${profil.cpv?('— '+profil.cpv):''}</div>
    <div class="muted">${profil.tel||''} ${profil.mail?(' · '+profil.mail):''}</div>
    <div class="muted">${profil.rpps?('RPPS '+profil.rpps):''} ${profil.amf?(' · N° fact. '+profil.amf):''}</div>
    <div class="muted">${profil.conv||''}${profil.drom?' · DROM-COM':''}</div>`;
}
function renderProfilApercu(){document.getElementById('profilApercu').innerHTML=enteteHTML();}

// ---- wizard ----
function fillRegions(){const s=document.getElementById('w_region');
  s.innerHTML='<option value="">— choisir —</option>'+REGIONS.map(r=>`<option value="${r[0]}">${r[1]}</option>`).join('');}
function onRegion(){
  const r=document.getElementById('w_region').value, actes=actesRegion(r);
  const mixChir=actes.some(a=>a.chirurgie)&&actes.some(a=>!a.chirurgie);
  const mixRef=actes.some(a=>a.referentiel)&&actes.some(a=>!a.referentiel);
  document.getElementById('w_chir_wrap').classList.toggle('hidden',!mixChir);
  document.getElementById('w_ref_wrap').classList.toggle('hidden',!mixRef);
  document.getElementById('w_chir').value='';document.getElementById('w_ref').value='';
  renderActes();
}
// reflete la valeur des inputs caches sur les boutons segmentes
function syncSeg(){
  document.querySelectorAll('.seg').forEach(seg=>{
    const v=(document.getElementById(seg.dataset.for)||{}).value||'';
    seg.querySelectorAll('button').forEach(b=>b.classList.toggle('on',b.dataset.v===v));
  });
}
function renderActes(){
  syncSeg();
  const r=document.getElementById('w_region').value;
  const box=document.getElementById('w_actes');
  if(!r){box.innerHTML='<div class="empty"><span class="big">01</span>Choisis une région pour voir les actes.</div>';return;}
  let actes=actesRegion(r);
  const c=document.getElementById('w_chir').value, rf=document.getElementById('w_ref').value;
  if(!document.getElementById('w_chir_wrap').classList.contains('hidden')&&c) actes=actes.filter(a=>a.chirurgie===(c==='oui'));
  if(!document.getElementById('w_ref_wrap').classList.contains('hidden')&&rf) actes=actes.filter(a=>a.referentiel===(rf==='oui'));
  box.innerHTML = actes.map(a=>{
    const i=KB.actes.indexOf(a), v=acteALaDate(a,dateSeance);
    return `<button type="button" class="acte" onclick="addActe(${i})">
      <span><b class="c">${a.code} ${v.coefficient}</b> <span class="lib">${a.libelle}</span></span>
      <span class="t">${eur(tarif(v.coefficient))}</span></button>`;
  }).join('') || '<div class="empty">Aucun acte avec ces critères — ajuste ci-dessus.</div>';
  // Rappels : criteres manquants, + paliers a venir SUR CETTE REGION uniquement
  // (annoncer les 5 NMI a un kine du rachis, c'est du bruit).
  let av = [];
  actes.forEach(a=>(a._paliers||[]).forEach(p=>{ if(p.a_partir_du>dateSeance)
    av.push(`<b>${a.code} ${a.coefficient} → ${p.coefficient}</b> au ${frDate(p.a_partir_du)} (${a.libelle})`); }));
  const rappels = controleCriteres().map(m=>`<div class="alert info">${m}</div>`);
  if(av.length) rappels.push(`<div class="alert info noprint"><b>Barème à venir</b> — ${av.length} acte(s) `
    +`de cette région changent bientôt :<br>${av.join('<br>')}. Les séances d'ici là gardent le barème actuel.</div>`);
  document.getElementById('criteres').innerHTML = rappels.join('');
}
function addActe(i){
  const a=KB.actes[i], v=acteALaDate(a,dateSeance);
  // `src` = index dans KB.actes -> permet de RECOTER la ligne si la date change
  panier.push({src:i,code:a.code,coef:v.coefficient,tarif:tarif(v.coefficient),palier:v.palier,
    conditionnel:v.conditionnel,condition:v.condition,
    libelle:a.libelle,article:a.article,referentiel:a.referentiel,chirurgie:a.chirurgie,seance:null,region:a.region});
  render();
}

// Recote tout le panier au bareme de la date courante. Sans ca, une ligne ajoutee
// avant de corriger la date resterait figee au mauvais bareme — et la justification
// l'attesterait.
function recoter(){
  panier.forEach(l=>{
    if(l.src==null) return;                       // bilans/supplements : pas de paliers
    const v=acteALaDate(KB.actes[l.src], dateSeance);
    l.coef=v.coefficient; l.tarif=tarif(v.coefficient); l.palier=v.palier;
    l.conditionnel=v.conditionnel; l.condition=v.condition;
  });
}

function setDateSeance(v){
  dateSeance = v || isoAujourdhui();
  // Le champ est resynchronise systematiquement : un appel non issu du champ
  // (reset, pre-remplissage OCR, futur code) laisserait sinon la date affichee en
  // desaccord avec le bareme applique -> une preuve qui atteste autre chose que ce
  // qu'elle affiche. C'est exactement l'incoherence silencieuse a proscrire ici.
  const c=document.getElementById('w_date');
  if(c && c.value!==dateSeance) c.value=dateSeance;
  recoter(); renderActes(); render();
}
function setSeance(idx,val){
  const n=String(val).trim();
  panier[idx].seance = /^\d+$/.test(n) ? parseInt(n) : null;
  render();
}
// Nb de seances PRESCRITES, editable a la main : si l'OCR echoue (ou en flux 100%
// manuel), c'est le seul moyen de renseigner ce champ -> et c'est lui qui declenche
// l'alerte anticipee « DAP a prevoir des la Xe seance » (cf. alerteDap). Vide = null.
function setPrescrites(idx,val){
  const n=String(val).trim();
  panier[idx].prescrites = /^\d+$/.test(n) ? parseInt(n) : null;
  render();
}
function openPicker(kind){
  const list = kind==='bilan'?KB.bilans:KB.supplements;
  const titre = kind==='bilan'?'Type de bilan (BDK)':'Supplément';
  let h='<div style="border:1px solid var(--accent-line);background:var(--accent-wash);border-radius:8px;padding:10px;margin-top:var(--sp-2)"><b style="font-size:12.5px">'+titre+'</b><div class="actes">';
  list.forEach((x,i)=>{ h+='<button type="button" class="acte" onclick="pickItem(\''+kind+'\','+i+')"><span><b class="c">'+x.code+' '+x.coefficient+'</b> <span class="lib">'+x.libelle+'</span></span><span class="t">'+eur(tarif(x.coefficient))+'</span></button>'; });
  h+='</div><div class="muted" style="margin-top:6px;cursor:pointer" onclick="closePicker()">✕ fermer</div></div>';
  document.getElementById('picker').innerHTML=h;
}
function closePicker(){document.getElementById('picker').innerHTML='';}
function pickItem(kind,i){
  const x=(kind==='bilan'?KB.bilans:KB.supplements)[i];
  panier.push({src:null,code:x.code,coef:x.coefficient,tarif:tarif(x.coefficient),palier:null,libelle:x.libelle,article:'—',referentiel:false,chirurgie:false,seance:null,region:null});
  closePicker(); render();
}
function onDom(){document.getElementById('w_dom_wrap').classList.toggle('hidden',!document.getElementById('w_dom').checked);render();}
function removeLigne(i){panier.splice(i,1);render();}
// Patient : local uniquement. On re-rend la feuille pour propager le nom vers
// l'en-tete imprime et la justification. La valeur ne part nulle part.
function setPatient(v){ patient = v; render(); }
function reset(){panier=[];document.getElementById('w_dom').checked=false;document.getElementById('w_dom_wrap').classList.add('hidden');
  patient='';const pf=document.getElementById('f_patient');if(pf)pf.value='';   // une feuille = un patient
  closePicker();render();}

// ANTI-SOUS-COTATION — ce que l'outil peut faire, et ce qu'il ne DOIT pas faire.
//
// Tentative abandonnee (2026-07-17) : suggerer « l'acte le mieux cote de la region ».
// Deux echecs mesures sur l'app reelle :
//   1. Bruit — dans une region les coefficients sont quasi identiques (tout membre_inf
//      tient entre 8,00 et 8,12 = 9 centimes). L'alerte se declenchait a chaque
//      cotation pour un gain derisoire et DESENSIBILISAIT a l'alerte DAP, qui est la
//      vraie securite. Une alerte qui crie tout le temps ne protege plus de rien.
//   2. DANGER — les regions regroupent des actes cliniquement heterogenes. Sur une
//      atteinte radiculaire (NMI 8.5) le controle proposait TER 16 « +16,57 € »
//      (paralysie cerebrale de l'enfant). Aucun rapport clinique. C'est exactement le
//      comportement qui PROVOQUE un indu, dans un produit dont la promesse est la
//      defendabilite.
//
// Conclusion : l'outil ne peut PAS detecter une sous-cotation — il ignore ce qui a
// ete cliniquement fait. Le chiffre de sous-cotation se mesure avec le kine
// (ordonnances reelles : ce qu'il a facture vs ce que le moteur defend), pas ici.
//
// Ce qui est sur ET utile : verifier que les CRITERES qui changent la cotation sont
// renseignes. Un critere non repondu = liste non filtree = risque de prendre le
// mauvais acte. C'est la, en amont, que se joue la sous-cotation.
function controleCriteres(){
  const out=[];
  const r=document.getElementById('w_region').value; if(!r) return out;
  const paires=[['w_chir_wrap','w_chir','post-chirurgical (opéré / non opéré)'],
                ['w_ref_wrap','w_ref','référentiel HAS (au / hors référentiel)']];
  paires.forEach(([wrap,inp,nom])=>{
    if(document.getElementById(wrap).classList.contains('hidden')) return;
    if(document.getElementById(inp).value) return;
    out.push(`Critère non renseigné : <b>${nom}</b>. Il change la cotation — précise-le pour ne voir que les actes qui te concernent.`);
  });
  return out;
}

// ---- rendu feuille ----
function render(){
  let dep=null;
  if(document.getElementById('w_dom') && document.getElementById('w_dom').checked){
    const km=parseInt(document.getElementById('w_km').value||'0'), t=document.getElementById('w_terrain').value;
    dep=ligneDeplacement(km,t);
  }
  const allLignes = dep?panier.concat([dep]):panier;
  const total=Math.round(allLignes.reduce((s,l)=>s+l.tarif,0)*100)/100;
  const today=frDate(dateSeance);
  const alertes=[];
  panier.forEach(l=>{const ref=trouverRef(l); if(ref) alertes.push(alerteDap(ref,(l.seance==null)?null:l.seance,l.prescrites));});

  // Hors perimetre : on refuse de coter plutot que de produire une preuve fausse.
  if(dateHorsPerimetre(dateSeance)){
    document.getElementById('feuille').innerHTML=
      `<div class="alert danger"><b>Séance du ${frDate(dateSeance)} — cotation impossible</b><br>`
      +`La base ne couvre les tarifs qu'à partir du <span class="num">${frDate(KB._meta.applicable_depuis)}</span> `
      +`(${KB._meta.source}). Coter cette séance donnerait un barème faux, et la justification l'attesterait. `
      +`Se référer au tableau SNMKR en vigueur à cette date.</div>`;
    return;
  }
  if(!panier.length && !dep){
    document.getElementById('feuille').innerHTML=
      // pas de « à gauche » : en mobile l'assistant est au-dessus (une colonne)
      '<div class="empty"><span class="big">€</span>Aucun acte.<br>Choisis une région, puis l\'acte réalisé.</div>';
    return;
  }

  const patientLigne = patient.trim() ? `<div class="muted" style="margin-top:4px">Patient : <b>${esc(patient.trim())}</b></div>` : '';
  let h=`<div class="fh"><div>${enteteHTML()}</div>
    <div style="text-align:right"><div class="n">FEUILLE DE SOINS</div><div class="muted">Récapitulatif de cotation</div>
    <div class="muted num">séance du ${today}</div>${patientLigne}</div></div>`;
  // Palier CONDITIONNEL : jamais en silence. Risque asymetrique — si le palier
  // n'entre pas en vigueur et qu'on l'a applique, le kine SURCOTE (indu) ; s'il
  // entre en vigueur et qu'on l'ignore, il sous-cote (perte, sans risque legal).
  // La faute qu'on ne doit pas causer est la premiere.
  const cond = panier.filter(l=>l.conditionnel);
  if(cond.length){
    h+=`<div class="alert warn"><b>⚠ Cotation sous réserve</b> — `
      +cond.map(l=>`<span class="num">${l.code} ${l.coef}</span> applique le palier du `
        +`<span class="num">${frDate(l.palier)}</span>`).join(', ')
      +`, dont l'entrée en vigueur est <b>conditionnelle</b> (avenant 7 §C : « sous réserve d'une `
      +`modification préalable de la liste des actes », et exposée au comité d'alerte ONDAM — `
      +`précédent du gel de juillet 2025). <b>Vérifie le tableau SNMKR en vigueur avant de facturer.</b></div>`;
  }
  // CUMUL — regle NGAP officielle : « une seule cotation par seance, correspondant au
  // traitement de la pathologie ou du territoire anatomique en cause » (cf.
  // 16_REGLES_CUMUL_NGAP.md, source ameli). L'app additionnait sans avertir -> total
  // potentiellement illegal = l'indu qu'on promet d'eviter. On ALERTE (ne bloque pas,
  // ne recalcule pas : l'application de l'exception art. 11B a 50% reste a cadrer).
  // On ne compte QUE les actes de reeducation (region != null) ; bilans/supplements
  // (region == null) et deplacement se cumulent -> exclus. Garde-fou sur le CERTAIN.
  const reeduc = panier.filter(l=>l.region);
  if(reeduc.length>=2){
    h+=`<div class="alert warn"><b>⚠ Cumul à vérifier</b> — tu as <span class="num">${reeduc.length}</span> actes de `
      +`rééducation (${reeduc.map(l=>l.code+' '+l.coef).join(', ')}). En principe, <b>une seule rééducation se cote `
      +`par séance</b> (NGAP : une seule cotation par séance). Pour plusieurs zones, un acte « plusieurs territoires » `
      +`(art. 1D) existe. Sinon c'est une exception (art. 11B, 2ᵉ acte à 50 %) — le total ci-dessous les additionne `
      +`à 100 %, <b>à corriger si le cumul n'est pas permis</b>.</div>`;
  }
  // les alertes DAP sont le coeur anti-indu : en HAUT, pas en pied de page
  alertes.filter(a=>a.lvl!=='info').forEach(a=>h+=`<div class="alert ${a.lvl}">${a.msg}</div>`);
  h+=`<table class="ftab"><thead><tr><th>Code</th><th>Coef</th><th>Acte</th><th class="r">Tarif</th><th class="noprint"></th></tr></thead><tbody>`;
  panier.forEach((l,idx)=>{
    const ref=trouverRef(l);
    const inp = ref?`<div class="seance noprint">`
      +`<span>Prescrites</span><input type="number" min="1" inputmode="numeric" data-fk="presc-${idx}" value="${l.prescrites!=null?l.prescrites:''}" oninput="setPrescrites(${idx},this.value)" placeholder="—" title="Nombre de séances prescrites sur l'ordonnance — à saisir si l'OCR ne l'a pas lu ; déclenche l'alerte « DAP à prévoir »">`
      +`<span>Séance n°</span><input type="number" min="1" inputmode="numeric" data-fk="seance-${idx}" value="${l.seance!=null?l.seance:''}" oninput="setSeance(${idx},this.value)" placeholder="—" title="Numéro de la séance en cours">`
      +`</div>`:'';
    h+=`<tr><td><b class="c">${l.code}</b></td><td class="num">${l.coef}</td><td>${l.libelle}${inp}</td><td class="r">${eur(l.tarif)}</td>
      <td class="noprint"><span class="x" onclick="removeLigne(${idx})">✕</span></td></tr>`;
  });
  if(dep) h+=`<tr><td><b class="c">${dep.code}</b></td><td class="num">${dep.coef}</td><td>${dep.libelle}</td><td class="r">${eur(dep.tarif)}</td><td class="noprint"></td></tr>`;
  h+=`</tbody></table><div class="tot"><span>TOTAL</span><span>${eur(total)}</span></div>`;
  alertes.filter(a=>a.lvl==='info').forEach(a=>h+=`<div class="alert info">${a.msg}</div>`);

  // JUSTIFICATION = le produit. Elle epingle la VERSION DU BAREME : sans ca, une preuve
  // ne vaut rien (le bareme a change 3 fois en 8 mois). Cf. 05_REPOSITIONNEMENT_PREUVE.md.
  h+=`<div class="justif"><b>Justification (à conserver — anti-indu) :</b><br>`+
     (patient.trim()?`Feuille établie le ${today} pour le patient <b>${esc(patient.trim())}</b>.<br>`:'')+
     panier.map(l=>`• ${l.code} ${l.coef} (art. ${l.article})${l.palier?(' [palier du '+frDate(l.palier)+']'):''} : `
       +`${l.libelle}${l.seance!=null?(' — séance n°'+l.seance):''}.`).join('<br>')+
     `<br>Pièces : ordonnance + BDK. Vérifier la cohérence soins ↔ prescription.
      <div class="src">Barème appliqué : ${KB._meta.source} · base v${KB._meta.version}
      · lettre-clé ${eur(lettre())} · <b>barème en vigueur à la date de la séance (${today})</b></div>
      <i>Aide à la décision — proposition de cotation non télétransmise. Le praticien valide et reste responsable.</i></div>`;
  // Les inputs Prescrites/Séance sont DANS le tableau reconstruit a chaque frappe
  // (oninput -> render). Sans ca, le focus saute apres chaque chiffre -> impossible
  // de taper « 30 ». On memorise l'input actif (data-fk) et on le restaure.
  const feuille=document.getElementById('feuille');
  const ae=document.activeElement;
  const fk=(ae&&ae.dataset&&ae.dataset.fk&&feuille.contains(ae))?ae.dataset.fk:null;
  feuille.innerHTML=h;
  if(fk){
    const el=feuille.querySelector('[data-fk="'+fk+'"]');
    if(el){ el.focus(); try{ el.setSelectionRange(el.value.length,el.value.length); }catch(e){} }
  }
}

// ========================================================================
//  COPIER POUR VEGA — presse-papiers optimise pour la re-saisie manuelle.
//
//  Il n'existe PAS d'API pour ecrire une cotation dans VEGA (cf. 13_INTEGRATION_
//  VEGA §1 : aucune API publique). Le frein d'adoption n°1 = la double saisie. On
//  reduit donc la friction (voie C/D) : un bloc texte compact, une ligne par acte,
//  DAP si applicable, total. Regle de confidentialite : le nom du patient N'Y EST
//  JAMAIS — un presse-papiers peut fuiter (autre appli, historique). L'identite
//  reste locale (cf. 07_UI_DESIGN §3.9), seule la cotation part au presse-papiers.
function texteVega(){
  // Meme calcul que render() : deplacement inclus, meme total.
  let dep=null;
  if(document.getElementById('w_dom') && document.getElementById('w_dom').checked){
    const km=parseInt(document.getElementById('w_km').value||'0'), t=document.getElementById('w_terrain').value;
    dep=ligneDeplacement(km,t);
  }
  const allLignes = dep?panier.concat([dep]):panier;
  if(!allLignes.length) return '';
  if(dateHorsPerimetre(dateSeance)) return '';   // pas de cotation hors perimetre
  const total=Math.round(allLignes.reduce((s,l)=>s+l.tarif,0)*100)/100;
  const lignes=[];
  lignes.push('Cotation séance du '+frDate(dateSeance));
  panier.forEach(l=>{
    lignes.push(l.code+' '+l.coef+' — '+l.libelle+' — '+eur(l.tarif)
      +(l.conditionnel?' (sous réserve — palier conditionnel, vérifier SNMKR)':''));
    // Sous-ligne DAP / prescription (« e » plein, pas d'exposant : champ VEGA = texte brut)
    const ref=trouverRef(l);
    if(ref){
      const parts=[];
      if(l.prescrites!=null) parts.push('Séances prescrites : '+l.prescrites);
      if(l.seance!=null)     parts.push('séance n°'+l.seance);
      if(l.seance!=null && l.seance>=ref.dap_des_seance) parts.push('⚠ DAP REQUISE');
      parts.push('DAP dès la '+ref.dap_des_seance+'e séance');
      lignes.push('  '+parts.join(' · '));
    }
  });
  if(dep) lignes.push(dep.code+' — '+dep.libelle+' — '+eur(dep.tarif));
  lignes.push('Total séance : '+eur(total));
  lignes.push('Barème : '+KB._meta.source+' · base v'+KB._meta.version+' · lettre-clé '+eur(lettre()));
  return lignes.join('\n');
}
// Retour visuel « Copié ✓ » 1,5 s. clipboard.writeText marche en contexte securise
// (https + localhost) ; fallback textarea/execCommand pour file:// ou http non securise.
function copierVega(btn){
  const t=texteVega();
  const flash=(txt)=>{ const old=btn.dataset.label||btn.textContent; btn.dataset.label=old;
    btn.textContent=txt; btn.disabled=true;
    setTimeout(()=>{ btn.textContent=old; btn.disabled=false; },1500); };
  if(!t){ flash('Rien à copier'); return; }
  const ok=()=>flash('Copié ✓');
  const fallback=()=>{ try{
      const ta=document.createElement('textarea'); ta.value=t;
      ta.style.position='fixed'; ta.style.opacity='0'; document.body.appendChild(ta);
      ta.focus(); ta.select(); document.execCommand('copy'); document.body.removeChild(ta); ok();
    }catch(e){ flash('Copie impossible'); } };
  if(navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(t).then(ok).catch(fallback);
  } else fallback();
}

// ========================================================================
//  CAVIARDAGE DE L'ORDONNANCE — donnee de sante, masquee AVANT tout envoi.
//
//  Principe non negociable : l'image ORIGINALE non masquee ne quitte JAMAIS le
//  poste. Elle ne vit que dans `ordoImg` (en memoire) et dans les pixels du
//  canvas. Seul `caviarderEtAnalyser()` produit un blob, et ce blob est celui du
//  canvas APRES gravure des rectangles noirs -> la seule version qui part au
//  cloud est la version masquee. Aucun blob de l'original n'est jamais cree.
//
//  Le kine masque nom / prenom / date de naissance / NIR du patient (le
//  prescripteur peut rester). Geste universel : glisser (souris OU doigt), comme
//  un outil de capture. Les rectangles sont GRAVES dans les pixels (fillRect),
//  pas un overlay CSS qu'un envoi contournerait.
//
//  ITERATION 2 — l'app masque toute seule, le kine valide d'un regard.
//  Quand l'app est SERVIE (http) : a la selection d'une image, on lance une
//  detection OCR 100 % LOCALE (tesseract.js + pack FR, charges paresseusement
//  depuis /static/tesseract/). On repere les LIBELLES imprimes (« Patient »,
//  « Nom », « Ne(e) le », « NIR », « N° SS »…) et on pre-pose un masque sur la
//  VALEUR a droite du libelle ; on masque aussi tout motif type NIR (13-15
//  chiffres). L'apercu apparait DEJA masque -> le kine verifie et clique.
//  L'image NON masquee ne sort jamais du poste (meme pas vers notre backend) :
//  la detection lit le canvas en memoire, rien n'est televerse pour ca.
//  Le dessin manuel reste le filet : ajouter un masque manque, annuler, effacer.
//  En file:// (hors-ligne) ou si les assets ne chargent pas -> flux manuel de la
//  brique 1, inchange, sans erreur console.
// ========================================================================
const CAV_MAXDIM = 2000;   // borne la resolution envoyee (memoire + poids du blob)
let ordoImg=null, ordoCanvas=null, ordoCtx=null;
let masques=[];            // {x,y,w,h} en pixels-canvas
let curMask=null, cavDrawing=false;

// ---- detection auto (local) ----
// URL ABSOLUE obligatoire : tesseract.js cree son worker depuis un blob: (origine
// opaque) qui appelle importScripts() ; un chemin racine « /static/… » y est
// invalide (pas d'origine pour le resoudre). location.origin corrige ca, et reste
// bon en prod HTTPS.
const TESS_BASE=location.origin+'/static/tesseract';
// La detection a besoin du backend pour servir les assets -> seulement en http.
// En file:// on degrade proprement vers le flux manuel.
const AUTO_OK = location.protocol.indexOf('http')===0;
let tessLoading=null;      // promesse singleton de creation du worker
let autoCount=0;           // nb de masques auto-proposes pour l'image courante
let cavRetouche=false;     // le kine a-t-il modifie les masques apres l'auto ?

function onOrdoFile(input){
  const f=input.files[0]; if(!f) return;
  const panel=document.getElementById('ocrPanel');
  // PDF (ou tout non-image) : le canvas ne rend pas un PDF sans lib -> on refuse
  // proprement plutot que d'envoyer un fichier non caviarde.
  const estImage = /^image\/(png|jpe?g|webp)$/i.test(f.type) || /\.(png|jpe?g|webp)$/i.test(f.name);
  if(!estImage){
    panel.innerHTML='<div class="alert warn">Pour le caviardage, prends l\'ordonnance en photo '
      +'(PNG / JPG / WebP). Le PDF n\'est pas supporté ici.</div>';
    input.value=''; return;
  }
  const url=URL.createObjectURL(f);
  const img=new Image();
  img.onload=()=>{ URL.revokeObjectURL(url); ordoImg=img; masques=[]; curMask=null;
    autoCount=0; cavRetouche=false; buildCaviardage(); };
  img.onerror=()=>{ URL.revokeObjectURL(url);
    panel.innerHTML='<div class="alert warn">Image illisible — réessaie avec une photo nette.</div>'; };
  img.src=url;
}

// Microcopie du bloc (id=cavHint), selon l'etat :
const HINT_MANUEL='Masque le <b>nom</b>, le <b>prénom</b> et la <b>date de naissance</b> du patient — '
  +'glisse le doigt (ou la souris) dessus. Le prescripteur peut rester.';
const HINT_AUTO_OK='Aperçu <b>déjà masqué</b> aux zones patient détectées. Vérifie d\'un regard — '
  +'ajoute un masque manquant en glissant, ou « Annuler le dernier ». Le prescripteur peut rester.';
const HINT_AUTO_VIDE='<b>Aucun bloc patient détecté</b> — masque le <b>nom</b>, le <b>prénom</b> et la '
  +'<b>date de naissance</b> toi-même en glissant dessus. Le prescripteur peut rester.';

function buildCaviardage(){
  const scale=Math.min(1, CAV_MAXDIM/Math.max(ordoImg.naturalWidth, ordoImg.naturalHeight));
  const w=Math.max(1,Math.round(ordoImg.naturalWidth*scale)), hh=Math.max(1,Math.round(ordoImg.naturalHeight*scale));
  // Hint initial : en mode auto on annonce la detection ; en manuel, la consigne d'origine.
  const hint0 = AUTO_OK ? 'Détection du bloc patient…' : HINT_MANUEL;
  const overlay = AUTO_OK
    ? '<div class="cavov" id="cavOverlay"><span class="sp"></span><span>Détection du bloc patient…</span></div>'
    : '';
  document.getElementById('ocrPanel').innerHTML=
    '<div class="cav">'
    +'<div class="hint" id="cavHint">'+hint0+'</div>'
    +'<div class="cavwrap"><canvas id="ordoCanvas" width="'+w+'" height="'+hh+'"></canvas>'+overlay+'</div>'
    +'<div class="cavbar">'
    +'<span class="pill cavcount" id="cavCount">0 masque</span>'
    +'<span class="grow"></span>'
    +'<button type="button" class="act ghost mini" onclick="undoMask()">Annuler le dernier masque</button>'
    +'<button type="button" class="act ghost mini" onclick="clearMasks()">Tout effacer</button>'
    +'</div>'
    +'<div class="chk"><input type="checkbox" id="cavNone" onchange="updateCavBtn()">'
    +'<label for="cavNone">Aucune info patient visible sur cette photo</label></div>'
    +'<button type="button" id="cavGo" class="act" disabled onclick="caviarderEtAnalyser()" style="margin-top:var(--sp-2)">Analyser</button>'
    +'<div class="cavnote">La version originale non masquée reste en mémoire sur ce poste — '
    +'elle n\'est envoyée nulle part. Seule l\'image masquée part à l\'analyse.</div>'
    +'</div>';
  ordoCanvas=document.getElementById('ordoCanvas');
  ordoCtx=ordoCanvas.getContext('2d');
  redrawOrdo();
  attachCavEvents();
  updateCavBtn();
  // Auto-proposition : masquer tout seul, sans bloquer le geste manuel (le kine
  // peut deja dessiner pendant que l'OCR tourne). Tout echec -> flux manuel.
  if(AUTO_OK) lancerDetection();
}

// Charge tesseract.js + coeur WASM + pack FR PARESSEUSEMENT (uniquement ici, a la
// 1re image), une seule fois, puis reutilise le worker. Aucun logger -> console
// silencieuse. Rejet propre si un asset manque -> l'appelant degrade en manuel.
function ensureTess(){
  if(tessLoading) return tessLoading;
  tessLoading=(async()=>{
    if(typeof Tesseract==='undefined'){
      await new Promise((res,rej)=>{
        const s=document.createElement('script');
        s.src=TESS_BASE+'/tesseract.min.js'; s.onload=res;
        s.onerror=()=>rej(new Error('tesseract indisponible'));
        document.head.appendChild(s);
      });
    }
    // OEM 1 = LSTM (coherent avec tessdata_fast). gzip:false : le pack FR est
    // servi non compresse (fra.traineddata). Chemins 100 % locaux.
    // corePath pointe le coeur EMBARQUE (.wasm.js, wasm inline) : evite un 2e fetch
    // du .wasm que le worker (origine blob: opaque) ne saurait pas resoudre -> sinon
    // gel a « initializing ». Self-hosted robuste.
    return await Tesseract.createWorker('fra', 1, {
      workerPath: TESS_BASE+'/worker.min.js',
      corePath: TESS_BASE+'/tesseract-core-simd-lstm.wasm.js',
      langPath: TESS_BASE, gzip: false,
    });
  })().catch(err=>{ tessLoading=null; throw err; });   // permet un retry a la prochaine image
  return tessLoading;
}

async function lancerDetection(){
  const canvasAuMoment=ordoCanvas;   // garde-fou : si l'image change entre-temps, on jette
  try{
    const worker=await ensureTess();
    if(ordoCanvas!==canvasAuMoment) return;              // une autre image a ete chargee
    // Reconnait le canvas courant (fond image, aucun masque grave a cet instant).
    const {data}=await worker.recognize(ordoCanvas,{},{blocks:true});
    if(ordoCanvas!==canvasAuMoment) return;
    const zones=zonesPatient(data, ordoCanvas.width, ordoCanvas.height);
    zones.forEach(z=>masques.push(z));
    autoCount=zones.length;
    const hint=document.getElementById('cavHint');
    if(hint) hint.innerHTML = zones.length ? HINT_AUTO_OK : HINT_AUTO_VIDE;
  }catch(e){
    // Degradation propre : assets absents / OCR en echec -> flux manuel, zero erreur.
    const hint=document.getElementById('cavHint'); if(hint) hint.innerHTML=HINT_MANUEL;
  }finally{
    const ov=document.getElementById('cavOverlay'); if(ov) ov.remove();
    redrawOrdo(); updateCavBtn();
  }
}

// Analyse la sortie OCR et rend des rectangles {x,y,w,h} (coords canvas) a masquer.
// Deux regles : (1) libelle imprime reconnu -> masquer la VALEUR a sa droite,
// jusqu'au bord (large a dessein : l'OCR photo est approximatif, mieux vaut trop
// que trop peu) ; (2) motif type NIR (13-15 chiffres) ou qu'il soit.
function zonesPatient(data, W, H){
  const norm=s=>String(s||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]/g,'');
  // Libelles patient. Volontairement PAS « rpps »/« am »/« docteur » (prescripteur).
  const ANCRES=['patient','patiente','nom','prenom','ne','nee','naissance','nir',
                'ss','secu','securite','sociale','assure','assuree','beneficiaire','matricule','insee'];
  const lignes=[];
  (data.blocks||[]).forEach(b=>(b.paragraphs||[]).forEach(p=>(p.lines||[]).forEach(l=>lignes.push(l))));
  const zones=[];
  lignes.forEach(l=>{
    const mots=l.words||[];
    // Un libelle est une ancre situee dans la moitie GAUCHE (position d'etiquette).
    // Evite de masquer un « ne »/« nom » qui trainerait dans le corps de texte.
    let droiteAncre=null;
    mots.forEach(wd=>{
      const b=wd.bbox||{}; if(b.x0==null) return;
      if(b.x0 > W*0.55) return;
      if(ANCRES.indexOf(norm(wd.text))>=0)
        droiteAncre = droiteAncre==null ? b.x1 : Math.max(droiteAncre,b.x1);
    });
    if(droiteAncre!=null){
      const y0=l.bbox.y0, y1=l.bbox.y1, pad=Math.max(4,(y1-y0)*0.4);
      const x=Math.max(0, droiteAncre+2);
      zones.push({x:x, y:Math.max(0,y0-pad), w:Math.max(0,W-x), h:(y1-y0)+2*pad});
    }
    // Motif NIR : 13 chiffres (ou 15 avec la cle). RPPS = 11 chiffres -> ignore.
    mots.forEach(wd=>{
      const b=wd.bbox||{}; if(b.x0==null) return;
      const chiffres=String(wd.text||'').replace(/\D/g,'');
      if(chiffres.length>=13 && chiffres.length<=15){
        const pad=Math.max(4,(b.y1-b.y0)*0.35);
        zones.push({x:Math.max(0,b.x0-pad), y:Math.max(0,b.y0-pad),
          w:(b.x1-b.x0)+2*pad, h:(b.y1-b.y0)+2*pad});
      }
    });
  });
  return zones;
}

// Redessine : image de fond + tous les masques graves (noir opaque) + le masque
// en cours de trace. Appele a chaque mouvement -> trace « en direct ».
function redrawOrdo(){
  if(!ordoCtx) return;
  ordoCtx.drawImage(ordoImg,0,0,ordoCanvas.width,ordoCanvas.height);
  ordoCtx.fillStyle='#000';
  masques.forEach(m=>ordoCtx.fillRect(m.x,m.y,m.w,m.h));
  if(curMask) ordoCtx.fillRect(curMask.x,curMask.y,curMask.w,curMask.h);
}

// Convertit un evenement (souris ou tactile) en coordonnees-canvas.
function cavPos(ev){
  const rect=ordoCanvas.getBoundingClientRect();
  const src=(ev.touches&&ev.touches[0])||(ev.changedTouches&&ev.changedTouches[0])||ev;
  const sx=ordoCanvas.width/rect.width, sy=ordoCanvas.height/rect.height;
  return {x:(src.clientX-rect.left)*sx, y:(src.clientY-rect.top)*sy};
}
function cavStart(ev){ ev.preventDefault(); cavDrawing=true; const p=cavPos(ev); curMask={x0:p.x,y0:p.y,x:p.x,y:p.y,w:0,h:0}; }
function cavMove(ev){
  if(!cavDrawing||!curMask) return; ev.preventDefault();
  const p=cavPos(ev);
  curMask.x=Math.min(curMask.x0,p.x); curMask.y=Math.min(curMask.y0,p.y);
  curMask.w=Math.abs(p.x-curMask.x0); curMask.h=Math.abs(p.y-curMask.y0);
  redrawOrdo();
}
function cavEnd(ev){
  if(!cavDrawing) return; cavDrawing=false;
  if(curMask && curMask.w>4 && curMask.h>4){ masques.push({x:curMask.x,y:curMask.y,w:curMask.w,h:curMask.h}); cavRetouche=true; }
  curMask=null; redrawOrdo(); updateCavBtn();
}
// Souris ET tactile explicitement cables (le brief exige les deux gestes).
function attachCavEvents(){
  ordoCanvas.addEventListener('mousedown',cavStart);
  window.addEventListener('mousemove',cavMove);
  window.addEventListener('mouseup',cavEnd);
  ordoCanvas.addEventListener('touchstart',cavStart,{passive:false});
  ordoCanvas.addEventListener('touchmove',cavMove,{passive:false});
  ordoCanvas.addEventListener('touchend',cavEnd);
  ordoCanvas.addEventListener('touchcancel',cavEnd);
}
function undoMask(){ masques.pop(); cavRetouche=true; redrawOrdo(); updateCavBtn(); }
function clearMasks(){ masques=[]; cavRetouche=true; redrawOrdo(); updateCavBtn(); }
// GARDE-FOU : envoi impossible tant qu'aucun masque n'est pose, SAUF si le kine
// atteste explicitement (case a cocher) qu'aucune info patient n'est visible.
// Jamais d'envoi silencieux non caviarde.
function updateCavBtn(){
  const cnt=document.getElementById('cavCount'); if(cnt) cnt.textContent=masques.length+' masque'+(masques.length>1?'s':'');
  const none=document.getElementById('cavNone'); const go=document.getElementById('cavGo');
  if(go) go.disabled = !(masques.length>0 || (none&&none.checked));
}

function caviarderEtAnalyser(){
  if(!ordoCanvas) return;
  // Metrique de confiance : ne compte que les envois OU l'auto a propose >=1 masque.
  // « accepte sans retouche » = le kine n'a ni ajoute, ni annule, ni tout efface.
  if(autoCount>0) bumpCavStats(!cavRetouche);
  redrawOrdo();   // s'assure que le canvas porte bien tous les masques graves
  // toBlob lit le canvas MASQUE -> le blob ne contient que la version noircie.
  // A aucun moment on ne cree ni n'envoie un blob de l'image originale.
  ordoCanvas.toBlob(blob=>{
    const panel=document.getElementById('ocrPanel');
    panel.innerHTML='<div class="muted" style="margin-top:8px">Lecture de l\'ordonnance…</div>';
    const fd=new FormData(); fd.append('ordonnance', blob, 'ordonnance.png');   // meme endpoint, rien a changer cote serveur
    sendOcr(fd, panel);
  }, 'image/png');
}

// ---- OCR (necessite le backend server.py) ----
async function sendOcr(fd, panel){
  try{
    const r=await fetch('/api/ocr',{method:'POST',body:fd});
    const data=await r.json().catch(()=>({}));
    if(!r.ok){ panel.innerHTML='<div class="alert warn">OCR indisponible : '+(data.error||r.status)+'</div>'; return; }
    renderOcr(data);
  }catch(err){
    panel.innerHTML='<div class="alert warn">OCR nécessite le serveur (lancer server.py, pas ouvrir le fichier directement).</div>';
  }
}
function renderOcr(data){
  const e=data.extraction||{}, c=data.candidats||[];
  // NB : on ignore volontairement tout `e.patient_nom` renvoye par l'OCR (vide dans
  // le flux caviarde de toute facon) — l'identite patient est saisie localement et
  // ne doit jamais etre ecrasee par une lecture cloud.
  let h='<div style="border:1px solid var(--accent-line);background:var(--accent-wash);border-radius:8px;padding:12px;margin-top:10px">';
  h+='<b style="font-size:12.5px">Ordonnance lue</b> <span class="pill">confiance '+(e.confiance||'?')+'</span>';
  h+='<div style="margin:6px 0;font-size:13px">'+(e.pathologie_texte||'')+'</div>';
  h+='<div class="muted">Zone : '+(e.zone||'?')+' · Chirurgie : '+(e.chirurgie||'?')
     +' · Séances : '+(e.nb_seances_prescrites||'—')+' · Domicile : '+(e.domicile?'oui':'non')
     +' · Bilan : '+(e.mention_bilan?'oui':'non')+'</div>';
  (e.alertes||[]).forEach(a=>h+='<div class="alert warn">'+a+'</div>');
  h+='<div class="muted" style="margin-top:8px">Actes proposés — clique le bon :</div><div class="actes">';
  const se = e.nb_seances_prescrites ? e.nb_seances_prescrites : 'null';
  c.forEach(a=>{ h+='<button type="button" class="acte" onclick="addActeFromOcr('+a.index+','+se+')">'
     +'<span><b class="c">'+a.code+' '+a.coefficient+'</b> <span class="lib">'+a.libelle+'</span></span>'
     +'<span class="t">'+eur(tarif(a.coefficient))+'</span></button>'; });
  h+='</div></div>';
  document.getElementById('ocrPanel').innerHTML=h;
  if(e.domicile){ const d=document.getElementById('w_dom'); d.checked=true; onDom(); }
}
function addActeFromOcr(i, prescrites){
  const a=KB.actes[i], v=acteALaDate(a,dateSeance);
  // `prescrites` va dans prescrites, PAS dans seance (cf. alerteDap). Le n° de la
  // seance en cours n'est PAS sur l'ordonnance : seul le kine le connait -> il reste
  // null, et le champ « Séance n° » attend sa saisie.
  panier.push({src:i,code:a.code,coef:v.coefficient,tarif:tarif(v.coefficient),palier:v.palier,
    conditionnel:v.conditionnel,condition:v.condition,
    libelle:a.libelle,article:a.article,
    referentiel:a.referentiel,chirurgie:a.chirurgie,seance:null,
    prescrites:(prescrites===null||prescrites===undefined||prescrites===0)?null:prescrites,region:a.region});
  render();
}

// ---- init ----
document.querySelectorAll('.seg').forEach(seg=>{
  seg.addEventListener('click', ev=>{
    const b=ev.target.closest('button'); if(!b) return;
    const inp=document.getElementById(seg.dataset.for);
    inp.value = (inp.value===b.dataset.v) ? '' : b.dataset.v;   // re-clic = deselectionne
    renderActes();
  });
});
document.getElementById('bareme').textContent =
  'barème v'+KB._meta.version+' · lettre-clé '+eur(lettre());
// Deconnexion : seulement en mode SERVI (http). En file:// c'est un lien mort -> masque.
if(location.protocol.indexOf('http')===0) document.getElementById('nav-out').style.display='';
const _wd=document.getElementById('w_date');
_wd.value=dateSeance; _wd.min=KB._meta.applicable_depuis||'';
fillRegions(); renderActes(); render();
</script>
</body>
</html>
"""

html = TEMPLATE.replace("__FONTS__", FONTS).replace("__CATALOGUE_JSON__", json.dumps(KB, ensure_ascii=False))
out = ICI / "kinecotation.html"
out.write_text(html, encoding="utf-8")
print(f"OK  {out.name}  ({len(html)/1024:.0f} Ko)  — base NGAP v{KB['_meta']['version']}")
