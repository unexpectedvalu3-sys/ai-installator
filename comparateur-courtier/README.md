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
