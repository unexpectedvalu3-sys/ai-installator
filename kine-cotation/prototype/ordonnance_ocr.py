#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KinéCotation — OCR ordonnance via provider IA abstrait (prototype)

Role STRICT du LLM : PERCEPTION uniquement. Il lit l'ordonnance (photo/scan)
et en extrait les FAITS CLINIQUES structures. Il ne calcule JAMAIS la cotation
ni un coefficient : c'est le moteur deterministe (cotation_engine.py + base
officielle ngap_kine.json) qui fait la cotation. Cette separation est une
garantie de securite (pas d'hallucination de tarif de facturation sante).

Pipeline : ordonnance (image) -> vision (provider actif) -> extraction structuree
           -> matching avec le catalogue officiel -> facture pre-remplie a valider.

Le provider est abstrait (llm.py, CLAUDE.md §4.2) : defaut = Mistral (FR/UE) pour
la souverainete des donnees. Aucun nom de fournisseur ne vit dans ce fichier.

⚠️ RGPD : une ordonnance est une donnee de sante et l'image SORT du poste vers le
provider. Benchmark = ordonnances ANONYMISEES uniquement (protocole §0.1).
Production sur donnees reelles = Mistral Enterprise + ZDR + DPA art. 28.

Pre-requis :
    pip install -r requirements.txt
    MISTRAL_API_KEY (ou KINE_LLM_PROVIDER=anthropic + ANTHROPIC_API_KEY)

Usage :
    python ordonnance_ocr.py chemin/vers/ordonnance.jpg
    python llm.py                     # verifie provider / modele / cle
"""

import base64
import json
import os
import re
import sys
from pathlib import Path

try:
    from pydantic import BaseModel, Field
except ImportError:
    print("Installer les dependances : pip install -r requirements.txt")
    sys.exit(1)

import cotation_engine as ce
import llm  # couche provider abstraite (CLAUDE.md §4.2) — voir 06_PROVIDER_IA.md

# Le modele n'est PLUS choisi ici : il depend du provider actif (KINE_LLM_PROVIDER,
# defaut = mistral pour la souverainete FR/UE). Bascule dans llm.py, nulle part ailleurs.

MEDIA_TYPES = {
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".gif": "image/gif", ".webp": "image/webp",
}

ZONES_VALIDES = list(ce.REGIONS.values())

SYSTEME = """Tu es un assistant d'extraction pour kinesitherapeutes. On te donne la
photo ou le scan d'une ordonnance medicale de kinesitherapie.

Ta SEULE mission : extraire fidelement les faits cliniques presents sur l'ordonnance.
Tu NE proposes PAS de cotation, PAS de lettre-cle, PAS de coefficient, PAS de tarif :
un moteur separe s'en charge a partir de tes faits.

Regles :
- N'invente rien. Si une information est absente ou illisible, mets null et signale-le
  dans 'alertes'.
- Recopie le diagnostic / la zone / le geste exactement comme ecrit (pathologie_texte).
- Deduis 'zone', 'chirurgie' et 'specialite' uniquement si l'ordonnance le permet sans
  ambiguite ; sinon mets 'inconnu' + alerte.
- Champs texte absents/illisibles : chaine vide "". Seances non indiquees : 0.
- Signale toute ordonnance incomplete ou non conforme (pas de date, pas de prescripteur,
  pas de nombre de seances, mention illisible) dans 'alertes'.
- 'confiance' = ta confiance globale dans l'extraction (low / medium / high)."""


class Ordonnance(BaseModel):
    # Schema volontairement plat (pas de types nullables) pour rester compatible
    # structured outputs. Sentinelles : "" / "inconnu" / 0 = information absente.
    patient_nom: str = Field("", description="Nom du patient si lisible, sinon ''")
    prescripteur: str = Field("", description="Medecin prescripteur, sinon ''")
    date_prescription: str = Field("", description="Date de l'ordonnance, sinon ''")
    pathologie_texte: str = Field("", description="Diagnostic / motif recopie tel quel")
    zone: str = Field("inconnu", description="rachis | membre_sup | membre_inf | specialite | inconnu")
    cote: str = Field("inconnu", description="droite | gauche | bilateral | inconnu")
    chirurgie: str = Field("inconnu", description="oui | non | inconnu")
    specialite: str = Field("", description="ex: respiratoire, neuro, vasculaire, perineal... sinon ''")
    nb_seances_prescrites: int = Field(0, description="Nombre de seances prescrites, 0 si non indique")
    domicile: bool = Field(False, description="True si prise en charge a domicile demandee")
    urgence: bool = Field(False, description="True si caractere urgent / desencombrement")
    mention_bilan: bool = Field(False, description="True si un bilan (BDK) est mentionne")
    confiance: str = Field("medium", description="low | medium | high")
    alertes: list[str] = Field(default_factory=list, description="Anomalies / ambiguites / champs manquants")


def encoder_image(path: Path):
    ext = path.suffix.lower()
    if ext == ".pdf":
        return ("document", "application/pdf", base64.standard_b64encode(path.read_bytes()).decode())
    if ext not in MEDIA_TYPES:
        raise ValueError(f"Format non supporte : {ext} (png/jpg/webp/pdf)")
    return ("image", MEDIA_TYPES[ext], base64.standard_b64encode(path.read_bytes()).decode())


def _extraire_json(texte: str) -> dict:
    """Recupere le 1er objet JSON d'une reponse (tolere les fences ```json)."""
    t = texte.strip()
    if "```" in t:
        t = t.split("```")[1]
        if t.lstrip().lower().startswith("json"):
            t = t.lstrip()[4:]
    debut, fin = t.find("{"), t.rfind("}")
    if debut == -1 or fin == -1:
        raise ValueError(f"Pas de JSON dans la reponse : {texte[:200]}")
    return json.loads(t[debut:fin + 1])


def lire_ordonnance(path: Path) -> Ordonnance:
    source = encoder_image(path)  # (kind, media_type, data_b64)

    cles = ", ".join(Ordonnance.model_fields)
    instruction = (SYSTEME + "\n\nReponds UNIQUEMENT par un objet JSON valide (aucun texte autour) "
                   f"avec EXACTEMENT ces cles : {cles}.")
    texte = llm._call_llm(
        systeme=instruction,
        invite="Extrais les faits cliniques. Reponds en JSON.",
        source=source,
    )
    data = _extraire_json(texte)
    # Normalisation defensive (le modele peut renvoyer un bool ou null)
    c = data.get("chirurgie")
    if isinstance(c, bool):
        data["chirurgie"] = "oui" if c else "non"
    for champ in ("zone", "cote", "chirurgie"):
        if data.get(champ) in (None, ""):
            data[champ] = "inconnu"
    for champ in ("patient_nom", "prescripteur", "date_prescription", "pathologie_texte", "specialite"):
        if data.get(champ) is None:
            data[champ] = ""
    if data.get("nb_seances_prescrites") in (None, ""):
        data["nb_seances_prescrites"] = 0
    return Ordonnance(**data)


STOP = {"reeducation", "apres", "suite", "pose", "operee", "opere", "non", "les", "des",
        "une", "dans", "cadre", "consequences", "affection", "secondaire", "avec", "sans",
        "pour", "chez", "tout", "partie", "moins", "deux", "meme", "totale", "initial"}


def _mots(txt: str) -> set:
    txt = (txt or "").lower()
    txt = re.sub(r"[^a-zàâäéèêëîïôöûüç0-9]+", " ", txt)
    return {w for w in txt.split() if len(w) > 3 and w not in STOP}


def proposer_actes(ordo: Ordonnance, kb):
    """Matching deterministe par mots-cles : texte clinique -> actes du catalogue officiel."""
    mots = _mots(ordo.pathologie_texte) | _mots(ordo.zone) | _mots(ordo.specialite)
    chir = {"oui": True, "non": False}.get(ordo.chirurgie)  # None si inconnu

    scores = []
    for a in kb["actes"]:
        score = len(mots & _mots(a["libelle"]))
        if score == 0:
            continue
        if chir is not None and a["chirurgie"] == chir:
            score += 0.5  # bonus coherence chirurgie
        scores.append((score, a))
    scores.sort(key=lambda x: -x[0])
    return [a for _, a in scores]


def afficher(ordo: Ordonnance, kb):
    print("\n" + "=" * 64)
    print("  EXTRACTION ORDONNANCE (a valider par le kine)")
    print("=" * 64)
    print(f"  Patient        : {ordo.patient_nom or '—'}")
    print(f"  Prescripteur   : {ordo.prescripteur or '—'}    Date : {ordo.date_prescription or '—'}")
    print(f"  Pathologie     : {ordo.pathologie_texte or '—'}")
    print(f"  Zone / cote    : {ordo.zone} / {ordo.cote}    Chirurgie : {ordo.chirurgie}")
    print(f"  Seances prescr.: {ordo.nb_seances_prescrites or '—'}    Domicile : {ordo.domicile}    Urgence : {ordo.urgence}")
    print(f"  Bilan mentionne: {ordo.mention_bilan}    Confiance : {ordo.confiance}")
    if ordo.alertes:
        print("  ALERTES extraction :")
        for a in ordo.alertes:
            print(f"   [!] {a}")

    print("-" * 64)
    print("  ACTES CANDIDATS (catalogue officiel — le kine choisit) :")
    candidats = proposer_actes(ordo, kb)
    if not candidats:
        print("   Aucun match automatique — passer par l'arbre interactif (cotation_engine.py).")
    for a in candidats[:8]:
        print(f"   {a['code']:<5}{a['coefficient']:>6}  {a['tarif_metropole']:>6.2f}€  "
              f"(art.{a['article']})  {a['libelle']}")

    # Alerte referentiel/DAP si un candidat est sous referentiel et nb seances connu
    for a in candidats[:8]:
        ref = ce.trouver_referentiel(a, kb)
        if ref:
            seance = ordo.nb_seances_prescrites or None  # 0 = non precise -> None
            print("  " + ce.alerte_dap(ref, seance))
            break
    print("\n  /!\\ Extraction = aide. Le kine valide l'acte exact puis genere la facture.")
    print("=" * 64 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python ordonnance_ocr.py chemin/vers/ordonnance.(jpg|png|pdf)")
        sys.exit(1)
    try:
        llm.verifier_cle()
    except llm.LLMIndisponible as e:
        print(f"[!] {e}")
        sys.exit(1)

    chemin = Path(sys.argv[1])
    if not chemin.exists():
        print(f"Fichier introuvable : {chemin}")
        sys.exit(1)

    kb = ce.charger_kb()
    ordo = lire_ordonnance(chemin)
    afficher(ordo, kb)
