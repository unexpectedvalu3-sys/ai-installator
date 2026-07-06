#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Benchmark OCR — etape 2 : scoring.

Compare predictions.csv (OCR) a verite_terrain.csv (rempli par le kine) et
produit les metriques A-E du protocole, segmentees manuscrit/tape.

Usage :
    python score.py <dossier_images>
    (le dossier doit contenir predictions.csv et verite_terrain.csv)
"""

import csv
import sys
from pathlib import Path

SEP = ";"


def lire_csv(path):
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=SEP))


def to_bool(v):
    return str(v).strip().lower() in ("oui", "true", "1", "o", "vrai", "yes")


def to_int(v):
    s = "".join(c for c in str(v) if c.isdigit())
    return int(s) if s else None


def pct(n, d):
    return f"{100*n/d:.0f}%" if d else "n/a"


def main(dossier):
    base = Path(dossier)
    pred_f = base / "predictions.csv"
    vt_f = base / "verite_terrain.csv"
    if not pred_f.exists() or not vt_f.exists():
        print("Manque predictions.csv ou verite_terrain.csv dans", dossier)
        print("(remplir verite_terrain_modele.csv et l'enregistrer sous verite_terrain.csv)")
        return

    preds = {r["id"]: r for r in lire_csv(pred_f)}
    verites = lire_csv(vt_f)

    # Accumulateurs : par segment (tape / manuscrit / global)
    segments = ["tape", "manuscrit", "global"]
    stat = {s: {"n": 0, "chir_ok": 0, "chir_n": 0, "seances_ok": 0, "seances_n": 0,
                "bilan_ok": 0, "bilan_n": 0, "domicile_ok": 0, "domicile_n": 0,
                "top1": 0, "top3": 0, "top5": 0, "acte_n": 0,
                "dap_ok": 0, "dap_n": 0} for s in segments}
    conf = {"low": [0, 0], "medium": [0, 0], "high": [0, 0]}  # [erreurs, total]
    detail = []

    for vt in verites:
        ido = vt["id"]
        p = preds.get(ido)
        if not p or p.get("confiance") == "ERREUR":
            detail.append([ido, "PREDICTION MANQUANTE/ERREUR"])
            continue
        typ = "manuscrit" if "manus" in (vt.get("type(manuscrit/tape)", "").lower()) else "tape"
        segs = [typ, "global"]

        erreurs = []

        def champ(nom_vt, val_pred_bool, val_vt_str, key):
            """Compare un champ booleen ; alimente les stats des segments."""
            vt_raw = val_vt_str.strip()
            if vt_raw == "":
                return
            ok = (to_bool(val_pred_bool) == to_bool(vt_raw))
            for s in segs:
                stat[s][key + "_ok"] += ok
                stat[s][key + "_n"] += 1
            if not ok:
                erreurs.append(nom_vt)

        champ("chirurgie", p["chirurgie"], vt.get("chirurgie(oui/non)", ""), "chir")
        champ("bilan", p["bilan"], vt.get("bilan(oui/non)", ""), "bilan")
        champ("domicile", p["domicile"], vt.get("domicile(oui/non)", ""), "domicile")

        # nb seances (entier)
        vt_se = to_int(vt.get("nb_seances", ""))
        if vt_se is not None:
            ok = (to_int(p["nb_seances"]) == vt_se)
            for s in segs:
                stat[s]["seances_ok"] += ok
                stat[s]["seances_n"] += 1
            if not ok:
                erreurs.append("nb_seances")

        # acte top-K
        vt_acte = to_int(vt.get("acte_id_correct", ""))
        if vt_acte is not None:
            top = [to_int(x) for x in str(p["top5_acte_ids"]).split()]
            for s in segs:
                stat[s]["acte_n"] += 1
                if top[:1] == [vt_acte] or vt_acte in top[:1]:
                    stat[s]["top1"] += 1
                if vt_acte in top[:3]:
                    stat[s]["top3"] += 1
                if vt_acte in top[:5]:
                    stat[s]["top5"] += 1
            if vt_acte not in top[:3]:
                erreurs.append("acte_top3")

        # DAP
        vt_dap = vt.get("dap_attendue(oui/non)", "").strip()
        if vt_dap:
            ok = (str(p["dap_pred"]).strip().lower() == vt_dap.lower())
            for s in segs:
                stat[s]["dap_ok"] += ok
                stat[s]["dap_n"] += 1
            if not ok:
                erreurs.append("dap")

        for s in segs:
            stat[s]["n"] += 1

        # Calibration confiance
        c = p.get("confiance", "medium")
        if c in conf:
            conf[c][1] += 1
            if erreurs:
                conf[c][0] += 1

        detail.append([ido, typ, p["confiance"], "OK" if not erreurs else "KO: " + ",".join(erreurs)])

    # ---- Rapport console ----
    print("\n" + "=" * 60)
    print("  RAPPORT BENCHMARK OCR")
    print("=" * 60)
    g = stat["global"]
    print(f"  Echantillon : {g['n']} ordonnances "
          f"({stat['manuscrit']['n']} manuscrites, {stat['tape']['n']} tapees)")
    print("-" * 60)
    print(f"  {'Metrique':<26}{'tape':>10}{'manuscrit':>12}{'global':>10}")

    def ligne(label, key_ok, key_n):
        vals = "".join(f"{pct(stat[s][key_ok], stat[s][key_n]):>{12 if s=='manuscrit' else 10}}"
                       for s in ["tape", "manuscrit", "global"])
        print(f"  {label:<26}{vals}")

    print("  A. Champs critiques (exact)")
    ligne("   - chirurgie", "chir_ok", "chir_n")
    ligne("   - nb_seances", "seances_ok", "seances_n")
    ligne("   - bilan", "bilan_ok", "bilan_n")
    ligne("   - domicile", "domicile_ok", "domicile_n")
    print("  B. Bon acte dans...")
    ligne("   - top-1", "top1", "acte_n")
    ligne("   - top-3", "top3", "acte_n")
    ligne("   - top-5", "top5", "acte_n")
    print("  C. Alerte DAP")
    ligne("   - correcte", "dap_ok", "dap_n")
    print("-" * 60)
    print("  D. Calibration confiance (taux d'erreur) :")
    for c in ["high", "medium", "low"]:
        err, tot = conf[c]
        print(f"     confiance={c:<7} {err}/{tot} erreurs  ({pct(err, tot)})")
    print("=" * 60)

    # ---- CSV detail ----
    out = base / "rapport_benchmark.csv"
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=SEP)
        w.writerow(["id", "type", "confiance", "resultat"])
        w.writerows(detail)
    print(f"  Detail par ordonnance -> {out}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python score.py <dossier_images>")
        sys.exit(1)
    main(sys.argv[1])
