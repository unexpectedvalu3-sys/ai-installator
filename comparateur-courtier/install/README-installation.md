# Comparateur Courtier — Installation chez le client

Installation en **un double-clic** pour un poste Windows. Mettre à jour = un autre
double-clic. Pas de ligne de commande, pas de connaissances techniques.

## Ce qu'il faut fournir au client (une seule fois, à l'inscription)

Donne-lui ces 3 éléments, **en privé** (jamais par un canal public) :

1. Le dossier d'installation `install/` (ou un zip : `Installer.bat` + `installer.ps1`).
2. Sa clé **OPENROUTER_API_KEY** (comparateur).
3. Sa clé **ANTHROPIC_API_KEY** (courrier de synthèse).

> Ne lui donne JAMAIS ta propre clé personnelle : crée une clé dédiée par client
> dans les consoles OpenRouter / Anthropic, pour pouvoir révoquer/limiter chacune.

## Côté client — installation

1. S'assurer que [Python 3.10+](https://www.python.org/downloads/) et
   [Git](https://git-scm.com/download/win) sont installés (cocher *Add to PATH*).
2. Double-cliquer sur **`Installer.bat`** (dans `install/`).
3. Suivre l'assistant :
   - coller la clé OpenRouter, puis la clé Anthropic ;
   - choisir un identifiant (email) + un mot de passe (min 8 caractères).
4. À la fin : un raccourci **« Comparateur Courtier »** est créé sur le Bureau,
   l'app démarre et le navigateur s'ouvre sur http://localhost:8000.

Le compte et les clés sont stockés dans `.env` (jamais commité). Le mot de passe
n'est **jamais** stocké en clair : seul son hash PBKDF2 l'est.

## Utilisation quotidienne

- Double-clic sur le raccourci Bureau **« Comparateur Courtier »** → l'app démarre,
  navigateur ouvert sur http://localhost:8000.
- La fenêtre noire doit **rester ouverte** pendant l'utilisation (c'est le serveur).
- Pour arrêter : fermer la fenêtre noire.

## Mettre à jour

Double-clic sur le raccourci Bureau **« Comparateur — Mettre à jour »** (ou sur
`install\Mettre_a_jour.bat`). Le script :

1. arrête l'app si elle tourne ;
2. télécharge la dernière version depuis GitHub (`git pull`) ;
3. met à jour les dépendances (`pip install -r requirements.txt`) ;
4. relance l'app.

> Les clés et le compte du client sont **conservés** (le `.env` n'est pas touché).

## Où l'app est installée

`%LOCALAPPDATA%\ComparateurCourtier\app\comparateur-courtier\` — c'est un clone du
dépôt GitHub. Le client peut donc recevoir des mises à jour sans intervention.

## Coté exploitant (toi) — pousser une mise à jour

1. Modifie le code dans `comparateur-courtier/`.
2. Commit + push :
   ```bash
   cd C:\...\Claude\Projects\ai-installator
   git add comparateur-courtier
   git commit -m "comparateur: <ce qui change>"
   git push origin main
   ```
3. Les clients n'ont qu'à double-cliquer **« Mettre à jour »**.

**Ne JAMAIS** committer `.env` (clés + hash de mot de passe). Il est dans
`.gitignore` — vérifie quand même : `git status` ne doit pas le lister.

## Pannes courantes

| Symptôme | Cause / solution |
|---|---|
| `Python est introuvable` à l'install | Installer Python 3.10+ (cocher *Add to PATH*). |
| `Git est introuvable` à l'install | Installer Git pour Windows. |
| Page ne s'ouvre pas / « connexion refusée » | Attendre 5-10 s après le démarrage ; vérifier que la fenêtre noire est ouverte. |
| « Accès réservé » / boucle de connexion | Mot de passe oublié → supprimer `.env` et relancer `Installer.bat` pour recréer le compte. |
| `git pull a échoué` (mise à jour) | Fichier local modifié → `git stash` dans le dossier d'install puis réessayer. |
| Port 8000 occupé | Fermer l'autre app, ou éditer `demarrer.bat` (port 8000 → 8001). |
