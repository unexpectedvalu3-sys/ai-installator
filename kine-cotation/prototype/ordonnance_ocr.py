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
import unicodedata
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
- Deduis 'zone' et 'specialite' uniquement si l'ordonnance le permet sans ambiguite ;
  sinon mets 'inconnu' + alerte.
- 'chirurgie' = EXACTEMENT 'oui', 'non' ou 'inconnu' (jamais de texte libre comme
  'operee') : 'oui' si un geste chirurgical est mentionne (opere, prothese,
  arthroplastie, reconstruction, reinsertion, suture, arthroscopie, amputation,
  ligamentoplastie) ; 'non' si explicitement non opere ou aucun geste ; 'inconnu'
  seulement si vraiment ambigu.
- Champs texte absents/illisibles : chaine vide "". Seances non indiquees : 0.
- TYPES STRICTS. Respecte le type de chaque cle, ne mets JAMAIS de texte a la place :
  * 'domicile', 'urgence', 'mention_bilan' = booleen true ou false (PAS le texte de
    l'element). Ex. si l'ordonnance mentionne un bilan -> "mention_bilan": true.
  * 'nb_seances_prescrites' = entier (ex. 30), pas "30 seances".
  * 'alertes' = liste de chaines (ex. []), jamais une chaine seule.
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


_NEGATIONS = {"false", "0", "non", "faux", "no", "n", "aucun", "absent", "null", "none", "inconnu"}


def _to_bool(v):
    """Coerce un booleen de PRESENCE -> bool.

    domicile/urgence/mention_bilan repondent a 'est-ce present ?'. Les modeles open
    (Qwen) y mettent souvent le TEXTE de l'element ('- Bilan diagnostic...') au lieu
    de true -> une chaine descriptive non vide = presence = True. Seules les
    negations explicites (et le vide) valent False. Diagnostic mesure le 2026-07-18.
    """
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    if isinstance(v, (int, float)):
        return v != 0
    s = str(v).strip().lower()
    if not s:
        return False
    return s not in _NEGATIONS


def _to_int(v):
    """Coerce un entier lache -> int. '50 seances' -> 50 ; rien de numerique -> 0."""
    if isinstance(v, bool):
        return 0
    if isinstance(v, int):
        return v
    m = re.search(r"\d+", str(v if v is not None else ""))
    return int(m.group()) if m else 0


_CHIR_MOTS = ("oper", "chirurg", "prothes", "arthroplast", "reconstruc",
              "reinsertion", "suture", "arthroscop", "amputation", "ligamentoplast")


def _to_chirurgie(v):
    """Coerce le statut chirurgical -> 'oui' | 'non' | 'inconnu'.

    Les modeles renvoient souvent du texte libre ('operee', 'operee le 30/05') au
    lieu de oui/non -> le score (booleen) le lit comme non-oui et RATE les cas
    operes. On mappe : negation explicite -> non ; mot chirurgical -> oui.
    Diagnostic mesure le 2026-07-18 (chirurgie 70% = les 3 cas operes rates).
    """
    if isinstance(v, bool):
        return "oui" if v else "non"
    s = str(v if v is not None else "").strip().lower()
    if not s or s == "inconnu":
        return "inconnu"
    if "non oper" in s or "non-oper" in s or "sans chirurg" in s:
        return "non"
    if any(m in s for m in _CHIR_MOTS):
        return "oui"
    if s in ("oui", "o", "true", "vrai", "yes"):
        return "oui"
    if s in ("non", "n", "false", "faux", "no"):
        return "non"
    return "inconnu"


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
    # Normalisation defensive. INDISPENSABLE pour la voie B : les modeles open
    # (Qwen2.5-VL, etc.) rendent un JSON plus lache que Claude/Mistral -> booleens
    # en mots francais ("oui"/"non"), entiers en texte ("50 seances"). Sans coercion,
    # le schema Pydantic strict rejette TOUT (10/10 erreurs mesurees). On coerce ici
    # pour benchmarker les modeles a armes egales (fair OCR, pas fair formatage JSON).
    data["chirurgie"] = _to_chirurgie(data.get("chirurgie"))
    for champ in ("zone", "cote"):
        if data.get(champ) in (None, ""):
            data[champ] = "inconnu"
    for champ in ("patient_nom", "prescripteur", "date_prescription", "pathologie_texte", "specialite"):
        if data.get(champ) is None:
            data[champ] = ""
    for champ in ("domicile", "urgence", "mention_bilan"):
        if champ in data:
            data[champ] = _to_bool(data[champ])
    data["nb_seances_prescrites"] = _to_int(data.get("nb_seances_prescrites"))
    al = data.get("alertes")
    if not isinstance(al, list):  # Qwen rend "" au lieu de [] ; d'autres une string
        data["alertes"] = [al] if isinstance(al, str) and al.strip() else []
    return Ordonnance(**data)


STOP = {"reeducation", "apres", "suite", "pose", "operee", "opere", "non", "les", "des",
        "une", "dans", "cadre", "consequences", "affection", "secondaire", "avec", "sans",
        "pour", "chez", "tout", "partie", "moins", "deux", "meme", "totale", "initial"}


def _mots(txt: str) -> set:
    txt = (txt or "").lower()
    txt = re.sub(r"[^a-zàâäéèêëîïôöûüç0-9]+", " ", txt)
    return {w for w in txt.split() if len(w) > 3 and w not in STOP}


# Synonymes anatomiques/pathologiques -> region de la base. INDISPENSABLE : une vraie
# ordonnance ecrit « lombaire », la base dit « lombalgie / lombo / rachis » -> le matching
# par mots EXACTS rend 0 acte (mesure sur la 1re vraie ordonnance de Malcom, 2026-07-22 :
# zone lue « lombaire », zero acte propose). On mappe donc la zone + la patho lues vers une
# region, et on propose les actes de cette region meme sans mot commun exact.
REGION_SYNONYMES = {
    "rachis": ["rachis", "lombaire", "lombalgie", "lombo", "lombosacr", "lumbago", "dorsal",
               "dorso", "cervical", "cervicalgie", "cervico", "vertebr", "sciatique",
               "sciatalgie", "cruralgie", "disc", "hernie", "scoliose", "spondyl", "dos"],
    "membre_inf": ["membre inf", "genou", "hanche", "coxo", "cheville", "pied", "cuisse",
                   "jambe", "tibia", "femur", "femoro", "rotul", "patell", "menisq",
                   "ligament croise", "lca", "achille", "talon", "orteil", "malleol",
                   "gonarthrose", "coxarthrose", "ptg", "pth", "arthroplastie du genou",
                   "arthroplastie de hanche", "prothese de genou", "prothese de hanche"],
    "membre_sup": ["membre sup", "epaule", "scapul", "coude", "poignet", "main", "avant-bras",
                   "avant bras", "doigt", "coiff", "rotateur", "humerus", "carpien",
                   "canal carpien", "radius", "cubital", "pouce", "epicondyl", "clavicul"],
    "respiratoire": ["respiratoire", "bronch", "bpco", "pulmonaire", "desencombr", "poumon",
                     "asthm", "mucoviscidose", "kine respi", "encombrement"],
    "neuro_musculaire": ["neuro", "hemipleg", "parapleg", "tetrapleg", "avc", "myopath",
                         "sclerose", "parkinson", "paralys", "encephalopath", "radiculaire",
                         "tronculaire", "hemiplegie", "sep"],
    "vasculaire": ["vasculaire", "lymphoedeme", "lymphatique", "oedeme", "veineux", "drainage lymphatique"],
    "abdo_perineo": ["perine", "perineal", "abdomin", "uro-gyneco", "post-partum", "post partum",
                     "incontinence", "reeducation perineale"],
    "rhumato_inflammatoire": ["rhumatisme inflammatoire", "polyarthrit", "spondylarthrit"],
    "maxillo_orl": ["maxillo", "temporo-mandibul", "mandibul", "paralysie faciale", "atm"],
    "geriatrie": ["deambulation", "personne agee", "geriatr"],
    "amputation": ["amputation", "ampute", "moignon", "appareillage"],
    "brulures": ["brulure", "brule"],
    "palliatif": ["palliatif", "soins palliatifs"],
}


def _sansacc(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", (s or "").lower())
                   if unicodedata.category(c) != "Mn")


def deduire_region(ordo: Ordonnance):
    """Region de la base la plus plausible d'apres zone + patho + specialite lues.
    Rend la region (str) ou None. Robuste au vocabulaire : « lombaire » -> « rachis »."""
    txt = _sansacc(" ".join([ordo.zone or "", ordo.pathologie_texte or "", ordo.specialite or ""]))
    if not txt.strip():
        return None
    meilleure, nmax = None, 0
    for region, syns in REGION_SYNONYMES.items():
        n = sum(1 for s in syns if _sansacc(s) in txt)
        if n > nmax:
            meilleure, nmax = region, n
    return meilleure


def _stems(mots, n=4):
    return {w[:n] for w in mots if len(w) >= n}


def proposer_actes(ordo: Ordonnance, kb):
    """Texte clinique -> actes du catalogue. Combine 3 signaux, du plus fort au plus
    faible : mots-cles EXACTS, REGION deduite (synonymes), et RACINES de 4 lettres
    (« lombaire » ~ « lombalgie »). Sans la region, une vraie ordonnance rend 0 acte."""
    mots = _mots(ordo.pathologie_texte) | _mots(ordo.zone) | _mots(ordo.specialite)
    stems = _stems(mots)
    chir = {"oui": True, "non": False}.get(ordo.chirurgie)  # None si inconnu
    region = deduire_region(ordo)

    scores = []
    for a in kb["actes"]:
        amots = _mots(a["libelle"])
        score = len(mots & amots)                       # mots exacts (fort)
        if region and a.get("region") == region:
            score += 1                                  # region deduite (fait remonter la zone)
        score += 0.4 * len(stems & _stems(amots))       # racines partagees (lomb ~ lomb)
        if score == 0:
            continue
        if chir is not None and a["chirurgie"] == chir:
            score += 0.5                                # bonus coherence chirurgie
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
