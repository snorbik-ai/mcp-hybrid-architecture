#!/usr/bin/env node
/**
 * ========================================================================================
 * OUTIL #01 : WEB ASSETS MANAGER — ORCHESTRATEUR DES 4 COUCHES DE TESTS
 * ========================================================================================
 * Exécute séquentiellement :
 * 1. Tests Unitaires (test_01_unit.mjs)
 * 2. Tests d'Intégration (test_02_integration.mjs)
 * 3. Tests de Validation Code/Clean Arch & Performance (test_03_validation_perf.mjs)
 * 4. Tests Smoke Multi-Canal (test_04_smoke.mjs)
 * ========================================================================================
 */

import { runUnitTests } from './test_01_unit.mjs';
import { runIntegrationTests } from './test_02_integration.mjs';
import { runValidationAndPerfTests } from './test_03_validation_perf.mjs';
import { runSmokeTests } from './test_04_smoke.mjs';

async function main() {
  const jsonOnly = process.argv.includes('--json');
  const t0 = performance.now();

  const suites = [
    await runUnitTests(),
    await runIntegrationTests(),
    await runValidationAndPerfTests(),
    await runSmokeTests()
  ];

  const totalTests = suites.reduce((acc, s) => acc + s.total, 0);
  const totalPassed = suites.reduce((acc, s) => acc + s.passed, 0);
  const totalFailed = suites.reduce((acc, s) => acc + s.failed, 0);
  const durationMs = Math.round((performance.now() - t0) * 100) / 100;

  const report = {
    tool: '01_web_assets_manager',
    status: totalFailed === 0 ? 'PASS' : 'FAIL',
    total_tests: totalTests,
    passed: totalPassed,
    failed: totalFailed,
    duration_ms: durationMs,
    suites
  };

  if (jsonOnly) {
    console.log(JSON.stringify(report, null, 2));
  } else {
    console.log('================================================================================');
    console.log('🧪 RAPPORT DE TESTS — OUTIL #01 : 01_web_assets_manager');
    console.log('================================================================================');
    for (const s of suites) {
      console.log(`✅ [${s.suite}] : ${s.passed}/${s.total} réussis`);
      for (const d of s.details) {
        console.log(`   • ${d.name}`);
      }
    }
    console.log('--------------------------------------------------------------------------------');
    console.log(`🏆 BILAN : ${totalPassed}/${totalTests} TESTS VALIDÉS (${durationMs} ms) — STATUT : ${report.status}`);
    console.log('================================================================================');
  }

  if (totalFailed > 0) process.exit(1);
}

main().catch((err) => {
  console.error('Erreur critique de la suite de tests :', err);
  process.exit(1);
});
