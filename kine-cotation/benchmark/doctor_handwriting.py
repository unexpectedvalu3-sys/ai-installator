#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Filtre GRIBOUILLIS MEDICAL REEL (axe 1 bis) — transcription de mots manuscrits
de medecin, taux d'erreur caractere + exactitude mot.

    python benchmark/doctor_handwriting.py [N]      # defaut = tout le jeu (46)

Complement de rimes_handwriting.py. RIMES teste l'ecriture cursive FR sur des
lettres manuscrites PROPRES (registre assurance). Ici on teste l'autre extreme :
le « gribouillis de medecin » — des MOTS MANUSCRITS isoles (noms de medicaments,
termes cliniques). Jeu : MMMuzammil/Medical_Prescription_Handwritten_Words (HF,
licence MIT, 46 images de mots ; le NOM du fichier = la verite terrain).

⚠️ Ce que ce test mesure — et ne mesure PAS :
  - langue = ANGLAIS / latin (Amoxicillin, Paracetamol, Fever...). Il teste la
    lecture de mots medicaux manuscrits, PAS le francais (RIMES reste la ref FR).
  - unite = MOT ISOLE, pas une ligne. Metrique adaptee : CER (comme RIMES) POUR
    la comparabilite, + exactitude mot (le vrai KPI d'un nom de medicament : bon
    ou faux, un seul caractere faux = mauvais medicament).
  - 46 images : echantillon petit -> stats indicatives, pas de p90 fiable.

Provider = KINE_LLM_PROVIDER (identique a rimes_handwriting) :
    mistral | anthropic | selfhosted -> chat via llm._call_llm
    mistral-ocr                      -> endpoint OCR dedie /v1/ocr

Exemples :
    KINE_LLM_PROVIDER=selfhosted KINE_LLM_BASE_URL=http://localhost:11434/v1 \
    KINE_LLM_MODELE=qwen2.5vl:7b  python benchmark/doctor_handwriting.py
    KINE_LLM_PROVIDER=anthropic   python benchmark/doctor_handwriting.py
    KINE_LLM_PROVIDER=mistral-ocr MISTRAL_API_KEY=... python benchmark/doctor_handwriting.py

Sortie : stats console + detail par image dans benchmark/doctor/<tag>.csv
(idx;label;cer;exact;hyp ; meme ordre deterministe entre providers -> face-a-face
possible via doctor_aggregate.py).
"""

import base64
import csv
import io
import os
import re
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))  # pour importer rimes_handwriting
import rimes_handwriting as rh  # noqa: E402  (reutilise cer / _norm / _mistral_ocr / llm)

llm = rh.llm
cer = rh.cer
_norm = rh._norm

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

REPO = "MMMuzammil/Medical_Prescription_Handwritten_Words"  # HF dataset, licence MIT
OUT_DIR = Path(__file__).resolve().parent / "doctor"

SYST = ("You transcribe a SINGLE handwritten English medical word (a drug name, a "
        "dosage/frequency term, or a clinical term). Output ONLY the transcribed "
        "word, exactly as written, with no quotes, no added punctuation, no "
        "commentary and no prefix.")
INVITE = "Transcribe exactly the single handwritten word in this image."


def img_b64_blanc(img) -> str:
    """PNG b64, en APLATISSANT la transparence sur fond BLANC.

    Les images du jeu sont en RGBA (ecriture sombre sur fond transparent).
    rh.png_b64 fait convert('RGB') qui composite sur du NOIR -> texte noir sur
    fond noir = illisible. On composite donc explicitement sur blanc.
    """
    from PIL import Image
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        rgba = img.convert("RGBA")
        fond = Image.new("RGB", rgba.size, (255, 255, 255))
        fond.paste(rgba, mask=rgba.split()[-1])
        img = fond
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _cle_mot(s: str) -> str:
    """Normalisation pour l'exactitude MOT : minuscules, sans espace ni ponctuation."""
    return re.sub(r"[^a-z0-9]+", "", _norm(s).lower())


def transcrire(provider: str, modele: str, b64: str) -> str:
    """1 essai + 2 retries (rate limits / 5xx). Prompt ANGLAIS (mots medicaux)."""
    for essai in range(3):
        try:
            if provider == "mistral-ocr":
                return rh._mistral_ocr(b64, modele)
            return llm._call_llm(SYST, INVITE, ("image", "image/png", b64))
        except Exception as e:
            msg = str(e)
            if essai < 2 and any(k in msg for k in ("429", "500", "502", "503", "timed out", "timeout")):
                time.sleep(2 ** essai * 3)
                continue
            raise


def charger_jeu():
    """Telecharge les images du jeu HF (cache local) ; label = nom de fichier."""
    from huggingface_hub import hf_hub_download, list_repo_files
    from PIL import Image
    fichiers = [f for f in list_repo_files(REPO, repo_type="dataset")
                if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    fichiers.sort(key=lambda f: os.path.basename(f).lower())  # ordre deterministe
    jeu = []
    for f in fichiers:
        label = os.path.splitext(os.path.basename(f))[0]
        chemin = hf_hub_download(REPO, f, repo_type="dataset")
        jeu.append((label, Image.open(chemin)))
    return jeu


def main():
    provider = os.environ.get("KINE_LLM_PROVIDER", "mistral").strip().lower()
    if provider == "mistral-ocr":
        modele = os.environ.get("KINE_LLM_MODELE") or "mistral-ocr-latest"
    else:
        llm.verifier_cle()
        modele = llm.modele_actif()

    jeu = charger_jeu()
    n = int(sys.argv[1]) if len(sys.argv) > 1 else len(jeu)
    jeu = jeu[:n]

    tag = re.sub(r"[^a-z0-9]+", "-", f"{provider}_{modele}".lower()).strip("-")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUT_DIR / f"{tag}.csv"
    print(f"Provider : {provider} / {modele}   |   {len(jeu)} mots manuscrits ({REPO})")
    print(f"Detail -> {out_csv.relative_to(RACINE)}\n")

    rows, t0 = [], time.time()
    for i, (label, img) in enumerate(jeu, 1):
        typ = "chiffre" if label.isdigit() else "mot"
        try:
            hyp = _norm(transcrire(provider, modele, img_b64_blanc(img)))
        except Exception as e:
            print(f"  [erreur {i} '{label}'] {str(e)[:90]}")
            continue
        c = cer(label, hyp)
        ex = int(_cle_mot(hyp) == _cle_mot(label))
        rows.append({"idx": i, "label": label, "type": typ,
                     "cer": round(c, 4), "exact": ex, "hyp": hyp})
        if i % 10 == 0:
            done = [r for r in rows]
            print(f"  {i:>3}/{len(jeu)}  |  exact {sum(r['exact'] for r in done)/len(done):5.0%}  "
                  f"CER med {_med([r['cer'] for r in done]):5.1%}  "
                  f"({(time.time()-t0)/len(done):.1f}s/img)")

    if not rows:
        print("Aucun mot transcrit.")
        return
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["idx", "label", "type", "cer", "exact", "hyp"],
                           delimiter=";")
        w.writeheader()
        w.writerows(rows)
    _resume(provider, modele, rows)


def _med(xs):
    s = sorted(xs)
    return s[len(s) // 2] if s else 0.0


def _bloc(rows):
    """Sous-groupe -> (n, exact%, CER median, CER moyen PLAFONNE a 100%/item)."""
    n = len(rows)
    if not n:
        return (0, 0.0, 0.0, 0.0)
    acc = sum(r["exact"] for r in rows) / n
    cers = [r["cer"] for r in rows]
    moy_cap = sum(min(c, 1.0) for c in cers) / n  # CER brut inexploitable (mots isoles courts)
    return (n, acc, _med(cers), moy_cap)


def _resume(provider, modele, rows):
    mots = [r for r in rows if r["type"] == "mot"]
    chiffres = [r for r in rows if r["type"] == "chiffre"]
    n, acc, med, capm = _bloc(rows)
    print("\n" + "=" * 72)
    print(f"  {provider} / {modele}   —   {n} images manuscrites (ANGLAIS)")
    print(f"  KPI = exactitude MOT (un nom de medicament est bon ou faux) :")
    print(f"    MOTS (medicaments/termes) : {_bloc(mots)[1]:6.2%}   "
          f"({sum(r['exact'] for r in mots)}/{len(mots)})")
    print(f"    CHIFFRES isoles           : {_bloc(chiffres)[1]:6.2%}   "
          f"({sum(r['exact'] for r in chiffres)}/{len(chiffres)})   [glyphe seul, ambigu]")
    print(f"    TOUTES images             : {acc:6.2%}   ({sum(r['exact'] for r in rows)}/{n})")
    print(f"  CER median : {med:6.2%}   |   CER moyen (plafonne 100%/img) : {capm:6.2%}")
    print(f"  (CER brut non affiche : un glyphe court + sortie verbeuse -> CER >100%, "
          f"non representatif ; l'exactitude mot est le juge.)")
    print("=" * 72)


if __name__ == "__main__":
    main()
