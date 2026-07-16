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

# Configuration locale. Depuis la v1.2 (connexion « boîte mail »), l'installateur
# est UNIVERSEL : il ne dépose plus de .env — les identifiants et clés API viennent
# du registre de comptes au login (accounts.py). Le .env local ne sert plus qu'à :
#   - SECRET_KEY (signature des sessions), générée au 1er lancement, unique par install ;
#   - COOKIE_INSECURE=1 (app locale en http://127.0.0.1) ;
#   - rétro-compatibilité : les .env posés par les anciens installateurs (identifiants
#     + clés) continuent d'être lus et de fonctionner tels quels.
try:
    _envp = APP_DIR / ".env"
    _txt = _envp.read_text(encoding="utf-8") if _envp.exists() else ""
    _add = []
    if "SECRET_KEY=" not in _txt:
        import secrets as _s
        _add.append(f"SECRET_KEY={_s.token_urlsafe(48)}")
    if "COOKIE_INSECURE=" not in _txt:
        _add.append("COOKIE_INSECURE=1")
    if _add:
        _txt = (_txt.rstrip("\n") + "\n" if _txt else "") + "\n".join(_add) + "\n"
        _envp.write_text(_txt, encoding="utf-8")
    from dotenv import load_dotenv
    load_dotenv(_envp, override=True)
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
        from version import APP_VERSION as current
    except Exception:
        current = "0"
    if _ver(tag) <= _ver(current):
        bulle(f"Vous avez déjà la dernière version ({current}).")
        return

    # Cherche l'asset (le nouvel .exe) dans la release + sa taille/empreinte
    asset_url = None
    asset_size = 0
    asset_sha = ""
    for a in release.get("assets", []):
        if a.get("name", "").lower() == UPDATE_ASSET.lower():
            asset_url = a["browser_download_url"]
            asset_size = int(a.get("size") or 0)
            d = str(a.get("digest") or "")
            if d.startswith("sha256:"):
                asset_sha = d[7:].lower()
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
    expected = asset_size or total
    if expected and len(data) != expected:
        bulle(f"Téléchargement incomplet ({len(data)}/{expected} octets). Réessaie la mise à jour.")
        return
    if asset_sha:
        import hashlib
        if hashlib.sha256(data).hexdigest().lower() != asset_sha:
            bulle("Fichier téléchargé corrompu (empreinte SHA256 différente). Réessaie la mise à jour.")
            return

    exe = Path(sys.executable) if getattr(sys, "frozen", False) else Path(sys.argv[0])
    tmp = exe.with_suffix(".exe.new")
    old = exe.with_suffix(".exe.old")
    try:
        tmp.write_bytes(data)
    except Exception as e:
        bulle(f"Écriture du fichier de mise à jour impossible :\n{e}")
        return

    # AUTO-TEST : le nouvel exe doit s'extraire et charger ses modules AVANT de
    # remplacer l'exe en service. S'il échoue (antivirus, fichier abîmé…), on
    # annule -> la version actuelle, qui fonctionne, reste en place.
    set_title("Comparateur Courtier — vérification de la mise à jour…")
    try:
        rc = subprocess.run([str(tmp), "--selftest"], timeout=240).returncode
    except Exception:
        rc = -1
    set_title("Comparateur Courtier")
    if rc != 0:
        try:
            tmp.unlink()
        except Exception:
            pass
        bulle(f"La nouvelle version a échoué l'auto-test (code {rc}). "
              "Mise à jour annulée : ta version actuelle reste en place. Réessaie plus tard.")
        return

    # Remplace l'exe en cours (Windows : on peut renommer un exe en cours d'exécution)
    try:
        if old.exists():
            old.unlink()
        exe.rename(old)           # renomme l'exe en cours (autorisé sous Windows)
        tmp.rename(exe)           # le nouvel exe prend sa place
    except Exception as e:
        bulle(f"Échec du remplacement de l'exe :\n{e}")
        return

    bulle(f"Mise à jour {tag} installée. L'application redémarre…")
    time.sleep(1.5)
    _spawn_with_babysitter(exe, APP_DIR)
    os._exit(0)


def _spawn_with_babysitter(exe, cwd):
    """Relance le nouvel exe DÉTACHÉ, via un petit surveillant PowerShell : si
    l'app n'est pas revenue au bout de ~22 s (raté d'extraction du bootloader
    PyInstaller au redémarrage — antivirus qui verrouille l'exe fraîchement
    remplacé), il la relance UNE fois. La garde d'instance unique (main) rend un
    éventuel double départ inoffensif."""
    import subprocess
    port = int(os.environ.get("PORT", "8000"))
    ps = ("$e='{exe}';$w='{cwd}';Start-Process -FilePath $e -WorkingDirectory $w;"
          "Start-Sleep 22;"
          "try{{$null=Invoke-WebRequest ('http://127.0.0.1:{port}/healthz') -UseBasicParsing -TimeoutSec 5}}"
          "catch{{Start-Process -FilePath $e -WorkingDirectory $w}}").format(
        exe=str(exe), cwd=str(cwd), port=port)
    flags = 0
    for name in ("DETACHED_PROCESS", "CREATE_NEW_PROCESS_GROUP", "CREATE_NO_WINDOW"):
        flags |= getattr(subprocess, name, 0)
    try:
        subprocess.Popen(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps],
                         close_fds=True, creationflags=flags)
    except Exception:
        subprocess.Popen([str(exe)], cwd=str(cwd))


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


def _port_available(p):
    import socket
    s = socket.socket()
    try:
        s.bind((HOST, p)); s.close(); return True
    except OSError:
        s.close(); return False


def _instance_alive(p):
    import urllib.request
    try:
        with urllib.request.urlopen(f"http://{HOST}:{p}/healthz", timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def main():
    global PORT
    # Instance unique : si l'app tourne déjà sur ce port, on ouvre simplement le
    # navigateur et on se retire (plus de crash « port occupé » en double-clic).
    if not _port_available(PORT):
        if _instance_alive(PORT):
            webbrowser.open(f"http://{HOST}:{PORT}")
            return
        for cand in range(PORT + 1, PORT + 21):   # port pris par une autre app -> suivant
            if _port_available(cand):
                PORT = cand
                break
    _cleanup_stale()
    import app as appmod
    threading.Thread(target=_run_server, args=(appmod,), daemon=True).start()
    threading.Thread(target=_open_browser, daemon=True).start()
    _tray_icon(appmod)   # bloquant : rend la main quand l'utilisateur clique « Quitter »


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        # Auto-test utilisé par la mise à jour : le nouvel exe doit s'extraire et
        # charger tous ses modules lourds AVANT de remplacer l'exe en service.
        # Exit 0 = sain ; autre = on garde la version actuelle.
        try:
            import ssl              # noqa: F401  (_ssl + OpenSSL)
            import app              # noqa: F401  (fastapi, pydantic, httpx…)
            import uvicorn          # noqa: F401
            import pystray          # noqa: F401
            from PIL import Image   # noqa: F401  (_imaging)
            os._exit(0)
        except Exception:
            try:
                (APP_DIR / "selftest_erreur.log").write_text(traceback.format_exc(), encoding="utf-8")
            except Exception:
                pass
            os._exit(3)
    try:
        main()
    except Exception:
        try:
            (APP_DIR / "comparateur_erreur.log").write_text(traceback.format_exc(), encoding="utf-8")
        except Exception:
            pass
        # Échec transitoire d'extraction (_MEI incomplet : antivirus qui verrouille
        # les DLL fraîchement écrites, typique juste après une mise à jour) : on se
        # relance UNE fois en silence (nouvelle extraction) au lieu d'afficher la
        # boîte d'erreur. CC_RELAUNCHED évite toute boucle infinie.
        if getattr(sys, "frozen", False) and not os.environ.get("CC_RELAUNCHED"):
            import subprocess
            env = dict(os.environ, CC_RELAUNCHED="1")
            flags = 0
            for _n in ("DETACHED_PROCESS", "CREATE_NEW_PROCESS_GROUP", "CREATE_NO_WINDOW"):
                flags |= getattr(subprocess, _n, 0)
            time.sleep(2)
            try:
                subprocess.Popen([sys.executable], cwd=str(APP_DIR), env=env,
                                 close_fds=True, creationflags=flags)
                os._exit(1)
            except Exception:
                pass
        raise
