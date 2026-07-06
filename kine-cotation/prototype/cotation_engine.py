#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KinéCotation — moteur de cotation + facturation NGAP (prototype v1)

Catalogue officiel : SNMKR tableau NGAP v15a (tarifs au 01/01/2026, avenant 7).

Le coefficient depend de l'ACTE PRECIS (pas seulement de la lettre-cle) :
l'arbre filtre region -> chirurgie -> referentiel -> acte exact, puis sort la
ligne de facture (code + coefficient + tarif) + BDK + supplements + total.

AVERTISSEMENT : aide a la decision. Le kine reste seul responsable de sa
facturation. Verifier la version du tableau SNMKR/ameli en vigueur.

Usage :
    python cotation_engine.py            # mode interactif (guide -> facture)
    python cotation_engine.py --demo     # exemple de facture
    python cotation_engine.py --rechercher genou   # recherche d'actes
"""

import json
import sys
from pathlib import Path

KB_PATH = Path(__file__).resolve().parent.parent / "knowledge_base" / "ngap_kine.json"

REGIONS = {
    "1": ("rachis", "Rachis (lombalgie, cervicalgie, dorsal...)"),
    "2": ("membre_sup", "Membre superieur (epaule, coude, poignet, main)"),
    "3": ("membre_inf", "Membre inferieur (hanche, genou, cheville, pied)"),
    "4": ("multi_territoires", "Plusieurs membres / territoires"),
    "5": ("neuro_musculaire", "Neurologique / musculaire"),
    "6": ("rhumato_inflammatoire", "Rhumatisme inflammatoire"),
    "7": ("respiratoire", "Respiratoire"),
    "8": ("maxillo_orl", "Maxillo-faciale / ORL"),
    "9": ("vasculaire", "Vasculaire / lymphoedeme"),
    "10": ("abdo_perineo", "Abdominale / perineale"),
    "11": ("geriatrie", "Deambulation sujet age"),
    "12": ("amputation", "Amputation"),
    "13": ("brulures", "Brulures"),
    "14": ("palliatif", "Soins palliatifs"),
}


def charger_kb():
    with open(KB_PATH, encoding="utf-8") as f:
        return json.load(f)


def tarif(coefficient, kb, drom=False):
    valeur = kb["_meta"]["valeur_lettre_cle_eur"]["drom" if drom else "metropole"]
    return round(coefficient * valeur, 2)


# --- Selection d'actes -----------------------------------------------------
def actes_par_region(kb, region):
    return [a for a in kb["actes"] if a["region"] == region]


def filtrer(actes, chirurgie=None, referentiel=None):
    out = actes
    if chirurgie is not None:
        out = [a for a in out if a["chirurgie"] == chirurgie]
    if referentiel is not None:
        out = [a for a in out if a["referentiel"] == referentiel]
    return out


def rechercher(kb, motcle):
    m = motcle.lower()
    return [a for a in kb["actes"] if m in a["libelle"].lower()
            or m in a["code"].lower() or m in a["region"].lower()]


# --- Referentiel / DAP -----------------------------------------------------
def trouver_referentiel(acte, kb):
    lib = acte["libelle"].lower()
    for r in kb.get("referentiels", []):
        if r["match_libelle"] in lib:
            return r
    return None


def alerte_dap(ref, seance_num):
    """Retourne un message d'alerte si une DAP est requise pour cette seance."""
    seuil = ref["dap_des_seance"]
    base = (f"Referentiel HAS : {ref['situation']} -> pris en charge "
            f"{('1 a ' + str(ref['seances_avant_dap'])) if ref['seances_avant_dap'] else '0'} "
            f"seance(s), DAP a partir de la {seuil}e.")
    if ref["note"]:
        base += f" ({ref['note']})"
    if seance_num is not None and seance_num >= seuil:
        return "[!] DAP REQUISE — " + base + f" Or seance n°{seance_num}."
    if seance_num is not None and seance_num == seuil - 1:
        return "[i] Avant-derniere seance sans DAP — anticiper. " + base
    return "[i] " + base


# --- Deplacement -----------------------------------------------------------
def ligne_deplacement(kb, acte_article, drom=False, ik_km=0, terrain="plaine"):
    dep = kb["deplacements"]
    if str(acte_article) in dep["articles_IFS"]:
        montant, code, lib = dep["IFS_eur"], "IFS", "Indemnite forfaitaire de deplacement specifique"
    else:
        montant, code, lib = dep["IFD_eur"], "IFD", "Indemnite forfaitaire de deplacement"
    bareme = dep["IK_drom" if drom else "IK_metropole"]
    ik = round(ik_km * bareme.get(terrain, 0), 2)
    total = round(montant + ik, 2)
    detail = lib + (f" + IK {ik_km}km {terrain} ({ik}€)" if ik_km else "")
    return {"code": code, "coefficient": "-", "tarif": total, "libelle": detail,
            "article": "-", "referentiel": False, "chirurgie": False}


# --- Facturation -----------------------------------------------------------
def ligne(acte, kb, drom=False):
    return {
        "code": acte["code"],
        "coefficient": acte["coefficient"],
        "tarif": tarif(acte["coefficient"], kb, drom),
        "libelle": acte["libelle"],
        "article": acte.get("article", "-"),
        "referentiel": acte.get("referentiel", False),
        "chirurgie": acte.get("chirurgie", False),
    }


def generer_facture(lignes, kb, patient="—", date="—", drom=False, justif=True, alertes=None):
    total = round(sum(l["tarif"] for l in lignes), 2)
    out = []
    out.append("=" * 64)
    out.append("  FEUILLE DE SOINS — proposition de cotation (aide a la decision)")
    out.append("=" * 64)
    out.append(f"  Patient : {patient}      Date : {date}"
               + ("      [DROM-COM]" if drom else ""))
    out.append("-" * 64)
    out.append(f"  {'Code':<6}{'Coef':>6}{'Tarif':>9}   Acte")
    out.append("-" * 64)
    for l in lignes:
        flags = ("R" if l["referentiel"] else " ") + ("C" if l["chirurgie"] else " ")
        out.append(f"  {l['code']:<6}{l['coefficient']:>6}{l['tarif']:>8.2f}€ {flags} "
                   f"{l['libelle'][:40]}")
    out.append("-" * 64)
    out.append(f"  {'TOTAL':<6}{'':>6}{total:>8.2f}€")
    out.append("=" * 64)
    if alertes:
        out.append("  ALERTES SEANCES / ACCORD PREALABLE :")
        for a in alertes:
            out.append("   " + a)
        out.append("-" * 64)
    if justif:
        out.append("  JUSTIFICATION (a conserver - anti-indu) :")
        for l in lignes:
            out.append(f"   - {l['code']} {l['coefficient']} (art. {l['article']}) : "
                       f"{l['libelle']}.")
        out.append("   Pieces : ordonnance + BDK. Verifier coherence soins<->prescription.")
    out.append("  /!\\ Aide a la decision — le kine valide et reste responsable.")
    out.append("=" * 64)
    return "\n".join(out), total


# --- Mode interactif -------------------------------------------------------
def choisir(prompt, items, labelf):
    print("\n" + prompt)
    for i, it in enumerate(items, 1):
        print(f"  [{i}] {labelf(it)}")
    while True:
        r = input("> ").strip()
        if r.isdigit() and 1 <= int(r) <= len(items):
            return items[int(r) - 1]
        print("  Choix invalide.")


def oui(prompt):
    return input(f"\n{prompt} [o/n] > ").strip().lower().startswith("o")


def interactif(kb):
    print("\n### KinéCotation — guide de cotation -> facture (proto v1) ###")
    drom = oui("Exercice en DROM-COM ?")
    patient = input("\nNom patient (option) > ").strip() or "—"
    date = input("Date de seance (option) > ").strip() or "—"
    lignes = []
    alertes = []

    while True:
        items = list(REGIONS.values())
        choix = choisir("Region / type d'affection traite ?", items, lambda x: x[1])
        region = choix[0]
        actes = actes_par_region(kb, region)

        # Affinage chirurgie / referentiel si pertinent
        if any(a["chirurgie"] for a in actes) and any(not a["chirurgie"] for a in actes):
            chir = oui("Acte post-chirurgical (operee) ?")
            actes = filtrer(actes, chirurgie=chir)
        if any(a["referentiel"] for a in actes) and any(not a["referentiel"] for a in actes):
            ref = oui("Pathologie inscrite au REFERENTIEL ?")
            actes = filtrer(actes, referentiel=ref)

        if not actes:
            print("  Aucun acte ne correspond a ces filtres.")
            continue

        acte = choisir("Acte precis realise ?", actes,
                       lambda a: f"{a['code']} {a['coefficient']} ({a['tarif_metropole']}€) "
                                 f"- {a['libelle']}")
        lignes.append(ligne(acte, kb, drom))
        print(f"  + Ajoute : {acte['code']} {acte['coefficient']}")

        # Referentiel / DAP
        ref = trouver_referentiel(acte, kb)
        if ref:
            rep = input("\n  Cet acte releve d'un referentiel HAS. "
                        "N° de la seance dans la serie (Entree=ignorer) > ").strip()
            num = int(rep) if rep.isdigit() else None
            alertes.append(alerte_dap(ref, num))
            print("  " + alertes[-1])

        # Supplements
        if oui("Ajouter un supplement (balneo / bandage) ?"):
            sup = choisir("Supplement ?", kb["supplements"],
                          lambda s: f"{s['code']} {s['coefficient']} ({s['tarif_metropole']}€) - {s['libelle']}")
            lignes.append(ligne(sup, kb, drom))

        if not oui("Ajouter un autre acte a cette facture ?"):
            break

    # BDK
    if oui("Facturer un BILAN (BDK) ?"):
        bdk = choisir("Type de bilan ?", kb["bilans"],
                      lambda b: f"{b['code']} {b['coefficient']} ({b['tarif_metropole']}€) - {b['libelle']}")
        lignes.append(ligne(bdk, kb, drom))

    # Deplacement domicile
    if oui("Seance a domicile (deplacement) ?"):
        art = lignes[0]["article"] if lignes else "-"
        km = input("  Distance facturable en km (Entree=0) > ").strip()
        km = int(km) if km.isdigit() else 0
        terrain = "plaine"
        if km:
            t = input("  Terrain [1=plaine 2=montagne 3=pied/ski] > ").strip()
            terrain = {"2": "montagne", "3": "pied_ski"}.get(t, "plaine")
        lignes.append(ligne_deplacement(kb, art, drom, km, terrain))

    texte, _ = generer_facture(lignes, kb, patient, date, drom, alertes=alertes)
    print("\n" + texte)


# --- Demo / recherche ------------------------------------------------------
def demo(kb):
    # Cas : reprise post-prothese de genou (referentiel HAS), 26e seance -> DAP,
    # a domicile (15 km plaine) + bilan
    a_genou = next(a for a in kb["actes"] if "arthroplastie du genou" in a["libelle"])
    bdk = kb["bilans"][0]
    ref = trouver_referentiel(a_genou, kb)
    seance_num = 26  # depasse le seuil PTG (DAP des la 26e)
    alertes = [alerte_dap(ref, seance_num)]
    lignes = [
        ligne(a_genou, kb),
        ligne(bdk, kb),
        ligne_deplacement(kb, a_genou["article"], drom=False, ik_km=15, terrain="plaine"),
    ]
    texte, total = generer_facture(lignes, kb, patient="DUPONT Marie",
                                   date="27/06/2026", alertes=alertes)
    print("\n" + texte)
    print(f"\n[demo] total facture = {total}€ (PTG seance n°{seance_num})")


def cmd_rechercher(kb, motcle):
    res = rechercher(kb, motcle)
    print(f"\n{len(res)} acte(s) pour '{motcle}' :")
    for a in res:
        print(f"  {a['code']:<5}{a['coefficient']:>6}  {a['tarif_metropole']:>6.2f}€  "
              f"(art.{a['article']})  {a['libelle']}")


if __name__ == "__main__":
    kb = charger_kb()
    if "--demo" in sys.argv:
        demo(kb)
    elif "--rechercher" in sys.argv:
        i = sys.argv.index("--rechercher")
        cmd_rechercher(kb, sys.argv[i + 1] if i + 1 < len(sys.argv) else "")
    else:
        interactif(kb)
