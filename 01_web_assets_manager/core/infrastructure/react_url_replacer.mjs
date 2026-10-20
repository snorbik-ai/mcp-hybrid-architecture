/**
 * ========================================================================================
 * OUTIL INTERNE #01 : WEB ASSETS MANAGER — INFRASTRUCTURE ADAPTER #3
 * Responsabilité Technique Unique : Persistance du manifeste JSON et réécriture atomique
 * des URLs distantes dans les composants React (presentation/ et components/).
 * ========================================================================================
 */

import fs from 'node:fs';
import path from 'node:path';
import { IReactUrlReplacerPort } from '../domain/entities_and_ports.mjs';

export class ReactUrlReplacerAdapter extends IReactUrlReplacerPort {
  saveManifest(manifestPath, manifestItems) {
    fs.mkdirSync(path.dirname(manifestPath), { recursive: true });
    fs.writeFileSync(manifestPath, JSON.stringify(manifestItems, null, 2), 'utf8');
  }

  loadManifest(manifestPath) {
    if (!fs.existsSync(manifestPath)) return [];
    return JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  }

  replaceUrlsInSourceDirs(sourceDirs, urlMap, dryRun = false) {
    const compFiles = [];
    const scanDir = (dir) => {
      if (!fs.existsSync(dir)) return;
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      for (const entry of entries) {
        const full = path.join(dir, entry.name);
        if (entry.isDirectory()) {
          scanDir(full);
        } else if (
          entry.isFile() &&
          (entry.name.endsWith('.jsx') || entry.name.endsWith('.tsx') || entry.name.endsWith('.css'))
        ) {
          compFiles.push(full);
        }
      }
    };

    for (const dir of sourceDirs) {
      scanDir(dir);
    }

    let modifiedFiles = 0;
    let totalReplacements = 0;

    for (const filePath of compFiles) {
      let content = fs.readFileSync(filePath, 'utf8');
      let replacedInFile = 0;

      for (const [remoteUrl, localPath] of urlMap.entries()) {
        if (content.includes(remoteUrl)) {
          const occurrences = content.split(remoteUrl).length - 1;
          content = content.replaceAll(remoteUrl, localPath);
          replacedInFile += occurrences;
        }
      }

      if (replacedInFile > 0) {
        modifiedFiles++;
        totalReplacements += replacedInFile;
        if (!dryRun) {
          fs.writeFileSync(filePath, content, 'utf8');
        }
      }
    }

    return {
      scanned_files_count: compFiles.length,
      modified_files_count: modifiedFiles,
      total_replacements: totalReplacements
    };
  }
}
