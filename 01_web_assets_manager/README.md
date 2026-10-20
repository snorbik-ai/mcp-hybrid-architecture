# 🚗 Outil Interne #01 : Moissonneur d'Assets Web & Relieur Local React TSX (`01_web_assets_manager`)

> **Nom Industriel Évocateur Officiel :** Moissonneur d'Assets Web & Relieur Local React TSX  
> **Répertoire Autonome :** `01_web_assets_manager`  
> **Type d'architecture :** "Voiture Autonome" (100 % autonome, zéro dépendance externe)  
> **Conception :** Clean Architecture (`core/domain/` $\leftarrow$ `core/application/` $\leftarrow$ `core/infrastructure/`)  
> **Qualité & Tests :** 4 couches de tests (Unitaires, Intégration, Validation/Perf, Smoke) $\rightarrow$ **12/12 PASS**

---

## 📌 1. À quoi sert cet outil ? (Rôle & Vision)

Le **Web Assets Manager** résout le problème de dépendance aux CDN externes et de liens cassés lors de l'intégration de maquettes HTML :
- **Avant cet outil** : Les maquettes HTML (conçues sous Stitch / Tailwind) contenaient des balises `<img src="https://cdn.example.com/...">` distantes. Si le CDN devenait inaccessible ou si les composants React étaient copiés hors ligne, les images disparaissaient.
- **Grâce à cet outil** :
  1. Il parcourt récursivement toutes les maquettes HTML (`code.html`).
  2. Il télécharge automatiquement toutes les images distantes sans doublon.
  3. Il classe les visuels dans 7 répertoires métiers (`hero`, `projets`, `technique`, `guides`, `realisations`, `equipe`, `solutions`).
  4. Il réécrit automatiquement les URLs distantes dans tous les fichiers React (`.tsx`, `.jsx`, `.css`) pour pointer vers les assets locaux (`frontend/public/images/`).

---

## ⚙️ 2. Comment fonctionne-t-il ? (Sous le capot)

L'outil applique une **Clean Architecture** stricte :
- **Couche Domain (`core/domain/entities_and_ports.mjs`)** :
  - Entité métier [`MaquetteAssetEntity`](./core/domain/entities_and_ports.mjs) définissant les attributs immuables d'un asset (id, src originale, chemin local, catégorie, alt, pages d'utilisation, statut).
  - Interfaces abstraites (*Ports*) : `IHtmlMaquetteScannerPort`, `IAssetDownloaderPort`, `IReactUrlReplacerPort`.
- **Couche Application / Use Cases (`core/application/use_cases.mjs`)** :
  - `ScanAndDownloadMaquetteAssetsUseCase` : Orchestration du scan et du téléchargement idempotent.
  - `ReplaceRemoteUrlsInReactUseCase` : Scan des composants React et remplacement sécurisé des URLs (avec support `dry_run`).
  - `GetWebAssetsManifestUseCase` : Consultation de l'inventaire complet du manifeste JSON.
- **Couche Infrastructure (`core/infrastructure/`)** :
  - `HtmlMaquetteScannerAdapter` : Analyse syntaxique des maquettes et extraction des balises `<img>`.
  - `HttpsAssetDownloaderAdapter` : Téléchargement HTTPS résilient et classification sémantique par mots-clés de l'attribut `alt`.
  - `ReactUrlReplacerAdapter` : Écriture atomique du manifeste et substitution de chaînes dans les fichiers de code source.

---

## 🚀 3. Comment l'utiliser ? (Guide Pratique Multi-Canal)

### A. Contrôle Qualité & Tests (Obligatoire avant utilisation)
Double-cliquez sur `run_tests.bat` ou lancez :
```bash
run_tests.bat
# ou avec Node.js :
npm test
```
*Vérifie automatiquement les tests unitaires, l'intégration, la pureté de l'architecture, les benchmarks de latence (< 5 ms) et le bon fonctionnement des serveurs.*

### B. Canal 1 — Pour les Intelligences Artificielles (MCP)
- **Variante A (MCP JSON-RPC Stdio)** : `npm run mcp` ou `node canal_mcp/mcp_classic_stdio/mcp_server.mjs`. Expose les tools :
  - `scan_and_download_maquette_assets`
  - `replace_remote_urls_in_react`
  - `get_web_assets_manifest`
  - `run_quality_and_tests_suite` (l'IA peut exécuter et vérifier les tests toute seule)
- **Variante B (MCP Agent Coding)** : L'IA lit [`canal_mcp/mcp_agent_coding/context_llm.json`](./canal_mcp/mcp_agent_coding/context_llm.json) et archive ses comptes rendus de session dans `canal_mcp/mcp_agent_coding/history/` avec une fenêtre glissante de 30 tours via son `context_history_manager.py` embarqué.

### C. Canal 2 — Pour les Utilisateurs Humains (Interface Graphique Web UI)
```bash
npm run ui
# ou : node canal_ui/server.mjs --port 5181
```
Ouvrez `http://localhost:5181` dans votre navigateur :
- Visualisez les assets répertoriés.
- Lancez le scan ou le remplacement d'un clic.
- Exécutez les 4 couches de tests via le bouton d'audit dédié.

### D. Canal 3 — Pour les Développeurs & Scripts CLI
```bash
npm run extract   # Télécharge et génère le manifeste JSON
npm run replace   # Remplace les URLs dans le code React
```
Ou importez le SDK JavaScript dans votre propre code :
```javascript
import { WebAssetsSDK } from './canal_sdk_cli/sdk.mjs';
const sdk = new WebAssetsSDK();
const result = await sdk.scanAndDownloadAssets();
console.log(`Assets traités : ${result.total_urls}`);
```
