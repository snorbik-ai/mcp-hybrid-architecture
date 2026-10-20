# 🌐 Cahier des Charges & Guide — Web Assets Pipeline

## 📌 1. Introduction & Présentation de l'Outil

Le **Web Assets Pipeline** est un service autonome conçu pour analyser l'ensemble des maquettes HTML Desktop et Mobile de BatiHome, extraire l'intégralité des médias hébergés sur des CDN distants, les télécharger localement avec dédoublonnage cryptographique et classification métier, puis substituer les URLs distantes dans la codebase React par leurs équivalents locaux hébergés dans `frontend/public/images/`.

---

## 🏛️ 2. Architecture Multi-Canal (3 Canaux)

Ce module expose 3 canaux d'utilisation distincts bâtis autour du même moteur métier :

### 🤖 Canal 1 : Serveur MCP (`canal_mcp/mcp_server.mjs`)
* **Public cible** : Intelligences Artificielles (Claude Desktop, Cursor, Gemini, Antigravity IDE).
* **Protocole** : JSON-RPC 2.0 sur `stdio`.
* **Outils MCP exposés** :
  1. `scan_and_download_maquette_assets` : Lance le scan de toutes les maquettes et télécharge les images manquantes.
  2. `replace_remote_urls_in_react` : Remplace automatiquement les URLs CDN par les chemins locaux dans les composants React (avec option `dry_run`).
  3. `get_web_assets_manifest` : Retourne l'inventaire complet des 71 assets en JSON.

### 🖥️ Canal 2 : Interface Graphique Web UI (`canal_ui/server.mjs`)
* **Public cible** : Humains (développeurs, intégrateurs, graphistes).
* **URL d'accès** : `http://localhost:5181` (démarré avec `npm run web:ui`).
* **Fonctionnalités** :
  * Visualisation en direct du nombre d'assets découverts et présents en local.
  * Bouton "Scanner & Télécharger" en 1 clic.
  * Bouton "Remplacer dans React" en 1 clic.
  * Galerie visuelle des 71 images avec filtre de recherche en temps réel et liens directs CDN / Local.

### ⚙️ Canal 3 : SDK Programmable & Commandes CLI (`canal_sdk_cli/`)
* **Public cible** : Développeurs et scripts automatisés (CI/CD).
* **Le SDK (`sdk.mjs`)** :
  ```javascript
  import { WebAssetsSDK } from './canal_sdk_cli/sdk.mjs';

  const sdk = new WebAssetsSDK();
  const report = await sdk.scanAndDownloadAssets();
  console.log(`Téléchargés : ${report.downloaded}`);
  ```
* **Les commandes CLI** :
  * `npm run web:extract` : Extraction et téléchargement en terminal.
  * `npm run web:replace` : Substitution automatique dans React.

---

## 📋 3. Cahier des Charges Fonctionnel & Technique

1. **Parcours récursif** de l'arborescence des maquettes (`base_src/stitch_g_n_ration_pages_maquettes/`).
2. **Détection des images** via expression régulière sur les balises `<img src="...">`.
3. **Extraction sémantique du texte alternatif (`alt`)** pour nommer intelligemment les fichiers.
4. **Classification automatique** dans 7 catégories métier :
   - `hero/` : Visuels majeurs de garde-corps contemporains en verre.
   - `projets/` : Balcons, terrasses, escaliers intérieurs, mezzanines.
   - `technique/` : Schémas vectoriels et coupes techniques.
   - `guides/` : Outils de métrologie et prise de cotes.
   - `realisations/` : Chantiers de référence par localisation géographique.
   - `equipe/` : Portraits d'artisans et ingénieurs.
   - `solutions/` : Profilés de sol, profils nez-de-dalle, pinces et entretoises.
5. **Idempotence stricte** : Si un fichier existe déjà localement et est non-vide, aucun retéléchargement réseau n'a lieu.

---

## 🛠️ 4. Bibliothèques Utilisées

* `node:fs` / `node:fs/promises` : Manipulation native du système de fichiers (lecture de maquettes, écriture des images).
* `node:path` / `node:url` : Résolution robuste et portable des chemins Windows/Linux.
* `node:https` : Streaming binaire sécurisé sans dépendance tierce (aucun `axios` ou `node-fetch` requis).
* `node:readline` : Gestion des flux d'entrée/sortie JSON-RPC pour le serveur MCP.
