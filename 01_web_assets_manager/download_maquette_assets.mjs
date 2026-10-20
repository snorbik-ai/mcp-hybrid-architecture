/**
 * =============================================================================
 * OUTIL INTERNE : PIPELINE D'EXTRACTION & DE TÉLÉCHARGEMENT DES ASSETS WEB
 * =============================================================================
 * Écosystème : BatiHome E-Commerce & SaaS Garde-Corps
 * Fichier : outils_internes/web_assets_pipeline/download_maquette_assets.mjs
 * 
 * ALGORITHME GÉNÉRAL :
 * 1. Recherche récursive : Exploration du dossier `base_src/` pour identifier tous
 *    les prototypes HTML (`code.html`).
 * 2. Analyse lexicale (Regex) : Extraction de chaque balise `<img src="..." alt="...">`
 *    ciblant les CDN distants (`https://lh3.googleusercontent.com/...`).
 * 3. Dédoublonnage via Table de Hachage : Consolidation des doublons dans une `Map`
 *    pour s'assurer qu'une même image partagée n'est téléchargée qu'une seule fois.
 * 4. Classification sémantique : Analyse croisée du texte alternatif (`alt`) et
 *    du nom de la maquette pour classer l'image dans une catégorie métier :
 *    - 'hero'         : Visuels plein écran et ambiances majeures
 *    - 'projets'      : Typologies (terrasse, escalier, balcon, mezzanine)
 *    - 'solutions'    : Systèmes de fixation et variantes de pose
 *    - 'realisations' : Chantiers réels vérifiés par zone géographique
 *    - 'guides'       : Outils de prise de cotes et métrologie
 *    - 'technique'    : Coupes techniques et schémas vectoriels BE
 *    - 'equipe'       : Portraits d'atelier, architectes, artisans
 * 5. Téléchargement en flux binaire (Streaming HTTPS) : Écriture sur disque local
 *    sans recompression pour préserver la qualité originale.
 * 6. Production du Manifeste unifié : Génération de `assets-manifest.json` pour
 *    permettre la substitution automatisée dans la couche React.
 * =============================================================================
 */

import fs from 'fs';
import path from 'path';
import https from 'https';

// --- CONFIGURATION DES CHEMINS SYSTÈME ---
const PROJECT_ROOT = path.resolve('../..'); // Racine de batihome-ecommerce-garde-corps
const BASE_DIR = path.join(PROJECT_ROOT, 'base_src/stitch_g_n_ration_pages_maquettes');
const TARGET_BASE = path.join(PROJECT_ROOT, 'frontend/public/images');
const MANIFEST_PATH = path.join(PROJECT_ROOT, 'frontend/src/assets-manifest.json');

// --- INITIALISATION DE L'ARBORESCENCE LOCALE ---
const categories = ['hero', 'projets', 'solutions', 'realisations', 'guides', 'technique', 'equipe'];
for (const cat of categories) {
  const dir = path.join(TARGET_BASE, cat);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

/**
 * ÉTAPE 1 : Parcours récursif de l'arborescence des maquettes.
 * @param {string} dir Répertoire de départ
 * @returns {string[]} Liste absolue des chemins vers les fichiers 'code.html'
 */
function findHtmlFiles(dir) {
  let results = [];
  if (!fs.existsSync(dir)) return results;
  const list = fs.readdirSync(dir);
  for (const file of list) {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);
    if (stat.isDirectory()) {
      results = results.concat(findHtmlFiles(fullPath));
    } else if (file === 'code.html') {
      results.push(fullPath);
    }
  }
  return results;
}

const htmlFiles = findHtmlFiles(BASE_DIR);
console.log(`[Web Pipeline] Étape 1 : ${htmlFiles.length} maquettes HTML identifiées.`);

// --- ÉTAPE 2 & 3 : EXTRACTION REGEX ET DÉDOUBLONNAGE ---
// Clé: URL distante absolue, Valeur: { src, alt, pages: [liste des pages l'utilisant] }
const urlMap = new Map();

for (const htmlFile of htmlFiles) {
  const content = fs.readFileSync(htmlFile, 'utf8');
  const relPath = path.relative(BASE_DIR, htmlFile).replace(/\\/g, '/');
  
  // Regex pour capturer les balises img avec URLs Google CDN
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

console.log(`[Web Pipeline] Étape 2 : ${urlMap.size} images uniques consolidées.`);

/**
 * ÉTAPE 4 : Téléchargeur binaire sécurisé basé sur le module natif HTTPS.
 * @param {string} url URL distante de l'image
 * @param {string} dest Chemin absolu de destination sur le disque local
 * @returns {Promise<void>}
 */
function download(url, dest) {
  return new Promise((resolve, reject) => {
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

/**
 * ÉTAPE 5 : Heuristique de classification métier et génération de slug normalisé.
 * @param {{ src: string, alt: string, pages: string[] }} item Métadonnées de l'image
 * @param {number} index Index d'itération pour fallback d'unicité
 * @returns {{ category: string, filename: string }} Catégorie et nom de fichier local
 */
function categorizeAndName(item, index) {
  const altLower = (item.alt || '').toLowerCase();
  const pageStr = item.pages.join(' ').toLowerCase();

  let category = 'solutions';
  let slug = `image_${index + 1}`;

  // 1. Règle Hero : Ambiance duplex ou grand angle mer
  if (
    altLower.includes('duplex contemporain avec garde-corps verre') ||
    (pageStr.includes('p01_accueil_home') && (altLower.includes('duplex') || altLower.includes('hero'))) ||
    altLower.includes('seaside luxury villa') ||
    altLower.includes('mediterranean sea') ||
    altLower.includes('frameless glass balustrade secured by a continuous') ||
    altLower.includes('villa bord de mer')
  ) {
    category = 'hero';
  } 
  // 2. Règle Typologies Projet
  else if (pageStr.includes('projets') || altLower.includes('terrasse vue panoramique') || altLower.includes('escalier intérieur design') || altLower.includes('balcon appartement') || altLower.includes('mezzanine moderne')) {
    category = 'projets';
  } 
  // 3. Règle Dessins Techniques & Coupes BE
  else if (altLower.includes('coupe') || altLower.includes('croquis') || altLower.includes('technique') || altLower.includes('vector') || altLower.includes('cross section')) {
    category = 'technique';
  } 
  // 4. Règle Guides Métriques & Normes NF
  else if (pageStr.includes('guide') || altLower.includes('mètre') || altLower.includes('niveau à bulle') || altLower.includes('règle') || altLower.includes('prise de cotes')) {
    category = 'guides';
  } 
  // 5. Règle Chantiers Réels (Villes de référence)
  else if (pageStr.includes('realisation') || altLower.includes('cassis') || altLower.includes('haussmann') || altLower.includes('lyon') || altLower.includes('annecy') || altLower.includes('bordeaux') || altLower.includes('cannes')) {
    category = 'realisations';
  } 
  // 6. Règle Équipe & Métiers
  else if (altLower.includes('portrait') || altLower.includes('architect') || altLower.includes('engineer') || altLower.includes('atelier')) {
    category = 'equipe';
  }

  // Normalisation du nom de fichier : caractères minuscules alphanumériques
  let cleaned = altLower.replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '').slice(0, 35);
  if (!cleaned) cleaned = `asset_${index + 1}`;
  slug = `${category}_${cleaned}`;

  return { category, filename: `${slug}.jpg` };
}

/**
 * Point d'entrée principal : Orchestre le téléchargement et la création du manifeste.
 */
export async function extractAndDownloadWebAssets() {
  const manifest = [];
  let index = 0;

  for (const [src, item] of urlMap.entries()) {
    const { category, filename } = categorizeAndName(item, index);
    const dest = path.join(TARGET_BASE, category, filename);
    const publicUrl = `/images/${category}/${filename}`;

    console.log(`[Web Pipeline] [${index + 1}/${urlMap.size}] Traitement : ${category}/${filename}...`);
    try {
      // Idempotence : on ne retélécharge pas si le fichier existe déjà
      if (!fs.existsSync(dest)) {
        await download(src, dest);
      }
      manifest.push({
        id: filename.replace('.jpg', ''),
        originalSrc: src,
        localPath: publicUrl,
        category,
        filename,
        alt: item.alt,
        usedInPages: item.pages
      });
    } catch (e) {
      console.warn(`[Web Pipeline] Avertissement sur ${src}: ${e.message}`);
    }
    index++;
  }

  // Sauvegarde synchrone du fichier manifeste pour les autres outils
  fs.writeFileSync(MANIFEST_PATH, JSON.stringify(manifest, null, 2), 'utf8');
  console.log(`[Web Pipeline] Succès : Manifeste généré avec ${manifest.length} entrées dans ${MANIFEST_PATH}`);
  return manifest;
}

// Détection de l'exécution directe en ligne de commande
if (process.argv[1].endsWith('download_maquette_assets.mjs')) {
  extractAndDownloadWebAssets();
}
