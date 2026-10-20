/**
 * =============================================================================
 * OUTIL INTERNE : REMPLACEUR AUTOMATISÉ D'URLS CDN DANS LA CODEBASE REACT
 * =============================================================================
 * Écosystème : BatiHome E-Commerce & SaaS Garde-Corps
 * Fichier : outils_internes/web_assets_pipeline/replace_remote_urls.mjs
 * 
 * ALGORITHME GÉNÉRAL :
 * 1. Chargement de la table de correspondance : Lecture du fichier `assets-manifest.json`
 *    produit par l'étape de téléchargement. Chaque couple `originalSrc -> localPath`
 *    est indexé dans une `Map`.
 * 2. Découverte récursive des composants React : Scan des répertoires de code
 *    sources TypeScript/React (`.tsx`, `.ts`) sous `frontend/src/presentation/`.
 * 3. Remplacement déterministe (In-Place String Replacement) : Pour chaque fichier,
 *    recherche de toutes les occurrences des URLs distantes et remplacement
 *    par leur chemin local `/images/...`.
 * 4. Préservation de l'intégrité du code : Seules les chaînes exactes sont remplacées,
 *    préservant l'indentation, les imports, le JSX et les types TypeScript.
 * =============================================================================
 */

import fs from 'fs';
import path from 'path';

// --- CONFIGURATION DES CHEMINS ---
const PROJECT_ROOT = path.resolve('../..'); // Racine de batihome-ecommerce-garde-corps
const MANIFEST_PATH = path.join(PROJECT_ROOT, 'frontend/src/assets-manifest.json');
const TARGET_DIR = path.join(PROJECT_ROOT, 'frontend/src/presentation');

/**
 * Fonction principale exécutant le remplacement.
 */
export function replaceRemoteUrls() {
  // Vérification de la présence préalable du manifeste
  if (!fs.existsSync(MANIFEST_PATH)) {
    console.error(`[URL Replacer] Erreur : Manifeste introuvable à l'emplacement : ${MANIFEST_PATH}`);
    console.error(`[URL Replacer] Conseil : Exécutez d'abord 'npm run web:extract' pour générer le manifeste.`);
    return;
  }

  // ÉTAPE 1 : Construction de la table de hachage O(1) pour les correspondances
  const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8'));
  const urlMap = new Map();
  for (const item of manifest) {
    urlMap.set(item.originalSrc, item.localPath);
  }
  console.log(`[URL Replacer] ${urlMap.size} correspondances chargées depuis le manifeste.`);

  /**
   * ÉTAPE 2 : Recherche récursive des composants TypeScript / React.
   * @param {string} dir Répertoire à scanner
   * @returns {string[]} Chemins absolus des fichiers .tsx et .ts
   */
  function getTsxFiles(dir) {
    let results = [];
    if (!fs.existsSync(dir)) return results;
    const list = fs.readdirSync(dir);
    for (const file of list) {
      const fullPath = path.join(dir, file);
      const stat = fs.statSync(fullPath);
      if (stat.isDirectory()) {
        results = results.concat(getTsxFiles(fullPath));
      } else if (file.endsWith('.tsx') || file.endsWith('.ts')) {
        results.push(fullPath);
      }
    }
    return results;
  }

  const files = getTsxFiles(TARGET_DIR);
  let totalReplaced = 0;
  let filesModified = 0;

  // ÉTAPE 3 : Remplacement dans chaque composant
  for (const file of files) {
    let content = fs.readFileSync(file, 'utf8');
    let modified = false;

    for (const [remoteUrl, localPath] of urlMap.entries()) {
      if (content.includes(remoteUrl)) {
        content = content.replaceAll(remoteUrl, localPath);
        modified = true;
        totalReplaced++;
      }
    }

    if (modified) {
      fs.writeFileSync(file, content, 'utf8');
      filesModified++;
      console.log(`[URL Replacer] Mis à jour : ${path.relative(PROJECT_ROOT, file)}`);
    }
  }

  console.log(`=======================================================`);
  console.log(`[URL Replacer] SUCCÈS : ${totalReplaced} URLs distantes remplacées.`);
  console.log(`[URL Replacer] ${filesModified} fichier(s) composant(s) mis à jour.`);
  console.log(`=======================================================`);
}

// Détection de l'exécution directe en ligne de commande
if (process.argv[1].endsWith('replace_remote_urls.mjs')) {
  replaceRemoteUrls();
}
