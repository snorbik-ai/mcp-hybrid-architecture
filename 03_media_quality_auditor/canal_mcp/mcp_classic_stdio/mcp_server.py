#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #03 : MEDIA QUALITY AUDITOR — CANAL 1 (VARIANTE 1 : MCP CLASSIC STDIO)
========================================================================================
Serveur MCP JSON-RPC 2.0 exposant :
1. audit_media_folder
2. get_certified_hero_candidates
3. clean_duplicate_media
4. run_quality_and_tests_suite
========================================================================================
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any

current_dir = Path(__file__).resolve().parent
tool_root = current_dir.parent.parent
if str(tool_root) not in sys.path:
    sys.path.insert(0, str(tool_root))

from canal_sdk_cli.sdk import MediaAuditorPipeline

PIPELINE = MediaAuditorPipeline()
WORKSPACE_ROOT = tool_root.parent.parent.resolve()
TEST_RUNNER = tool_root / "tests" / "run_all_suites.py"

TOOLS_SCHEMA = [
    {
        "name": "audit_media_folder",
        "description": "Analyse un dossier d'images (Pillow + MD5) : résolutions, formats, poids et qualification VALID_HD, REJECTED_LOW_RES ou DUPLICATE.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "folder_path": {"type": "string", "default": "frontend/public/assets/catalogue_verre"},
                "min_width": {"type": "integer", "default": 1200},
                "min_height": {"type": "integer", "default": 700}
            },
            "required": []
        }
    },
    {
        "name": "get_certified_hero_candidates",
        "description": "Extrait la liste des images certifiées HD répondant aux exigences de netteté.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "folder_path": {"type": "string", "default": "frontend/public/assets/catalogue_verre"}
            },
            "required": []
        }
    },
    {
        "name": "clean_duplicate_media",
        "description": "Détecte et purge les fichiers en doublon (empreintes MD5 identiques ou suffixes ' copy').",
        "inputSchema": {
            "type": "object",
            "properties": {
                "folder_path": {"type": "string", "default": "frontend/public/assets/catalogue_verre"},
                "dry_run": {"type": "boolean", "default": True}
            },
            "required": []
        }
    },
    {
        "name": "run_quality_and_tests_suite",
        "description": "Exécute les 4 couches de tests de 03_media_quality_auditor (Unitaires, Intégration, Validation/Performance, Smoke).",
        "inputSchema": {"type": "object", "properties": {}, "required": []}
    }
]


def resolve_path(p: str) -> str:
    if os.path.isabs(p):
        return p
    candidate = WORKSPACE_ROOT / p
    if candidate.exists():
        return str(candidate)
    fallback = WORKSPACE_ROOT / "frontend" / "public" / "assets" / "catalogue_verre"
    return str(fallback)


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
                    "name": "03-media-quality-auditor-mcp",
                    "version": "2.0.0"
                }
            }
        }

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS_SCHEMA}}

    if method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        folder_path = resolve_path(args.get("folder_path", "frontend/public/assets/catalogue_verre"))

        try:
            if tool_name == "audit_media_folder":
                min_w = int(args.get("min_width", 1200))
                min_h = int(args.get("min_height", 700))
                result = PIPELINE.audit_directory(folder_path, min_width=min_w, min_height=min_h)
            elif tool_name == "get_certified_hero_candidates":
                result = PIPELINE.get_certified_hero_candidates(folder_path)
            elif tool_name == "clean_duplicate_media":
                dry_run = bool(args.get("dry_run", True))
                result = PIPELINE.clean_duplicates(folder_path, dry_run=dry_run)
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
                    "content": [{"type": "text", "text": f"Erreur d'exécution : {str(e)}"}]
                }
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Méthode non implémentée : {method}"}
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
