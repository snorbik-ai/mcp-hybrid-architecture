#!/usr/bin/env node
/**
 * ========================================================================================
 * CANAL 1 : SERVEUR MCP (MODEL CONTEXT PROTOCOL) — WEB ASSETS PIPELINE
 * ========================================================================================
 * Qu'est-ce que ce serveur MCP ?
 * Il implémente la spécification standardisée Model Context Protocol (JSON-RPC 2.0 sur stdio)
 * pour permettre à tout Agent IA (Claude Desktop, Cursor, Gemini, Antigravity IDE) d'exécuter
 * directement l'ingestion d'assets web et le refactoring d'URLs.
 * 
 * Outils MCP exposés à l'IA :
 * 1. `scan_and_download_maquette_assets` : Crawler & téléchargeur automatique
 * 2. `replace_remote_urls_in_react`    : Substituteur d'URLs distantes dans les composants
 * 3. `get_web_assets_manifest`          : Consultation de l'inventaire des 71 assets
 * 
 * Démarrage :
 *   node mcp_server.mjs
 * 
 * Auteur : BatiHome Dev Team
 * ========================================================================================
 */

import readline from 'node:readline';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { WebAssetsSDK } from '../canal_sdk_cli/sdk.mjs';

const sdk = new WebAssetsSDK();

const TOOLS = [
  {
    name: 'scan_and_download_maquette_assets',
    description: "Analyse tous les fichiers HTML de maquettes (code.html), extrait les URLs d'images CDN, les télécharge localement dans frontend/public/images/ et génère le fichier assets-manifest.json.",
    inputSchema: {
      type: 'object',
      properties: {},
      required: []
    }
  },
  {
    name: 'replace_remote_urls_in_react',
    description: "Parcourt tous les composants React (.jsx, .tsx, .css) et remplace les URLs distantes par leurs équivalents locaux enregistrés dans le manifeste.",
    inputSchema: {
      type: 'object',
      properties: {
        dry_run: {
          type: 'boolean',
          description: "Si true, effectue une simulation sans modifier les fichiers sur le disque."
        }
      },
      required: []
    }
  },
  {
    name: 'get_web_assets_manifest',
    description: "Récupère le manifeste JSON des assets web locaux (total d'images, statut, chemins originaux et locaux).",
    inputSchema: {
      type: 'object',
      properties: {},
      required: []
    }
  }
];

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

rl.on('line', async (line) => {
  const trimmed = line.trim();
  if (!trimmed) return;

  try {
    const request = JSON.parse(trimmed);
    const { id, method, params } = request;

    if (method === 'initialize') {
      const response = {
        jsonrpc: '2.0',
        id,
        result: {
          protocolVersion: '2024-11-05',
          capabilities: {
            tools: {}
          },
          serverInfo: {
            name: 'batihome-web-assets-pipeline',
            version: '1.0.0'
          }
        }
      };
      process.stdout.write(JSON.stringify(response) + '\n');
      return;
    }

    if (method === 'tools/list') {
      const response = {
        jsonrpc: '2.0',
        id,
        result: {
          tools: TOOLS
        }
      };
      process.stdout.write(JSON.stringify(response) + '\n');
      return;
    }

    if (method === 'tools/call') {
      const toolName = params?.name;
      const toolArgs = params?.arguments || {};

      let resultText = '';

      if (toolName === 'scan_and_download_maquette_assets') {
        const res = await sdk.scanAndDownloadAssets();
        resultText = JSON.stringify(res, null, 2);
      } else if (toolName === 'replace_remote_urls_in_react') {
        const res = await sdk.replaceRemoteUrls({ dryRun: Boolean(toolArgs.dry_run) });
        resultText = JSON.stringify(res, null, 2);
      } else if (toolName === 'get_web_assets_manifest') {
        const res = await sdk.getManifest();
        resultText = JSON.stringify(res, null, 2);
      } else {
        throw new Error(`Outil inconnu : ${toolName}`);
      }

      const response = {
        jsonrpc: '2.0',
        id,
        result: {
          content: [
            {
              type: 'text',
              text: resultText
            }
          ]
        }
      };
      process.stdout.write(JSON.stringify(response) + '\n');
      return;
    }

    // Requête non supportée
    process.stdout.write(JSON.stringify({
      jsonrpc: '2.0',
      id,
      error: { code: -32601, message: `Méthode non implémentée: ${method}` }
    }) + '\n');

  } catch (err) {
    process.stdout.write(JSON.stringify({
      jsonrpc: '2.0',
      id: null,
      error: { code: -32700, message: `Parse error ou exception: ${err.message}` }
    }) + '\n');
  }
});
