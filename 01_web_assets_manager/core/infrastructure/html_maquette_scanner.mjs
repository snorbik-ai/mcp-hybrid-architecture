/**
 * ========================================================================================
 * OUTIL INTERNE #01 : WEB ASSETS MANAGER — INFRASTRUCTURE ADAPTER #1
 * Responsabilité Technique Unique : Parcours récursif des maquettes HTML et extraction
 * des balises <img> distantes (CDN).
 * ========================================================================================
 */

import fs from 'node:fs';
import path from 'node:path';
import { IHtmlMaquetteScannerPort } from '../domain/entities_and_ports.mjs';

export class HtmlMaquetteScannerAdapter extends IHtmlMaquetteScannerPort {
  findHtmlFiles(dir) {
    let results = [];
    if (!fs.existsSync(dir)) return results;
    const list = fs.readdirSync(dir);
    for (const file of list) {
      const fullPath = path.join(dir, file);
      const stat = fs.statSync(fullPath);
      if (stat.isDirectory()) {
        results = results.concat(this.findHtmlFiles(fullPath));
      } else if (file === 'code.html') {
        results.push(fullPath);
      }
    }
    return results;
  }

  extractImageTagsFromHtml(maquettesDir) {
    const htmlFiles = this.findHtmlFiles(maquettesDir);
    const urlMap = new Map();

    for (const htmlFile of htmlFiles) {
      const content = fs.readFileSync(htmlFile, 'utf8');
      const relPath = path.relative(maquettesDir, htmlFile).replace(/\\/g, '/');
      const imgRegex = /<img[^>]+src=["'](https:\/\/[^"']+)["'][^>]*>/g;
      let match;
      while ((match = imgRegex.exec(content)) !== null) {
        const fullTag = match[0];
        const src = match[1];
        const altMatch = fullTag.match(/alt=["']([^"']*)["']/);
        const alt = altMatch ? altMatch[1] : '';

        if (!urlMap.has(src)) {
          urlMap.set(src, { src, alt, pages: [relPath] });
        } else {
          const entry = urlMap.get(src);
          if (!entry.pages.includes(relPath)) entry.pages.push(relPath);
          if (!entry.alt && alt) entry.alt = alt;
        }
      }
    }
    return urlMap;
  }
}
