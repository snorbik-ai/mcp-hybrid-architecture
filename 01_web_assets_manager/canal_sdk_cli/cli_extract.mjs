#!/usr/bin/env node
/**
 * CANAL 3 : CLI EXTRACTION — WEB ASSETS PIPELINE
 */
import { WebAssetsSDK } from './sdk.mjs';

const sdk = new WebAssetsSDK();

console.log('\n======================================================================');
console.log('🚀 BATIHOME WEB ASSETS PIPELINE — CANAL CLI EXTRACTION');
console.log('======================================================================');

try {
  const result = await sdk.scanAndDownloadAssets();
  console.log(`✅ Extraction terminée avec succès !`);
  console.log(`   • URLs trouvées      : ${result.total_urls}`);
  console.log(`   • Nouveaux téléchargés: ${result.downloaded}`);
  console.log(`   • Déjà présents      : ${result.existing}`);
  console.log(`   • Échecs             : ${result.failed}`);
  console.log(`   • Manifeste          : ${result.manifest_path}`);
  console.log('======================================================================\n');
} catch (err) {
  console.error('❌ Erreur :', err.message);
  process.exit(1);
}
