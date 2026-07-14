# -*- coding: utf-8 -*-
"""Sessions nommées persistées (Comparateur / Fiche DDA) : permet d'enregistrer
un travail en cours sous un nom, d'en démarrer un nouveau, et de retrouver plus
tard une session précédente dans une liste. Un fichier JSON par « kind »
(`data/sessions_<kind>.json`), même esprit que jour.json (pas de base de données)."""
import os, json, time, uuid
from pathlib import Path

BASE = Path(__file__).parent
DATA = Path(os.environ.get("DATA_DIR", BASE / "data"))


def _path(kind):
    return DATA / f"sessions_{kind}.json"


def _load(kind):
    p = _path(kind)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"items": []}


def _save(kind, store):
    p = _path(kind)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")


def list_sessions(kind):
    """Liste légère (sans le contenu `data`) triée par dernière modif décroissante."""
    store = _load(kind)
    items = [{"id": it["id"], "nom": it["nom"], "updated_at": it["updated_at"]}
             for it in store["items"]]
    return sorted(items, key=lambda x: x["updated_at"], reverse=True)


def save_session(kind, session_id, nom, data):
    """Crée ou met à jour (si `session_id` correspond à une session existante)."""
    store = _load(kind)
    now = time.time()
    if session_id:
        for it in store["items"]:
            if it["id"] == session_id:
                it["nom"] = nom
                it["data"] = data
                it["updated_at"] = now
                _save(kind, store)
                return session_id
    session_id = uuid.uuid4().hex[:12]
    store["items"].append({"id": session_id, "nom": nom, "data": data,
                            "created_at": now, "updated_at": now})
    _save(kind, store)
    return session_id


def get_session(kind, session_id):
    store = _load(kind)
    for it in store["items"]:
        if it["id"] == session_id:
            return it
    return None


def delete_session(kind, session_id):
    store = _load(kind)
    before = len(store["items"])
    store["items"] = [it for it in store["items"] if it["id"] != session_id]
    _save(kind, store)
    return len(store["items"]) < before
