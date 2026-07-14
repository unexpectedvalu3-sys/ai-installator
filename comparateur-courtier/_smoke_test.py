# -*- coding: utf-8 -*-
"""Smoke test hors-ligne (aucune clé API) : auth, routing, fail-closed, logique.
Lancer : .venv\\Scripts\\python _smoke_test.py"""
import os, base64, hashlib, secrets

def make_hash(pw, iterations=200_000):
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, iterations)
    return f"pbkdf2${iterations}${base64.b64encode(salt).decode()}${base64.b64encode(dk).decode()}"

# Config d'auth AVANT d'importer l'app (auth lit l'env à l'import).
os.environ["APP_USER"] = "enzo@test.fr"
os.environ["APP_PASSWORD_HASH"] = make_hash("motdepasse123")
os.environ["SECRET_KEY"] = "clef-de-test-" + "x" * 32
os.environ["COOKIE_INSECURE"] = "1"
os.environ["DATA_DIR"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_data")

from fastapi.testclient import TestClient
import app as appmod
import auth, llm, compare

HTML = {"accept": "text/html,application/xhtml+xml"}
c = TestClient(appmod.app)
R = []
def check(name, cond, extra=""):
    R.append((name, bool(cond), extra))

r = c.get("/healthz");                              check("healthz 200", r.status_code == 200, r.status_code)
r = c.get("/", headers=HTML, follow_redirects=False)
check("/ sans session -> 303 /login", r.status_code == 303 and r.headers.get("location") == "/login", f"{r.status_code} {r.headers.get('location')}")
r = c.get("/login");                                check("/login 200 + contenu", r.status_code == 200 and "Espace courtier" in r.text, r.status_code)
r = c.post("/login", data={"user": "enzo@test.fr", "password": "faux"}, follow_redirects=False)
check("login mauvais mdp -> 401", r.status_code == 401, r.status_code)
r = c.post("/login", data={"user": "enzo@test.fr", "password": "motdepasse123"}, follow_redirects=False)
check("login ok -> 303 /", r.status_code == 303 and r.headers.get("location") == "/", r.status_code)
check("cookie de session posé", auth.COOKIE_NAME in c.cookies, list(c.cookies.keys()))
r = c.get("/", headers=HTML);                       check("/ avec session 200 + accueil", r.status_code == 200 and "Vos outils" in r.text, r.status_code)
r = c.get("/comparateur", headers=HTML);            check("/comparateur 200", r.status_code == 200 and "Comparateur" in r.text, r.status_code)
r = c.get("/fiche-dda", headers=HTML);              check("/fiche-dda 200", r.status_code == 200, r.status_code)
r = c.get("/cabinet");                              check("/cabinet json (acpr présent)", r.status_code == 200 and "acpr" in r.json(), r.status_code)
r = c.get("/cabinet");                              check("/cabinet raison_sociale vide (neutralisé)", r.json().get("raison_sociale") == "", repr(r.json().get("raison_sociale")))

# route protégée sans session (client neuf) -> 401
c2 = TestClient(appmod.app)
r = c2.get("/cabinet");                             check("/cabinet sans session -> 401", r.status_code == 401, r.status_code)
r = c2.post("/comparateur/export-xlsx", json={});  check("POST protégé sans session -> 401", r.status_code == 401, r.status_code)

r = c.get("/logout", follow_redirects=False);       check("/logout -> 303 /login", r.status_code == 303, r.status_code)

# --- logique offline ---
d = llm._parse_json('```json\n{"a":1}\n```');       check("_parse_json gère les fences", d == {"a": 1}, d)
sample = {
    "offres": [{"assureur": "AXA", "formule": "Confort", "cotisation": "45,00 €/mois", "frais_adhesion": "30 €"},
               {"assureur": "April", "formule": "Essentiel", "cotisation": "38,00 €/mois", "frais_adhesion": "—"}],
    "garanties": [{"module": "A — Hospitalisation", "poste": "Chambre particulière", "valeurs": ["60 €", "40 €"]}],
    "recommandation": {"offre": "AXA — Confort", "pourquoi": "meilleur rapport"},
}
blob = compare.build_xlsx(sample)
check("build_xlsx produit un .xlsx", blob[:2] == b"PK" and len(blob) > 2000, f"{len(blob)} octets")

print("\n=== RESULTATS ===")
ok = sum(1 for _, c_, _ in R if c_)
for name, cond, extra in R:
    print(("  OK   " if cond else " FAIL  ") + name + ("" if cond else f"   -> {extra}"))
print(f"\n{ok}/{len(R)} tests passes")
