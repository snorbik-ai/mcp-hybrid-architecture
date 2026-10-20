@echo off
setlocal enabledelayedexpansion

echo ================================================================================
echo           MCP-HYBRID-ARCHITECTURE : REINITIALISATION DE L'ENVIRONNEMENT VIRTUEL
echo ================================================================================
echo.
echo ATTENTION : Cette operation va :
echo   1. Supprimer integralement l'environnement virtuel local (.venv)
echo   2. Nettoyer les caches Python temporaires (__pycache__)
echo   3. Relancer une installation propre via install.bat
echo.
echo Vos configurations et fichiers sources ne seront PAS affectes.
echo.

set /p CONFIRM="Etes-vous certain de vouloir reinitialiser l'environnement ? [O/N] : "
if /i not "!CONFIRM!"=="O" if /i not "!CONFIRM!"=="Y" (
    echo.
    echo [ANNULATION] Operation annulee par l'utilisateur. Rien n'a ete modifie.
    exit /b 0
)

echo.
if exist "%~dp0.venv" (
    echo [1/3] Suppression du dossier .venv en cours...
    rmdir /s /q "%~dp0.venv"
    if errorlevel 1 (
        echo [ERREUR] Impossible de supprimer .venv. Verifiez qu'aucun terminal ou script n'est actif.
        exit /b 1
    )
    echo [OK] Ancien environnement .venv supprime.
) else (
    echo [1/3] Aucun dossier .venv a supprimer.
)

echo [2/3] Nettoyage des caches temporaires Python...
for /d /r "%~dp0" %%d in (__pycache__) do (
    if exist "%%d" rmdir /s /q "%%d" 2>nul
)
echo [OK] Caches temporaires purges.

echo.
echo [3/3] Reconstruction de l'environnement virtuel et reinstallation...
call "%~dp0install.bat" all
if errorlevel 1 (
    echo.
    echo [ERREUR] La reconstruction de l'environnement a echoue.
    exit /b 1
)

echo.
echo ================================================================================
echo [SUCCES] L'environnement mcp-hybrid-architecture a ete reinitialise a neuf avec succes !
echo ================================================================================
exit /b 0
