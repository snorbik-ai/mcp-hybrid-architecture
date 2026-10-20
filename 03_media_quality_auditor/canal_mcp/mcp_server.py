#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
BatiHome Internal Tool — Media Auditor & Quality Pipeline
Module : canal_mcp/mcp_server.py (Canal 1 : Serveur MCP pour IA & Agents)
===============================================================================
Serveur MCP officiel en Python pour permettre aux agents IA d'auditer la qualité
des images, qualifier les résolutions et éliminer les doublons graphiques.
Protocole : JSON-RPC 2.0 sur stdio.
"""

import sys
import os
import json

# Import du SDK
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "canal_sdk_cli"))
from sdk import MediaAuditorPipeline

PIPELINE = MediaAuditorPipeline()
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

TOOLS_SCHEMA = [
    {
        "name": "audit_media_folder",
        "description": "Analyse un dossier d'images BatiHome (Pillow) : extrait les résolutions, formats, poids et qualifie chaque image en VALID_HD, REJECTED_LOW_RES ou DUPLICATE selon des seuils minimaux.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "folder_path": {
                    "type": "string",
                    "description": "Chemin relatif ou absolu du dossier (ex: frontend/public/images/hero)"
                },
                "min_width": {
                    "type": "integer",
                    "description": "Largeur minimale en pixels (défaut: 1200)",
                    "default": 1200
                },
                "min_height": {
                    "type": "integer",
                    "description": "Hauteur minimale en pixels (défaut: 700)",
                    "default": 700
                }
            },
            "required": ["folder_path"]
        }
    },
    {
        "name": "get_certified_hero_candidates",
        "description": "Extrait la banque candidate des images certifiées haute définition répondant strictement aux exigences de netteté architecturale BatiHome (équivalent ou supérieur à hero-terrasse.png).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "folder_path": {
                    "type": "string",
                    "description": "Chemin du dossier d'images (ex: frontend/public/images/hero)"
                }
            },
            "required": ["folder_path"]
        }
    },
    {
        "name": "clean_duplicate_media",
        "description": "Détecte et purge les fichiers en doublon (empreintes MD5 identiques ou suffixes ' copy') dans un dossier de médias BatiHome.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "folder_path": {
                    "type": "string",
                    "description": "Chemin du dossier d'images à nettoyer"
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "Si true, simule uniquement sans supprimer les fichiers du disque. Si false, supprime réellement.",
                    "default": True
                }
            },
            "required": ["folder_path"]
        }
    }
]

def resolve_path(p: str) -> str:
    if os.path.isabs(p):
        return p
    return os.path.abspath(os.path.join(WORKSPACE_ROOT, p))

def handle_request(req):
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
                    "name": "batihome-media-auditor-mcp",
                    "version": "1.0.0"
                }
            }
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS_SCHEMA}
        }

    if method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        folder_path = resolve_path(args.get("folder_path", "frontend/public/images/hero"))

        try:
            if tool_name == "audit_media_folder":
                min_w = args.get("min_width", 1200)
                min_h = args.get("min_height", 700)
                result = PIPELINE.audit_directory(folder_path, min_width=min_w, min_height=min_h)
            elif tool_name == "get_certified_hero_candidates":
                result = PIPELINE.get_certified_hero_candidates(folder_path)
            elif tool_name == "clean_duplicate_media":
                dry_run = args.get("dry_run", True)
                result = PIPELINE.clean_duplicates(folder_path, dry_run=dry_run)
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
                    "content": [{
                        "type": "text",
                        "text": json.dumps(result, indent=2, ensure_ascii=False)
                    }]
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
            err_res = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(err)}"}
            }
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
