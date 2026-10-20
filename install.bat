@echo off
setlocal enabledelayedexpansion

echo ================================================================================
echo          MCP-HYBRID-ARCHITECTURE : SCRIPT D'INSTALLATION ET VERIFICATION [WINDOWS]
echo ================================================================================
echo.

set TARGET=%1
if "%TARGET%"=="" set TARGET=all

:: 1. Cas particulier cible 01 : Verification Node.js
if "%TARGET%"=="01" (
    where node >nul 2>&1
    if errorlevel 1 (
        echo [ERREUR] Node.js est obligatoire pour l'outil #01 [01_web_assets_manager].
        echo Rendez-vous sur https://nodejs.org/ pour installer Node.js LTS [v18+].
        exit /b 1
    )
    for /f "tokens=*" %%i in ('node -v 2^>nul') do set NODE_VER=%%i
    echo [OK] Node.js detecte avec succes : !NODE_VER!
    echo [OK] L'outil #01 n'utilise que des API Node.js natives [aucun node_modules externe requis].
    echo [SUCCES] L'outil #01 est pret a l'emploi !
    exit /b 0
)

:: 2. Detection de l'interpreteur Python
set PYTHON_CMD=
python -c "import sys; sys.exit(0 if (sys.version_info.major==3 and sys.version_info.minor>=10) else 1)" >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
) else (
    py -3 -c "import sys; sys.exit(0 if (sys.version_info.major==3 and sys.version_info.minor>=10) else 1)" >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=py -3
    )
)

if "%PYTHON_CMD%"=="" (
    echo [ERREUR] Python 3.10 ou superieur n'a pas ete detecte sur cette machine.
    echo.
    echo Explication :
    echo   Les outils 02, 03, 04, 05 et la passerelle HTTP necessitent Python 3.10 ou superieur [64-bit].
    echo.
    echo Solution recommandee :
    echo   1. Telechargez Python depuis le site officiel : https://www.python.org/downloads/
    echo   2. Lors de l'installation, cochez IMPERATIVEMENT la case : Add python.exe to PATH
    echo   3. Relancez ensuite ce script install.bat.
    echo.
    set /p OPEN_WEB="Souhaitez-vous ouvrir la page officielle de telechargement ? [O/N] : "
    if /i "!OPEN_WEB!"=="O" start https://www.python.org/downloads/
    if /i "!OPEN_WEB!"=="Y" start https://www.python.org/downloads/
    exit /b 1
)

echo [OK] Moteur Python valide detecte : %PYTHON_CMD%
echo.

:: 3. Information Node.js
where node >nul 2>&1
if errorlevel 1 (
    echo [INFO] Node.js n'a pas ete detecte. L'outil #01 necessitera Node.js v18+.
    echo        Les outils #02, #03, #04 et #05 fonctionnent sans Node.js.
) else (
    echo [OK] Moteur Node.js detecte.
)
echo.

:: 4. Creation ou verification de l'environnement virtuel .venv
if not exist "%~dp0.venv\Scripts\python.exe" (
    echo [1/3] Creation de l'environnement virtuel local dans .venv...
    %PYTHON_CMD% -m venv "%~dp0.venv"
    if errorlevel 1 (
        echo [ERREUR] Impossible de creer l'environnement virtuel .venv.
        exit /b 1
    )
    echo [OK] Environnement virtuel cree avec succes [.venv].
) else (
    echo [1/3] Environnement virtuel local detecte [.venv].
)

set VENV_PY="%~dp0.venv\Scripts\python.exe"
set VENV_PIP="%~dp0.venv\Scripts\pip.exe"

:: 5. Mise a niveau minimale de pip
echo [2/3] Verification de l'installateur pip...
%VENV_PY% -m pip install --upgrade pip --quiet

:: 6. Installation des dependances selon la cible demandee
echo [3/3] Installation des dependances pour la cible : %TARGET%...

if "%TARGET%"=="all" (
    %VENV_PIP% install -r "%~dp0requirements-all.txt"
) else if "%TARGET%"=="02" (
    %VENV_PIP% install -r "%~dp002_pdf_technical_extractor\requirements.txt"
) else if "%TARGET%"=="03" (
    %VENV_PIP% install -r "%~dp003_media_quality_auditor\requirements.txt"
) else if "%TARGET%"=="04" (
    %VENV_PIP% install -r "%~dp004_ecommerce_catalog_scanner\requirements.txt"
) else if "%TARGET%"=="05" (
    %VENV_PIP% install -r "%~dp005_visual_catalog_sync\requirements.txt"
) else (
    echo [ATTENTION] Cible inconnue %TARGET%. Installation complete par defaut...
    %VENV_PIP% install -r "%~dp0requirements-all.txt"
)

if errorlevel 1 (
    echo [ERREUR] L'installation des dependances a rencontre une erreur.
    echo Executez doctor.bat pour diagnostiquer.
    exit /b 1
)

echo.
echo ================================================================================
echo                     CONTROLE DE SANTE FINAL [DOCTOR]
echo ================================================================================
%VENV_PY% "%~dp0mcp_shared\mcp_doctor.py"

echo.
echo ================================================================================
echo [SUCCES] Installation terminee et prete a l'emploi !
echo ================================================================================
echo Commandes recommandees :
echo   - Diagnostiquer l'etat : doctor.bat
echo   - Lancer les tests      : run_all_tests.bat
echo   - Reinitialiser l'env   : reset_env.bat
echo   - Lancer la passerelle  : python mcp_shared\mcp_http_gateway.py --port 5185
echo.
exit /b 0
