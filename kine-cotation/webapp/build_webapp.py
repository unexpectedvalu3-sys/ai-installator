#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genere l'app web autonome KineCotation a partir de la base officielle.

Source unique : ../knowledge_base/ngap_kine.json -> injecte dans le template HTML.
Sortie : kinecotation.html (un seul fichier, a ouvrir dans un navigateur).

    python build_webapp.py
"""

import json
from pathlib import Path

ICI = Path(__file__).resolve().parent
KB = json.loads((ICI.parent / "knowledge_base" / "ngap_kine.json").read_text(encoding="utf-8"))

TEMPLATE = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>KinéCotation — assistant de cotation NGAP</title>
<style>
  :root{--bg:#f4f6f9;--card:#fff;--ink:#1c2733;--mut:#6b7a8d;--acc:#1f6feb;--acc2:#0e9f6e;
        --warn:#b54708;--danger:#b42318;--line:#e3e8ef;}
  *{box-sizing:border-box}
  body{margin:0;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:var(--bg);color:var(--ink)}
  header{background:var(--ink);color:#fff;padding:14px 22px;display:flex;align-items:center;gap:16px}
  header h1{font-size:18px;margin:0;font-weight:700}
  header .sub{color:#9fb3c8;font-size:13px}
  nav{margin-left:auto;display:flex;gap:8px}
  nav button{background:#2b3a4a;color:#cdd9e5;border:0;padding:8px 14px;border-radius:8px;cursor:pointer;font-size:14px}
  nav button.on{background:var(--acc);color:#fff}
  main{max-width:1080px;margin:18px auto;padding:0 16px;display:grid;grid-template-columns:1fr 1fr;gap:18px}
  @media(max-width:880px){main{grid-template-columns:1fr}}
  .card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px}
  .card h2{margin:0 0 12px;font-size:15px;text-transform:uppercase;letter-spacing:.04em;color:var(--mut)}
  label{display:block;font-size:13px;color:var(--mut);margin:10px 0 4px}
  input,select{width:100%;padding:9px 10px;border:1px solid var(--line);border-radius:8px;font-size:14px;background:#fff}
  .row{display:flex;gap:10px}.row>*{flex:1}
  .chk{display:flex;align-items:center;gap:8px;margin-top:12px}.chk input{width:auto}
  button.act{background:var(--acc);color:#fff;border:0;padding:10px 16px;border-radius:9px;cursor:pointer;font-size:14px;font-weight:600}
  button.act:hover{filter:brightness(1.07)}
  button.ghost{background:#eef2f7;color:var(--ink)}
  .pill{display:inline-block;background:#eef2f7;border-radius:999px;padding:3px 10px;font-size:12px;color:var(--mut)}
  .actes{display:flex;flex-direction:column;gap:6px;max-height:230px;overflow:auto;margin-top:8px}
  .acte{display:flex;justify-content:space-between;gap:8px;border:1px solid var(--line);border-radius:8px;padding:8px 10px;cursor:pointer;font-size:13px}
  .acte:hover{border-color:var(--acc);background:#f5f9ff}
  .acte .c{font-weight:700;color:var(--acc)}
  .ligne{display:flex;justify-content:space-between;font-size:13px;padding:6px 0;border-bottom:1px dashed var(--line)}
  .ligne .x{color:var(--danger);cursor:pointer;margin-left:8px}
  .tot{display:flex;justify-content:space-between;font-weight:700;font-size:16px;margin-top:8px}
  .alert{border-radius:8px;padding:9px 11px;font-size:13px;margin-top:8px}
  .alert.danger{background:#fef3f2;color:var(--danger);border:1px solid #fecdca}
  .alert.warn{background:#fffaeb;color:var(--warn);border:1px solid #fedf89}
  .alert.info{background:#eff8ff;color:#175cd3;border:1px solid #b2ddff}
  .muted{color:var(--mut);font-size:12px}
  /* feuille imprimable */
  #feuille{background:#fff;border:1px solid var(--line);border-radius:12px;padding:24px}
  .fh{display:flex;justify-content:space-between;border-bottom:2px solid var(--ink);padding-bottom:10px}
  .fh .n{font-weight:700;font-size:16px}
  .ftab{width:100%;border-collapse:collapse;margin-top:14px;font-size:13px}
  .ftab th,.ftab td{text-align:left;padding:6px 4px;border-bottom:1px solid var(--line)}
  .ftab td.r{text-align:right}
  .justif{font-size:12px;color:var(--mut);margin-top:12px;border-top:1px dashed var(--line);padding-top:10px}
  .hidden{display:none}
  @media print{header,nav,#tab-cotation .builder,.noprint{display:none!important}
    body{background:#fff}main{display:block;max-width:none}#feuille{border:0}}
</style>
</head>
<body>
<header>
  <h1>KinéCotation</h1><span class="sub">assistant de cotation NGAP — anti sous-cotation / anti-indu</span>
  <nav>
    <button id="nav-cot" class="on" onclick="show('cotation')">Cotation</button>
    <button id="nav-prof" onclick="show('profil')">Mon profil</button>
  </nav>
</header>

<main id="tab-profil" class="hidden">
  <div class="card">
    <h2>Profil praticien</h2>
    <p class="muted">Saisi une fois. Apparait en en-tete de chaque feuille de soins. Stocke localement sur ce poste.</p>
    <label>Nom et prenom</label><input id="p_nom" placeholder="Claire DUBOIS">
    <label>Qualite</label><input id="p_qual" value="Masseur-Kinésithérapeute D.E.">
    <div class="row"><div><label>N° RPPS</label><input id="p_rpps" placeholder="10101010101"></div>
      <div><label>N° de facturation (AM)</label><input id="p_amf" placeholder="691234567"></div></div>
    <label>Adresse du cabinet</label><input id="p_adr" placeholder="12 rue des Lilas">
    <div class="row"><div><label>Code postal / Ville</label><input id="p_cpv" placeholder="69003 LYON"></div>
      <div><label>Téléphone</label><input id="p_tel" placeholder="04 78 00 00 00"></div></div>
    <label>Email</label><input id="p_mail" placeholder="cabinet@exemple.fr">
    <label>Conventionnement / secteur</label><input id="p_conv" placeholder="Conventionné secteur 1">
    <div class="chk"><input type="checkbox" id="p_drom"><label style="margin:0">Exercice en DROM-COM (lettre-clé 2,43 € au lieu de 2,21 €)</label></div>
    <p style="margin-top:16px"><button class="act" onclick="saveProfil()">Enregistrer</button>
      <span id="psaved" class="pill" style="display:none">✓ enregistré</span></p>
  </div>
  <div class="card">
    <h2>Aperçu en-tête</h2>
    <div id="profilApercu"></div>
  </div>
</main>

<main id="tab-cotation">
  <div class="card builder">
    <h2>Construire la feuille de soins</h2>
    <label>📷 Importer une ordonnance (photo) — pré-remplissage OCR</label>
    <input type="file" accept="image/*,.pdf" onchange="uploadOrdo(this)">
    <div id="ocrPanel"></div>
    <hr style="border:0;border-top:1px solid var(--line);margin:14px 0">
    <label>1. Région / type d'affection</label>
    <select id="w_region" onchange="onRegion()"></select>
    <div id="w_chir_wrap" class="hidden"><label>2. Acte post-chirurgical (opéré) ?</label>
      <select id="w_chir" onchange="renderActes()"><option value="">— préciser —</option><option value="oui">Opéré (chirurgie)</option><option value="non">Non opéré (médical)</option></select></div>
    <div id="w_ref_wrap" class="hidden"><label>3. Pathologie inscrite au référentiel HAS ?</label>
      <select id="w_ref" onchange="renderActes()"><option value="">— préciser —</option><option value="oui">Oui (référentiel)</option><option value="non">Non (hors référentiel)</option></select></div>
    <label>4. Acte précis réalisé</label>
    <div id="w_actes" class="actes"></div>

    <hr style="border:0;border-top:1px solid var(--line);margin:16px 0">
    <div class="row noprint">
      <button class="act ghost" onclick="openPicker('bilan')">+ Bilan (BDK)</button>
      <button class="act ghost" onclick="openPicker('supp')">+ Supplément</button>
    </div>
    <div id="picker"></div>
    <div class="chk"><input type="checkbox" id="w_dom" onchange="onDom()"><label style="margin:0">Séance à domicile (déplacement)</label></div>
    <div id="w_dom_wrap" class="hidden row" style="margin-top:8px">
      <div><label>Distance facturable (km)</label><input id="w_km" type="number" min="0" value="0" oninput="render()"></div>
      <div><label>Terrain</label><select id="w_terrain" onchange="render()"><option value="plaine">Plaine</option><option value="montagne">Montagne</option><option value="pied_ski">À pied / ski</option></select></div>
    </div>
    <p class="muted" style="margin-top:14px">Astuce : l'OCR d'ordonnance (à venir) pré-remplira ces champs depuis une photo.</p>
  </div>

  <div class="card">
    <h2 class="noprint">Feuille de soins</h2>
    <div id="feuille"></div>
    <p class="noprint" style="margin-top:14px">
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
let panier = [];      // {code,coef,tarif,libelle,article,referentiel,chirurgie,seance}

// ---- helpers cotation (miroir du moteur Python) ----
const lettre = ()=> profil.drom ? KB._meta.valeur_lettre_cle_eur.drom : KB._meta.valeur_lettre_cle_eur.metropole;
const tarif = c => Math.round(c*lettre()*100)/100;
const eur = n => n.toFixed(2).replace('.',',')+' €';
const actesRegion = r => KB.actes.filter(a=>a.region===r);
const trouverRef = a => KB.referentiels.find(r=>a.libelle.toLowerCase().includes(r.match_libelle));
function alerteDap(ref,seance){
  const seuil=ref.dap_des_seance;
  let b=`Référentiel HAS : ${ref.situation} → ${ref.seances_avant_dap?('1 à '+ref.seances_avant_dap):'0'} séance(s), DAP dès la ${seuil}ᵉ.`;
  if(ref.note) b+=` (${ref.note})`;
  if(seance!=null && seance>=seuil) return {lvl:'danger',msg:'⚠ DAP REQUISE — '+b+` Or séance n°${seance}.`};
  if(seance!=null && seance===seuil-1) return {lvl:'warn',msg:'Avant-dernière séance sans DAP — anticiper. '+b};
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
function renderActes(){
  const r=document.getElementById('w_region').value; if(!r){document.getElementById('w_actes').innerHTML='';return;}
  let actes=actesRegion(r);
  const c=document.getElementById('w_chir').value, rf=document.getElementById('w_ref').value;
  if(!document.getElementById('w_chir_wrap').classList.contains('hidden')&&c) actes=actes.filter(a=>a.chirurgie===(c==='oui'));
  if(!document.getElementById('w_ref_wrap').classList.contains('hidden')&&rf) actes=actes.filter(a=>a.referentiel===(rf==='oui'));
  document.getElementById('w_actes').innerHTML = actes.map(a=>{
    const i=KB.actes.indexOf(a);
    return `<div class="acte" onclick="addActe(${i})"><span><b class="c">${a.code} ${a.coefficient}</b> — ${a.libelle}</span><span>${eur(tarif(a.coefficient))}</span></div>`;
  }).join('') || '<div class="muted">Précise les filtres ci-dessus.</div>';
}
function addActe(i){
  const a=KB.actes[i];
  panier.push({code:a.code,coef:a.coefficient,tarif:tarif(a.coefficient),libelle:a.libelle,article:a.article,referentiel:a.referentiel,chirurgie:a.chirurgie,seance:null});
  render();
}
function setSeance(idx,val){
  const n=String(val).trim();
  panier[idx].seance = /^\d+$/.test(n) ? parseInt(n) : null;
  render();
}
function openPicker(kind){
  const list = kind==='bilan'?KB.bilans:KB.supplements;
  const titre = kind==='bilan'?'Type de bilan (BDK)':'Supplément';
  let h='<div style="border:1px solid var(--acc);border-radius:10px;padding:10px;margin-top:8px"><b>'+titre+'</b><div class="actes">';
  list.forEach((x,i)=>{ h+='<div class="acte" onclick="pickItem(\''+kind+'\','+i+')"><span><b class="c">'+x.code+' '+x.coefficient+'</b> — '+x.libelle+'</span><span>'+eur(tarif(x.coefficient))+'</span></div>'; });
  h+='</div><div class="muted" style="margin-top:6px;cursor:pointer" onclick="closePicker()">✕ fermer</div></div>';
  document.getElementById('picker').innerHTML=h;
}
function closePicker(){document.getElementById('picker').innerHTML='';}
function pickItem(kind,i){
  const x=(kind==='bilan'?KB.bilans:KB.supplements)[i];
  panier.push({code:x.code,coef:x.coefficient,tarif:tarif(x.coefficient),libelle:x.libelle,article:'—',referentiel:false,chirurgie:false,seance:null});
  closePicker(); render();
}
function onDom(){document.getElementById('w_dom_wrap').classList.toggle('hidden',!document.getElementById('w_dom').checked);render();}
function removeLigne(i){panier.splice(i,1);render();}
function reset(){panier=[];document.getElementById('w_dom').checked=false;document.getElementById('w_dom_wrap').classList.add('hidden');closePicker();render();}

// ---- rendu feuille ----
function render(){
  let dep=null;
  if(document.getElementById('w_dom') && document.getElementById('w_dom').checked){
    const km=parseInt(document.getElementById('w_km').value||'0'), t=document.getElementById('w_terrain').value;
    dep=ligneDeplacement(km,t);
  }
  const allLignes = dep?panier.concat([dep]):panier;
  const total=Math.round(allLignes.reduce((s,l)=>s+l.tarif,0)*100)/100;
  const today=new Date().toLocaleDateString('fr-FR');
  // alertes derivees du panier (recalculees a chaque rendu)
  const alertes=[];
  panier.forEach(l=>{const ref=trouverRef(l); if(ref) alertes.push(alerteDap(ref,(l.seance==null)?null:l.seance));});

  let h=`<div class="fh"><div>${enteteHTML()}</div>
    <div style="text-align:right"><div class="n">FEUILLE DE SOINS</div><div class="muted">Récapitulatif de cotation</div><div class="muted">${today}</div></div></div>`;
  h+=`<table class="ftab"><thead><tr><th>Code</th><th>Coef</th><th>Acte</th><th class="r">Tarif</th><th class="noprint"></th></tr></thead><tbody>`;
  if(!panier.length && !dep) h+=`<tr><td colspan="5" class="muted">Ajoute un acte via l'assistant à gauche.</td></tr>`;
  panier.forEach((l,idx)=>{
    const ref=trouverRef(l);
    const inp = ref?`<br><span class="noprint muted">n° séance : <input type="number" min="1" style="width:70px" value="${l.seance!=null?l.seance:''}" oninput="setSeance(${idx},this.value)"></span>`:'';
    h+=`<tr><td><b>${l.code}</b></td><td>${l.coef}</td><td>${l.libelle}${inp}</td><td class="r">${eur(l.tarif)}</td>
      <td class="noprint"><span class="x" onclick="removeLigne(${idx})">✕</span></td></tr>`;
  });
  if(dep) h+=`<tr><td><b>${dep.code}</b></td><td>${dep.coef}</td><td>${dep.libelle}</td><td class="r">${eur(dep.tarif)}</td><td class="noprint"></td></tr>`;
  h+=`</tbody></table><div class="tot"><span>TOTAL</span><span>${eur(total)}</span></div>`;
  alertes.forEach(a=>h+=`<div class="alert ${a.lvl}">${a.msg}</div>`);
  if(panier.length || dep){
    h+=`<div class="justif"><b>Justification (à conserver — anti-indu) :</b><br>`+
       panier.map(l=>`• ${l.code} ${l.coef} (art. ${l.article}) : ${l.libelle}${l.seance!=null?(' — séance n°'+l.seance):''}.`).join('<br>')+
       `<br>Pièces : ordonnance + BDK. Vérifier la cohérence soins ↔ prescription.<br>
        <i>Aide à la décision — proposition de cotation non télétransmise. Le praticien valide et reste responsable.</i></div>`;
  }
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
  let h='<div style="border:1px solid var(--acc);border-radius:10px;padding:12px;margin-top:10px">';
  h+='<b>Ordonnance lue</b> <span class="pill">confiance '+(e.confiance||'?')+'</span>';
  h+='<div class="muted" style="margin:6px 0">'+(e.pathologie_texte||'')+'</div>';
  h+='<div class="muted">Zone : '+(e.zone||'?')+' · Chirurgie : '+(e.chirurgie||'?')
     +' · Séances : '+(e.nb_seances_prescrites||'—')+' · Domicile : '+(e.domicile?'oui':'non')
     +' · Bilan : '+(e.mention_bilan?'oui':'non')+'</div>';
  (e.alertes||[]).forEach(a=>h+='<div class="alert warn">'+a+'</div>');
  h+='<div class="muted" style="margin-top:8px">Actes proposés — clique le bon :</div><div class="actes">';
  const se = e.nb_seances_prescrites ? e.nb_seances_prescrites : 'null';
  c.forEach(a=>{ h+='<div class="acte" onclick="addActeFromOcr('+a.index+','+se+')">'
     +'<span><b class="c">'+a.code+' '+a.coefficient+'</b> — '+a.libelle+'</span>'
     +'<span>'+eur(tarif(a.coefficient))+'</span></div>'; });
  h+='</div></div>';
  document.getElementById('ocrPanel').innerHTML=h;
  if(e.domicile){ const d=document.getElementById('w_dom'); d.checked=true; onDom(); }
  if(e.mention_bilan){ /* le kine ajoute le BDK via le bouton, le type reste son choix */ }
}
function addActeFromOcr(i, seances){
  const a=KB.actes[i];
  panier.push({code:a.code,coef:a.coefficient,tarif:tarif(a.coefficient),libelle:a.libelle,article:a.article,referentiel:a.referentiel,chirurgie:a.chirurgie,seance:(seances===null||seances===undefined)?null:seances});
  render();
}

// ---- init ----
fillRegions(); render();
</script>
</body>
</html>
"""

html = TEMPLATE.replace("__CATALOGUE_JSON__", json.dumps(KB, ensure_ascii=False))
out = ICI / "kinecotation.html"
out.write_text(html, encoding="utf-8")
print(f"Genere : {out}  ({len(html)//1024} Ko, {len(KB['actes'])} actes embarques)")
