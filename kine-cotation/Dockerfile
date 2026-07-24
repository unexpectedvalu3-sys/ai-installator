# KineCotation — image d'hebergement (host-neutre : Render, Fly, VPS, Scaleway...)
# Serveur SANS ETAT : pas de base, sessions dans un cookie signe, profil + dossier
# de preuve dans le navigateur du kine. Le seul flux de donnee de sante est l'OCR
# (proxy transitoire vers Mistral, fichier temporaire supprime aussitot).
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Regenere l'app depuis la base NGAP : la HTML servie colle TOUJOURS a ngap_kine.json
# (une app qui embarquerait un vieux bareme attesterait le mauvais bareme).
RUN python webapp/build_webapp.py

ENV HOST=0.0.0.0 PORT=8770
EXPOSE 8770
# HEALTHCHECK simple sur /healthz (public)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request,os;urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','8770')+'/healthz').read()" || exit 1

CMD ["python", "webapp/server.py"]
