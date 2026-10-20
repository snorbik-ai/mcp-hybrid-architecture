@echo off
echo ================================================================================
echo [CONTROLEUR GLOBAL] SUITE DES 5 VOITURES AUTONOMES (4 COUCHES DE TESTS CHACUNE)
echo ================================================================================

call "%~dp001_web_assets_manager\run_tests.bat"
if errorlevel 1 exit /b 1

call "%~dp002_pdf_technical_extractor\run_tests.bat"
if errorlevel 1 exit /b 1

call "%~dp003_media_quality_auditor\run_tests.bat"
if errorlevel 1 exit /b 1

call "%~dp004_ecommerce_catalog_scanner\run_tests.bat"
if errorlevel 1 exit /b 1

call "%~dp005_visual_catalog_sync\run_tests.bat"
if errorlevel 1 exit /b 1

echo.
echo ================================================================================
echo [SUCCES TOTAL] LES 5 OUTILS AUTONOMES ONT VALIDE LEURS 4 COUCHES DE TESTS !
echo ================================================================================
exit /b 0
