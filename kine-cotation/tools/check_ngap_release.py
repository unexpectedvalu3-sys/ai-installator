#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veille NGAP — detecte une nouvelle version du tableau SNMKR et DIFFE contre la base.

    python tools/check_ngap_release.py            # rapport console
    python tools/check_ngap_release.py --json     # sortie machine (CI)

Codes de sortie :
    0 = base a jour        2 = nouvelle version detectee (drift)      1 = erreur

POURQUOI CE SCRIPT EXISTE
-------------------------
La base NGAP est a la fois l'actif et le passif du produit : si elle est en retard,
le kine cote faux ET la justification generee ATTESTE le mauvais bareme. Or le
bareme bouge vite : v15a -> v19 en 7 mois, trois bareme en huit mois
(01/01/2026, 28/05/2026, 01/09/2026).

CE QUE CE SCRIPT NE FAIT PAS, ET POURQUOI
-----------------------------------------
Il ne met PAS a jour la base et ne publie RIEN tout seul. Le plan projet classe
« donnees NGAP fausses -> mauvaise cotation -> on cause un indu » en risque
CRITIQUE. Une chaine scrape-PDF -> release automatique pousserait des coefficients
non verifies chez tous les kines, et la preuve les attesterait.

Concretement, un diff (code, coefficient, tarif) est fiable — mais il ne capture pas :
  - a QUEL acte rattacher un triplet (il y a plusieurs TER, plusieurs NMI…) ;
  - les actes ajoutes/supprimes, les libelles remanies ;
  - les seuils DAP et les referentiels HAS ;
  - les champs editoriaux (article, region, chirurgie, referentiel).
Ce sont des jugements humains. Le script leve l'alarme et montre l'ecart ;
Enzo tranche et bump la base a la main (comme le 17/07/2026 : 3 lignes sur 82).

Ensuite seulement, le build + la release de l'app peuvent etre automatiques.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
KB_PATH = RACINE / "knowledge_base" / "ngap_kine.json"
PAGE_SNMKR = "https://snmkr.fr/boite-a-outils/la-ngap/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; KineCotation-veille/1.0)"}

# "TER 9,79 ‧ 21,64 €" — le separateur du PDF est U+2027, le tarif parfois colle au €
LIGNE_TARIF = re.compile(r"\b([A-Z]{2,3})\s+(\d{1,2}(?:,\d{1,2})?)\s*[‧·•]\s*(\d{1,3},\d{2})\s*€")
LIEN_PDF = re.compile(r"https?://[^\s\"']*tableau-ngap[_-]v(\d+)([a-z]?)\.pdf", re.I)


def _get(url: str) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45).read()


def version_tuple(num: str, suffixe: str):
    return (int(num), suffixe or "")


def derniere_version_publiee():
    """Rend (version_str, url) du tableau le plus recent publie par le SNMKR."""
    html = _get(PAGE_SNMKR).decode("utf-8", "replace")
    trouves = [(version_tuple(n, s), f"v{n}{s}", u) for u, n, s in
               ((m.group(0), m.group(1), m.group(2)) for m in LIEN_PDF.finditer(html))]
    if not trouves:
        raise RuntimeError(f"Aucun lien tableau-ngap trouve sur {PAGE_SNMKR} "
                           "(la page a peut-etre change de structure — verifier a la main).")
    trouves.sort(key=lambda t: t[0])
    _, ver, url = trouves[-1]
    return ver, url


def version_de_la_base(kb) -> str:
    m = re.search(r"tableau-ngap[_-](v\d+[a-z]?)\.pdf", kb["_meta"].get("source_url", ""), re.I)
    if m:
        return m.group(1).lower()
    m = re.search(r"\bv(\d+[a-z]?)\b", kb["_meta"].get("source", ""), re.I)
    return f"v{m.group(1)}".lower() if m else "?"


def _pdftotext() -> str:
    exe = shutil.which("pdftotext")
    if exe:
        return exe
    # poppler installe par winget mais pas toujours dans le PATH du shell courant
    for p in Path("C:/Users").glob("*/AppData/Local/Microsoft/WinGet/Packages/"
                                   "oschwartz10612.Poppler*/**/bin/pdftotext.exe"):
        return str(p)
    raise RuntimeError("pdftotext introuvable — installer poppler "
                       "(winget install --id oschwartz10612.Poppler / apt-get install poppler-utils)")


def triplets_du_pdf(url: str):
    """Rend {(code, coef): tarif} lus dans le PDF publie."""
    with tempfile.TemporaryDirectory() as d:
        pdf = Path(d) / "t.pdf"
        pdf.write_bytes(_get(url))
        txt = subprocess.run([_pdftotext(), "-layout", "-enc", "UTF-8", str(pdf), "-"],
                             capture_output=True, text=True, encoding="utf-8", errors="replace")
        if txt.returncode != 0:
            raise RuntimeError(f"pdftotext a echoue : {txt.stderr[:200]}")
    out = {}
    for code, coef, tarif in LIGNE_TARIF.findall(txt.stdout):
        out[(code, float(coef.replace(",", ".")))] = float(tarif.replace(",", "."))
    return out


def triplets_de_la_base(kb):
    """Rend {(code, coef): tarif} de la base, cotations FUTURES incluses.

    Les cotations datees (_a_partir_du/_futur, ex. les 5 NMI qui prennent +1 point
    au 01/09) figurent dans le PDF publie. Sans les inclure ici, le veilleur les
    signalerait comme « absentes de la base » a chaque passage : une fausse alarme
    permanente, qui apprend a ignorer l'outil.
    """
    out = {}
    for section in ("actes", "bilans", "supplements"):
        for a in kb.get(section, []):
            out[(a["code"], float(a["coefficient"]))] = float(a["tarif_metropole"])
            f = a.get("_futur")
            if f:
                out[(a["code"], float(f["coefficient"]))] = float(f["tarif_metropole"])
    return out


def diff(pdf: dict, base: dict):
    nouveaux = sorted(k for k in pdf if k not in base)
    disparus = sorted(k for k in base if k not in pdf)
    modifies = sorted((k, base[k], pdf[k]) for k in pdf if k in base and abs(pdf[k] - base[k]) >= 0.005)
    return nouveaux, disparus, modifies


def main():
    ap = argparse.ArgumentParser(description="Veille NGAP — detection de drift (ne publie rien).")
    ap.add_argument("--json", action="store_true", help="sortie machine")
    args = ap.parse_args()

    kb = json.loads(KB_PATH.read_text(encoding="utf-8"))
    v_base = version_de_la_base(kb)
    v_pub, url = derniere_version_publiee()
    drift = v_base != v_pub

    rapport = {"version_base": v_base, "version_publiee": v_pub, "url": url,
               "base_version_interne": kb["_meta"]["version"], "drift": drift,
               "nouveaux": [], "disparus": [], "modifies": []}

    if drift:
        try:
            n, d, m = diff(triplets_du_pdf(url), triplets_de_la_base(kb))
            rapport["nouveaux"] = [f"{c} {co}" for c, co in n]
            rapport["disparus"] = [f"{c} {co}" for c, co in d]
            rapport["modifies"] = [{"cle": f"{c} {co}", "base_eur": av, "publie_eur": ap_}
                                   for (c, co), av, ap_ in m]
        except Exception as e:
            rapport["erreur_diff"] = str(e)

    if args.json:
        print(json.dumps(rapport, ensure_ascii=False, indent=2))
        return 2 if drift else 0

    print(f"\n  Base locale   : {v_base}  (ngap_kine.json v{kb['_meta']['version']})")
    print(f"  Publie SNMKR  : {v_pub}")
    print(f"  {url}\n")
    if not drift:
        print("  A JOUR — rien a faire.\n")
        return 0

    print(f"  /!\\ NOUVELLE VERSION : {v_base} -> {v_pub}\n")
    if "erreur_diff" in rapport:
        print(f"  Diff impossible ({rapport['erreur_diff']}) — comparer a la main.\n")
        return 2
    if rapport["modifies"]:
        print("  TARIFS MODIFIES :")
        for x in rapport["modifies"]:
            print(f"    {x['cle']:<12} {x['base_eur']:>6.2f} EUR  ->  {x['publie_eur']:>6.2f} EUR")
    if rapport["nouveaux"]:
        print(f"\n  ABSENTS DE LA BASE ({len(rapport['nouveaux'])}) : {', '.join(rapport['nouveaux'][:12])}")
    if rapport["disparus"]:
        print(f"\n  PLUS DANS LE PDF ({len(rapport['disparus'])}) : {', '.join(rapport['disparus'][:12])}")
    if not (rapport["modifies"] or rapport["nouveaux"] or rapport["disparus"]):
        print("  Aucun ecart de tarif — la nouvelle version ne touche peut-etre que la mise en forme,\n"
              "  les seuils DAP ou les libelles. VERIFIER A LA MAIN (le diff ne lit que code+coef+tarif).")
    print("\n  --> Le diff n'est PAS une validation. Verifier le PDF, corriger ngap_kine.json,\n"
          "      bump _meta.version + _changelog + source_url, puis commiter.\n"
          "      La release de l'app se declenchera toute seule sur ce commit.\n")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"[erreur] {exc}", file=sys.stderr)
        sys.exit(1)
