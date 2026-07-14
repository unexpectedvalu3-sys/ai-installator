@echo off
REM Installer.bat — double-clic pour lancer l'installation (relance en PS1 non bloque).
chcp 65001 >nul
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0installer.ps1"
if errorlevel 1 pause
