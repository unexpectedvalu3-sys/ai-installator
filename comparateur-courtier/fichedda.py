# -*- coding: utf-8 -*-
"""Générateur de fiche DDA (devoir de conseil — Code des assurances L521-1 et s.).

- Infos cabinet : config éditable persistée (data/cabinet.json), pré-remplie avec
  ce qu'on sait + champs à remplir (ORIAS…).
- Justification du conseil : rédigée par l'IA (Claude/Sonnet — rédactionnel fin).
La mise en page de la fiche imprimable est côté page (static/fiche-dda.html).
"""
import os, json
from pathlib import Path

import llm  # helper _call_llm (Claude/Sonnet) — voir llm.py

BASE = Path(__file__).parent
DATA = Path(os.environ.get("DATA_DIR", BASE / "data"))
CABINET_FILE = DATA / "cabinet.json"

# Valeurs par défaut GÉNÉRIQUES : les champs propres au cabinet (raison sociale,
# adresse, ORIAS, conseillers…) sont VIDES — à remplir par le courtier via l'écran
# « Cabinet » (persisté dans data/cabinet.json). Seuls restent pré-remplis les
# éléments réglementaires nationaux (ACPR, médiation) et les formulations types,
# que le courtier peut ajuster.
CABINET_DEFAUT = {
    "raison_sociale": "",
    "adresse": "",
    "telephone": "",
    "email": "",
    "statut": "Courtier en assurances (intermédiaire immatriculé à l'ORIAS)",
    "orias": "",
    "acpr": "ACPR — 4 Place de Budapest, CS 92459, 75436 Paris Cedex 09",
    "mediateur": "La Médiation de l'Assurance — TSA 50110, 75441 Paris Cedex 09 — mediation-assurance.org",
    "reclamation": "Toute réclamation peut être adressée par écrit au cabinet. À défaut de réponse satisfaisante sous deux mois, le médiateur de l'assurance ci-dessus peut être saisi.",
    "liens_assureurs": "Le cabinet ne détient aucune participation directe ou indirecte ≥ 10 % chez une entreprise d'assurance, et aucune entreprise d'assurance ne détient ≥ 10 % du cabinet.",
    "remuneration": "Au titre de ce contrat, le cabinet est rémunéré par des commissions incluses dans la prime/cotisation versée à l'assureur.",
    "conseillers": "",
}


def load_cabinet():
    cab = dict(CABINET_DEFAUT)
    if CABINET_FILE.exists():
        try:
            cab.update(json.loads(CABINET_FILE.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            pass
    return cab


def save_cabinet(data):
    cab = dict(CABINET_DEFAUT)
    cab.update({k: v for k, v in (data or {}).items() if k in CABINET_DEFAUT})
    CABINET_FILE.parent.mkdir(parents=True, exist_ok=True)
    CABINET_FILE.write_text(json.dumps(cab, ensure_ascii=False, indent=2), encoding="utf-8")
    return cab


PROMPT_CONSEIL = """Tu es l'assistant d'un cabinet de courtage en assurance. Rédige la
JUSTIFICATION DU CONSEIL d'une fiche DDA (devoir de conseil, Code des assurances),
en français, ton professionnel et juridiquement prudent.

Besoins et exigences exprimés par le client :
{besoins}

Produit recommandé : {reco}
Produits écartés (le cas échéant) : {ecartes}

Consignes :
- 130 à 200 mots, un à deux paragraphes, sans titre.
- Relie EXPLICITEMENT chaque besoin exprimé à une caractéristique du produit recommandé.
- Reste factuel ; ne mentionne aucune garantie qui n'est pas fournie ; n'invente pas de chiffres.
- Si des produits sont écartés, explique brièvement pourquoi en une phrase.
- Termine par une phrase rappelant que le client reste libre de son choix et a reçu l'information nécessaire.
Réponds UNIQUEMENT par le texte de la justification, sans préambule ni guillemets.
"""


def rediger_conseil(besoins, reco, ecartes=""):
    prompt = PROMPT_CONSEIL.format(
        besoins=(besoins or "—").strip(),
        reco=(reco or "—").strip(),
        ecartes=(ecartes or "—").strip(),
    )
    txt = llm._call_llm([], prompt, max_tokens=900)
    return txt.strip()
