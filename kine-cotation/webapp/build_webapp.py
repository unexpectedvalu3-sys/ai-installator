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
/* mobile : le header ne doit pas manger l'ecran. La baseline est du marketing,
   le barème est de la preuve -> on sacrifie la baseline, on garde le barème. */
@media(max-width:640px){
  header{padding:var(--sp-3) var(--sp-4);gap:var(--sp-2);flex-wrap:nowrap}
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

/* n° de seance : il PILOTE l'alerte DAP -> il est promu, pas planque */
.seance{display:inline-flex;align-items:center;gap:6px;margin-top:6px;padding:4px 8px;
  background:var(--paper-2);border:1px solid var(--line);border-radius:6px}
.seance span{font-size:11px;color:var(--ink-soft)}
.seance input{width:56px;padding:3px 6px;font-family:var(--mono);font-size:12.5px;text-align:center}
/* nb de seances PRESCRITES (lu sur l'ordonnance) — distinct du n° de seance en cours */
.presc{font-size:10.5px;color:var(--accent-deep);background:var(--accent-wash);
  border:1px solid var(--accent-line);border-radius:4px;padding:2px 6px}

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
      <div class="file"><input type="file" accept="image/*,.pdf" onchange="uploadOrdo(this)"></div>
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
    <div id="feuille"></div>
    <p class="noprint" style="margin-top:var(--sp-4);display:flex;gap:var(--sp-2)">
      <button class="act" onclick="window.print()">Imprimer / PDF</button>
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
  let r={coefficient:a.coefficient, tarif_metropole:a.tarif_metropole, palier:null};
  (a._paliers||[]).slice().sort((x,y)=>x.a_partir_du<y.a_partir_du?-1:1)
    .forEach(p=>{ if(d>=p.a_partir_du) r={coefficient:p.coefficient, tarif_metropole:p.tarif_metropole, palier:p.a_partir_du}; });
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
  if(t==='profil') loadProfilForm();
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
function reset(){panier=[];document.getElementById('w_dom').checked=false;document.getElementById('w_dom_wrap').classList.add('hidden');closePicker();render();}

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

  let h=`<div class="fh"><div>${enteteHTML()}</div>
    <div style="text-align:right"><div class="n">FEUILLE DE SOINS</div><div class="muted">Récapitulatif de cotation</div>
    <div class="muted num">séance du ${today}</div></div></div>`;
  // les alertes DAP sont le coeur anti-indu : en HAUT, pas en pied de page
  alertes.filter(a=>a.lvl!=='info').forEach(a=>h+=`<div class="alert ${a.lvl}">${a.msg}</div>`);
  h+=`<table class="ftab"><thead><tr><th>Code</th><th>Coef</th><th>Acte</th><th class="r">Tarif</th><th class="noprint"></th></tr></thead><tbody>`;
  panier.forEach((l,idx)=>{
    const ref=trouverRef(l);
    const presc = l.prescrites!=null ? `<span class="presc num" title="lu sur l'ordonnance">${l.prescrites} prescrites</span>` : '';
    const inp = ref?`<div class="seance noprint"><span>Séance n°</span><input type="number" min="1" value="${l.seance!=null?l.seance:''}" oninput="setSeance(${idx},this.value)" placeholder="—">${presc}</div>`:'';
    h+=`<tr><td><b class="c">${l.code}</b></td><td class="num">${l.coef}</td><td>${l.libelle}${inp}</td><td class="r">${eur(l.tarif)}</td>
      <td class="noprint"><span class="x" onclick="removeLigne(${idx})">✕</span></td></tr>`;
  });
  if(dep) h+=`<tr><td><b class="c">${dep.code}</b></td><td class="num">${dep.coef}</td><td>${dep.libelle}</td><td class="r">${eur(dep.tarif)}</td><td class="noprint"></td></tr>`;
  h+=`</tbody></table><div class="tot"><span>TOTAL</span><span>${eur(total)}</span></div>`;
  alertes.filter(a=>a.lvl==='info').forEach(a=>h+=`<div class="alert info">${a.msg}</div>`);

  // JUSTIFICATION = le produit. Elle epingle la VERSION DU BAREME : sans ca, une preuve
  // ne vaut rien (le bareme a change 3 fois en 8 mois). Cf. 05_REPOSITIONNEMENT_PREUVE.md.
  h+=`<div class="justif"><b>Justification (à conserver — anti-indu) :</b><br>`+
     panier.map(l=>`• ${l.code} ${l.coef} (art. ${l.article})${l.palier?(' [palier du '+frDate(l.palier)+']'):''} : `
       +`${l.libelle}${l.seance!=null?(' — séance n°'+l.seance):''}.`).join('<br>')+
     `<br>Pièces : ordonnance + BDK. Vérifier la cohérence soins ↔ prescription.
      <div class="src">Barème appliqué : ${KB._meta.source} · base v${KB._meta.version}
      · lettre-clé ${eur(lettre())} · <b>barème en vigueur à la date de la séance (${today})</b></div>
      <i>Aide à la décision — proposition de cotation non télétransmise. Le praticien valide et reste responsable.</i></div>`;
  document.getElementById('feuille').innerHTML=h;
}

// ---- OCR (necessite le backend server.py) ----
async function uploadOrdo(input){
  const f=input.files[0]; if(!f) return;
  const panel=document.getElementById('ocrPanel');
  panel.innerHTML='<div class="muted" style="margin-top:8px">Lecture de l\'ordonnance…</div>';
  const fd=new FormData(); fd.append('ordonnance', f);
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
