#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mini-backend KineCotation : sert l'app web + endpoint OCR ordonnance.

Le HTML reste utilisable seul (arbre de decision). Servi par ce backend, le
bouton "Importer une ordonnance" appelle /api/ocr (cle API cote serveur).

    set ANTHROPIC_API_KEY=sk-ant-...
    python server.py            # http://localhost:8770

Pre-requis : pip install flask anthropic pydantic
"""

import sys
import tempfile
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parent / "prototype"))
import cotation_engine as ce      # noqa: E402
import ordonnance_ocr as ocr      # noqa: E402

app = Flask(__name__)
KB = ce.charger_kb()
EXT_OK = {".png", ".jpg", ".jpeg", ".webp", ".pdf"}


@app.route("/")
def index():
    return send_from_directory(ICI, "kinecotation.html")


@app.route("/api/ocr", methods=["POST"])
def api_ocr():
    f = request.files.get("ordonnance")
    if not f or not f.filename:
        return jsonify(error="aucun fichier"), 400
    ext = Path(f.filename).suffix.lower()
    if ext not in EXT_OK:
        return jsonify(error=f"format non supporte ({ext})"), 400

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        f.save(tmp.name)
        chemin = Path(tmp.name)
    try:
        ordo = ocr.lire_ordonnance(chemin)
        cands = ocr.proposer_actes(ordo, KB)[:6]
        candidats = []
        for a in cands:
            ref = ce.trouver_referentiel(a, KB)
            candidats.append({
                "index": KB["actes"].index(a),
                "code": a["code"], "coefficient": a["coefficient"],
                "libelle": a["libelle"], "article": a["article"],
                "referentiel": a["referentiel"],
                "ref_situation": ref["situation"] if ref else None,
            })
        return jsonify(extraction=ordo.model_dump(), candidats=candidats)
    except Exception as e:
        return jsonify(error=str(e)), 500
    finally:
        try:
            chemin.unlink()
        except OSError:
            pass


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8770, debug=False)
