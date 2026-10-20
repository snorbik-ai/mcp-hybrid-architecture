#!/usr/bin/env bash
set -e

echo "================================================================================"
echo "[CONTROLEUR GLOBAL] EXECUTION DES 5 SUITES DE TESTS MCP"
echo "================================================================================"

# Outil 01 (Node.js)
node 01_web_assets_manager/tests/run_all_suites.mjs

# Outils 02 a 05 (Python 3.10+)
PYTHON_BIN="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_BIN="python"
fi

$PYTHON_BIN 02_pdf_technical_extractor/tests/run_all_suites.py
$PYTHON_BIN 03_media_quality_auditor/tests/run_all_suites.py
$PYTHON_BIN 04_ecommerce_catalog_scanner/tests/run_all_suites.py
$PYTHON_BIN 05_visual_catalog_sync/tests/run_all_suites.py

echo ""
echo "================================================================================"
echo "[SUCCES TOTAL] LES 5 OUTILS AUTONOMES ONT VALIDE LEURS 4 COUCHES DE TESTS (52/52) !"
echo "================================================================================"
