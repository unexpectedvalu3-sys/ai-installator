# -*- coding: utf-8 -*-
"""Comparateur Courtier — comparateur mutuelle + fiche DDA (devoir de conseil).

Version allégée, dérivée de Modul'R : on ne garde QUE le comparateur de garanties
et la fiche DDA (toute la partie extraction de dossiers / export CSV Modul'R est
retirée). Destiné à un hébergement web, UN déploiement par courtier, protégé par
un login (formulaire + session — voir auth.py).

Routes :
  /            accueil (les deux outils)
  /login       formulaire de connexion  ·  /logout
  /comparateur + /comparer + /comparateur/export-xlsx
  /fiche-dda   + /cabinet (GET/POST) + /fiche-dda/conseil
  /sessions/*  sessions de travail nommées (comparateur / fiche_dda)
  /healthz     sonde de disponibilité (publique)
"""
import os
import json
import threading
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response, RedirectResponse
from fastapi.staticfiles import StaticFiles

import auth
import compare
import fichedda
import sessions_store

BASE = Path(__file__).parent
DATA = Path(os.environ.get("DATA_DIR", BASE / "data"))   # runtime — volume persistant en prod
DATA.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Comparateur Courtier")

# Chemins publics (accessibles sans session). Tout le reste exige une session.
# /static/* est public : l'icône (mascotte.png) doit s'afficher sur la page de login.
PUBLIC_PATHS = {"/login", "/logout", "/healthz"}
PUBLIC_PREFIXES = ("/static/",)


@app.middleware("http")
async def require_session(request: Request, call_next):
    path = request.url.path
    # Fail-closed : sans configuration d'auth complète, rien n'est servi.
    if not auth.configured():
        if path == "/healthz":
            return JSONResponse({"status": "auth_not_configured"}, status_code=503)
        return HTMLResponse(
            "<h1>Configuration incomplète</h1><p>APP_USER, APP_PASSWORD_HASH et "
            "SECRET_KEY doivent être définis (voir set_password.py).</p>",
            status_code=503)
    if path in PUBLIC_PATHS or any(path.startswith(p) for p in PUBLIC_PREFIXES):
        return await call_next(request)
    token = request.cookies.get(auth.COOKIE_NAME)
    if token and auth.read_session_token(token):
        return await call_next(request)
    # Non authentifié : les appels d'API répondent 401, la navigation redirige.
    accept = request.headers.get("accept", "")
    if request.method != "GET" or "text/html" not in accept:
        return JSONResponse({"error": "Non authentifié"}, status_code=401)
    return RedirectResponse("/login", status_code=303)


app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")


# ---------------------------------------------------------------- Auth (login)
def _render_login(error=""):
    html = (BASE / "static" / "login.html").read_text(encoding="utf-8")
    block = f'<div class="err">{error}</div>' if error else ""
    return html.replace("__ERROR__", block, 1)


@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    # Déjà connecté -> accueil
    token = request.cookies.get(auth.COOKIE_NAME)
    if token and auth.read_session_token(token):
        return RedirectResponse("/", status_code=303)
    return _render_login()


@app.post("/login")
async def login_submit(request: Request):
    form = await request.form()
    user = (form.get("user") or "").strip()
    password = form.get("password") or ""
    if not auth.check_credentials(user, password):
        return HTMLResponse(_render_login("Identifiant ou mot de passe incorrect."),
                            status_code=401)
    resp = RedirectResponse("/", status_code=303)
    resp.set_cookie(
        auth.COOKIE_NAME, auth.make_session_token(user),
        max_age=auth.SESSION_MAX_AGE, httponly=True,
        samesite="lax", secure=auth.COOKIE_SECURE, path="/")
    return resp


@app.get("/logout")
def logout():
    resp = RedirectResponse("/login", status_code=303)
    resp.delete_cookie(auth.COOKIE_NAME, path="/")
    return resp


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


# ---------------------------------------------------------------- Mise à jour
@app.get("/update")
def update_check():
    """Vérifie GitHub Releases pour une nouvelle version de l'exe.
    Renvoie JSON {update_available, tag, url} ou {error}."""
    import urllib.request, urllib.error, json, os, sys
    repo = "unexpectedvalu3-sys/ai-installator"
    asset_name = "ComparateurCourtier.exe"
    try:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{repo}/releases/latest",
            headers={"User-Agent": "ComparateurCourtier"})
        with urllib.request.urlopen(req, timeout=15) as r:
            release = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"update_available": False, "tag": "", "url": ""}
        return JSONResponse({"error": f"Impossible de vérifier : {e}"}, status_code=502)
    except Exception as e:
        return JSONResponse({"error": f"Impossible de vérifier : {e}"}, status_code=502)
    tag = release.get("tag_name", "")
    asset_url = None
    for a in release.get("assets", []):
        if a.get("name", "").lower() == asset_name.lower():
            asset_url = a["browser_download_url"]
            break
    if not tag or not asset_url:
        return {"update_available": False, "tag": tag or "", "url": ""}
    # compare la version courante (embarquée) avec le tag de la release,
    # numériquement (une comparaison de chaînes casserait à 1.0.10 vs 1.0.3).
    try:
        import embedded_config as _cfg
        current = _cfg.APP_VERSION
    except Exception:
        current = "0"

    def _ver(s):
        out = []
        for p in str(s or "0").lstrip("vV").split("."):
            try:
                out.append(int(p))
            except ValueError:
                out.append(0)
        return tuple(out)

    if _ver(tag) <= _ver(current):
        return {"update_available": False, "tag": tag, "url": "", "current": current}
    return {"update_available": True, "tag": tag, "url": asset_url,
            "current": current,
            "notes": (release.get("body") or "")[:500]}


# --- État partagé du téléchargement de MAJ (pour la barre de progression) ---
_UPDATE = {"state": "idle", "pct": 0, "downloaded": 0, "total": 0, "tag": "", "error": ""}
_UPDATE_LOCK = threading.Lock()
_UPDATE_REPO = "unexpectedvalu3-sys/ai-installator"
_UPDATE_ASSET = "ComparateurCourtier.exe"


def _latest_asset_url():
    """Renvoie (tag, asset_url) de la dernière release ; asset_url None si absent."""
    import urllib.request
    req = urllib.request.Request(
        f"https://api.github.com/repos/{_UPDATE_REPO}/releases/latest",
        headers={"User-Agent": "ComparateurCourtier"})
    with urllib.request.urlopen(req, timeout=15) as r:
        release = json.loads(r.read().decode())
    tag = release.get("tag_name", "")
    for a in release.get("assets", []):
        if a.get("name", "").lower() == _UPDATE_ASSET.lower():
            return tag, a["browser_download_url"]
    return tag, None


def _do_update(asset_url, tag):
    """Télécharge le nouvel exe EN STREAMING (met à jour _UPDATE['pct']), remplace
    l'exe en cours, puis relance le nouvel exe DÉTACHÉ — le mode détaché évite que
    l'enfant hérite d'un handle sur le dossier temp _MEI (cause du warning au
    redémarrage). Tourne dans un thread."""
    import urllib.request, sys, subprocess, time
    try:
        req = urllib.request.Request(asset_url, headers={"User-Agent": "ComparateurCourtier"})
        with urllib.request.urlopen(req, timeout=600) as r:
            total = int(r.headers.get("Content-Length") or 0)
            buf = bytearray()
            got = 0
            with _UPDATE_LOCK:
                _UPDATE.update(state="downloading", pct=0, downloaded=0, total=total, tag=tag, error="")
            while True:
                chunk = r.read(262144)          # 256 Ko
                if not chunk:
                    break
                buf += chunk
                got += len(chunk)
                if total:
                    with _UPDATE_LOCK:
                        _UPDATE["pct"] = int(got * 100 / total)
                        _UPDATE["downloaded"] = got
            data = bytes(buf)
    except Exception as e:
        with _UPDATE_LOCK:
            _UPDATE.update(state="error", error=f"Téléchargement : {e}")
        return
    # remplace l'exe (rename trick Windows)
    exe = Path(sys.executable) if getattr(sys, "frozen", False) else Path(sys.argv[0]).resolve()
    tmp = exe.with_suffix(".exe.new")
    old = exe.with_suffix(".exe.old")
    try:
        tmp.write_bytes(data)
        if old.exists():
            old.unlink()
        exe.rename(old)
        tmp.rename(exe)
    except Exception as e:
        with _UPDATE_LOCK:
            _UPDATE.update(state="error", error=f"Remplacement : {e}")
        return
    with _UPDATE_LOCK:
        _UPDATE.update(state="restarting", pct=100)
    time.sleep(1.5)   # laisse le navigateur afficher 100 % avant la coupure
    flags = 0
    for name in ("DETACHED_PROCESS", "CREATE_NEW_PROCESS_GROUP", "CREATE_NO_WINDOW"):
        flags |= getattr(subprocess, name, 0)
    try:
        subprocess.Popen([str(exe)], cwd=str(exe.parent), close_fds=True, creationflags=flags)
    except Exception:
        subprocess.Popen([str(exe)], cwd=str(exe.parent))
    os._exit(0)


@app.get("/update/progress")
def update_progress():
    with _UPDATE_LOCK:
        return dict(_UPDATE)


@app.post("/update")
async def update_apply():
    """Démarre le téléchargement de la MAJ en arrière-plan et rend la main tout de
    suite : le navigateur suit l'avancement via GET /update/progress."""
    with _UPDATE_LOCK:
        if _UPDATE["state"] in ("downloading", "restarting"):
            return {"started": True, "state": _UPDATE["state"]}
    try:
        tag, asset_url = _latest_asset_url()
    except Exception as e:
        return JSONResponse({"error": f"Impossible de vérifier : {e}"}, status_code=502)
    if not asset_url:
        return JSONResponse({"error": "Aucune mise à jour disponible."}, status_code=404)
    with _UPDATE_LOCK:
        _UPDATE.update(state="downloading", pct=0, downloaded=0, total=0, tag=tag, error="")
    threading.Thread(target=_do_update, args=(asset_url, tag), daemon=True).start()
    return {"started": True, "tag": tag}


# ---------------------------------------------------------------- Accueil
@app.get("/", response_class=HTMLResponse)
def index():
    return (BASE / "static" / "index.html").read_text(encoding="utf-8")


# ---------------------------------------------------------------- Comparateur
@app.get("/comparateur", response_class=HTMLResponse)
def comparateur():
    return (BASE / "static" / "comparateur.html").read_text(encoding="utf-8")


@app.post("/comparer")
async def comparer(files: list[UploadFile] = File(...)):
    payload = [(f.filename, await f.read()) for f in files]
    try:
        return compare.compare(payload)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=502)


@app.post("/comparateur/export-xlsx")
async def comparateur_export_xlsx(req: Request):
    """Télécharge le tableau comparatif en Excel (colonne recommandée surlignée).
    Reçoit le JSON de comparaison déjà affiché (pas de nouvel appel IA)."""
    try:
        raw = await req.body()
        data = json.loads(raw.decode("utf-8", errors="replace"))
    except Exception as e:
        return JSONResponse({"error": f"Requête invalide : {e}"}, status_code=400)
    try:
        blob = compare.build_xlsx(data)
    except Exception as e:
        return JSONResponse({"error": f"Export Excel impossible : {e}"}, status_code=500)
    return Response(blob, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": 'attachment; filename="comparatif_mutuelle.xlsx"'})


# ---------------------------------------------------------------- Fiche DDA
@app.get("/fiche-dda", response_class=HTMLResponse)
def fiche_dda():
    return (BASE / "static" / "fiche-dda.html").read_text(encoding="utf-8")


@app.get("/cabinet")
def cabinet_get():
    return fichedda.load_cabinet()


@app.post("/cabinet")
async def cabinet_post(req: Request):
    return fichedda.save_cabinet(await req.json())


@app.post("/fiche-dda/conseil")
async def fiche_dda_conseil(req: Request):
    try:
        raw = await req.body()
        b = json.loads(raw.decode("utf-8", errors="replace"))
        return {"texte": fichedda.rediger_conseil(b.get("besoins", ""), b.get("reco", ""), b.get("ecartes", ""))}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=502)


# ---------------------------------------------------------------- Sessions nommées
SESSION_KINDS = {"comparateur", "fiche_dda"}


@app.get("/sessions/{kind}")
def sessions_list(kind: str):
    if kind not in SESSION_KINDS:
        return JSONResponse({"error": "kind invalide"}, status_code=400)
    return {"sessions": sessions_store.list_sessions(kind)}


@app.post("/sessions/{kind}")
async def sessions_save(kind: str, req: Request):
    if kind not in SESSION_KINDS:
        return JSONResponse({"error": "kind invalide"}, status_code=400)
    b = await req.json()
    nom = (b.get("nom") or "").strip() or "Sans nom"
    sid = sessions_store.save_session(kind, b.get("id"), nom, b.get("data") or {})
    return {"id": sid}


@app.get("/sessions/{kind}/{sid}")
def sessions_get(kind: str, sid: str):
    if kind not in SESSION_KINDS:
        return JSONResponse({"error": "kind invalide"}, status_code=400)
    it = sessions_store.get_session(kind, sid)
    if not it:
        return JSONResponse({"error": "session introuvable"}, status_code=404)
    return it


@app.post("/sessions/{kind}/{sid}/supprimer")
def sessions_delete(kind: str, sid: str):
    if kind not in SESSION_KINDS:
        return JSONResponse({"error": "kind invalide"}, status_code=400)
    return {"ok": sessions_store.delete_session(kind, sid)}
