#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
CANAL 1 : SERVEUR MCP (MODEL CONTEXT PROTOCOL) — PDF ASSETS PIPELINE
========================================================================================
Qu'est-ce que MCP ?
Le Model Context Protocol (MCP) est le protocole standardisé créé pour permettre aux
assistants d'Intelligence Artificielle (Claude, Gemini, Antigravity, Cursor) d'exécuter
des outils en toute sécurité sur la machine locale.

En branchant ce serveur MCP :
- Un agent IA peut ingérer un catalogue PDF fourni par un client ou un fabricant.
- L'IA peut extraire les fiches techniques, coupes de garde-corps et photos produits.
- L'IA peut lire le texte extrait (`full_text.md`) pour conseiller l'utilisateur en direct.

Démarrage :
  python mcp_server.py
  (Le serveur écoute sur stdio conformément à la spécification MCP)

Auteur : BatiHome Dev Team
========================================================================================
"""

import sys
import json
from pathlib import Path

# Résolution des imports pour charger le SDK
current_dir = Path(__file__).resolve().parent
sdk_dir = current_dir.parent / "canal_sdk_cli"
if str(sdk_dir) not in sys.path:
    sys.path.insert(0, str(sdk_dir))

from sdk import PdfProcessorSDK

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("ERREUR : La bibliothèque FastMCP n'est pas installée. Exécutez : pip install mcp", file=sys.stderr)
    sys.exit(1)

# Initialisation du serveur MCP pour BatiHome PDF
mcp = FastMCP("batihome-pdf-pipeline")
sdk = PdfProcessorSDK()


@mcp.tool()
def process_pdf_document(pdf_path: str, output_dir: str = "output", dpi: int = 150) -> str:
    """
    Traite un fichier PDF complet : découpe chaque page dans un dossier dédié,
    génère les rendus PNG haute résolution (150 DPI), extrait toutes les images
    brutes incorporées sans recompression et classe automatiquement les photos
    et schémas techniques.

    Args:
        pdf_path: Chemin absolu ou relatif vers le fichier PDF cible.
        output_dir: Répertoire d'exportation (défaut : "output").
        dpi: Résolution de pixellisation des pages (défaut : 150).

    Returns:
        Un résumé au format JSON contenant le statut, le total de pages, les images et chemins.
    """
    try:
        results = sdk.process_pdf(pdf_path=pdf_path, output_dir=output_dir, dpi=dpi)
        return json.dumps(results, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


@mcp.tool()
def get_pdf_manifest(document_dir: str) -> str:
    """
    Récupère le manifeste JSON complet d'un document PDF préalablement extrait,
    listant toutes les pages, leurs coordonnées, dimensions et la catégorisation
    des photos produits et schémas techniques.

    Args:
        document_dir: Dossier du document traité (ex: "output/garde_corps_vi_tree").

    Returns:
        Le contenu du fichier manifest.json.
    """
    try:
        manifest = sdk.get_manifest(document_dir)
        return json.dumps(manifest, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


@mcp.tool()
def get_pdf_document_text(document_dir: str) -> str:
    """
    Récupère l'intégralité du texte extrait d'un document PDF au format Markdown.
    Idéal pour les tâches d'analyse IA, de synthèse documentaire ou de RAG.

    Args:
        document_dir: Dossier du document traité (ex: "output/garde_corps_vi_tree").

    Returns:
        Le texte intégral du document structuré par page.
    """
    try:
        return sdk.get_document_text(document_dir)
    except Exception as e:
        return f"Erreur lors de la lecture du texte : {e}"


if __name__ == "__main__":
    # Démarre l'écoute stdio pour les clients MCP (Antigravity, Cursor, Claude)
    mcp.run()
