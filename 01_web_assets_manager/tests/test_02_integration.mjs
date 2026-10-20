#!/usr/bin/env node
/**
 * ========================================================================================
 * OUTIL #01 : WEB ASSETS MANAGER — COUCHE TECHNIQUE DE TESTS (2/4 : TESTS D'INTÉGRATION)
 * ========================================================================================
 * Teste l'intégration réelle entre le conteneur DI (WebAssetsSDK), les adaptateurs
 * système de fichiers et le manifeste JSON.
 * ========================================================================================
 */

import assert from 'node:assert/strict';
import fs from 'node:fs';
import { WebAssetsSDK } from '../canal_sdk_cli/sdk.mjs';

export async function runIntegrationTests() {
  const results = [];
  const sdk = new WebAssetsSDK();

  // Test 1 : Intégration DI Container & découverte des maquettes HTML réelles
  {
    const htmlFiles = sdk.findHtmlFiles(sdk.maquettesDir);
    assert.ok(Array.isArray(htmlFiles), 'findHtmlFiles doit retourner un tableau');
    assert.ok(htmlFiles.length >= 10, `Attendu >= 10 maquettes code.html, trouvé ${htmlFiles.length}`);
    results.push({
      name: `Integration::HtmlMaquetteScannerAdapter found ${htmlFiles.length} code.html files`,
      passed: true
    });
  }

  // Test 2 : Lecture du manifeste réel via GetWebAssetsManifestUseCase
  {
    const manifestRes = await sdk.getManifest();
    assert.ok(typeof manifestRes.total_assets === 'number');
    results.push({
      name: `Integration::GetWebAssetsManifestUseCase loaded ${manifestRes.total_assets} assets`,
      passed: true
    });
  }

  // Test 3 : Simulation dry-run de ReplaceRemoteUrlsInReactUseCase sur frontend/src/presentation
  {
    const repRes = await sdk.replaceRemoteUrls({ dryRun: true });
    assert.ok(repRes.status === 'success' || repRes.status === 'warning');
    results.push({
      name: `Integration::ReplaceRemoteUrlsInReactUseCase dry-run scanned ${repRes.scanned_files_count || 0} React files`,
      passed: true
    });
  }

  return { suite: '02_INTEGRATION_TESTS', total: results.length, passed: results.length, failed: 0, details: results };
}
