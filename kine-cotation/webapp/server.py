#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend KineCotation : sert l'app web (login-gardee) + endpoint OCR ordonnance.

Deux modes d'usage :
  - kinecotation.html ouvert DIRECTEMENT (file://) : cotation / DAP / dossier de
    preuve marchent hors-ligne, sans login, sans OCR. Rien ne sort du poste.
  - servi par ce backend : login (auth.py) + OCR (/api/ocr). La cle Mistral vit
    cote serveur, jamais dans le navigateur.

    python set_password.py       # 1x : cree le compte du kine (il tape son mdp)
    python server.py             # http://127.0.0.1:8770

Pre-requis : pip install -r ../requirements.txt  (flask, itsdangerous, mistralai...)
Config : webapp/.env (voir .env.example) — jamais commite.
"""

import os
import sys
import tempfile
from pathlib import Path

# charge webapp/.env AVANT d'importer auth (qui lit les variables au chargement)
ICI = Path(__file__).resolve().parent
try:
    from dotenv import load_dotenv
    load_dotenv(ICI / ".env")
except ImportError:
    pass  # dotenv optionnel : en prod les variables sont dans l'environnement

from flask import Flask, jsonify, request, send_from_directory, redirect, make_response

sys.path.insert(0, str(ICI.parent / "prototype"))
import cotation_engine as ce      # noqa: E402
import ordonnance_ocr as ocr      # noqa: E402
import auth                        # noqa: E402

app = Flask(__name__)
KB = ce.charger_kb()
EXT_OK = {".png", ".jpg", ".jpeg", ".webp", ".pdf"}
PUBLIC = {"/login", "/logout", "/healthz"}


# ------------------------------------------------------------------ page login
def _page_login(erreur=""):
    err = f'<p class="err">{erreur}</p>' if erreur else ""
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>KinéCotation — connexion</title><style>
:root{{--paper:#F2F5F4;--card:#FBFCFC;--ink:#0E1C19;--ink-soft:rgba(14,28,25,.6);
  --line:rgba(14,28,25,.28);--accent:#0B6E5F;--accent-deep:#084F44;--danger:#96261B}}
*{{box-sizing:border-box}}
body{{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
  background:var(--paper);color:var(--ink);
  font-family:-apple-system,Segoe UI,Roboto,sans-serif}}
.box{{width:340px;max-width:92vw;background:var(--card);border:1px solid var(--line);
  border-radius:12px;padding:32px}}
h1{{font-size:18px;margin:0 0 4px}}
.sub{{color:var(--ink-soft);font-size:13px;margin:0 0 22px}}
label{{display:block;font-size:12.5px;color:var(--ink-soft);margin:14px 0 5px}}
input{{width:100%;padding:10px 12px;border:1px solid var(--line);border-radius:7px;
  font-size:14px;background:#fff}}
input:focus{{outline:0;border-color:var(--accent);box-shadow:0 0 0 3px rgba(11,110,95,.1)}}
button{{width:100%;margin-top:22px;padding:11px;border:0;border-radius:7px;
  background:var(--accent);color:#fff;font-size:14px;font-weight:600;cursor:pointer}}
button:hover{{background:var(--accent-deep)}}
.err{{background:#FBEDEB;color:var(--danger);border:1px solid rgba(150,38,27,.3);
  border-radius:7px;padding:9px 11px;font-size:12.5px;margin:0 0 8px}}
.foot{{color:var(--ink-soft);font-size:11px;margin-top:18px;line-height:1.5}}
</style></head><body>
<form class="box" method="post" action="/login">
  <h1>KinéCotation</h1>
  <p class="sub">cote au juste tarif, avec la preuve derrière</p>
  {err}
  <label for="u">Identifiant</label>
  <input id="u" name="user" type="email" autocomplete="username" autofocus required>
  <label for="p">Mot de passe</label>
  <input id="p" name="password" type="password" autocomplete="current-password" required>
  <button type="submit">Se connecter</button>
  <p class="foot">Aide à la décision — le praticien valide et reste responsable.
  Données de cotation stockées localement sur ce poste.</p>
</form></body></html>"""


# ---------------------------------------------------------------- middleware
@app.before_request
def _garde():
    if request.path in PUBLIC or request.path.startswith("/static/"):
        return None
    if not auth.configured():
        # fail-closed : pas de config -> on ne sert RIEN (jamais l'app en clair)
        return jsonify(error="auth non configurée — lancer set_password.py"), 503
    token = request.cookies.get(auth.COOKIE_NAME)
    if token and auth.read_session_token(token):
        return None
    if request.path.startswith("/api/"):
        return jsonify(error="Non authentifié"), 401
    return redirect("/login", code=303)


@app.route("/healthz")
def healthz():
    return jsonify(status="ok", auth_configured=auth.configured())


@app.route("/login", methods=["GET", "POST"])
def login():
    token = request.cookies.get(auth.COOKIE_NAME)
    if token and auth.read_session_token(token):
        return redirect("/", code=303)
    if request.method == "GET":
        return _page_login()
    user = (request.form.get("user") or "").strip()
    pwd = request.form.get("password") or ""
    if not auth.check_credentials(user, pwd):
        return _page_login("Identifiant ou mot de passe incorrect."), 401
    resp = make_response(redirect("/", code=303))
    resp.set_cookie(auth.COOKIE_NAME, auth.make_session_token(user),
                    max_age=auth.SESSION_MAX_AGE, httponly=True,
                    secure=auth.COOKIE_SECURE, samesite="Lax")
    return resp


@app.route("/logout")
def logout():
    resp = make_response(redirect("/login", code=303))
    resp.delete_cookie(auth.COOKIE_NAME)
    return resp


# ---------------------------------------------------------------- app + OCR
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
    if not auth.configured():
        print("[!] Auth non configurée. Lance d'abord :  python set_password.py")
    app.run(host="127.0.0.1", port=8770, debug=False)
