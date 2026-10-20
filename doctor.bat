@echo off
setlocal

:: 1. Priorite a l'environnement virtuel local .venv s'il existe
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" "%~dp0mcp_shared\mcp_doctor.py"
    exit /b %errorlevel%
)

:: 2. Test python direct
python "%~dp0mcp_shared\mcp_doctor.py"
if not errorlevel 9009 if not errorlevel 1 exit /b 0

:: 3. Test py -3
py -3 "%~dp0mcp_shared\mcp_doctor.py" >nul 2>&1
if not errorlevel 1 (
    py -3 "%~dp0mcp_shared\mcp_doctor.py"
    exit /b %errorlevel%
)

echo ================================================================================
echo               MCP-TOOLKIT : RAPPORT DE SANTE ET DIAGNOSTIC (DOCTOR)
echo ================================================================================
echo.
echo [ERREUR] Aucun interpreteur Python n'a ete trouve sur cette machine.
echo.
echo Recommandation :
echo   1. Installez Python 3.10 ou superieur (64-bit) depuis : https://python.org
echo   2. Cochez bien 'Add Python to PATH' lors de l'installation.
echo   3. Lancez install.bat pour finaliser la configuration.
echo.
exit /b 1
