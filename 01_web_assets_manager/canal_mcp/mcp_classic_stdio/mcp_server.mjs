#!/usr/bin/env node
/**
 * ========================================================================================
 * OUTIL INTERNE #01 : WEB ASSETS MANAGER — CANAL 1 (VARIANTE 1 : MCP CLASSIC STDIO)
 * ========================================================================================
 * Serveur MCP JSON-RPC 2.0 exposant :
 * 1. scan_and_download_maquette_assets
 * 2. replace_remote_urls_in_react
 * 3. get_web_assets_manifest
 * 4. run_quality_and_tests_suite (Exécution autonome des 4 couches de tests par l'IA)
 * ========================================================================================
 */

import readline from 'node:readline';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { WebAssetsSDK } from '../../canal_sdk_cli/sdk.mjs';

const execFileAsync = promisify(execFile);
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const TEST_RUNNER = path.resolve(__dirname, '../../tests/run_all_suites.mjs');

const sdk = new WebAssetsSDK();

export const TOOLS = [
  {
    name: 'scan_and_download_maquette_assets',
    description: "Analyse tous les fichiers HTML de maquettes (code.html), extrait les URLs d'images CDN, les télécharge localement dans frontend/public/images/ et génère assets-manifest.json.",
    inputSchema: { type: 'object', properties: {}, required: [] }
  },
  {
    name: 'replace_remote_urls_in_react',
    description: "Parcourt tous les composants React (frontend/src/presentation & components) et remplace les URLs distantes par leurs équivalents locaux.",
    inputSchema: {
      type: 'object',
      properties: {
        dry_run: { type: 'boolean', description: 'Simulation sans écriture disque si true.' }
      },
      required: []
    }
  },
  {
    name: 'get_web_assets_manifest',
    description: 'Récupère le manifeste JSON des assets web locaux.',
    inputSchema: { type: 'object', properties: {}, required: [] }
  },
  {
    name: 'run_quality_and_tests_suite',
    description: "Exécute les 4 couches de tests de l'outil #01 (Unitaires, Intégration, Validation/Performance, Smoke) et retourne le rapport JSON complet.",
    inputSchema: { type: 'object', properties: {}, required: [] }
  }
];

export async function handleMcpRequest(request) {
  const { id, method, params } = request;

  if (method === 'initialize') {
    return {
      jsonrpc: '2.0',
      id,
      result: {
        protocolVersion: '2024-11-05',
        capabilities: { tools: {} },
        serverInfo: { name: '01-web-assets-manager-mcp', version: '2.0.0' }
      }
    };
  }

  if (method === 'tools/list') {
    return { jsonrpc: '2.0', id, result: { tools: TOOLS } };
  }

  if (method === 'tools/call') {
    const toolName = params?.name;
    const toolArgs = params?.arguments || {};
    let resObj;

    if (toolName === 'scan_and_download_maquette_assets') {
      resObj = await sdk.scanAndDownloadAssets();
    } else if (toolName === 'replace_remote_urls_in_react') {
      resObj = await sdk.replaceRemoteUrls({ dryRun: Boolean(toolArgs.dry_run) });
    } else if (toolName === 'get_web_assets_manifest') {
      resObj = await sdk.getManifest();
    } else if (toolName === 'run_quality_and_tests_suite') {
      const { stdout } = await execFileAsync(process.execPath, [TEST_RUNNER, '--json']);
      resObj = JSON.parse(stdout);
    } else {
      throw new Error(`Outil inconnu : ${toolName}`);
    }

    return {
      jsonrpc: '2.0',
      id,
      result: { content: [{ type: 'text', text: JSON.stringify(resObj, null, 2) }] }
    };
  }

  return {
    jsonrpc: '2.0',
    id,
    error: { code: -32601, message: `Méthode non implémentée: ${method}` }
  };
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout, terminal: false });
  rl.on('line', async (line) => {
    const trimmed = line.trim();
    if (!trimmed) return;
    try {
      const req = JSON.parse(trimmed);
      const resp = await handleMcpRequest(req);
      process.stdout.write(JSON.stringify(resp) + '\n');
    } catch (err) {
      process.stdout.write(
        JSON.stringify({ jsonrpc: '2.0', id: null, error: { code: -32700, message: err.message } }) + '\n'
      );
    }
  });
}
