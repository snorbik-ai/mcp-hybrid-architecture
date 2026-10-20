#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #05 : VISUAL CATALOG SYNC — CANAL 1 (VARIANTE 1 : MCP CLASSIC STDIO)
========================================================================================
Serveur MCP JSON-RPC 2.0 exposant :
1. sync_visual_assets
2. compile_frontend_catalog
3. sync_and_compile_all
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

from canal_sdk_cli.sdk import VisualCatalogSyncSDK

sdk = VisualCatalogSyncSDK()
TEST_RUNNER = tool_root / "tests" / "run_all_suites.py"

TOOLS_SCHEMA = [
    {
        "name": "sync_visual_assets",
        "description": "Télécharge localement les images du catalogue (idempotent : ne retélécharge pas ce qui existe) avec noms de fichiers raccourcis pour respecter la limite Windows MAX_PATH. Renvoie un bilan (compteurs, chemin max).",
        "inputSchema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "compile_frontend_catalog",
        "description": "Compile le JSON catalogue en module TypeScript (RawGlassRailingCatalog.ts) et en inventaire Markdown.",
        "inputSchema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "sync_and_compile_all",
        "description": "Pipeline complet : synchronisation locale des images puis compilation TypeScript et Markdown.",
        "inputSchema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "run_quality_and_tests_suite",
        "description": "Exécute les 4 couches de tests de 05_visual_catalog_sync (Unitaires, Intégration, Validation/Performance, Smoke).",
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
                    "name": "05-visual-catalog-sync-mcp",
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
            if tool_name == "sync_visual_assets":
                result = sdk.sync_visual_assets()
            elif tool_name == "compile_frontend_catalog":
                result = sdk.compile_frontend_catalog()
            elif tool_name == "sync_and_compile_all":
                result = sdk.run_full_pipeline()
            elif tool_name == "run_quality_and_tests_suite":
                proc = subprocess.run([sys.executable, str(TEST_RUNNER), "--json"], capture_output=True, text=True, check=False)
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
