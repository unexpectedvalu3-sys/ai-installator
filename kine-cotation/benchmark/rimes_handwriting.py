#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Filtre MANUSCRIT FR (axe 1) — transcription sur RIMES, taux d'erreur caractere.

    python benchmark/rimes_handwriting.py [N]        # defaut N=50 lignes

Repond a la question que le synthetique (tape) NE PEUT PAS tester : le modele
sait-il lire l'ECRITURE cursive francaise ? On prend N lignes manuscrites reelles
de RIMES (Teklia/RIMES-2011-line, licence MIT — lettres a des assureurs, registre
proche du notre), on demande au provider actif de les transcrire, et on mesure le
CER (Character Error Rate = distance d'edition / longueur de reference).

Provider = KINE_LLM_PROVIDER :
    mistral | anthropic | selfhosted  -> appel chat via llm._call_llm
    mistral-ocr                       -> endpoint OCR DEDIE /v1/ocr (mistral-ocr-latest)

Exemples :
    KINE_LLM_PROVIDER=selfhosted KINE_LLM_BASE_URL=http://localhost:11434/v1 \
    KINE_LLM_MODELE=qwen2.5vl:7b  python benchmark/rimes_handwriting.py 200
    KINE_LLM_PROVIDER=mistral-ocr MISTRAL_API_KEY=... python benchmark/rimes_handwriting.py 50

Sortie : stats console + detail par ligne dans benchmark/rimes/<tag>.csv (rejouable,
sliceable pour comparer les providers sur le meme sous-ensemble de lignes).
"""

import base64
import csv
import io
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "prototype"))
import llm  # noqa: E402

SYST = ("Tu transcris du texte MANUSCRIT en francais. Rends UNIQUEMENT le texte "
        "transcrit, exactement, sans guillemets, sans commentaire, sans prefixe.")
INVITE = "Transcris exactement le texte manuscrit de cette image."
OUT_DIR = Path(__file__).resolve().parent / "rimes"


def cer(ref: str, hyp: str) -> float:
    ref, hyp = ref.strip(), hyp.strip()
    if not ref:
        return 0.0 if not hyp else 1.0
    prev = list(range(len(hyp) + 1))
    for i, rc in enumerate(ref, 1):
        cur = [i] + [0] * len(hyp)
        for j, hc in enumerate(hyp, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (rc != hc))
        prev = cur
    return prev[-1] / len(ref)


def _norm(s: str) -> str:
    s = re.sub(r"\s+", " ", (s or "").strip())
    return s.strip('"\'` ')


def png_b64(img) -> str:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _mistral_ocr(b64: str, modele: str) -> str:
    """Endpoint OCR DEDIE de Mistral (/v1/ocr) — rend du markdown, pas du chat."""
    key = os.environ.get("MISTRAL_API_KEY", "")
    if not key:
        raise llm.LLMIndisponible("MISTRAL_API_KEY absente (provider mistral-ocr).")
    payload = {"model": modele, "document": {"type": "image_url",
               "image_url": f"data:image/png;base64,{b64}"}}
    req = urllib.request.Request("https://api.mistral.ai/v1/ocr",
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json",
                                          "Authorization": f"Bearer {key}"})
    r = json.loads(urllib.request.urlopen(req, timeout=120).read())
    return " ".join(p.get("markdown", "") for p in r.get("pages", []))


def transcrire(provider: str, modele: str, b64: str) -> str:
    """Un essai + 2 retries avec backoff (rate limits / 5xx cloud)."""
    for essai in range(3):
        try:
            if provider == "mistral-ocr":
                return _mistral_ocr(b64, modele)
            return llm._call_llm(SYST, INVITE, ("image", "image/png", b64))
        except Exception as e:
            msg = str(e)
            if essai < 2 and any(k in msg for k in ("429", "500", "502", "503", "timed out", "timeout")):
                time.sleep(2 ** essai * 3)
                continue
            raise


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    provider = os.environ.get("KINE_LLM_PROVIDER", "mistral").strip().lower()
    if provider == "mistral-ocr":
        modele = os.environ.get("KINE_LLM_MODELE") or "mistral-ocr-latest"
    else:
        llm.verifier_cle()
        modele = llm.modele_actif()

    from datasets import load_dataset
    ds = load_dataset("Teklia/RIMES-2011-line", split="test", streaming=True)

    tag = re.sub(r"[^a-z0-9]+", "-", f"{provider}_{modele}".lower()).strip("-")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUT_DIR / f"{tag}.csv"
    print(f"Provider : {provider} / {modele}   |   cible {n} lignes RIMES")
    print(f"Detail -> {out_csv.relative_to(RACINE)}\n")

    cers, rows, t0 = [], [], time.time()
    for ex in ds:
        if len(cers) >= n:
            break
        ref = _norm(ex["text"])
        if len(ref) < 15:
            continue
        try:
            hyp = _norm(transcrire(provider, modele, png_b64(ex["image"])))
        except Exception as e:
            print(f"  [erreur ligne {len(cers)+1}] {str(e)[:90]}")
            continue
        c = cer(ref, hyp)
        cers.append(c)
        rows.append({"idx": len(cers), "cer": round(c, 4), "ref": ref, "hyp": hyp})
        if len(cers) % 10 == 0:
            moy = sum(cers) / len(cers)
            print(f"  {len(cers):>3} lignes  |  CER moyen courant {moy:5.1%}  "
                  f"({(time.time()-t0)/len(cers):.1f}s/ligne)")

    if not cers:
        print("Aucune ligne transcrite.")
        return
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["idx", "cer", "ref", "hyp"], delimiter=";")
        w.writeheader()
        w.writerows(rows)

    srt = sorted(cers)
    moy = sum(cers) / len(cers)
    p = lambda q: srt[min(len(srt) - 1, int(q * len(srt)))]
    print("\n" + "=" * 62)
    print(f"  {provider} / {modele}   —   {len(cers)} lignes")
    print(f"  CER moyen   : {moy:6.2%}   (precision caractere ~ {1-moy:.2%})")
    print(f"  CER median  : {p(0.5):6.2%}   |   p90 : {p(0.9):6.2%}   |   max : {srt[-1]:6.2%}")
    print(f"  lignes <5% : {sum(c<.05 for c in cers):>3}/{len(cers)}   "
          f"<10% : {sum(c<.10 for c in cers)}/{len(cers)}   "
          f"<20% : {sum(c<.20 for c in cers)}/{len(cers)}")
    print("=" * 62)


if __name__ == "__main__":
    main()
