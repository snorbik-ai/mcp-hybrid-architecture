#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test client MCP Stdio JSON-RPC 2.0 en conditions réelles sur le prototype BatiHome.
Simule le comportement d'un client MCP officiel (Cursor, Claude, Antigravity)
communiquant par stdin/stdout avec le serveur MCP de l'outil 04 via run_agent_lifecycle.
"""

import sys
import json
import subprocess
from pathlib import Path

MCP_SERVER_SCRIPT = (Path(__file__).parent.parent / "canal_mcp" / "mcp_classic_stdio" / "mcp_server.py").resolve()

def run_mcp_session(test_url: str):
    print("=" * 80)
    print(f"🤖 DÉMARRAGE DU CLIENT MCP STDIO (JSON-RPC 2.0)")
    print(f"• Serveur cible : {MCP_SERVER_SCRIPT}")
    print(f"• URL à scanner : {test_url}")
    print("=" * 80)

    proc = subprocess.Popen(
        [sys.executable, str(MCP_SERVER_SCRIPT)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        bufsize=1
    )

    def send_recv(req: dict) -> dict:
        req_line = json.dumps(req, ensure_ascii=False)
        print(f"\n➡️ [CLIENT -> SERVEUR MCP] : {req.get('method')}")
        proc.stdin.write(req_line + "\n")
        proc.stdin.flush()

        resp_line = proc.stdout.readline()
        if not resp_line:
            err = proc.stderr.read()
            raise RuntimeError(f"Le serveur MCP s'est arrêté inopinément. Stderr: {err}")
        
        return json.loads(resp_line)

    try:
        # Étape 1 : Protocole Handshake "initialize"
        print("\n--- ÉTAPE 1 : INITIALISATION MCP ---")
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "Antigravity-IDE-Client", "version": "1.0.0"}
            }
        }
        init_resp = send_recv(init_req)
        assert init_resp.get("result", {}).get("serverInfo", {}).get("name") == "04-ecommerce-catalog-scanner-mcp"
        print("✅ Handshake MCP validé avec succès !")

        # Étape 2 : Découverte des outils "tools/list"
        print("\n--- ÉTAPE 2 : DÉCOUVERTE DES OUTILS DISPONIBLES ---")
        list_req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        list_resp = send_recv(list_req)
        tools = list_resp.get("result", {}).get("tools", [])
        tool_names = [t["name"] for t in tools]
        print(f"✅ Outils découverts ({len(tools)}) : {tool_names}")
        assert "run_agent_lifecycle" in tool_names

        # Étape 3 : Appel de l'outil "tools/call" avec run_agent_lifecycle
        print(f"\n--- ÉTAPE 3 : APPEL RUN_AGENT_LIFECYCLE SUR BATIHOME ---")
        call_req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "run_agent_lifecycle",
                "arguments": {
                    "use_case": "scan_ecommerce_catalog",
                    "arguments": {
                        "url": test_url
                    }
                }
            }
        }
        call_resp = send_recv(call_req)

        content = call_resp.get("result", {}).get("content", [])
        assert len(content) > 0 and content[0]["type"] == "text"
        tool_text = content[0]["text"]

        print("\n" + "=" * 80)
        print("🎯 RÉPONSE SYNTHÉTIQUE COMPACTE (DIGEST-FIRST) FOURNIE PAR LE SERVEUR MCP :")
        print("=" * 80)
        print(tool_text)
        print("=" * 80)
        print("🏆 TEST MCP CLIENT EN CONDITIONS RÉELLES VALIDÉ À 100% SUR BATIHOME !")
        print("=" * 80)

    finally:
        proc.stdin.close()
        proc.terminate()
        proc.wait(timeout=3)

if __name__ == "__main__":
    url_to_test = sys.argv[1] if len(sys.argv) > 1 else "https://batihome.snorbik.fr/#P01_home"
    run_mcp_session(url_to_test)
