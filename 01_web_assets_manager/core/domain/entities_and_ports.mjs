/**
 * ========================================================================================
 * OUTIL INTERNE #01 : WEB ASSETS MANAGER — COUCHE DOMAIN (ENTITIES & PORTS)
 * ========================================================================================
 * Définit les entités immuables et les contrats d'interfaces (Ports) pour l'extraction
 * d'assets depuis les maquettes HTML et la réécriture des URLs dans React.
 * Zéro dépendance externe.
 * ========================================================================================
 */

export class MaquetteAssetEntity {
  constructor({ id, originalSrc, localPath, category, filename, alt = '', usedInPages = [], status = 'existant' }) {
    this.id = id;
    this.originalSrc = originalSrc;
    this.localPath = localPath;
    this.category = category;
    this.filename = filename;
    this.alt = alt;
    this.usedInPages = usedInPages;
    this.status = status;
  }
}

export class IHtmlMaquetteScannerPort {
  findHtmlFiles(_dir) { throw new Error('Not implemented'); }
  extractImageTagsFromHtml(_maquettesDir) { throw new Error('Not implemented'); }
}

export class IAssetDownloaderPort {
  categorizeAndName(_item, _index) { throw new Error('Not implemented'); }
  downloadIfMissing(_url, _destPath) { throw new Error('Not implemented'); }
}

export class IReactUrlReplacerPort {
  saveManifest(_manifestPath, _manifestItems) { throw new Error('Not implemented'); }
  loadManifest(_manifestPath) { throw new Error('Not implemented'); }
  replaceUrlsInSourceDirs(_sourceDirs, _urlMap, _dryRun) { throw new Error('Not implemented'); }
}
