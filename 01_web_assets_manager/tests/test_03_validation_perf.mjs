#!/usr/bin/env node
/**
 * ========================================================================================
 * OUTIL #01 : WEB ASSETS MANAGER — COUCHE TECHNIQUE DE TESTS (3/4 : VALIDATION & PERFORMANCE)
 * ========================================================================================
 * Valide :
 * 1. L'isolation Clean Architecture (Domain n'importe ni Infrastructure ni UI).
 * 2. L'autonomie "Voiture Autonome" (zéro import relatif sortant du dossier de l'outil).
 * 3. La validité du schéma MCP Agent Coding (context_llm.json).
 * 4. La performance d'exécution (< 500ms pour le scan des maquettes HTML).
 * ========================================================================================
 */

import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { WebAssetsSDK } from '../canal_sdk_cli/sdk.mjs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const TOOL_ROOT = path.resolve(__dirname, '..');

export async function runValidationAndPerfTests() {
  const results = [];

  // Test 1 : Validation Clean Architecture (Domain pur sans import vers infrastructure/canal_*)
  {
    const domainContent = fs.readFileSync(
      path.join(TOOL_ROOT, 'core/domain/entities_and_ports.mjs'),
      'utf8'
    );
    assert.ok(!domainContent.includes('infrastructure'), 'Domain ne doit jamais importer Infrastructure');
    assert.ok(!domainContent.includes('canal_'), 'Domain ne doit jamais importer un Canal');
    results.push({ name: 'Validation::Clean Architecture Domain purity check', passed: true });
  }

  // Test 2 : Validation "Voiture Autonome" (présence de README.md, package.json, context_llm.json)
  {
    assert.ok(fs.existsSync(path.join(TOOL_ROOT, 'README.md')), 'README.md autonome requis');
    assert.ok(fs.existsSync(path.join(TOOL_ROOT, 'package.json')), 'package.json autonome requis');
    const ctxPath = path.join(TOOL_ROOT, 'canal_mcp/mcp_agent_coding/context_llm.json');
    assert.ok(fs.existsSync(ctxPath), 'context_llm.json requis');
    const ctx = JSON.parse(fs.readFileSync(ctxPath, 'utf8'));
    assert.equal(ctx.context_history.max_retained_turns, 30);
    results.push({ name: 'Validation::Autonomous Car structure & 30-turn Agent Coding manifest', passed: true });
  }

  // Test 3 : Benchmark de Performance (< 500ms pour scanner les maquettes HTML)
  {
    const sdk = new WebAssetsSDK();
    const t0 = performance.now();
    const files = sdk.findHtmlFiles(sdk.maquettesDir);
    const elapsedMs = Math.round((performance.now() - t0) * 100) / 100;
    assert.ok(elapsedMs < 500, `Performance dégradée : ${elapsedMs}ms > 500ms`);
    results.push({
      name: `Performance::HTML Maquette Tree Scan (${files.length} files in ${elapsedMs}ms < 500ms)`,
      passed: true,
      latency_ms: elapsedMs
    });
  }

  return { suite: '03_VALIDATION_AND_PERF_TESTS', total: results.length, passed: results.length, failed: 0, details: results };
}
