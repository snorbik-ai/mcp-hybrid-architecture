#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
CLIENT & RUNNER D'AGENT IA EXTERNE (MODE 2 : AGENT AVEC INTERMÉDIAIRE)
========================================================================================
Qu'est-ce que ce runner ?
Ce script démontre concrètement comment une Intelligence Artificielle externe (ex: un
agent Python utilisant l'API OpenAI, Gemini, Claude, ou Ollama) consomme le serveur MCP
à travers l'intermédiaire HTTP Gateway ou via exécution directe.

Flux d'exécution de l'agent :
1. L'Agent se connecte à la passerelle (http://localhost:5185/tools) pour découvrir les outils.
2. L'Agent reçoit les schémas d'outils et peut les déclarer dans le LLM (`tools=[...]`).
3. Lorsque le LLM décide d'appeler un outil (Function Calling), le runner envoie la requête
   POST vers `/tools/call`.
4. La réponse structurée est réinjectée dans le prompt du LLM pour formuler la réponse finale.

Utilisation :
  python mcp_shared/mcp_agent_runner.py --demo

Auteur : BatiHome Dev Team
========================================================================================
"""

import sys
import json
import urllib.request
import urllib.error
import argparse
from pathlib import Path

DEFAULT_GATEWAY_URL = "http://localhost:5185"


class ExternalAiMcpClient:
    """
    Client intermédiaire utilisé par une IA externe pour dialoguer avec les outils MCP.
    """

    def __init__(self, gateway_url: str = DEFAULT_GATEWAY_URL):
        self.gateway_url = gateway_url.rstrip("/")

    def get_available_tools(self):
        """
        Interroge la passerelle pour récupérer la liste des outils et leurs schémas de paramètres.
        """
        url = f"{self.gateway_url}/tools"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "BatiHome-External-AI-Agent"})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data.get("tools", [])
        except urllib.error.URLError as e:
            raise ConnectionError(
                f"Impossible de joindre la passerelle MCP sur {url}.\n"
                f"Vérifiez que la passerelle est démarrée avec : npm run mcp:gateway\n"
                f"Erreur : {e}"
            )

    def call_tool(self, tool_name: str, arguments: dict):
        """
        Envoie un appel d'outil (Tool Call / Function Call) à la passerelle MCP.
        """
        url = f"{self.gateway_url}/tools/call"
        payload = json.dumps({"name": tool_name, "arguments": arguments}).encode("utf-8")
        try:
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json", "User-Agent": "BatiHome-External-AI-Agent"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as e:
            raise RuntimeError(f"Échec de l'appel d'outil '{tool_name}' : {e}")


def run_demo():
    print("\n" + "=" * 75)
    print("🤖 DÉMONSTRATION DU RUNNER D'AGENT IA EXTERNE (MODE 2 AVEC INTERMÉDIAIRE)")
    print("=" * 75)
    
    client = ExternalAiMcpClient()
    
    print("\n[Étape 1] Découverte dynamique des outils exposés par la passerelle...")
    try:
        tools = client.get_available_tools()
        print(f"✅ {len(tools)} outils découverts avec succès :")
        for t in tools:
            print(f"   • {t['name']} : {t['description']}")
    except ConnectionError as e:
        print(f"\n⚠️ {e}")
        print("\nConseil : Lancez 'python mcp_shared/mcp_http_gateway.py' dans un autre terminal d'abord.")
        return

    print("\n[Étape 2] Simulation d'une décision de l'Agent IA...")
    print("   User prompt : 'IA, donne-moi le texte extrait du catalogue VI_TREE pour vérifier la cote des profilés.'")
    print("   Décision IA : Appel de l'outil 'get_pdf_document_text' avec document_dir='output/garde_corps_vi_tree'")

    print("\n[Étape 3] Envoi du Tool Call à la passerelle...")
    try:
        result = client.call_tool("get_pdf_document_text", {"document_dir": "output/garde_corps_vi_tree"})
        print(f"✅ Résultat reçu de la passerelle (Statut: {result.get('status')}) !")
        text_preview = result.get("result", {}).get("full_text", "")[:350]
        print(f"   Aperçu du texte transmis à l'IA :\n   ---\n   {text_preview}...\n   ---")
        print("\n[Étape 4] L'Agent IA formule sa réponse au client en utilisant les données locales !")
        print("=" * 75 + "\n")
    except Exception as e:
        print(f"❌ Erreur lors de l'appel : {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Lance la démonstration simulée")
    args = parser.parse_args()
    run_demo()
