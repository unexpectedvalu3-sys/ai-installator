@echo off
REM demarrer.bat — Lance le Comparateur Courtier en local (double-clic / raccourci Bureau).
REM La fenetre DOIT rester ouverte pendant l'utilisation.
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo L'environnement n est pas installe. Lance install\Installer.bat d abord.
  pause
  exit /b 1
)
title Comparateur Courtier
echo.
echo  Comparateur Courtier — en cours d execution...
echo  Laisse cette fenetre ouverte. Navigateur : http://localhost:8000
echo  Pour arreter : ferme cette fenetre.
echo.
start "" http://localhost:8000
".venv\Scripts\python.exe" -m uvicorn app:app --host 127.0.0.1 --port 8000
echo.
echo Application arretee. Appuie sur une touche pour fermer.
pause >nul
