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

Providers : mistral (defaut) · anthropic · selfhosted (voie B, endpoint OpenAI-compat).
Mistral ET selfhosted passent par le meme appel HTTP OpenAI-compatible (urllib, sans
SDK) : le SDK mistralai s'installe de facon fragile ici (Defender).

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
    "mistral": "mistral-medium-latest",   # multimodal ; pixtral-* indispo sur le compte teste
    "anthropic": "claude-opus-4-8",
    # VOIE B (souverain) : modele OCR/vision OPEN auto-heberge, servi via une API
    # OpenAI-compatible (vLLM) sur GPU dans le perimetre HDS. La donnee ne sort pas
    # de notre infra. Defaut = Qwen2.5-VL-7B (Apache 2.0, manuscrit-capable). Voir
    # 11_VOIE_B_OCR_OPEN.md. Modele et endpoint surchargeables par env.
    "selfhosted": "Qwen/Qwen2.5-VL-7B-Instruct",
}

# Ce que verifier_cle() controle pour chaque provider (cle API, ou endpoint pour
# l'auto-heberge qui peut ne PAS exiger de cle).
CLES_ENV = {
    "mistral": "MISTRAL_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "selfhosted": "KINE_LLM_BASE_URL",
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
        if provider == "selfhosted":
            raise LLMIndisponible(
                "KINE_LLM_BASE_URL absente (provider selfhosted).\n"
                "  -> pointer vers l'endpoint OpenAI-compatible du modele auto-heberge, ex :\n"
                "     set KINE_LLM_BASE_URL=http://<gpu-hds>:8000/v1\n"
                "  (cle optionnelle : KINE_LLM_API_KEY ; modele : KINE_LLM_MODELE)"
            )
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


def _post_openai_compat(base: str, api_key: str, systeme: str, invite: str,
                        source: tuple, modele: str, json_object: bool = False) -> str:
    """Appel /chat/completions OpenAI-compatible via urllib (ZERO SDK).

    Sert Mistral cloud (api.mistral.ai/v1) ET l'auto-heberge (vLLM) : meme protocole.
    Choix d'urllib plutot que le SDK mistralai : ce dernier s'installe de facon
    fragile sur cette machine (Defender corrompt l'extraction du wheel) -> un appel
    HTTP direct, lisible et auditable, supprime la dependance et le point de casse.
    """
    import json as _json
    import urllib.request

    kind, media_type, data = source
    if kind == "document":
        raise LLMIndisponible("PDF non supporte (convertir en PNG/JPG). Voir 06_PROVIDER_IA.md.")

    payload = {
        "model": modele,
        "max_tokens": 1500,
        "temperature": 0,  # OCR = extraction deterministe
        "messages": [
            {"role": "system", "content": systeme},
            {"role": "user", "content": [
                {"type": "text", "text": invite},
                {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{data}"}},
            ]},
        ],
    }
    if json_object:
        payload["response_format"] = {"type": "json_object"}
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions",
        data=_json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    if api_key:
        req.add_header("Authorization", f"Bearer {api_key}")
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            resp = _json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:300]
        raise LLMIndisponible(f"HTTP {e.code} de {base} : {detail}") from e
    except Exception as e:
        raise LLMIndisponible(f"Endpoint injoignable ({base}) : {e}") from e
    try:
        return resp["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError):
        raise LLMIndisponible(f"Reponse inattendue : {str(resp)[:200]}")


def _appel_mistral(systeme: str, invite: str, source: tuple, modele: str) -> str:
    """Mistral cloud via son API OpenAI-compatible (plus de SDK mistralai)."""
    return _post_openai_compat(
        "https://api.mistral.ai/v1", os.environ.get("MISTRAL_API_KEY", ""),
        systeme, invite, source, modele, json_object=True)


def _appel_selfhosted(systeme: str, invite: str, source: tuple, modele: str) -> str:
    """Modele OPEN auto-heberge (voie B) via endpoint OpenAI-compatible (vLLM)."""
    base = os.environ.get("KINE_LLM_BASE_URL", "")
    if not base:
        raise LLMIndisponible("KINE_LLM_BASE_URL absente (provider selfhosted).")
    return _post_openai_compat(
        base, os.environ.get("KINE_LLM_API_KEY", ""),
        systeme, invite, source, modele)


_APPELS = {"anthropic": _appel_anthropic, "mistral": _appel_mistral,
           "selfhosted": _appel_selfhosted}


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
