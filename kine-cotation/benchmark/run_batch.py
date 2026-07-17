#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Benchmark OCR — etape 1 : extraction batch.

Lance l'OCR sur toutes les ordonnances d'un dossier et produit :
  - predictions.csv         : ce que l'OCR a extrait
  - verite_terrain_modele.csv : gabarit a remplir par le kine (sa verite)
  - catalogue_actes.csv     : feuille de reference (id <-> acte) pour remplir la verite

Usage :
    python run_batch.py <dossier_images>

Provider : herite de prototype/llm.py (defaut Mistral FR/UE). La cle du provider
actif doit etre dans l'environnement — `python prototype/llm.py` pour verifier.
Comparer des providers a iso-pipeline :
    KINE_LLM_PROVIDER=mistral    python run_batch.py ordonnances   # voie A (baseline)
    KINE_LLM_PROVIDER=anthropic  python run_batch.py ordonnances   # reference qualite
    KINE_LLM_PROVIDER=selfhosted KINE_LLM_BASE_URL=... KINE_LLM_MODELE=Qwen/Qwen2.5-VL-7B-Instruct \
                                 python run_batch.py ordonnances   # voie B (OCR open souverain)
    # Voir 11_VOIE_B_OCR_OPEN.md pour la voie souveraine.

⚠️ Ordonnances ANONYMISEES uniquement (cf. 00_PROTOCOLE_BENCHMARK_OCR.md §0).
"""

import csv
import sys
from pathlib import Path

# Importer le moteur + l'OCR depuis ../prototype
PROTO = Path(__file__).resolve().parent.parent / "prototype"
sys.path.insert(0, str(PROTO))
import cotation_engine as ce      # noqa: E402
import ordonnance_ocr as ocr      # noqa: E402

IMG_EXT = {".png", ".jpg", ".jpeg", ".webp", ".pdf"}
SEP = ";"


def ecrire_csv(path, entetes, lignes):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=SEP)
        w.writerow(entetes)
        w.writerows(lignes)


def export_catalogue(kb, dossier):
    lignes = [[i, a["code"], a["coefficient"], a["tarif_metropole"], a["article"],
               "R" if a["referentiel"] else "", a["libelle"]]
              for i, a in enumerate(kb["actes"])]
    ecrire_csv(dossier / "catalogue_actes.csv",
               ["acte_id", "code", "coef", "tarif", "article", "ref", "libelle"], lignes)


def dap_predite(cands, ordo, kb):
    for a in cands[:5]:
        ref = ce.trouver_referentiel(a, kb)
        if ref:
            s = ordo.nb_seances_prescrites or None
            if s is None:
                return "?"
            return "oui" if s >= ref["dap_des_seance"] else "non"
    return "non"


def main(dossier):
    base = Path(dossier)
    if not base.is_dir():
        print(f"Dossier introuvable : {dossier}")
        return
    images = sorted(p for p in base.iterdir() if p.suffix.lower() in IMG_EXT)
    if not images:
        print(f"Aucune image ({'/'.join(IMG_EXT)}) dans {dossier}")
        return

    kb = ce.charger_kb()
    export_catalogue(kb, base)

    preds, ids = [], []
    for p in images:
        ido = p.stem
        ids.append(ido)
        try:
            ordo = ocr.lire_ordonnance(p)
            cands = ocr.proposer_actes(ordo, kb)
            top = [kb["actes"].index(a) for a in cands[:5]]
            preds.append([
                ido, p.name, ordo.confiance,
                ordo.zone, ordo.chirurgie, ordo.nb_seances_prescrites,
                ordo.mention_bilan, ordo.domicile, ordo.urgence,
                (ordo.pathologie_texte or "").replace("\n", " ")[:120],
                " ".join(str(t) for t in top),
                dap_predite(cands, ordo, kb), "",
            ])
            print(f"[OK]  {p.name:<22} conf={ordo.confiance:<6} top_actes={top}")
        except Exception as e:
            preds.append([ido, p.name, "ERREUR", "", "", "", "", "", "", "", "", "", str(e)[:120]])
            print(f"[ERR] {p.name}: {e}")

    ecrire_csv(base / "predictions.csv",
               ["id", "fichier", "confiance", "zone", "chirurgie", "nb_seances",
                "bilan", "domicile", "urgence", "pathologie", "top5_acte_ids",
                "dap_pred", "erreur"], preds)

    # Gabarit de verite terrain (le kine remplit les colonnes vides)
    gabarit = [[i, "", "", "", "", "", "", "", ""] for i in ids]
    ecrire_csv(base / "verite_terrain_modele.csv",
               ["id", "type(manuscrit/tape)", "chirurgie(oui/non)", "nb_seances",
                "bilan(oui/non)", "domicile(oui/non)", "acte_id_correct",
                "dap_attendue(oui/non)", "commentaire"], gabarit)

    print(f"\n{len(images)} ordonnance(s) traitee(s).")
    print("Fichiers ecrits :")
    print(f"  - {base/'predictions.csv'}")
    print(f"  - {base/'verite_terrain_modele.csv'}  (a remplir -> enregistrer en verite_terrain.csv)")
    print(f"  - {base/'catalogue_actes.csv'}         (reference pour acte_id_correct)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python run_batch.py <dossier_images>")
        sys.exit(1)
    main(sys.argv[1])
