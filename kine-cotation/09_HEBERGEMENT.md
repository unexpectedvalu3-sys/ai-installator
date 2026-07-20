# KinéCotation — héberger pour le kiné (Malcom)

> 2026-07-18. But : Malcom (`malcom.dorante`) se connecte depuis chez lui, par navigateur.

> **MàJ 2026-07-20 (pilote).** OCR du pilote = **Claude Sonnet** via la **clé Anthropic existante**
> (plus de création de clé Mistral ; révoquer l'ancienne clé Mistral exposée). L'appel part chez
> Anthropic (**US**) — **nuance assumée pour le pilote** car l'image est **caviardée structurellement**
> (l'identité ne quitte pas le poste). **Cible souveraineté FR/UE pour la prod inchangée.** Pont de
> mise en ligne immédiate sans compte d'hôte : **tunnel Cloudflare** depuis le poste d'Enzo
> (`webapp/start_pilote.ps1`, cf. `14_GUIDE_PILOTE_MALCOM.md` § « Mise en ligne immédiate »).

---

## Ce que je peux faire, et ce que toi seul peux faire

**Prêt (fait) :** l'app est déployable telle quelle — serveur de production (waitress),
`PORT`/`HOST` lus dans l'environnement, `Dockerfile` + `Procfile`, cookie `Secure` en HTTPS,
login gardé, HTML régénérée au build depuis la base NGAP.

**Toi seul (secrets + compte d'hôte — mes garde-fous m'interdisent de le faire) :**
1. Créer un service chez un hébergeur et cliquer « déployer ».
2. Créer la clé Mistral (console fournisseur) et la coller dans les variables d'env de l'hôte.
3. Fixer le mot de passe de chaque kiné (via `make_account.py`).

Je ne peux pas cliquer « déployer » sur un compte que je n'ai pas, ni saisir une clé ou un mot de passe.

---

## Étapes (≈ 15 min)

### 1. Créer les comptes (en local — **multi-comptes**, un par kiné)
```
cd kine-cotation/webapp
python make_account.py
   Identifiant : malcom.dorante
   Mot de passe : ********   (FORT, 10+ car. — outil de santé)
```
Relance-le pour ajouter d'autres kinés (chacun son mot de passe). Le script écrit
`accounts.json` (registre, **gitignoré — les hash ne sont jamais publiés**) et imprime
`KINE_ACCOUNTS` + `SECRET_KEY` à coller à l'étape 3. Le mot de passe n'est jamais affiché.

> Pour que le kiné choisisse **lui-même** son mot de passe : il lance `make_account.py` chez lui et
> t'envoie seulement le bloc `KINE_ACCOUNTS` (le hash, pas le mot de passe). Pas d'écran « changer le
> mot de passe » : pour en changer, on relance `make_account.py` (il remplace l'entrée du compte).

### 2. Choisir un hébergeur (host-neutre — pas Railway, cf. préférence projet)
Options simples avec HTTPS gratuit : **Render**, **Fly.io**, **Scaleway** (FR/EU — à préférer).
- **Région UE** recommandée : même si rien de santé n'est stocké, l'OCR y transite.
- Racine du projet : `kine-cotation/`. Build : `pip install -r requirements.txt && python webapp/build_webapp.py`.
  Démarrage : `python webapp/server.py`. (Ou utilise le `Dockerfile`, qui fait tout ça.)

### 3. Variables d'environnement à coller dans le dashboard de l'hôte
```
KINE_ACCOUNTS={"comptes":[{"user":"malcom.dorante","password_hash":"pbkdf2$..."}]}
SECRET_KEY=...                     (sortie de make_account.py — stable, sinon les sessions sautent)
MISTRAL_API_KEY=...                (console.mistral.ai — pour l'OCR ; vide = app sans OCR)
HOST=0.0.0.0
# NE PAS mettre COOKIE_INSECURE : l'hôte est en HTTPS -> cookie Secure automatiquement.
```
Le registre `accounts.json` et `.env` ne sont **jamais** commités ; en hébergement, ces valeurs
vivent dans l'hôte (env `KINE_ACCOUNTS`), pas dans un fichier du repo. Pour beaucoup de comptes,
monter un disque et pointer `KINE_ACCOUNTS_FILE` vers un `accounts.json` persistant (édité par
`make_account.py`) évite de retoucher l'env à chaque ajout.

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
