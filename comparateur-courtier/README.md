# Comparateur Courtier

Outil web du courtier : **comparateur de mutuelle** + **fiche devoir de conseil (DDA)**.
Version allégée dérivée de Modul'R — on ne garde que ces deux outils, sans la partie
extraction de dossiers / export CSV. Un déploiement par courtier, protégé par un login.

## Ce que fait l'app
- **Comparateur** (`/comparateur`) : dépôt de devis mutuelle (PDF) → tableau comparatif
  aligné (5 modules : hospitalisation, soins courants, dentaire, optique, prévention),
  offre recommandée, courrier de synthèse client, export Excel. Moteur : GLM 5.2
  (OpenRouter) pour l'extraction, Claude pour la prose.
- **Fiche DDA** (`/fiche-dda`) : infos cabinet éditables + justification du conseil
  rédigée par Claude, prête à imprimer.
- **Sessions** : chaque outil enregistre/retrouve un travail nommé.

Aucune donnée de santé n'est demandée ni stockée. Aucun calcul de tarif : l'app
aligne des garanties déclarées sur les devis, elle ne produit pas de prix.

## Distribution : exe Windows autonome, un installateur par client
L'app est livrée comme **exe Windows** (tray icon, ouvre le navigateur, auto-update
via GitHub Releases). L'exe est **GÉNÉRIQUE** (aucun secret) : la config de chaque
client (clés API + identifiants) vit dans un `.env` que **son installateur** dépose
à côté de l'exe. Un seul build d'exe sert tous les clients.

```bash
# 1) Construire l'exe générique — UNE fois (ou à chaque changement de code, ~2 min)
python build_exe.py                     # -> dist/ComparateurCourtier.exe

# 2) Un installateur par client — quelques secondes chacun
python make_client.py sophie            # lit clients/sophie.txt -> dist/setup_sophie.exe
python make_client.py                   # lit keys.txt (compte par défaut) -> dist/setup_courtier.exe
```
- **Profils clients** : `keys.txt` (défaut) ou `clients/<nom>.txt` — format :
  `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`, `APP_USER`, `APP_PASSWORD`, (`LLM_MODEL`,
  `COMPARE_MODEL`). **Gitignore : jamais commités.**
- **Version** : dans `version.py` (source unique). Bumper puis `build_exe.py`.
- **Publier une MAJ** : `gh release create vX.Y.Z dist/ComparateurCourtier.exe …`.
  L'exe étant générique, l'asset public ne contient aucun secret. Les clients cliquent
  « Vérifier les mises à jour » (leur `.env` local est préservé).

## Lancer en local (dev)
```bash
cd comparateur-courtier
python -m venv .venv && .venv\Scripts\activate       # Windows
pip install -r requirements.txt
copy .env.example .env                                # remplir les clés + l'auth

# 1) Générer les identifiants (mot de passe jamais stocké en clair)
python set_password.py                                # copier APP_USER / APP_PASSWORD_HASH / SECRET_KEY dans .env
# 2) En http local, autoriser le cookie sans HTTPS :
#    ajouter COOKIE_INSECURE=1 dans .env
uvicorn app:app --reload
```
→ http://localhost:8000 → page de connexion.

## Déploiement (host-neutre : Render, Fly, VPS… — pas Railway)
- `Procfile` standard : `web: uvicorn app:app --host 0.0.0.0 --port $PORT`.
- Variables d'environnement à définir : `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`,
  `APP_USER`, `APP_PASSWORD_HASH`, `SECRET_KEY`, et `DATA_DIR` pointant vers un
  **volume persistant** (sinon `cabinet.json` et les sessions sont perdus au redémarrage).
- HTTPS obligatoire (le cookie de session est `Secure` par défaut). Ne PAS mettre
  `COOKIE_INSECURE` en prod.

## Sécurité
- Auth par formulaire + cookie de session signé (`itsdangerous`), mot de passe
  haché PBKDF2. Middleware **fail-closed** : sans `APP_USER`/`APP_PASSWORD_HASH`/
  `SECRET_KEY`, l'app ne sert rien (503).
- Changer `SECRET_KEY` déconnecte toutes les sessions.

## RGPD / prod
- La prose fine passe par Claude (US). Point de bascule unique `llm._call_llm`
  (Mistral EU possible pour la prod RGPD), comme dans Modul'R.
- Convention de sous-traitance (art. 28 RGPD) à prévoir avec chaque courtier.

## Fichiers
- `app.py` — routes (auth + comparateur + fiche DDA + sessions).
- `auth.py` — login/session ; `set_password.py` — génère les identifiants.
- `llm.py` — helpers Claude (`_call_llm`, `_parse_json`).
- `compare.py` — comparateur (GLM/OpenRouter + Excel). `fichedda.py` — fiche DDA.
- `sessions_store.py` — sessions nommées (JSON sous `DATA_DIR`).
- `static/` — `index.html` (accueil), `login.html`, `comparateur.html`, `fiche-dda.html`.

## Non inclus (à faire)
- Réception automatique des leads depuis la vitrine (webhook n8n → à câbler).
- Bascule provider EU pour la prod RGPD.
