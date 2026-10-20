@echo off
echo ================================================================================
echo [AUTO-TEST] EXECUTION DES 4 COUCHES DE TESTS : 01_web_assets_manager
echo ================================================================================
node "%~dp0tests\run_all_suites.mjs" %*
if errorlevel 1 exit /b 1
exit /b 0
