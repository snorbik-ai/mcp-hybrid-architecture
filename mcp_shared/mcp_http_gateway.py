#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
PASSERELLE INTERMÉDIAIRE MCP (HTTP / REST GATEWAY) — MODE 2 : IA EXTERNE
========================================================================================
Agrège les 5 serveurs MCP autonomes de la suite BatiHome / AXESTEEL :
- 01_web_assets_manager (Node.js)
- 02_pdf_technical_extractor (Python)
- 03_media_quality_auditor (Python)
- 04_ecommerce_catalog_scanner (Python)
- 05_visual_catalog_sync (Python)

Expose sur http://localhost:5185 pour les agents externes et orchestrateurs LLM :
- GET  /health     : Statut des 5 serveurs
- GET  /tools      : Liste unifiée de tous les outils découverts dynamiquement
- POST /tools/call : Routage transparent vers le serveur MCP concerné via JSON-RPC stdio
========================================================================================
"""

import sys
import json
import argparse
import subprocess
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from typing import Dict, Any, Tuple, Optional

CURRENT_DIR = Path(__file__).resolve().parent
TOOLS_ROOT = CURRENT_DIR.parent

MCP_SERVERS = {
    "01_web_assets_manager": {
        "command": "node",
        "args": ["01_web_assets_manager/canal_mcp/mcp_classic_stdio/mcp_server.mjs"],
        "cwd": TOOLS_ROOT
    },
    "02_pdf_technical_extractor": {
        "command": "python",
        "args": ["02_pdf_technical_extractor/canal_mcp/mcp_classic_stdio/mcp_server.py"],
        "cwd": TOOLS_ROOT
    },
    "03_media_quality_auditor": {
        "command": "python",
        "args": ["03_media_quality_auditor/canal_mcp/mcp_classic_stdio/mcp_server.py"],
        "cwd": TOOLS_ROOT
    },
    "04_ecommerce_catalog_scanner": {
        "command": "python",
        "args": ["04_ecommerce_catalog_scanner/canal_mcp/mcp_classic_stdio/mcp_server.py"],
        "cwd": TOOLS_ROOT
    },
    "05_visual_catalog_sync": {
        "command": "python",
        "args": ["05_visual_catalog_sync/canal_mcp/mcp_classic_stdio/mcp_server.py"],
        "cwd": TOOLS_ROOT
    }
}


def send_mcp_rpc(server_cfg: Dict[str, Any], method: str, params: Optional[Dict[str, Any]] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    cmd = [server_cfg["command"]] + server_cfg["args"]
    cwd = server_cfg["cwd"]
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # 1. Initialize obligatoire selon protocole MCP
        init_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "McpHttpGateway", "version": "2.0.0"}}
        }
        proc.stdin.write(json.dumps(init_payload) + "\n")
        proc.stdin.flush()
        _ = proc.stdout.readline()

        # 2. Requête cible
        req_payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": method,
            "params": params or {}
        }
        proc.stdin.write(json.dumps(req_payload) + "\n")
        proc.stdin.flush()
        line = proc.stdout.readline()
        
        try:
            proc.stdin.close()
            proc.terminate()
            proc.wait(timeout=2)
        except:
            proc.kill()

        if not line:
            return None, "Réponse vide reçue du serveur MCP"
            
        res = json.loads(line.strip())
        return res, None
    except Exception as e:
        return None, str(e)


def discover_all_tools() -> Dict[str, Any]:
    registry = {}
    server_tools = {}
    tool_counts = {}

    for s_name, s_cfg in MCP_SERVERS.items():
        res, err = send_mcp_rpc(s_cfg, "tools/list")
        tools = res.get("result", {}).get("tools", []) if (res and "result" in res) else []
        server_tools[s_name] = tools
        for t in tools:
            name = t["name"]
            tool_counts[name] = tool_counts.get(name, 0) + 1

    for s_name, tools in server_tools.items():
        prefix = s_name.split("_")[0]
        for t in tools:
            raw_name = t["name"]
            desc = t.get("description", "")
            params = t.get("inputSchema", {})

            if tool_counts[raw_name] > 1:
                scoped_name = f"{prefix}_{raw_name}"
                registry[scoped_name] = {
                    "name": scoped_name,
                    "target_tool": raw_name,
                    "description": f"[{s_name}] {desc}",
                    "parameters": params,
                    "server": s_name,
                    "is_alias": False
                }
            else:
                registry[raw_name] = {
                    "name": raw_name,
                    "target_tool": raw_name,
                    "description": desc,
                    "parameters": params,
                    "server": s_name,
                    "is_alias": False
                }
                scoped_name = f"{prefix}_{raw_name}"
                registry[scoped_name] = {
                    "name": scoped_name,
                    "target_tool": raw_name,
                    "description": f"[{s_name}] {desc}",
                    "parameters": params,
                    "server": s_name,
                    "is_alias": True
                }

    return registry


CACHED_TOOLS = discover_all_tools()


class McpGatewayHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path in ("/", "/health"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            active_tools = [m for m in CACHED_TOOLS.values() if not m.get("is_alias")]
            resp = {
                "status": "online",
                "service": "BatiHome MCP Universal Gateway (5 Outils Internes)",
                "mode": "Mode 2 - Passerelle Universelle JSON-RPC / HTTP REST",
                "total_tools": len(active_tools),
                "servers": list(MCP_SERVERS.keys())
            }
            self.wfile.write(json.dumps(resp, indent=2, ensure_ascii=False).encode("utf-8"))
            return

        if parsed.path == "/tools":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            tools_list = [
                {
                    "name": meta["name"],
                    "description": meta["description"],
                    "parameters": meta["parameters"],
                    "source_module": meta["server"]
                }
                for meta in CACHED_TOOLS.values()
                if not meta.get("is_alias", False)
            ]
            self.wfile.write(json.dumps({"tools": tools_list}, indent=2, ensure_ascii=False).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'{"error": "Endpoint non trouve"}')

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/tools/call":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            try:
                data = json.loads(body)
                tool_name = data.get("name")
                tool_args = data.get("arguments", {})

                if tool_name not in CACHED_TOOLS:
                    # Gestion d'aide en cas d'appel générique d'un outil dupliqué
                    available_matches = [k for k in CACHED_TOOLS.keys() if (not CACHED_TOOLS[k].get("is_alias")) and (k.endswith(f"_{tool_name}") or CACHED_TOOLS[k].get("target_tool") == tool_name)]
                    if available_matches:
                        msg = f"Nom d'outil ambigu '{tool_name}'. Veuillez préciser le module cible : {available_matches}"
                    else:
                        msg = f"Outil '{tool_name}' non reconnu parmi les outils exposés."
                    self.send_response(404)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "status": "error",
                        "message": msg
                    }, ensure_ascii=False).encode("utf-8"))
                    return

                tool_meta = CACHED_TOOLS[tool_name]
                server_name = tool_meta["server"]
                target_tool_name = tool_meta["target_tool"]
                server_cfg = MCP_SERVERS[server_name]

                rpc_res, rpc_err = send_mcp_rpc(
                    server_cfg,
                    "tools/call",
                    {"name": target_tool_name, "arguments": tool_args}
                )

                if rpc_err:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": rpc_err}, ensure_ascii=False).encode("utf-8"))
                    return

                # Déballage du résultat JSON-RPC
                is_error = rpc_res.get("result", {}).get("isError", False)
                content = rpc_res.get("result", {}).get("content", [])

                parsed_content = None
                if content and isinstance(content, list) and len(content) > 0:
                    raw_text = content[0].get("text", "")
                    try:
                        parsed_content = json.loads(raw_text)
                    except:
                        parsed_content = raw_text

                self.send_response(200 if not is_error else 400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "success" if not is_error else "error",
                    "tool": tool_name,
                    "target_tool": target_tool_name,
                    "server": server_name,
                    "result": parsed_content if parsed_content is not None else rpc_res.get("result")
                }, indent=2, ensure_ascii=False).encode("utf-8"))

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'{"error": "Endpoint non trouve"}')


def run(port: int = 5185):
    server_address = ("", port)
    httpd = HTTPServer(server_address, McpGatewayHandler)
    print(f"🌐 PASSERELLE MCP UNIVERSELLE ACTIVE SUR http://localhost:{port}")
    print(f"   • Outils unifiés découverts : {len(CACHED_TOOLS)}")
    for name, meta in CACHED_TOOLS.items():
        print(f"     - {name} ({meta['server']})")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt de la passerelle MCP.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-p", type=int, default=5185, help="Port d'écoute HTTP (défaut: 5185)")
    args = parser.parse_args()
    run(args.port)
