#!/usr/bin/env node
/**
 * ========================================================================================
 * OUTIL #01 : WEB ASSETS MANAGER — COUCHE TECHNIQUE DE TESTS (1/4 : TESTS UNITAIRES)
 * ========================================================================================
 * Teste les Entités du Domaine et les Use Cases de la couche Application en isolation
 * avec des adaptateurs simulés (Mocks / In-Memory Ports).
 * ========================================================================================
 */

import assert from 'node:assert/strict';
import { MaquetteAssetEntity } from '../core/domain/entities_and_ports.mjs';
import { HttpsAssetDownloaderAdapter } from '../core/infrastructure/https_asset_downloader.mjs';
import {
  ReplaceRemoteUrlsInReactUseCase,
  GetWebAssetsManifestUseCase
} from '../core/application/use_cases.mjs';

export async function runUnitTests() {
  const results = [];

  // Test 1 : Entité MaquetteAssetEntity
  {
    const entity = new MaquetteAssetEntity({
      id: 'hero_villa_1',
      originalSrc: 'https://cdn.example.com/villa.jpg',
      localPath: '/images/hero/hero_villa_1.jpg',
      category: 'hero',
      filename: 'hero_villa_1.jpg',
      alt: 'Villa bord de mer',
      usedInPages: ['desktop/p01_accueil_home/code.html'],
      status: 'existant'
    });
    assert.equal(entity.category, 'hero');
    assert.equal(entity.localPath, '/images/hero/hero_villa_1.jpg');
    results.push({ name: 'Domain::MaquetteAssetEntity instantiation & invariants', passed: true });
  }

  // Test 2 : Classification sémantique HttpsAssetDownloaderAdapter
  {
    const adapter = new HttpsAssetDownloaderAdapter();
    const cHero = adapter.categorizeAndName({ alt: 'Duplex contemporain avec garde-corps verre', pages: ['p01_accueil_home'] }, 0);
    const cTech = adapter.categorizeAndName({ alt: 'Coupe technique profil aluminium', pages: ['p02_solution'] }, 1);
    const cGuide = adapter.categorizeAndName({ alt: 'Prise de cotes avec niveau à bulle', pages: ['p05_guide'] }, 2);
    assert.equal(cHero.category, 'hero');
    assert.equal(cTech.category, 'technique');
    assert.equal(cGuide.category, 'guides');
    results.push({ name: 'Infrastructure::HttpsAssetDownloaderAdapter semantic categorization', passed: true });
  }

  // Test 3 : Use Case ReplaceRemoteUrlsInReactUseCase avec Mock Port (DI)
  {
    const mockReplacerPort = {
      loadManifest: () => [
        {
          originalSrc: 'https://cdn.example.com/img1.jpg',
          localPath: '/images/solutions/img1.jpg',
          status: 'existant'
        }
      ],
      replaceUrlsInSourceDirs: (_dirs, urlMap, dryRun) => ({
        scanned_files_count: 12,
        modified_files_count: urlMap.size,
        total_replacements: 3,
        dryRun
      })
    };
    const uc = new ReplaceRemoteUrlsInReactUseCase(mockReplacerPort);
    const out = await uc.execute({ manifestPath: 'mock.json', sourceDirs: ['src'], dryRun: true });
    assert.equal(out.status, 'success');
    assert.equal(out.total_replacements, 3);
    results.push({ name: 'Application::ReplaceRemoteUrlsInReactUseCase DI & mock port execution', passed: true });
  }

  // Test 4 : Use Case GetWebAssetsManifestUseCase avec Mock Port
  {
    const mockReplacerPort = {
      loadManifest: () => [{ id: 'a1' }, { id: 'a2' }]
    };
    const uc = new GetWebAssetsManifestUseCase(mockReplacerPort);
    const out = await uc.execute({ manifestPath: 'mock.json' });
    assert.equal(out.total_assets, 2);
    results.push({ name: 'Application::GetWebAssetsManifestUseCase DI & count validation', passed: true });
  }

  return { suite: '01_UNIT_TESTS', total: results.length, passed: results.length, failed: 0, details: results };
}
