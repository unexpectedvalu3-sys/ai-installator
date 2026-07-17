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
import re
import sys
from datetime import date, datetime
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


# --- Cotations datees ------------------------------------------------------
# La NGAP bouge par PALIERS : 01/01/2026, 28/05/2026 (avenant 8), 01/09/2026
# (+1 point sur 5 actes NMI neuro). Un acte peut donc porter "_paliers".
#
# La date qui fait foi est celle DE LA SEANCE, jamais "aujourd'hui" : une seance
# du 31/08 facturee le 05/09 se cote au bareme du 31/08. Et la justification doit
# attester le bareme en vigueur CE JOUR-LA.

class HorsPerimetreTemporel(ValueError):
    """Seance anterieure a l'historique de la base — on refuse plutot que de mentir."""


def _iso(d) -> str:
    """Normalise date | datetime | 'YYYY-MM-DD' -> 'YYYY-MM-DD' (comparable en str)."""
    if d is None:
        return date.today().isoformat()
    if isinstance(d, datetime):
        return d.date().isoformat()
    if isinstance(d, date):
        return d.isoformat()
    d = str(d).strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
        raise ValueError(f"Date attendue au format AAAA-MM-JJ, recu : {d!r}")
    return d


def verifier_date(kb, date_seance=None) -> str:
    """Refuse une date que la base ne sait pas coter.

    La base n'a PAS d'historique avant `applicable_depuis`. Coter une seance
    anterieure produirait un tarif faux — et la justification l'attesterait, ce qui
    est le pire echec possible pour un produit dont la promesse est la preuve.
    Mieux vaut ne rien rendre que rendre une preuve fausse.
    """
    d = _iso(date_seance)
    depuis = kb["_meta"].get("applicable_depuis")
    if depuis and d < depuis:
        raise HorsPerimetreTemporel(
            f"Seance du {d} : la base ne couvre les tarifs qu'a partir du {depuis} "
            f"({kb['_meta']['source']}). Coter cette seance donnerait un bareme faux. "
            "Se referer au tableau SNMKR en vigueur a cette date."
        )
    return d


def acte_a_la_date(acte, date_seance=None):
    """Rend (coefficient, tarif_metropole, palier_applique) a la date de la seance.

    Retient le DERNIER palier dont a_partir_du <= date. Sans palier applicable, les
    valeurs de premier niveau (valables depuis _meta.applicable_depuis) s'appliquent.
    """
    d = _iso(date_seance)
    coef, tar, palier = acte["coefficient"], acte["tarif_metropole"], None
    for p in sorted(acte.get("_paliers", []), key=lambda p: p["a_partir_du"]):
        if d >= p["a_partir_du"]:
            coef, tar, palier = p["coefficient"], p["tarif_metropole"], p
    return coef, tar, palier


def paliers_a_venir(kb, date_seance=None):
    """Paliers pas encore en vigueur — pour prevenir avant qu'ils tombent."""
    d = _iso(date_seance)
    out = []
    for a in kb["actes"]:
        for p in a.get("_paliers", []):
            if p["a_partir_du"] > d:
                out.append({"date": p["a_partir_du"], "code": a["code"], "libelle": a["libelle"],
                            "de": a["coefficient"], "vers": p["coefficient"]})
    return sorted(out, key=lambda x: (x["date"], x["code"]))


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
def ligne(acte, kb, drom=False, date_seance=None):
    """Ligne de facture cotee au bareme en vigueur A LA DATE DE LA SEANCE."""
    coef, _tarif_ref, palier = acte_a_la_date(acte, date_seance)
    return {
        "code": acte["code"],
        "coefficient": coef,
        "tarif": tarif(coef, kb, drom),
        "libelle": acte["libelle"],
        "article": acte.get("article", "-"),
        "referentiel": acte.get("referentiel", False),
        "chirurgie": acte.get("chirurgie", False),
        "palier": palier["a_partir_du"] if palier else None,
    }


def generer_facture(lignes, kb, patient="—", date_seance="—", drom=False, justif=True, alertes=None):
    total = round(sum(l["tarif"] for l in lignes), 2)
    out = []
    out.append("=" * 64)
    out.append("  FEUILLE DE SOINS — proposition de cotation (aide a la decision)")
    out.append("=" * 64)
    out.append(f"  Patient : {patient}      Date de seance : {date_seance}"
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
            palier = f" [palier du {l['palier']}]" if l.get("palier") else ""
            out.append(f"   - {l['code']} {l['coefficient']} (art. {l['article']}){palier} : "
                       f"{l['libelle']}.")
        out.append("   Pieces : ordonnance + BDK. Verifier coherence soins<->prescription.")
        # Une preuve qui ne dit pas SOUS QUEL BAREME elle a ete produite ne vaut rien :
        # le bareme a bouge 3 fois en 8 mois. Cf. 05_REPOSITIONNEMENT_PREUVE.md.
        m = kb["_meta"]
        out.append(f"   Bareme applique : {m['source']} | base v{m['version']} | "
                   f"lettre-cle {tarif(1, kb, drom):.2f}EUR | seance du {date_seance}")
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


def demander_date_seance(kb):
    """La date de la seance pilote le bareme -> elle n'est plus optionnelle."""
    defaut = date.today().isoformat()
    while True:
        saisie = input(f"\nDate de la seance [AAAA-MM-JJ, entree = {defaut}] > ").strip() or defaut
        try:
            return verifier_date(kb, saisie)
        except (HorsPerimetreTemporel, ValueError) as e:
            print(f"  {e}")


def interactif(kb):
    print("\n### KinéCotation — guide de cotation -> facture (proto v1) ###")
    drom = oui("Exercice en DROM-COM ?")
    patient = input("\nNom patient (option) > ").strip() or "—"
    date_seance = demander_date_seance(kb)
    for p in paliers_a_venir(kb, date_seance):
        print(f"  [i] {p['date']} : {p['code']} {p['de']} -> {p['vers']}  ({p['libelle'][:42]})")
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
        lignes.append(ligne(acte, kb, drom, date_seance))
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

    texte, _ = generer_facture(lignes, kb, patient, date_seance, drom, alertes=alertes)
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
