# -*- coding: utf-8 -*-
"""Helpers LLM partagés par le comparateur et la fiche DDA.

Extraits de l'app Modul'R (module `extract.py`) — on ne garde ici que les deux
fonctions dont dépendent `compare.py` et `fichedda.py` :

- `_call_llm`  : appel Claude (vision). Provider abstrait : pour la prod RGPD on
                 pourra basculer sur Mistral EU en ne touchant qu'à cette fonction.
- `_parse_json`: parse tolérant du JSON renvoyé par un LLM (gère les ``` fences et
                 le texte autour).

Le comparateur (`compare.py`) appelle en plus OpenRouter/GLM directement pour le
gros volume ; ces deux helpers-ci servent la prose fine (courrier de synthèse,
justification du conseil), toujours sur Claude.
"""
import os
import json

MODEL = os.environ.get("LLM_MODEL", "claude-sonnet-4-6")


def _call_llm(blocks, prompt, max_tokens=2000):
    """blocks = liste de blocs de contenu Anthropic (documents/images), éventuellement
    vide pour une requête texte seule. Renvoie le texte concaténé de la réponse."""
    from anthropic import Anthropic
    client = Anthropic()
    msg = client.messages.create(
        model=MODEL, max_tokens=max_tokens,
        messages=[{"role": "user", "content": blocks + [{"type": "text", "text": prompt}]}],
    )
    return "".join(b.text for b in msg.content if b.type == "text")


def _parse_json(text):
    """Parse le JSON d'une réponse LLM, tolérant aux ``` fences et au texte autour."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    if text and text[0] != "{":
        i = text.find("{")
        j = text.rfind("}")
        if i != -1 and j != -1 and j > i:
            text = text[i:j + 1]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Les LLM laissent parfois des virgules en fin de liste/objet (ex. "," ou ",//"").
        import re
        cleaned = re.sub(r",(\s*[}\]])", r"\1", text)
        cleaned = re.sub(r"//.*?$", "", cleaned, flags=re.MULTILINE)  # commentaires // ligne
        return json.loads(cleaned)
