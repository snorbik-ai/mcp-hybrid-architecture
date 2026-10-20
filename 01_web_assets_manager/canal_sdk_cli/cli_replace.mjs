#!/usr/bin/env node
/**
 * CANAL 3 : CLI REMPLACEMENT — WEB ASSETS PIPELINE
 */
import { WebAssetsSDK } from './sdk.mjs';

const sdk = new WebAssetsSDK();

console.log('\n======================================================================');
console.log('🔄 BATIHOME WEB ASSETS PIPELINE — CANAL CLI REMPLACEMENT REACT');
console.log('======================================================================');

try {
  const result = await sdk.replaceRemoteUrls();
  console.log(`✅ Remplacement terminé avec succès !`);
  console.log(`   • Fichiers modifiés  : ${result.modified_files_count}`);
  console.log(`   • URLs substituées   : ${result.total_replacements}`);
  console.log('======================================================================\n');
} catch (err) {
  console.error('❌ Erreur :', err.message);
  process.exit(1);
}
