#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Filtre MANUSCRIT FR (axe 1) — transcription sur RIMES, taux d'erreur caractere.

    python benchmark/rimes_handwriting.py [N]        # defaut N=15 lignes

Repond a la question que le synthetique (tape) NE PEUT PAS tester : le modele
sait-il lire l'ECRITURE cursive francaise ? On prend N lignes manuscrites reelles
de RIMES (Teklia/RIMES-2011-line, licence MIT — lettres a des assureurs, registre
proche du notre), on demande au provider actif de les transcrire, et on mesure le
CER (Character Error Rate = distance d'edition / longueur de reference).

C'est un 1er FILTRE des candidats voie B (11_VOIE_B_OCR_OPEN.md) AVANT de payer du
GPU ou d'attendre les vraies ordonnances : un modele qui ne lit pas le cursif FR
ici ne le lira pas sur une ordonnance manuscrite.

Provider : KINE_LLM_PROVIDER (mistral | anthropic | selfhosted), comme le benchmark
metier. Ex. local gratuit :
    KINE_LLM_PROVIDER=selfhosted KINE_LLM_BASE_URL=http://localhost:11434/v1 \
    KINE_LLM_MODELE=qwen2.5vl:7b python benchmark/rimes_handwriting.py 15
"""

import base64
import io
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "prototype"))
import llm  # noqa: E402

SYST = ("Tu transcris du texte MANUSCRIT en francais. Rends UNIQUEMENT le texte "
        "transcrit, exactement, sans guillemets, sans commentaire, sans prefixe.")
INVITE = "Transcris exactement le texte manuscrit de cette image."


def cer(ref: str, hyp: str) -> float:
    """Character Error Rate = distance de Levenshtein(ref, hyp) / len(ref)."""
    ref, hyp = ref.strip(), hyp.strip()
    if not ref:
        return 0.0 if not hyp else 1.0
    # Levenshtein (DP sur 2 lignes)
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


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    try:
        llm.verifier_cle()
    except llm.LLMIndisponible as e:
        print(f"[!] {e}")
        sys.exit(1)

    from datasets import load_dataset
    ds = load_dataset("Teklia/RIMES-2011-line", split="test", streaming=True)

    print(f"Provider : {llm.provider_actif()} / {llm.modele_actif()}   |   {n} lignes RIMES\n")
    total, cers, exemples = 0, [], []
    for ex in ds:
        if total >= n:
            break
        ref = _norm(ex["text"])
        if len(ref) < 15:      # ignore les fragments trop courts
            continue
        try:
            hyp = _norm(llm._call_llm(SYST, INVITE, ("image", "image/png", png_b64(ex["image"]))))
        except Exception as e:
            print(f"  [erreur] {str(e)[:80]}")
            continue
        c = cer(ref, hyp)
        cers.append(c)
        total += 1
        if len(exemples) < 3:
            exemples.append((ref, hyp, c))
        print(f"  ligne {total:>2}  CER={c:5.1%}")

    if not cers:
        print("Aucune ligne transcrite.")
        return
    moy = sum(cers) / len(cers)
    print("\n" + "=" * 60)
    print(f"  CER moyen   : {moy:5.1%}   (precision caractere ~ {1 - moy:.1%})")
    print(f"  CER median  : {sorted(cers)[len(cers) // 2]:5.1%}")
    print(f"  lignes CER<10% : {sum(c < .10 for c in cers)}/{len(cers)}")
    print("=" * 60)
    print("\n  Exemples (ref -> transcription) :")
    for ref, hyp, c in exemples:
        print(f"   [{c:.0%}] REF : {ref[:70]}")
        print(f"         HYP : {hyp[:70]}")
    print("\n  Lecture : CER < ~15-20% = lit correctement le cursif FR (candidat voie B viable).")
    print("            CER eleve = OCR reserve au tape, saisie clic pour le manuscrit.")


if __name__ == "__main__":
    main()
