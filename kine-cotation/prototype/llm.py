#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KinéCotation — couche PROVIDER IA abstraite.

Applique le pattern impose par CLAUDE.md §4.2 (« Provider IA abstrait, basculable
Mistral EU / local pour la prod RGPD ») : le reste du code ne connait AUCUN
fournisseur. Un seul point de bascule = cette fonction.

Role du LLM (rappel CLAUDE.md §4.1) : PERCEPTION uniquement. Il rend du texte /
du JSON de faits. Il ne calcule JAMAIS un coefficient ni un tarif : c'est
cotation_engine.py + ngap_kine.json (deterministe) qui cotent.

Choix du provider :
    KINE_LLM_PROVIDER = mistral (defaut) | anthropic
    KINE_LLM_MODELE   = surcharge optionnelle du modele

Cles (jamais commitees, jamais saisies par l'assistant) :
    MISTRAL_API_KEY      -> https://console.mistral.ai
    ANTHROPIC_API_KEY    -> https://console.anthropic.com

⚠️ RGPD — etat au 2026-07-17 (a re-verifier avant toute mise en production) :
  - Mistral « La Plateforme » (cloud) n'est PAS qualifiee HDS. Mistral heberge a
    Paris chez Scaleway (lui certifie HDS), mais l'hebergeur certifie ne transfere
    PAS sa qualification au service.
  - Le Zero Data Retention (ZDR), qui porte l'argument « pas de stockage -> pas
    d'hebergement -> HDS sans objet », est reserve a l'abonnement ENTERPRISE.
  - Donc : benchmark OK sur ordonnances ANONYMISEES (cf. benchmark/00_PROTOCOLE
    §0.1 : caviarder nom/prenom/date de naissance/NIR). Production sur donnees
    reelles = contrat Enterprise + ZDR + DPA art. 28 requis.
  - Ce fichier ne tranche pas le droit : il rend la bascule possible et tracable.
"""

import os

PROVIDER_DEFAUT = "mistral"

MODELES_DEFAUT = {
    # Vision + raisonnement en un appel : meme forme que l'appel Claude d'origine
    # (image -> JSON structure), donc comparable a iso-pipeline dans le benchmark.
    "mistral": "pixtral-large-latest",
    "anthropic": "claude-opus-4-8",
}

CLES_ENV = {
    "mistral": "MISTRAL_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
}


class LLMIndisponible(RuntimeError):
    """Provider mal configure (cle absente, SDK manquant, format non supporte)."""


def provider_actif() -> str:
    p = os.environ.get("KINE_LLM_PROVIDER", PROVIDER_DEFAUT).strip().lower()
    if p not in MODELES_DEFAUT:
        raise LLMIndisponible(
            f"Provider inconnu : {p!r}. Valeurs possibles : {', '.join(MODELES_DEFAUT)}."
        )
    return p


def modele_actif(provider: str = None) -> str:
    provider = provider or provider_actif()
    return os.environ.get("KINE_LLM_MODELE") or MODELES_DEFAUT[provider]


def verifier_cle(provider: str = None) -> None:
    provider = provider or provider_actif()
    var = CLES_ENV[provider]
    if not os.environ.get(var):
        raise LLMIndisponible(
            f"{var} absente de l'environnement (provider actif : {provider}).\n"
            f"  -> creer la cle sur la console du fournisseur, puis :  set {var}=..."
        )


def _appel_anthropic(systeme: str, invite: str, source: tuple, modele: str) -> str:
    try:
        import anthropic
    except ImportError as e:
        raise LLMIndisponible("pip install anthropic") from e

    kind, media_type, data = source
    bloc = {
        "type": "document" if kind == "document" else "image",
        "source": {"type": "base64", "media_type": media_type, "data": data},
    }
    resp = anthropic.Anthropic().messages.create(
        model=modele,
        max_tokens=1500,
        system=systeme,
        messages=[{"role": "user", "content": [bloc, {"type": "text", "text": invite}]}],
    )
    return next((b.text for b in resp.content if b.type == "text"), "")


def _appel_mistral(systeme: str, invite: str, source: tuple, modele: str) -> str:
    try:
        from mistralai import Mistral
    except ImportError as e:
        raise LLMIndisponible("pip install mistralai") from e

    kind, media_type, data = source
    if kind == "document":
        # Le chat vision Mistral attend une image. Un PDF passe par l'endpoint OCR
        # dedie (client.ocr.process / mistral-ocr-latest) = pipeline en 2 temps,
        # non implemente ici. Voir 06_PROVIDER_IA.md.
        raise LLMIndisponible(
            "PDF non supporte par le provider mistral dans cette version "
            "(convertir en PNG/JPG, ou utiliser le provider anthropic)."
        )

    contenu = [
        {"type": "text", "text": invite},
        {"type": "image_url", "image_url": f"data:{media_type};base64,{data}"},
    ]
    resp = Mistral(api_key=os.environ["MISTRAL_API_KEY"]).chat.complete(
        model=modele,
        max_tokens=1500,
        response_format={"type": "json_object"},  # force un objet JSON valide
        messages=[
            {"role": "system", "content": systeme},
            {"role": "user", "content": contenu},
        ],
    )
    return resp.choices[0].message.content or ""


_APPELS = {"anthropic": _appel_anthropic, "mistral": _appel_mistral}


def _call_llm(systeme: str, invite: str, source: tuple,
              provider: str = None, modele: str = None) -> str:
    """
    Appelle le provider actif et rend la reponse BRUTE (texte).

    systeme  : consigne systeme
    invite   : message utilisateur
    source   : (kind, media_type, data_b64) — kind = 'image' | 'document'
    """
    provider = provider or provider_actif()
    modele = modele or modele_actif(provider)
    verifier_cle(provider)
    return _APPELS[provider](systeme, invite, source, modele)


if __name__ == "__main__":
    p = provider_actif()
    print(f"Provider actif : {p}")
    print(f"Modele         : {modele_actif(p)}")
    print(f"Cle {CLES_ENV[p]:<18}: ", end="")
    try:
        verifier_cle(p)
        print("OK")
    except LLMIndisponible as e:
        print(f"MANQUANTE\n\n{e}")
