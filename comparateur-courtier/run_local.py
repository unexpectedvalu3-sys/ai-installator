# -*- coding: utf-8 -*-
"""Lanceur LOCAL du Comparateur Courtier (cible : exe autonome PyInstaller,
SANS fenêtre console — build --windowed).

Double-clic sur l'exe → lit le .env à côté de l'exe, démarre le serveur en
arrière-plan, ouvre le navigateur, et affiche une icône (la mascotte) dans la
zone de notification Windows : un clic (gauche ou droit) ouvre un petit menu
« Ouvrir le Comparateur » / « Quitter ».

- Clés API + auth : lues dans `.env` placé À CÔTÉ de l'exe. Jamais embarquées.
- Données (cabinet, sessions) : dossier `data/` créé à côté de l'exe.
- Aucune console (build --windowed) : les erreurs de démarrage vont dans
  `comparateur_erreur.log` à côté de l'exe.
"""
import os
import sys
import time
import threading
import traceback
import webbrowser
from pathlib import Path

if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).parent
    # ressources embarquées (static/ = templates + mascotte) : dans _MEIPASS
    # (temp auto-extrait par PyInstaller --onefile), PAS à côté de l'exe.
    BUNDLE_DIR = Path(sys._MEIPASS)
else:
    APP_DIR = Path(__file__).parent
    BUNDLE_DIR = APP_DIR

# Build --windowed (sans console) : sys.stdout/stderr valent None. Toute lib qui
# logge dessus (uvicorn, pystray, threading.excepthook...) plante alors le thread
# SILENCIEUSEMENT. On redirige donc vers un vrai fichier AVANT d'importer quoi
# que ce soit qui pourrait logger.
if getattr(sys, "frozen", False) and sys.stdout is None:
    _log = open(APP_DIR / "comparateur.log", "a", buffering=1, encoding="utf-8")
    sys.stdout = _log
    sys.stderr = _log

HOST = "127.0.0.1"
PORT = int(os.environ.get("PORT", "8000"))

os.environ.setdefault("DATA_DIR", str(APP_DIR / "data"))   # persistance à côté de l'exe

# Config embarquée (clés API + identifiants) compilée dans l'exe par build_exe.py.
# Au premier lancement, on écrit un .env à côté de l'exe avec ces valeurs + un
# SECRET_KEY unique par install. Les lancements suivants lisent ce .env directement.
try:
    import embedded_config as _cfg
    _need_env = not (APP_DIR / ".env").exists()
    if _need_env:
        import secrets as _s
        env_lines = list(_cfg.LINES) + [
            f"SECRET_KEY={_s.token_urlsafe(48)}",
            "COOKIE_INSECURE=1",
        ]
        (APP_DIR / ".env").write_text("\n".join(env_lines) + "\n", encoding="utf-8")
    from dotenv import load_dotenv
    load_dotenv(APP_DIR / ".env", override=True)
except Exception:
    # fallback : .env déjà présent (dev local sans build)
    try:
        from dotenv import load_dotenv
        load_dotenv(APP_DIR / ".env", override=True)
    except Exception:
        pass


def _open_browser():
    time.sleep(1.5)
    webbrowser.open(f"http://{HOST}:{PORT}")


def _run_server(appmod):
    import uvicorn
    config = uvicorn.Config(appmod.app, host=HOST, port=PORT, log_level="warning")
    uvicorn.Server(config).run()


def _tray_icon(appmod):
    """Icône dans la zone de notification (la mascotte) : rouvrir / mettre à jour / quitter.
    Bloque le thread principal (nécessaire côté Windows) jusqu'à « Quitter »."""
    import pystray
    from PIL import Image
    image = Image.open(BUNDLE_DIR / "static" / "mascotte.png")

    def _open(icon, item):
        webbrowser.open(f"http://{HOST}:{PORT}")

    def _quit(icon, item):
        icon.stop()
        os._exit(0)

    # Pas de default=True : sur Windows, un item "par défaut" fait que pystray
    # déclenche la même action au clic gauche ET au clic droit (le menu ne
    # s'ouvre alors jamais). Sans default, n'importe quel clic affiche ce petit
    # menu — comportement simple et fiable.
    menu = pystray.Menu(
        pystray.MenuItem("Ouvrir le Comparateur", _open),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Vérifier les mises à jour",
                         lambda icon, item: threading.Thread(target=_check_update, args=(icon,), daemon=True).start()),
        pystray.MenuItem("Quitter", _quit),
    )
    pystray.Icon("comparateur-courtier", image, "Comparateur Courtier", menu).run()


# Repo GitHub pour les mises à jour (tags/releases).
# Pour pousser une mise à jour : créer un GitHub Release avec le nouvel .exe en asset.
UPDATE_REPO = "unexpectedvalu3-sys/ai-installator"
UPDATE_ASSET = "ComparateurCourtier.exe"   # nom du fichier dans la release


def _ver(s):
    """'v1.0.10' -> (1, 0, 10) pour comparer les versions numériquement
    (une comparaison de chaînes casserait : '1.0.10' < '1.0.3' en lexicographique)."""
    parts = str(s or "0").lstrip("vV").split(".")
    out = []
    for p in parts:
        try:
            out.append(int(p))
        except ValueError:
            out.append(0)
    return tuple(out)


def _check_update(icon=None):
    """Vérifie GitHub Releases pour une nouvelle version. Si trouvée : télécharge
    le nouvel .exe EN STREAMING (progression dans l'info-bulle), remplace l'exe en
    cours (rename trick Windows), relance. Appelé DANS UN THREAD (voir le menu du
    tray) -> ne bloque jamais l'icône. Notifications en bulle (non bloquantes)
    plutôt qu'en boîte modale, sinon le téléchargement attend un clic OK."""
    import urllib.request, json, subprocess

    def bulle(msg, title="Mise à jour"):
        """Notification non bloquante (bulle du tray). Repli sur messagebox seulement
        si l'icône n'expose pas notify()."""
        try:
            if icon is not None and hasattr(icon, "notify"):
                icon.notify(msg, title)
                return
        except Exception:
            pass
        _notify(title, msg, info=True)

    def set_title(txt):
        try:
            if icon is not None:
                icon.title = txt
        except Exception:
            pass

    api = f"https://api.github.com/repos/{UPDATE_REPO}/releases/latest"
    try:
        req = urllib.request.Request(api, headers={"User-Agent": "ComparateurCourtier"})
        with urllib.request.urlopen(req, timeout=15) as r:
            release = json.loads(r.read().decode())
    except Exception as e:
        bulle(f"Impossible de vérifier les mises à jour :\n{e}")
        return

    tag = release.get("tag_name", "")
    if not tag:
        bulle("Aucune mise à jour disponible.")
        return

    # Déjà à jour ? -> on évite un téléchargement de 46 Mo inutile.
    try:
        import embedded_config as _cfg
        current = _cfg.APP_VERSION
    except Exception:
        current = "0"
    if _ver(tag) <= _ver(current):
        bulle(f"Vous avez déjà la dernière version ({current}).")
        return

    # Cherche l'asset (le nouvel .exe) dans la release
    asset_url = None
    for a in release.get("assets", []):
        if a.get("name", "").lower() == UPDATE_ASSET.lower():
            asset_url = a["browser_download_url"]
            break
    if not asset_url:
        bulle(f"Release {tag} trouvée mais l'exe n'y est pas ({UPDATE_ASSET}).")
        return

    # Téléchargement en streaming, avec progression dans l'info-bulle (46 Mo).
    bulle(f"Téléchargement de la mise à jour {tag}…\n"
          "L'application redémarrera automatiquement à la fin.")
    try:
        req = urllib.request.Request(asset_url, headers={"User-Agent": "ComparateurCourtier"})
        with urllib.request.urlopen(req, timeout=600) as r:
            total = int(r.headers.get("Content-Length") or 0)
            buf = bytearray()
            got = 0
            last_pct = -5
            while True:
                chunk = r.read(262144)          # 256 Ko par lecture
                if not chunk:
                    break
                buf += chunk
                got += len(chunk)
                if total:
                    pct = int(got * 100 / total)
                    if pct >= last_pct + 5:      # rafraîchit tous les 5 %
                        last_pct = pct
                        set_title(f"Comparateur Courtier — mise à jour {pct} %")
            data = bytes(buf)
    except Exception as e:
        set_title("Comparateur Courtier")
        bulle(f"Échec du téléchargement :\n{e}")
        return
    set_title("Comparateur Courtier")
    # Téléchargement tronqué (connexion coupée) -> NE PAS installer un exe corrompu.
    if total and len(data) != total:
        bulle(f"Téléchargement incomplet ({len(data)}/{total} octets). Réessaie la mise à jour.")
        return

    # Remplace l'exe en cours (Windows : on peut renommer un exe en cours d'exécution)
    exe = Path(sys.executable) if getattr(sys, "frozen", False) else Path(sys.argv[0])
    tmp = exe.with_suffix(".exe.new")
    old = exe.with_suffix(".exe.old")
    try:
        tmp.write_bytes(data)
        if old.exists():
            old.unlink()
        exe.rename(old)           # renomme l'exe en cours (autorisé sous Windows)
        tmp.rename(exe)           # le nouvel exe prend sa place
    except Exception as e:
        bulle(f"Échec du remplacement de l'exe :\n{e}")
        return

    bulle(f"Mise à jour {tag} installée. L'application redémarre…")
    time.sleep(1.5)
    # Relance le nouvel exe DÉTACHÉ (n'hérite pas des handles -> évite le warning
    # "Failed to remove temporary directory _MEI…") puis quitte.
    flags = 0
    for name in ("DETACHED_PROCESS", "CREATE_NEW_PROCESS_GROUP", "CREATE_NO_WINDOW"):
        flags |= getattr(subprocess, name, 0)
    try:
        subprocess.Popen([str(exe)], cwd=str(APP_DIR), close_fds=True, creationflags=flags)
    except Exception:
        subprocess.Popen([str(exe)], cwd=str(APP_DIR))
    os._exit(0)


def _notify(title, msg, info=False):
    """Notification Windows (bulle) via le tray icon si disponible, sinon messagebox."""
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk(); root.withdraw()
        root.attributes("-topmost", True)
        if info:
            messagebox.showinfo(title, msg, parent=root)
        else:
            messagebox.showwarning(title, msg, parent=root)
        root.destroy()
    except Exception:
        pass  # silencieux si tkinter indisponible


def _cleanup_stale():
    """Nettoie l'ancien exe (.old) laissé par une MAJ précédente. Best-effort.

    IMPORTANT : on NE touche PAS aux dossiers temp _MEI*. PyInstaller y extrait ses
    binaires (dont _pydantic_core.pyd), et les supprimer depuis l'app en cours —
    avant que tout soit importé — casse le démarrage (« No module named
    pydantic_core._pydantic_core »). Windows nettoie les _MEI orphelins tout seul."""
    try:
        if getattr(sys, "frozen", False):
            old = Path(sys.executable).with_suffix(".exe.old")
            if old.exists():
                try:
                    old.unlink()
                except Exception:
                    pass
    except Exception:
        pass


def main():
    _cleanup_stale()
    import app as appmod
    threading.Thread(target=_run_server, args=(appmod,), daemon=True).start()
    threading.Thread(target=_open_browser, daemon=True).start()
    _tray_icon(appmod)   # bloquant : rend la main quand l'utilisateur clique « Quitter »


if __name__ == "__main__":
    try:
        main()
    except Exception:
        try:
            (APP_DIR / "comparateur_erreur.log").write_text(traceback.format_exc(), encoding="utf-8")
        except Exception:
            pass
        raise
