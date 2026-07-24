#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Agrege les resultats RIMES (benchmark/rimes/*.csv) en un tableau comparatif.

    python benchmark/rimes_aggregate.py

Chaque <tag>.csv est produit par rimes_handwriting.py (colonnes idx;cer;ref;hyp).
Tous les runs parcourent RIMES test dans le MEME ordre deterministe -> l'idx N
designe la meme ligne d'un provider a l'autre. On produit donc :
  1. les stats completes de chaque run (sur son propre N) ;
  2. un FACE-A-FACE sur les K premieres lignes communes a tous (comparaison juste).
"""
import csv
from pathlib import Path

RIMES = Path(__file__).resolve().parent / "rimes"


def stats(cers):
    srt = sorted(cers)
    moy = sum(cers) / len(cers)
    p = lambda q: srt[min(len(srt) - 1, int(q * len(srt)))]
    return {"n": len(cers), "moy": moy, "med": p(0.5), "p90": p(0.9), "max": srt[-1],
            "u5": sum(c < .05 for c in cers) / len(cers),
            "u10": sum(c < .10 for c in cers) / len(cers)}


def charger():
    runs = {}
    for f in sorted(RIMES.glob("*.csv")):
        rows = list(csv.DictReader(open(f, encoding="utf-8-sig"), delimiter=";"))
        runs[f.stem] = {int(r["idx"]): float(r["cer"]) for r in rows if r.get("cer")}
    return runs


def ligne(tag, s):
    return (f"  {tag:<38} n={s['n']:>3}  moy {s['moy']:6.2%}  med {s['med']:6.2%}  "
            f"p90 {s['p90']:6.2%}  <5% {s['u5']:5.0%}  <10% {s['u10']:5.0%}")


def main():
    runs = charger()
    if not runs:
        print("Aucun resultat dans benchmark/rimes/ — lancer rimes_handwriting.py d'abord.")
        return

    print("=" * 92)
    print("  RIMES — transcription manuscrit FR : stats completes (chaque run sur son N)")
    print("=" * 92)
    for tag, d in sorted(runs.items(), key=lambda kv: stats(list(kv[1].values()))["moy"]):
        print(ligne(tag, stats(list(d.values()))))

    k = min(max(d) for d in runs.values())
    print("\n" + "=" * 92)
    print(f"  FACE-A-FACE sur les {k} premieres lignes COMMUNES (memes images)")
    print("=" * 92)
    table = []
    for tag, d in runs.items():
        cers = [d[i] for i in range(1, k + 1) if i in d]
        if cers:
            table.append((stats(cers)["moy"], tag, stats(cers)))
    for _, tag, s in sorted(table):
        print(ligne(tag, s))
    print("=" * 92)


if __name__ == "__main__":
    main()
