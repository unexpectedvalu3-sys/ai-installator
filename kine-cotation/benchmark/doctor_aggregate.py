#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Agrege les resultats GRIBOUILLIS MEDICAL (benchmark/doctor/*.csv) en un tableau.

    python benchmark/doctor_aggregate.py

Chaque <tag>.csv est produit par doctor_handwriting.py (idx;label;cer;exact;hyp).
Tous les runs parcourent le jeu dans le MEME ordre deterministe -> l'idx N designe
le meme mot d'un provider a l'autre. On produit :
  1. les stats de chaque run (CER + exactitude mot) ;
  2. un FACE-A-FACE sur les K premiers mots communs a tous.
"""
import csv
from pathlib import Path

DOCTOR = Path(__file__).resolve().parent / "doctor"


def _med(xs):
    s = sorted(xs)
    return s[len(s) // 2] if s else 0.0


def acc_split(recs):
    """recs = liste de (type, cer, exact). Rend exactitude mot / chiffre / global + CER med."""
    mots = [r for r in recs if r[0] == "mot"]
    chi = [r for r in recs if r[0] == "chiffre"]
    a = lambda rs: (sum(r[2] for r in rs) / len(rs)) if rs else 0.0
    return {"n": len(recs), "mot": a(mots), "nmot": len(mots), "chi": a(chi),
            "nchi": len(chi), "all": a(recs), "med": _med([r[1] for r in recs])}


def charger():
    runs = {}
    for f in sorted(DOCTOR.glob("*.csv")):
        rows = list(csv.DictReader(open(f, encoding="utf-8-sig"), delimiter=";"))
        runs[f.stem] = {int(r["idx"]): (r.get("type", "mot"), float(r["cer"]), int(r["exact"]))
                        for r in rows if r.get("cer")}
    return runs


def ligne(tag, s):
    return (f"  {tag:<40} MOTS {s['mot']:6.1%} ({s['nmot']})  "
            f"chiffres {s['chi']:5.1%} ({s['nchi']})  "
            f"global {s['all']:6.1%}  CERmed {s['med']:5.1%}")


def main():
    runs = charger()
    if not runs:
        print("Aucun resultat dans benchmark/doctor/ — lancer doctor_handwriting.py d'abord.")
        return

    print("=" * 96)
    print("  GRIBOUILLIS MEDICAL — mots manuscrits (ANGLAIS) : exactitude par run")
    print("  KPI = exactitude MOT (un nom de medicament est bon ou faux)")
    print("=" * 96)
    for tag, d in sorted(runs.items(), key=lambda kv: -acc_split(list(kv[1].values()))["mot"]):
        print(ligne(tag, acc_split(list(d.values()))))

    k = min(max(d) for d in runs.values())
    print("\n" + "=" * 96)
    print(f"  FACE-A-FACE sur les {k} premieres images COMMUNES (memes glyphes)")
    print("=" * 96)
    table = []
    for tag, d in runs.items():
        recs = [d[i] for i in range(1, k + 1) if i in d]
        if recs:
            table.append((-acc_split(recs)["mot"], tag, acc_split(recs)))
    for _, tag, s in sorted(table):
        print(ligne(tag, s))
    print("=" * 96)


if __name__ == "__main__":
    main()
