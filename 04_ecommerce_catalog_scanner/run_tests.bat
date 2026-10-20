@echo off
echo ================================================================================
echo [AUTO-TEST] EXECUTION DES 4 COUCHES DE TESTS : 04_ecommerce_catalog_scanner
echo ================================================================================
python "%~dp0tests\run_all_suites.py" %*
if errorlevel 1 exit /b 1
exit /b 0
