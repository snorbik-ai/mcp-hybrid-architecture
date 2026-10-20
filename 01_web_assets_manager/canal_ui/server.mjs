#!/usr/bin/env node
/**
 * ========================================================================================
 * OUTIL INTERNE #01 : WEB ASSETS MANAGER — CANAL 2 : MINI-APP WEB UI (:5181)
 * ========================================================================================
 * Serveur HTTP autonome avec correction du routage d'images par sous-catégorie
 * (/images/hero/..., /images/solutions/...) et endpoint d'exécution des tests (/api/run-tests).
 * ========================================================================================
 */

import http from 'node:http';
import fs from 'node:fs/promises';
import fsSync from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { WebAssetsSDK } from '../canal_sdk_cli/sdk.mjs';

const execFileAsync = promisify(execFile);
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const sdk = new WebAssetsSDK();
const STATIC_DIR = path.join(__dirname, 'static');
const IMAGES_DIR = sdk.destDir;
const TEST_RUNNER = path.resolve(__dirname, '../tests/run_all_suites.mjs');

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.svg': 'image/svg+xml'
};

export function createWebAssetsServer() {
  return http.createServer(async (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
      res.writeHead(200);
      return res.end();
    }

    const parsedUrl = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
    const pathname = parsedUrl.pathname;

    if (req.method === 'GET' && pathname === '/api/health') {
      res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
      return res.end(JSON.stringify({ status: 'online', tool: '01_web_assets_manager', port: 5181 }));
    }

    if (req.method === 'GET' && pathname === '/api/manifest') {
      try {
        const manifest = await sdk.getManifest();
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
        return res.end(JSON.stringify(manifest));
      } catch (err) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        return res.end(JSON.stringify({ error: err.message }));
      }
    }

    if (req.method === 'POST' && pathname === '/api/scan-download') {
      try {
        const result = await sdk.scanAndDownloadAssets();
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
        return res.end(JSON.stringify(result));
      } catch (err) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        return res.end(JSON.stringify({ status: 'error', message: err.message }));
      }
    }

    if (req.method === 'POST' && pathname === '/api/replace') {
      try {
        const result = await sdk.replaceRemoteUrls({ dryRun: true });
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
        return res.end(JSON.stringify(result));
      } catch (err) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        return res.end(JSON.stringify({ status: 'error', message: err.message }));
      }
    }

    if (req.method === 'POST' && pathname === '/api/run-tests') {
      try {
        const { stdout } = await execFileAsync(process.execPath, [TEST_RUNNER, '--json']);
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
        return res.end(stdout);
      } catch (err) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        return res.end(JSON.stringify({ status: 'error', message: err.message }));
      }
    }

    // Correction du bug d'accès aux sous-dossiers d'images (/images/hero/..., /images/solutions/...)
    if (pathname.startsWith('/images/')) {
      const relSubpath = pathname.slice('/images/'.length).replace(/\.\./g, '');
      const targetPath = path.join(IMAGES_DIR, relSubpath);
      if (fsSync.existsSync(targetPath) && fsSync.statSync(targetPath).isFile()) {
        const ext = path.extname(targetPath).toLowerCase();
        res.writeHead(200, { 'Content-Type': MIME_TYPES[ext] || 'application/octet-stream' });
        return fsSync.createReadStream(targetPath).pipe(res);
      }
    }

    let filePath = path.join(STATIC_DIR, pathname === '/' ? 'index.html' : pathname);
    if (fsSync.existsSync(filePath) && (await fs.stat(filePath)).isFile()) {
      const ext = path.extname(filePath).toLowerCase();
      res.writeHead(200, { 'Content-Type': MIME_TYPES[ext] || 'text/plain' });
      const content = await fs.readFile(filePath);
      return res.end(content);
    }

    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('404 Not Found');
  });
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const portIdx = process.argv.indexOf('--port');
  const port = portIdx !== -1 && process.argv[portIdx + 1] ? Number(process.argv[portIdx + 1]) : 5181;
  const server = createWebAssetsServer();
  server.listen(port, () => {
    console.log(`🌐 [01_web_assets_manager] Web UI active sur http://localhost:${port}`);
  });
}
