@echo off
REM Mettre_a_jour.bat — double-clic pour mettre a jour le Comparateur Courtier.
chcp 65001 >nul
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0update.ps1"
if errorlevel 1 pause
