#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
MCP-HYBRID-ARCHITECTURE : DIAGNOSTIC D'ENVIRONNEMENT ET RAPPORT DE SANTE (DOCTOR)
========================================================================================
Diagnostique :
1. Version Python, architecture 64-bit, chemin d'execution
2. Environnement virtuel (.venv)
3. Disponibilite de Node.js (pour l'outil 01)
4. Dependances et packages metiers (fitz, PIL, bs4, playwright)
5. Syntaxe des configurations (mcp_config.json, .env.example)
6. Disponibilite du port reseau de la passerelle HTTP (5185)
========================================================================================
"""

import sys
import os
import socket
import json
import subprocess
import shutil

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def run_doctor():
    print("=" * 80)
    print("           MCP-HYBRID-ARCHITECTURE : RAPPORT DE SANTE ET DIAGNOSTIC (DOCTOR)")
    print("=" * 80)
    print()

    errors = 0
    warnings = 0

    # 1. Python
    print("[1/6] Diagnostic du Moteur Python...")
    v = sys.version_info
    py_ver = f"{v.major}.{v.minor}.{v.micro}"
    is_64 = sys.maxsize > 2**32
    print(f"  [OK] Version Python   : {py_ver} ({sys.executable})")
    
    if v.major < 3 or (v.major == 3 and v.minor < 10):
        print("  [ERREUR] Python >= 3.10 est obligatoire.")
        errors += 1
    else:
        print("  [OK] Version Python valide (>= 3.10).")

    if not is_64:
        print("  [ATTENTION] Architecture 32-bit detectee. Recommande : 64-bit.")
        warnings += 1
    else:
        print("  [OK] Architecture 64-bit confirmee.")
    print()

    # 2. Node.js (Tool 01)
    print("[2/6] Diagnostic de Node.js (requis pour 01_web_assets_manager)...")
    node_bin = shutil.which("node")
    if node_bin:
        try:
            res = subprocess.run([node_bin, "-v"], capture_output=True, text=True, timeout=5)
            node_ver = res.stdout.strip()
            print(f"  [OK] Node.js detecte  : {node_ver} ({node_bin})")
        except Exception:
            print("  [OK] Node.js detecte dans le PATH.")
    else:
        print("  [ATTENTION] Node.js non detecte dans le PATH.")
        print("              L'outil #01 ne pourra pas demarrer sans Node.js v18+.")
        print("              Les outils #02, #03, #04, #05 restent 100% operationnels.")
        warnings += 1
    print()

    # 3. Environnement virtuel
    print("[3/6] Diagnostic de l'Environnement Virtuel (.venv)...")
    venv_dir = os.path.join(ROOT_DIR, ".venv")
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    if os.path.isdir(venv_dir):
        print(f"  [OK] Dossier .venv detecte : {venv_dir}")
    elif in_venv:
        print(f"  [OK] Environnement virtuel actif : {sys.prefix}")
    else:
        print("  [ATTENTION] Aucun dossier .venv local detecte.")
        print("              Conseil : Executez 'install.bat' pour isoler les dependances.")
        warnings += 1
    print()

    # 4. Dependances Python
    print("[4/6] Diagnostic des Dependances Python (Packages Metiers)...")
    deps = [
        ("PyMuPDF (fitz)", "fitz", "Outil #02 - Extraction PDF & rendu HD 150 DPI", True),
        ("Pillow (PIL)", "PIL", "Outil #03 - Audit nettete & dimensions", True),
        ("BeautifulSoup4", "bs4", "Outil #04 - Parsing DOM catalogue e-commerce", True),
        ("Playwright", "playwright", "Outil #04 - Rendu dynamique SPAs React (Optionnel)", False),
    ]

    for label, mod_name, desc, required in deps:
        try:
            mod = __import__(mod_name)
            ver = getattr(mod, "__version__", getattr(mod, "version", "present"))
            print(f"  [OK] {label:<18} v{ver:<10} -> {desc}")
        except ImportError:
            if required:
                print(f"  [MANQUE] {label:<16} [NON INSTALLE] -> {desc}")
                errors += 1
            else:
                print(f"  [INFO]   {label:<16} [NON INSTALLE] -> {desc}")
    print()

    # 5. Configurations & fichiers
    print("[5/6] Diagnostic des Fichiers de Configuration...")
    cfg_file = os.path.join(ROOT_DIR, "mcp_config.json")
    if os.path.isfile(cfg_file):
        try:
            with open(cfg_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            servers = data.get("mcpServers", {})
            print(f"  [OK] mcp_config.json valide ({len(servers)} serveurs declares).")
        except Exception as e:
            print(f"  [ERREUR] Erreur de lecture de mcp_config.json : {e}")
            errors += 1
    else:
        print("  [ERREUR] mcp_config.json introuvable.")
        errors += 1

    env_file = os.path.join(ROOT_DIR, ".env.example")
    if os.path.isfile(env_file):
        print("  [OK] Fichier .env.example present.")
    else:
        print("  [ATTENTION] Fichier .env.example absent.")
        warnings += 1
    print()

    # 6. Reseau / Port passerelle HTTP (5185)
    print("[6/6] Diagnostic Reseau (Disponibilite Port 5185)...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.settimeout(1.0)
        result = sock.connect_ex(("127.0.0.1", 5185))
        if result == 0:
            print("  [INFO] Port 5185 actif (passerelle mcp_http_gateway en ecoute).")
        else:
            print("  [OK] Port 5185 libre pour la passerelle mcp_http_gateway.")
    except Exception as e:
        print(f"  [INFO] Verification port : {e}")
    finally:
        sock.close()
    print()

    # Synthese
    print("=" * 80)
    print("                             SYNTHESE DU DIAGNOSTIC")
    print("=" * 80)
    if errors == 0:
        if warnings == 0:
            print("  [ETAT : PARFAIT] Tous les composants sont operationnels. 100% pret.")
        else:
            print(f"  [ETAT : FONCTIONNEL] ({warnings} avertissement(s)).")
            print("  Le toolkit fonctionne. Consultez les remarques ci-dessus si necessaire.")
    else:
        print(f"  [ETAT : ATTENTION REQUISE] ({errors} erreur(s), {warnings} avertissement(s)).")
        print("  Veuillez lancer 'install.bat' pour installer les modules manquants.")
    print("=" * 80)

    return 0 if errors == 0 else 1

if __name__ == "__main__":
    sys.exit(run_doctor())
