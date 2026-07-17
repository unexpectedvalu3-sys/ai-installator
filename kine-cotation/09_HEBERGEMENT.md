# KinéCotation — héberger pour le kiné (Malcom)

> 2026-07-18. But : Malcom (`malcom.dorante`) se connecte depuis chez lui, par navigateur.

---

## Ce que je peux faire, et ce que toi seul peux faire

**Prêt (fait) :** l'app est déployable telle quelle — serveur de production (waitress),
`PORT`/`HOST` lus dans l'environnement, `Dockerfile` + `Procfile`, cookie `Secure` en HTTPS,
login gardé, HTML régénérée au build depuis la base NGAP.

**Toi seul (secrets + compte d'hôte — mes garde-fous m'interdisent de le faire) :**
1. Créer un service chez un hébergeur et cliquer « déployer ».
2. Créer la clé Mistral (console fournisseur) et la coller dans les variables d'env de l'hôte.
3. Fixer le mot de passe de Malcom (via `set_password.py`).

Je ne peux pas cliquer « déployer » sur un compte que je n'ai pas, ni saisir une clé ou un mot de passe.

---

## Étapes (≈ 15 min)

### 1. Créer le compte de Malcom (en local, une fois)
```
cd kine-cotation/webapp
python set_password.py
   Identifiant : malcom.dorante
   Mot de passe : ********   (choisis-en un FORT, 10+ car. — outil de santé)
```
Le script imprime `APP_USER`, `APP_PASSWORD_HASH`, `SECRET_KEY`. Garde-les pour l'étape 3.
Le mot de passe n'est jamais affiché ni stocké en clair.

> Pour que Malcom choisisse **lui-même** son mot de passe : il lance `set_password.py` chez lui
> et t'envoie seulement les 3 lignes (le hash, pas le mot de passe). Sinon, choisis-le et
> transmets-le lui par un canal sûr. Auth mono-compte : pas d'écran « changer le mot de passe » —
> pour en changer, on relance `set_password.py` et on met à jour `APP_PASSWORD_HASH`.

### 2. Choisir un hébergeur (host-neutre — pas Railway, cf. préférence projet)
Options simples avec HTTPS gratuit : **Render**, **Fly.io**, **Scaleway** (FR/EU — à préférer).
- **Région UE** recommandée : même si rien de santé n'est stocké, l'OCR y transite.
- Racine du projet : `kine-cotation/`. Build : `pip install -r requirements.txt && python webapp/build_webapp.py`.
  Démarrage : `python webapp/server.py`. (Ou utilise le `Dockerfile`, qui fait tout ça.)

### 3. Variables d'environnement à coller dans le dashboard de l'hôte
```
APP_USER=malcom.dorante
APP_PASSWORD_HASH=pbkdf2$...      (sortie de set_password.py)
SECRET_KEY=...                     (sortie de set_password.py — stable, sinon les sessions sautent)
MISTRAL_API_KEY=...                (console.mistral.ai — pour l'OCR ; vide = app sans OCR)
HOST=0.0.0.0
# NE PAS mettre COOKIE_INSECURE : l'hôte est en HTTPS -> cookie Secure automatiquement.
```
`.env` n'est **jamais** commité ; en hébergement, ces valeurs vivent dans l'hôte, pas dans un fichier.

### 4. Déployer, puis vérifier
- `https://<ton-app>/healthz` → `{"status":"ok","auth_configured":true}`
- `https://<ton-app>/` → redirige vers `/login`
- login `malcom.dorante` + mot de passe → l'app.

---

## OCR en phase de test — la règle (cf. `06_PROVIDER_IA.md`, `benchmark/00_PROTOCOLE §0`)

Malcom **peut** utiliser l'OCR **sur ordonnances ANONYMISÉES uniquement** : caviarder nom, prénom,
date de naissance, NIR avant la photo ; garder le clinique. Raisons :
- une ordonnance = donnée de santé ; la « phase de test » n'exempte pas — le patient n'a pas
  consenti à ce que sa prescription parte chez Mistral ;
- Mistral standard n'a pas le **Zero Data Retention** (réservé à Enterprise) → sur données réelles
  identifiées, il faut Enterprise + ZDR + DPA. Anonymisé, le test est propre et reste en UE.
- **Bonus** : ces tests d'OCR produisent en même temps les données du benchmark OCR.

Sans `MISTRAL_API_KEY`, l'app fonctionne entièrement **sans** OCR (cotation, DAP, dossier de preuve).

---

## Posture données (à savoir / à pouvoir dire)

- Serveur **sans état** : pas de base, sessions dans un cookie signé, **profil + dossier de preuve
  dans le navigateur de Malcom** (localStorage). Rien de santé stocké côté serveur.
- Seul flux de santé : l'OCR, **proxy transitoire** → le fichier temporaire est supprimé aussitôt.
- Ce n'est pas une mise en production « vrais patients » : c'est un pilote design-partner sur
  données anonymisées. Le passage prod (Enterprise/ZDR/DPA, convention art. 28) reste devant nous.
