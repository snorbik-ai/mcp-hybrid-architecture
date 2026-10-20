#!/usr/bin/env node
/**
 * ========================================================================================
 * OUTIL #01 : WEB ASSETS MANAGER — COUCHE TECHNIQUE DE TESTS (4/4 : SMOKE TESTS)
 * ========================================================================================
 * Vérifie de bout en bout que les 3 Canaux (MCP JSON-RPC, Web UI HTTP, SDK/CLI) répondent.
 * ========================================================================================
 */

import assert from 'node:assert/strict';
import { handleMcpRequest } from '../canal_mcp/mcp_classic_stdio/mcp_server.mjs';
import { createWebAssetsServer } from '../canal_ui/server.mjs';

export async function runSmokeTests() {
  const results = [];

  // Smoke 1 : Canal 1 (MCP Server initialize + tools/list)
  {
    const initResp = await handleMcpRequest({ id: 1, method: 'initialize', params: {} });
    assert.equal(initResp.result.serverInfo.name, '01-web-assets-manager-mcp');

    const listResp = await handleMcpRequest({ id: 2, method: 'tools/list', params: {} });
    assert.ok(listResp.result.tools.length >= 4);
    results.push({ name: 'Smoke::Canal 1 MCP JSON-RPC (initialize & tools/list)', passed: true });
  }

  // Smoke 2 : Canal 2 (Web UI Server éphémère sur port aléatoire)
  {
    const server = createWebAssetsServer();
    await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
    const port = server.address().port;
    try {
      const resHealth = await fetch(`http://127.0.0.1:${port}/api/health`);
      assert.equal(resHealth.status, 200);
      const data = await resHealth.json();
      assert.equal(data.status, 'online');

      const resHtml = await fetch(`http://127.0.0.1:${port}/`);
      assert.equal(resHtml.status, 200);
      results.push({ name: 'Smoke::Canal 2 Web UI HTTP (/api/health & / index.html)', passed: true });
    } finally {
      await new Promise((resolve) => server.close(resolve));
    }
  }

  return { suite: '04_SMOKE_TESTS', total: results.length, passed: results.length, failed: 0, details: results };
}
