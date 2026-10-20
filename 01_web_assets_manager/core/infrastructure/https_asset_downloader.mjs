/**
 * ========================================================================================
 * OUTIL INTERNE #01 : WEB ASSETS MANAGER — INFRASTRUCTURE ADAPTER #2
 * Responsabilité Technique Unique : Classification sémantique des visuels et téléchargement
 * binaire HTTPS sécurisé avec gestion d'idempotence.
 * ========================================================================================
 */

import fs from 'node:fs';
import path from 'node:path';
import https from 'node:https';
import { IAssetDownloaderPort } from '../domain/entities_and_ports.mjs';

export class HttpsAssetDownloaderAdapter extends IAssetDownloaderPort {
  categorizeAndName(item, index, customRules = null) {
    const altLower = (item.alt || '').toLowerCase();
    const pageStr = (item.pages || []).join(' ').toLowerCase();
    const combined = `${altLower} ${pageStr}`;

    let category = 'solutions';

    // Règle 1 : Bannières / Hero / Carrousels (Universel)
    if (
      combined.includes('hero') ||
      combined.includes('banner') ||
      combined.includes('banniere') ||
      combined.includes('slider') ||
      combined.includes('headline') ||
      combined.includes('cover') ||
      altLower.includes('duplex contemporain avec garde-corps verre') ||
      (pageStr.includes('p01_accueil_home') && (altLower.includes('duplex') || altLower.includes('hero'))) ||
      altLower.includes('seaside luxury villa') ||
      altLower.includes('mediterranean sea') ||
      altLower.includes('frameless glass balustrade secured by a continuous') ||
      altLower.includes('villa bord de mer')
    ) {
      category = 'hero';
    // Règle 2 : Schémas Techniques / Plans CAO (Universel)
    } else if (
      combined.includes('coupe') ||
      combined.includes('croquis') ||
      combined.includes('technique') ||
      combined.includes('technical') ||
      combined.includes('schema') ||
      combined.includes('plan') ||
      combined.includes('cad') ||
      combined.includes('vector') ||
      combined.includes('cross section') ||
      combined.includes('blueprint')
    ) {
      category = 'technique';
    // Règle 3 : Guides / Documentation / Notices (Universel)
    } else if (
      combined.includes('guide') ||
      combined.includes('notice') ||
      combined.includes('manuel') ||
      combined.includes('tuto') ||
      combined.includes('mètre') ||
      combined.includes('niveau à bulle') ||
      combined.includes('règle') ||
      combined.includes('prise de cotes')
    ) {
      category = 'guides';
    // Règle 4 : Équipe / Collaborateurs (Universel)
    } else if (
      combined.includes('portrait') ||
      combined.includes('architect') ||
      combined.includes('engineer') ||
      combined.includes('atelier') ||
      combined.includes('equipe') ||
      combined.includes('team') ||
      combined.includes('avatar')
    ) {
      category = 'equipe';
    // Règle 5 : Réalisations / Études de cas (Universel)
    } else if (
      combined.includes('realisation') ||
      combined.includes('reference') ||
      combined.includes('chantier') ||
      combined.includes('cassis') ||
      combined.includes('haussmann') ||
      combined.includes('lyon') ||
      combined.includes('annecy') ||
      combined.includes('bordeaux') ||
      combined.includes('cannes')
    ) {
      category = 'realisations';
    // Règle 6 : Projets / Espaces d'application (Universel)
    } else if (
      combined.includes('projet') ||
      combined.includes('project') ||
      combined.includes('terrasse') ||
      combined.includes('escalier') ||
      combined.includes('balcon') ||
      combined.includes('mezzanine')
    ) {
      category = 'projets';
    }

    let cleaned = altLower.replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '').slice(0, 35);
    if (!cleaned) cleaned = `asset_${index + 1}`;
    const slug = `${category}_${cleaned}`;

    return { category, filename: `${slug}.jpg` };
  }

  downloadStream(url, dest) {
    return new Promise((resolve, reject) => {
      fs.mkdirSync(path.dirname(dest), { recursive: true });
      const file = fs.createWriteStream(dest);
      https.get(url, (response) => {
        if (response.statusCode === 200) {
          response.pipe(file);
          file.on('finish', () => file.close(resolve));
        } else {
          file.close();
          fs.unlink(dest, () => {});
          reject(new Error(`Échec HTTP ${response.statusCode}: ${response.statusMessage}`));
        }
      }).on('error', (err) => {
        file.close();
        fs.unlink(dest, () => {});
        reject(err);
      });
    });
  }

  async downloadIfMissing(url, destPath) {
    if (fs.existsSync(destPath) && fs.statSync(destPath).size > 0) {
      return { downloaded: false, existing: true, status: 'existant' };
    }
    try {
      await this.downloadStream(url, destPath);
      return { downloaded: true, existing: false, status: 'téléchargé' };
    } catch (e) {
      return { downloaded: false, existing: false, status: `erreur: ${e.message}` };
    }
  }
}
