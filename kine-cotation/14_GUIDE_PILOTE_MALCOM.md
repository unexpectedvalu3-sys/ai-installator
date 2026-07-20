# KinéCotation — guide de la première séance (Malcom)

> Bienvenue. Cet outil te fait une **cotation NGAP défendable** en quelques clics, avec la
> **preuve** qui va derrière (barème daté, justification, alerte DAP). Il ne remplace pas VEGA :
> il t'évite de chercher le bon coefficient et te prépare la re-saisie. Tu restes seul maître de
> ta facturation. Compte 5 minutes pour lire ceci, une fois.

---

## 1. Se connecter

1. Ouvre le lien que t'envoie Enzo (`https://…`) dans ton navigateur (mets-le en favori).
2. Identifiant : **`malcom.dorante`** · mot de passe : celui que tu as choisi.
3. La connexion tient **30 jours** : au cabinet tu ne la retapes quasiment jamais.

Tes données de cotation (ton profil, tes feuilles) restent **sur ton poste**, pas sur un serveur.

---

## 2. Le flux ordonnance (photo → cotation)

C'est le cœur du gain de temps. Étape par étape :

1. **Prends l'ordonnance en photo** (bouton *Ordonnance*). Photo nette, à plat, bien éclairée.
2. **L'app masque le bloc patient toute seule** : elle repère nom / prénom / date de naissance /
   n° de sécu et pose un rectangle noir dessus. Tu vois l'aperçu **déjà caviardé**.
3. **Vérifie le masque d'un coup d'œil.** S'il manque un bout d'identité : **glisse ton doigt**
   (ou la souris) sur la zone pour ajouter un rectangle. Trop masqué ? *Annuler le dernier* /
   *Tout effacer*. Le **nom du médecin peut rester** (ce n'est pas une donnée patient).
4. **Appuie sur *Analyser*.** C'est **seulement là** que l'image part, **masquée**. L'app te
   propose alors des actes et le nombre de séances prescrites.

> ⚠️ Le bouton *Analyser* reste **bloqué tant qu'aucun masque n'est posé**. C'est voulu :
> jamais d'envoi d'une ordonnance non caviardée.

**Pas d'OCR ?** Si l'app tourne sans clé OCR, ou hors-ligne, elle te le dit proprement : tu
construis la cotation à la main (section 3), tout le reste marche.

### Pourquoi ce masquage — c'est important
Une ordonnance, c'est une **donnée de santé**. C'est **ta responsabilité de professionnel de
santé** que l'identité de ton patient ne parte pas dans la nature. Alors on ne prend aucun risque :
**l'image part masquée**, et **l'identité du patient ne quitte jamais ton poste**. C'est ce qui te
permet d'utiliser l'outil l'esprit tranquille pendant le pilote.

---

## 3. Construire la cotation

1. **La date de la séance — commence par ça.** Ce **n'est pas** forcément la date du jour : c'est la
   date où le soin a été fait. Elle **pilote le barème** (la NGAP a changé 3 fois en un an). Une
   séance du 31/08 facturée le 05/09 se cote au barème du **31/08**. Change la date → tout se recote.
2. **Choisis la région** (genou, rachis, épaule…), puis réponds aux deux questions rapides
   (*Opéré / Non opéré*, *Au référentiel / Hors référentiel*) : un clic, la liste d'actes se réduit
   à **ce qui te concerne**.
3. **Clique l'acte réalisé.** Il s'ajoute à la feuille avec son coefficient et son tarif.
4. **Le n° de séance** (sous la ligne de l'acte) : indique où tu en es (séance 1, 12, 30…). Il
   **déclenche l'alerte DAP**.

### L'alerte DAP — ta sécurité anti-indu
Quand une **Demande d'Accord Préalable** est requise, une bannière s'affiche **en haut de la
feuille** :
- **orange** = elle approche (anticipe le bilan) ;
- **rouge « ⚠ DAP REQUISE »** = tu es à/au-delà du seuil : ne facture pas sans DAP.

Si l'app a lu le nombre de séances prescrites, elle te prévient **dès la 1ʳᵉ séance** qu'une DAP
tombera plus loin. C'est un plan de charge, pas un reproche.

---

## 4. Le champ « Patient » (local)

Dans l'en-tête de la feuille, un champ **Nom + prénom du patient**. Il sert juste à imprimer une
feuille propre et à personnaliser la justification. **Il ne part nulle part** : ni au serveur, ni
enregistré — une feuille = un patient. *Vider* le remet à zéro. (Note le « saisi localement, jamais
transmis » sous le champ : c'est vrai au sens strict.)

---

## 5. Imprimer / archiver la feuille

Bouton **Imprimer / PDF** : tu obtiens la **feuille de soins** (actes + coefficients + total) avec la
**justification** (barème daté, source SNMKR, pièces). Le réflexe à prendre : **archive-la avec
l'ordonnance et le BDK**. C'est exactement ce qui te défend en cas de contrôle — une cotation qui dit
*sous quel barème* et *sur quelle base* elle a été faite.

---

## 6. Copier pour VEGA

Comme il n'existe pas d'API pour écrire directement dans VEGA, on t'évite au maximum la double
saisie : le bouton **Copier la cotation** met dans ton presse-papiers un **bloc texte compact** —
une ligne par acte, la DAP si besoin, le total — que tu **colles / recopies dans VEGA** en quelques
secondes. Exemple :

```
Cotation séance du 28/05/2026
RIC 8.12 — Après arthroplastie du genou — 17,95 €
  séance n°30 · ⚠ DAP REQUISE · DAP dès la 26e séance
AMK 10.7 — Bilan diagnostic kiné — 23,65 €
Total séance : 41,60 €
Barème : SNMKR — Tableau NGAP v19 (28/05/2026) · base v1.5 · lettre-clé 2,21 €
```

> Le **nom du patient n'y est jamais** (un presse-papiers peut fuiter vers une autre appli). Tu
> ressaisis l'identité dans VEGA comme d'habitude — elle, elle ne circule pas.

---

## 7. Ce qu'on mesure ensemble pendant le pilote

Deux choses, et elles comptent :

1. **Le taux de caviardage auto accepté** — visible dans **Mon profil** (« Caviardage auto : N/M
   acceptés sans retouche »). Plus tu l'utilises, plus on sait si l'auto-masquage est fiable. Rien à
   faire de spécial : sers-toi du flux ordonnance normalement, le compteur avance seul.
2. **Le chiffre de sous-cotation (le plus important).** Une session ensemble : on prend **5 à 10 de
   tes ordonnances réelles**, tu les cotes **à la main comme d'habitude**, puis on compare avec ce
   que propose le moteur. L'écart en **€/séance × ton volume annuel** = ce que l'outil te fait
   récupérer sur un an. C'est le vrai test de valeur.

---

## 8. Ce qu'on te demande (pour le benchmark)

En plus de te servir de l'app, garde-nous **15 à 20 ordonnances anonymisées à la main** : caviarde
nom / prénom / date de naissance / n° de sécu **au feutre noir** avant de photographier ou scanner.
Elles servent à mesurer la lecture automatique sur du vrai terrain. **Ce sont des ordonnances à part**
du flux de l'app (l'app, elle, masque toute seule) — là, c'est **toi** qui masques au feutre, et on
part de ce lot pour le benchmark.

---

## 9. Les limites — à garder en tête

- **C'est une aide à la décision.** L'outil propose ; **tu valides et tu restes responsable** de ta
  facturation. Vérifie toujours par rapport au tableau SNMKR en vigueur.
- **L'OCR pré-remplit, il ne décide pas.** Relis ce que l'app a lu, **surtout les nombres** (nombre
  de séances, coefficients) : une photo peut être mal lue. Tu corriges en un clic.
- On est en **pilote sur données anonymisées**, pas en production « vrais patients » : c'est normal,
  c'est la bonne façon de commencer proprement.

Des questions, un truc pas clair, un bug ? Écris à Enzo — c'est exactement ce qu'on veut entendre
pendant le pilote.

---
---

# Déploiement — 15 min, actions Enzo

> Section technique (pas pour Malcom). État au 2026-07-20 : **aucun CLI d'hébergeur authentifié sur
> la machine** (ni `render`, ni `flyctl`, ni `scw`, aucune variable/credential) → le déploiement
> autonome par l'assistant est **impossible sans franchir un garde-fou** (créer un compte / coller un
> token = saisie de secret). Donc **ces étapes sont à faire par toi**. L'app est prête (Dockerfile,
> `server.py` waitress, `PORT`/`HOST` lus dans l'env, fail-closed). Réf : `09_HEBERGEMENT.md`.

## A. Créer le compte de Malcom (en local, aucun secret dans le repo)

```bash
cd kine-cotation/webapp
python make_account.py
   Identifiant : malcom.dorante
   Mot de passe : ********      # FORT, 10+ car. (ou fais-le taper par Malcom chez lui)
```

Le script écrit `accounts.json` (gitignoré) **et imprime le bloc `KINE_ACCOUNTS` + `SECRET_KEY`** à
coller à l'étape C. Le mot de passe n'est jamais affiché.

## B. Hébergeur recommandé : **Render, région Frankfurt (EU)**

Render = le plus rapide (tu l'utilises déjà pour DocInvy) **et** compatible EU en choisissant la
région **Frankfurt** — l'OCR transite alors en UE (exigence de `09_HEBERGEMENT.md`). Alternative
souveraineté FR pure : **Scaleway Serverless Containers** (même image Docker, région `fr-par`) — plus
d'étapes, à réserver si tu veux du 100 % France.

**Pas-à-pas Render (Docker) :**
1. [dashboard.render.com](https://dashboard.render.com) → **New +** → **Web Service**.
2. Connecte le repo GitHub `unexpectedvalu3-sys/ai-installator`, branche `kine-cotation/socle-v1.2`
   (ou `main` après merge de la PR #1).
3. **Root Directory** : `kine-cotation`  ·  **Runtime** : **Docker** (le `Dockerfile` fait le build
   `pip install` + `python webapp/build_webapp.py` + lance `server.py`).
4. **Region** : **Frankfurt (EU Central)**.  **Instance Type** : *Free* (suffit pour le pilote).
5. **Health Check Path** : `/healthz`.
6. **Environment** : colle le bloc de l'étape C, puis **Create Web Service**.
7. Ne mets **pas** `PORT` : Render l'injecte, `server.py` le lit. Ne mets **pas** `COOKIE_INSECURE`
   (HTTPS Render → cookie `Secure` automatique).

> Fail-closed attendu : si tu déploies **avant** d'avoir mis `KINE_ACCOUNTS`, `/healthz` renvoie
> `auth_configured:false` et l'app répond **503** (elle ne sert jamais l'app en clair). C'est **le
> comportement voulu** tant que le compte de Malcom n'est pas configuré.

## C. Variables d'environnement — bloc PRÊT À COLLER

```
HOST=0.0.0.0
KINE_ACCOUNTS=            # ← sortie de make_account.py (JSON {"comptes":[...]}), NE PAS committer
SECRET_KEY=              # ← sortie de make_account.py (stable, sinon les sessions sautent)
KINE_LLM_PROVIDER=anthropic
KINE_LLM_MODELE=claude-sonnet-5
ANTHROPIC_API_KEY=       # ← COPIER depuis modulr-app/.env (clé existante ; ne pas créer de clé)
# NE PAS définir PORT (injecté par Render) ni COOKIE_INSECURE (HTTPS -> cookie Secure auto).
```

**Provider OCR du pilote = Claude Sonnet** (clé Anthropic déjà en main, mutualisée avec Modul'R) —
plus besoin de créer une clé Mistral. ⚠️ **Révoque l'ancienne clé Mistral qui a pu être exposée.**
Nuance souveraineté : l'appel OCR part chez Anthropic (US) — assumé pour le pilote car l'image est
**caviardée structurellement** (l'identité patient ne quitte jamais le poste) ; la cible
souveraineté FR/UE pour la **production** reste inchangée (voir `06_PROVIDER_IA.md`, `09_HEBERGEMENT.md`).

Valeurs non-secrètes déjà bonnes : `HOST=0.0.0.0`. Les champs vides sont **tes** secrets, à ne
jamais committer.

## D. Vérifier après déploiement (3 commandes)

Remplace `APP` par l'URL Render (`https://kinecotation-xxxx.onrender.com`).

```bash
# 1. HEALTHZ — l'app vit et l'auth est configurée
curl -s https://APP/healthz
#    attendu : {"auth_configured":true,"status":"ok"}   (false = KINE_ACCOUNTS manquant → 503)

# 2. LOGIN / fail-closed — la racine n'est jamais servie en clair
curl -s -o /dev/null -w "%{http_code} -> %{redirect_url}\n" https://APP/
#    attendu : 303 -> https://APP/login     (puis connexion malcom.dorante dans le navigateur)

# 3. OCR — après login dans le navigateur, téléverse une ordonnance ANONYMISÉE
#    attendu : des actes candidats proposés.  Si ANTHROPIC_API_KEY vide : message "OCR indisponible"
#    propre (pas d'erreur) — l'app reste utilisable sans OCR.
```

Envoie ensuite l'URL + l'identifiant à Malcom. C'est en ligne.

---
---

# Mise en ligne immédiate (tunnel depuis le poste d'Enzo)

> Le chemin **le plus rapide** pour donner l'accès à Malcom **maintenant**, sans compte d'hébergeur,
> sans déploiement. Utile pour démarrer le pilote le jour même. Le passage **Render (15 min)
> documenté plus haut** reste la voie durable ; ceci en est le **pont**.

## Ce que c'est
Un **tunnel Cloudflare** (`cloudflared`) expose le serveur qui tourne **sur le poste d'Enzo** derrière
une URL publique HTTPS `https://xxxxx.trycloudflare.com`. Aucun compte, aucune carte, aucun DNS :
Cloudflare fabrique l'URL à la volée. Le serveur reste en `127.0.0.1:8770` ; seul le tunnel sort.

## Les limites — honnêtes
- **URL éphémère** : elle **change à chaque redémarrage du tunnel** (relance de `start_pilote.ps1`).
  Il faut la **redonner à Malcom** après chaque relance. Mets-la en favori le temps d'une session,
  pas pour la semaine.
- **Le poste d'Enzo doit rester allumé** (et connecté) pendant que Malcom utilise l'app : si la
  machine dort ou s'éteint, l'URL tombe.
- **C'est un pont de pilote, pas de la production.** Débit best-effort, pas de SLA, pas de domaine
  stable. Dès que le pilote se confirme, on bascule sur **Render (section plus haut)** pour une URL
  fixe et une machine qui n'est pas celle d'Enzo.

## Démarrer / redémarrer
```powershell
cd kine-cotation\webapp
powershell -ExecutionPolicy Bypass -File start_pilote.ps1
```
Le script : (1) lance le serveur (waitress, port 8770) en process **détaché** ; (2) ouvre le tunnel ;
(3) **affiche l'URL publique** à dicter à Malcom. Prérequis déjà en place : compte `malcom.dorante`
(`accounts.json`), `webapp/.env` (SECRET_KEY + provider Claude + clé Anthropic), `cloudflared` installé.

**Où lire l'URL** : elle s'affiche en clair à la fin de `start_pilote.ps1` (cadre vert). Si tu l'as
perdue, elle est aussi dans le log du tunnel : `kine-cotation\webapp\pilote_tunnel.log` (cherche
`trycloudflare.com`).

**Arrêter** : ferme les process `python` et `cloudflared` (Gestionnaire des tâches), ou
`Get-Process python,cloudflared | Stop-Process`.

Identifiant/mot de passe de Malcom : voir `webapp/PILOTE_ACCES_MALCOM.txt` (fichier local gitignoré,
à transmettre par un canal sûr **puis supprimer**).
