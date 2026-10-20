#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #02 : PDF TECHNICAL EXTRACTOR — CANAL 1 (VARIANTE 1 : MCP CLASSIC STDIO)
========================================================================================
Serveur MCP JSON-RPC 2.0 autonome (zéro dépendance externe bloquante) exposant :
1. process_pdf_document
2. get_pdf_manifest
3. get_pdf_document_text
4. run_quality_and_tests_suite
========================================================================================
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any

current_dir = Path(__file__).resolve().parent
tool_root = current_dir.parent.parent
if str(tool_root) not in sys.path:
    sys.path.insert(0, str(tool_root))

from canal_sdk_cli.sdk import PdfProcessorSDK

sdk = PdfProcessorSDK()
TEST_RUNNER = tool_root / "tests" / "run_all_suites.py"

TOOLS_SCHEMA = [
    {
        "name": "process_pdf_document",
        "description": "Traite un catalogue ou devis PDF : découpe par page, rendu HD 150 DPI, extraction d'images brutes et classification.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pdf_path": {"type": "string", "description": "Chemin vers le fichier PDF cible"},
                "output_dir": {"type": "string", "default": "output"},
                "dpi": {"type": "integer", "default": 150}
            },
            "required": ["pdf_path"]
        }
    },
    {
        "name": "get_pdf_manifest",
        "description": "Lit l'index technique manifest.json d'un document PDF préalablement extrait.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document_dir": {"type": "string", "description": "Chemin du dossier du document traité"}
            },
            "required": ["document_dir"]
        }
    },
    {
        "name": "get_pdf_document_text",
        "description": "Retourne le texte intégral Markdown extrait d'un PDF pour le RAG ou l'analyse IA.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document_dir": {"type": "string", "description": "Chemin du dossier du document traité"}
            },
            "required": ["document_dir"]
        }
    },
    {
        "name": "run_quality_and_tests_suite",
        "description": "Exécute les 4 couches de tests de 02_pdf_technical_extractor (Unitaires, Intégration, Validation/Performance, Smoke).",
        "inputSchema": {"type": "object", "properties": {}, "required": []}
    }
]


def handle_request(req: Dict[str, Any]) -> Dict[str, Any]:
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "02-pdf-technical-extractor-mcp",
                    "version": "2.0.0"
                }
            }
        }

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS_SCHEMA}}

    if method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        try:
            if tool_name == "process_pdf_document":
                pdf_path = args.get("pdf_path")
                if not pdf_path:
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "isError": True,
                            "content": [{"type": "text", "text": "Erreur de validation : Le paramètre obligatoire 'pdf_path' est manquant ou vide."}]
                        }
                    }
                target_file = Path(pdf_path)
                if not target_file.exists():
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "isError": True,
                            "content": [{"type": "text", "text": f"Erreur de validation : Le fichier PDF spécifié est introuvable : '{pdf_path}'."}]
                        }
                    }
                result = sdk.process_pdf(
                    pdf_path=str(target_file),
                    output_dir=args.get("output_dir", "output"),
                    dpi=int(args.get("dpi", 150))
                )
            elif tool_name == "get_pdf_manifest":
                doc_dir = args.get("document_dir")
                if not doc_dir:
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "isError": True,
                            "content": [{"type": "text", "text": "Erreur de validation : Le paramètre obligatoire 'document_dir' est manquant ou vide."}]
                        }
                    }
                result = sdk.get_manifest(doc_dir)
            elif tool_name == "get_pdf_document_text":
                doc_dir = args.get("document_dir")
                if not doc_dir:
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "isError": True,
                            "content": [{"type": "text", "text": "Erreur de validation : Le paramètre obligatoire 'document_dir' est manquant ou vide."}]
                        }
                    }
                result = {"full_text": sdk.get_document_text(doc_dir)}
            elif tool_name == "run_quality_and_tests_suite":
                proc = subprocess.run(
                    [sys.executable, str(TEST_RUNNER), "--json"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                result = json.loads(proc.stdout)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Outil inconnu : {tool_name}"}
                }

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "isError": True,
                    "content": [{"type": "text", "text": f"Erreur : {str(e)}"}]
                }
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Méthode non supportée : {method}"}
    }


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            res = handle_request(req)
            if res:
                sys.stdout.write(json.dumps(res, ensure_ascii=False) + "\n")
                sys.stdout.flush()
        except Exception as err:
            sys.stdout.write(json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": str(err)}
            }) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
