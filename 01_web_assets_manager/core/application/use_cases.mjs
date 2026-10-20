/**
 * ========================================================================================
 * OUTIL INTERNE #01 : WEB ASSETS MANAGER — COUCHE APPLICATION (USE CASES / SERVICES MÉTIERS)
 * ========================================================================================
 * Chaque Use Case reçoit ses adaptateurs d'infrastructure par Injection de Dépendances (DI).
 * ========================================================================================
 */

import fs from 'node:fs';
import path from 'node:path';
import { MaquetteAssetEntity } from '../domain/entities_and_ports.mjs';

export class ScanAndDownloadMaquetteAssetsUseCase {
  constructor(htmlScannerPort, downloaderPort, replacerPort) {
    this.htmlScanner = htmlScannerPort;
    this.downloader = downloaderPort;
    this.replacer = replacerPort;
  }

  async execute({ maquettesDir, destDir, manifestPath, categories }) {
    for (const cat of categories) {
      const dir = path.join(destDir, cat);
      if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    }

    const urlMap = this.htmlScanner.extractImageTagsFromHtml(maquettesDir);
    const manifest = [];
    let downloadedCount = 0;
    let existingCount = 0;
    let failedCount = 0;
    let index = 0;

    for (const [src, item] of urlMap.entries()) {
      const { category, filename } = this.downloader.categorizeAndName(item, index);
      const dest = path.join(destDir, category, filename);
      const publicUrl = `/images/${category}/${filename}`;

      const res = await this.downloader.downloadIfMissing(src, dest);
      if (res.downloaded) downloadedCount++;
      else if (res.existing) existingCount++;
      else failedCount++;

      manifest.push(
        new MaquetteAssetEntity({
          id: filename.replace('.jpg', ''),
          originalSrc: src,
          localPath: publicUrl,
          category,
          filename,
          alt: item.alt,
          usedInPages: item.pages,
          status: res.status
        })
      );
      index++;
    }

    this.replacer.saveManifest(manifestPath, manifest);

    return {
      status: 'success',
      total_urls: urlMap.size,
      downloaded: downloadedCount,
      existing: existingCount,
      failed: failedCount,
      manifest_path: manifestPath,
      images_dir: destDir,
      assets: manifest
    };
  }
}

export class ReplaceRemoteUrlsInReactUseCase {
  constructor(replacerPort) {
    this.replacer = replacerPort;
  }

  async execute({ manifestPath, sourceDirs, dryRun = false }) {
    const manifest = this.replacer.loadManifest(manifestPath);
    if (!manifest || manifest.length === 0) {
      return {
        status: 'warning',
        dry_run: dryRun,
        scanned_files_count: 0,
        modified_files_count: 0,
        total_replacements: 0,
        message: `Manifeste vide ou introuvable : ${manifestPath}`
      };
    }

    const urlMap = new Map();
    for (const item of manifest) {
      if (item.localPath && !String(item.status || '').startsWith('erreur')) {
        urlMap.set(item.originalSrc, item.localPath);
      }
    }

    const stats = this.replacer.replaceUrlsInSourceDirs(sourceDirs, urlMap, dryRun);
    return {
      status: 'success',
      dry_run: dryRun,
      ...stats
    };
  }
}

export class GetWebAssetsManifestUseCase {
  constructor(replacerPort) {
    this.replacer = replacerPort;
  }

  async execute({ manifestPath }) {
    const manifest = this.replacer.loadManifest(manifestPath);
    return {
      total_assets: manifest.length,
      assets: manifest
    };
  }
}
