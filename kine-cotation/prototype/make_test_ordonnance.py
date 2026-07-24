#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genere un BATCH d'ordonnances kine FICTIVES + leur verite terrain automatique.

    python make_test_ordonnance.py [dossier_sortie]
    (defaut : ../benchmark/synthetiques/)

Atout du synthetique : la verite terrain est GRATUITE (on sait ce qu'on genere).
Le script ecrit les images ET verite_terrain.csv (auto), directement scorable par
benchmark/score.py -> on peut faire tourner le benchmark AVANT d'avoir les vraies
ordonnances de Malcom.

LIMITE ASSUMEE : ce sont des ordonnances TAPEES (corps en pseudo-manuscrit
italique, pas de la vraie ecriture). Elles valident la chaine d'extraction + la
cotation + la DAP + le prompt (validite JSON) sur le cas TAPE, et l'aptitude des
modeles a lire du FR structure. Elles NE valident PAS le manuscrit reel -> pour
ca : RIMES (FR manuscrit) en 1er filtre, puis les vraies ordonnances anonymisees.
Voir benchmark/00_PROTOCOLE_BENCHMARK_OCR.md §« Sources de donnees de test ».
"""

import csv
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ICI = Path(__file__).resolve().parent
KB = json.loads((ICI.parent / "knowledge_base" / "ngap_kine.json").read_text(encoding="utf-8"))

F = "C:/Windows/Fonts/arial.ttf"
FB = "C:/Windows/Fonts/arialbd.ttf"
FI = "C:/Windows/Fonts/ariali.ttf"


def font(p, s):
    try:
        return ImageFont.truetype(p, s)
    except OSError:
        # hors Windows (les chemins ci-dessus sont Windows) : police PIL par defaut.
        # Les images synthetiques sont commitees -> pas besoin de regenerer ailleurs.
        try:
            return ImageFont.load_default(s)
        except TypeError:
            return ImageFont.load_default()


# Chaque cas exerce une branche de l'arbre : zone, chirurgie, referentiel, seances
# (autour des seuils DAP), domicile, bilan. `acte_match` = fragment du libelle qui
# identifie l'acte attendu dans la base (resolu en acte_id ci-dessous).
CAS = [
    {"f": "syn_01_ptg_genou.png", "medecin": "Dr Jean MOREAU", "ville": "Lyon", "date": "27/06/2026",
     "patient": "Mme Claire FONTAINE", "ne": "14/03/1968",
     "chirurgie": "oui", "seances": 30, "bilan": "oui", "domicile": "oui",
     "acte_match": "arthroplastie du genou",
     "corps": ["Reeducation du genou DROIT suite a la pose", "d'une prothese totale de genou (PTG)",
               "operee le 10/06/2026.", "", "- 30 seances de reeducation",
               "- Bilan diagnostic kinesitherapique initial", "- Soins a domicile (mobilite reduite)"]},

    {"f": "syn_02_lombalgie.png", "medecin": "Dr Sophie BERNARD", "ville": "Paris", "date": "20/06/2026",
     "patient": "M. Karim HADDAD", "ne": "02/11/1985",
     "chirurgie": "non", "seances": 10, "bilan": "oui", "domicile": "non",
     "acte_match": "Lombalgie commune",
     "corps": ["Reeducation dans le cadre d'une", "lombalgie commune non operee.", "",
               "- 10 seances de masso-kinesitherapie", "- Bilan diagnostic kinesitherapique"]},

    {"f": "syn_03_lca_genou.png", "medecin": "Dr Paul RENAUD", "ville": "Nantes", "date": "15/06/2026",
     "patient": "M. Lucas PETIT", "ne": "22/07/1997",
     "chirurgie": "oui", "seances": 40, "bilan": "oui", "domicile": "non",
     "acte_match": "ligament croise anterieur",
     "corps": ["Reeducation apres reconstruction du", "ligament croise anterieur (LCA) du", "genou gauche, operee le 01/06/2026.", "",
               "- 40 seances de reeducation", "- Bilan diagnostic kinesitherapique"]},

    {"f": "syn_04_coiffe_epaule.png", "medecin": "Dr Amelie GIRARD", "ville": "Lille", "date": "12/06/2026",
     "patient": "Mme Nadia CHERIF", "ne": "08/09/1972",
     "chirurgie": "oui", "seances": 50, "bilan": "oui", "domicile": "non",
     "acte_match": "coiffe des rotateurs",
     "corps": ["Reeducation apres reinsertion des", "tendons de la coiffe des rotateurs", "epaule droite, operee le 30/05/2026.", "",
               "- 50 seances", "- Bilan diagnostic kinesitherapique"]},

    {"f": "syn_05_entorse_cheville.png", "medecin": "Dr Marc LEROY", "ville": "Toulouse", "date": "25/06/2026",
     "patient": "M. Hugo MARTIN", "ne": "17/02/2001",
     "chirurgie": "non", "seances": 10, "bilan": "non", "domicile": "non",
     "acte_match": "entorse externe recente de cheville",
     "corps": ["Reeducation d'une entorse externe", "recente de la cheville droite,", "non operee.", "", "- 10 seances"]},

    {"f": "syn_06_cervicalgie.png", "medecin": "Dr Julie ROUSSEAU", "ville": "Bordeaux", "date": "18/06/2026",
     "patient": "Mme Sylvie DUBOIS", "ne": "03/05/1965",
     "chirurgie": "non", "seances": 15, "bilan": "oui", "domicile": "non",
     "acte_match": "cervicalgie",
     "corps": ["Reeducation d'une cervicalgie commune", "non specifique.", "",
               "- 15 seances de masso-kinesitherapie", "- Bilan diagnostic kinesitherapique"]},

    {"f": "syn_07_hemiplegie.png", "medecin": "Dr Olivier FABRE", "ville": "Strasbourg", "date": "10/06/2026",
     "patient": "M. Andre GARNIER", "ne": "29/12/1951",
     "chirurgie": "non", "seances": 50, "bilan": "oui", "domicile": "oui",
     "acte_match": "hemiplegie",
     "corps": ["Reeducation neurologique d'une", "hemiplegie droite suite a AVC.", "",
               "- 50 seances de reeducation", "- Bilan diagnostic neurologique", "- Soins a domicile"]},

    {"f": "syn_08_fracture_poignet.png", "medecin": "Dr Claire NOEL", "ville": "Rennes", "date": "22/06/2026",
     "patient": "Mme Emma LAMBERT", "ne": "11/04/1988",
     "chirurgie": "non", "seances": 25, "bilan": "oui", "domicile": "non",
     "acte_match": "extremite distale des deux os de l'avant-bras",
     "corps": ["Reeducation apres fracture de", "l'extremite distale des deux os de", "l'avant-bras gauche, non operee.", "",
               "- 25 seances", "- Bilan diagnostic kinesitherapique"]},

    {"f": "syn_09_incomplete.png", "medecin": "Dr Thomas MERCIER", "ville": "Dijon", "date": "24/06/2026",
     "patient": "M. Yanis BOUCHER", "ne": "06/08/1979",
     "chirurgie": "non", "seances": 0, "bilan": "non", "domicile": "non",
     "acte_match": "Lombalgie commune",
     "corps": ["Reeducation lombalgie.", "", "(nombre de seances non precise", " - ordonnance incomplete)"]},

    {"f": "syn_10_respiratoire.png", "medecin": "Dr Laure VIDAL", "ville": "Montpellier", "date": "19/06/2026",
     "patient": "Mme Alice ROBERT", "ne": "27/10/1960",
     "chirurgie": "non", "seances": 15, "bilan": "oui", "domicile": "oui",
     "acte_match": "respiratoire",
     "corps": ["Kinesitherapie respiratoire dans le", "cadre d'une BPCO.", "",
               "- 15 seances", "- Bilan diagnostic", "- Soins a domicile"]},
]


def resoudre_acte_id(fragment, chirurgie):
    """Index dans KB.actes de l'acte attendu.

    Un fragment de libelle peut matcher DEUX actes (variante operee / non operee,
    ex. 'coiffe des rotateurs' = tendinopathie non-op ET reinsertion op). On
    departage par le flag chirurgie du CAS -> sinon la verite terrain serait fausse
    (mauvais acte, mauvais seuil DAP). Bug attrape a l'audit du 2026-07-18.
    """
    frag = fragment.lower()
    veut_chir = (chirurgie == "oui")
    matches = [i for i, a in enumerate(KB["actes"]) if frag in a["libelle"].lower()]
    for i in matches:
        if KB["actes"][i]["chirurgie"] == veut_chir:
            return i
    return matches[0] if matches else ""  # aucun match chir -> 1er, ou "" (non resolu)


def dap_attendue(acte_id, seances):
    """oui/non selon le referentiel HAS de l'acte et le nb de seances prescrites."""
    if acte_id == "" or not seances:
        return ""
    a = KB["actes"][acte_id]
    for r in KB.get("referentiels", []):
        if r["match_libelle"] in a["libelle"].lower():
            return "oui" if seances >= r["dap_des_seance"] else "non"
    return "non"


def generer(nom, c, dossier):
    W, H = 1000, 1400
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    big, med, reg = font(FB, 30), font(FB, 22), font(F, 22)
    small, ital, hand = font(F, 18), font(FI, 22), font(FI, 26)

    d.rectangle([20, 20, W - 20, H - 20], outline="black", width=2)
    d.text((50, 50), c["medecin"], font=big, fill="black")
    d.text((50, 95), "Medecin Generaliste", font=reg, fill="black")
    d.text((50, 125), "12 rue des Lilas", font=small, fill="black")
    d.text((50, 150), "RPPS : 10101010101", font=small, fill="black")
    d.text((650, 95), f"{c['ville']}, le {c['date']}", font=reg, fill="black")
    d.line([50, 215, W - 50, 215], fill="black", width=1)
    d.text((50, 240), f"Patient : {c['patient']}", font=med, fill="black")
    d.text((50, 275), f"Ne(e) le : {c['ne']}", font=reg, fill="black")
    d.text((400, 330), "O R D O N N A N C E", font=big, fill="black")
    d.line([50, 385, W - 50, 385], fill="black", width=1)
    d.text((70, 430), "Prescription de masso-kinesitherapie :", font=reg, fill="black")

    y = 510
    for ligne in c["corps"]:
        d.text((70, y), ligne, font=hand, fill=(20, 20, 80))
        y += 48

    d.text((620, 1180), "Signature et cachet :", font=small, fill="black")
    d.text((650, 1230), c["medecin"], font=ital, fill=(20, 20, 80))
    d.line([640, 1290, 920, 1290], fill="gray", width=1)
    d.text((50, 1330), "DOCUMENT FICTIF - genere pour test logiciel - aucune valeur medicale.",
           font=small, fill="gray")
    img.save(dossier / nom)


def main():
    dossier = Path(sys.argv[1]) if len(sys.argv) > 1 else (ICI.parent / "benchmark" / "synthetiques")
    dossier.mkdir(parents=True, exist_ok=True)

    lignes_vt = []
    for c in CAS:
        generer(c["f"], c, dossier)
        aid = resoudre_acte_id(c["acte_match"], c["chirurgie"])
        lignes_vt.append([
            Path(c["f"]).stem, "tape", c["chirurgie"], c["seances"] or "",
            c["bilan"], c["domicile"], aid, dap_attendue(aid, c["seances"]),
            f"synthetique — {c['acte_match']}" + ("" if aid != "" else " [ACTE NON RESOLU]"),
        ])

    vt = dossier / "verite_terrain.csv"
    with open(vt, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["id", "type(manuscrit/tape)", "chirurgie(oui/non)", "nb_seances",
                    "bilan(oui/non)", "domicile(oui/non)", "acte_id_correct",
                    "dap_attendue(oui/non)", "commentaire"])
        w.writerows(lignes_vt)

    non_resolus = [l[0] for l in lignes_vt if l[6] == ""]
    print(f"OK  {len(CAS)} ordonnances synthetiques -> {dossier}")
    print(f"    verite terrain auto -> {vt.name}")
    if non_resolus:
        print(f"    /!\\ actes non resolus (verifier acte_match) : {', '.join(non_resolus)}")
    else:
        print("    tous les actes resolus dans la base.")
    print(f"\nBenchmark :  KINE_LLM_PROVIDER=... python benchmark/run_batch.py {dossier}")
    print(f"             python benchmark/score.py {dossier}")


if __name__ == "__main__":
    main()
