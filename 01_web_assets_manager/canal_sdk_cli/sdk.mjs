#!/usr/bin/env node
/**
 * ========================================================================================
 * OUTIL INTERNE #01 : WEB ASSETS MANAGER — CANAL 3 : SDK (CONTENEUR D'INJECTION DE DÉPENDANCES)
 * ========================================================================================
 * Assemble les adaptateurs d'Infrastructure à responsabilité unique dans les Use Cases
 * de la couche Application (Clean Architecture).
 * ========================================================================================
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { HtmlMaquetteScannerAdapter } from '../core/infrastructure/html_maquette_scanner.mjs';
import { HttpsAssetDownloaderAdapter } from '../core/infrastructure/https_asset_downloader.mjs';
import { ReactUrlReplacerAdapter } from '../core/infrastructure/react_url_replacer.mjs';
import {
  ScanAndDownloadMaquetteAssetsUseCase,
  ReplaceRemoteUrlsInReactUseCase,
  GetWebAssetsManifestUseCase
} from '../core/application/use_cases.mjs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export class WebAssetsSDK {
  constructor(options = {}) {
    this.toolRoot = path.resolve(__dirname, '..');
    this.workspaceRoot = options.workspaceRoot || path.resolve(__dirname, '../../..');

    const localMaquettes = path.join(this.toolRoot, 'data/sample_maquettes');
    const wsMaquettes = path.join(this.workspaceRoot, 'base_src/stitch_g_n_ration_pages_maquettes');
    this.maquettesDir = options.maquettesDir || (fs.existsSync(wsMaquettes) ? wsMaquettes : localMaquettes);

    const localManifest = path.join(this.toolRoot, 'data/assets-manifest.json');
    const wsManifest = path.join(this.workspaceRoot, 'frontend/src/assets-manifest.json');
    this.manifestPath = options.manifestPath || (fs.existsSync(wsManifest) ? wsManifest : localManifest);

    this.destDir = options.destDir || path.join(this.workspaceRoot, 'frontend/public/images');

    // Supporte à la fois la Clean Architecture frontend/src/presentation et frontend/src/components
    this.sourceDirs = options.sourceDirs || [
      path.join(this.workspaceRoot, 'frontend/src/presentation'),
      path.join(this.workspaceRoot, 'frontend/src/components')
    ];
    this.categories = ['hero', 'projets', 'solutions', 'realisations', 'guides', 'technique', 'equipe'];

    // Injection de Dépendances (Infrastructure -> Use Cases)
    this.htmlScannerAdapter = options.htmlScannerAdapter || new HtmlMaquetteScannerAdapter();
    this.downloaderAdapter = options.downloaderAdapter || new HttpsAssetDownloaderAdapter();
    this.replacerAdapter = options.replacerAdapter || new ReactUrlReplacerAdapter();

    this.scanUseCase = new ScanAndDownloadMaquetteAssetsUseCase(
      this.htmlScannerAdapter,
      this.downloaderAdapter,
      this.replacerAdapter
    );
    this.replaceUseCase = new ReplaceRemoteUrlsInReactUseCase(this.replacerAdapter);
    this.manifestUseCase = new GetWebAssetsManifestUseCase(this.replacerAdapter);
  }

  findHtmlFiles(dir) {
    return this.htmlScannerAdapter.findHtmlFiles(dir);
  }

  categorizeAndName(item, index) {
    return this.downloaderAdapter.categorizeAndName(item, index);
  }

  async scanAndDownloadAssets() {
    return this.scanUseCase.execute({
      maquettesDir: this.maquettesDir,
      destDir: this.destDir,
      manifestPath: this.manifestPath,
      categories: this.categories
    });
  }

  async replaceRemoteUrls({ dryRun = false } = {}) {
    return this.replaceUseCase.execute({
      manifestPath: this.manifestPath,
      sourceDirs: this.sourceDirs,
      dryRun
    });
  }

  async getManifest() {
    return this.manifestUseCase.execute({
      manifestPath: this.manifestPath
    });
  }
}
