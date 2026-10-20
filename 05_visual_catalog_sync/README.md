# 🚗 Outil Interne #05 : Moissonneur Visuel Safe-Path & Compilateur TypeScript (`05_visual_catalog_sync`)

> **Nom Industriel Évocateur Officiel :** Moissonneur Visuel Safe-Path & Compilateur TypeScript  
> **Répertoire Autonome :** `05_visual_catalog_sync`  
> **Type d'architecture :** "Voiture Autonome" (100 % autonome, zéro dépendance externe)  
> **Conception :** Clean Architecture (`core/domain/` $\leftarrow$ `core/application/` $\leftarrow$ `core/infrastructure/`)  
> **Qualité & Tests :** 4 couches de tests (Unitaires, Intégration, Validation/Perf, Smoke) $\rightarrow$ **9/9 PASS**

---

## 📌 1. À quoi sert cet outil ? (Rôle & Vision)

Le **Visual Catalog Sync** assure le pont technique entre les données brutes moissonnées sur le Web et le code applicatif du Frontend React TypeScript :
- **Avant cet outil** : Le téléchargement d'images aux noms SEO très longs sous Windows provoquait l'erreur système fatale `[WinError 206] / [Errno 2] Nom de fichier ou extension trop long` (limite `MAX_PATH` de 260 caractères). De plus, il fallait écrire à la main les interfaces et objets TypeScript pour intégrer les produits au configurateur 3D.
- **Grâce à cet outil** :
  1. Il télécharge de manière idempotente les 140 images de produits et de vignettes de catégories.
  2. Il tronque intelligemment les noms de fichiers (`max_base_len=38`) pour garantir que chaque chemin sur disque reste strictement `< 245 caractères` (zéro échec sous Windows).
  3. Il synchronise automatiquement les visuels vers le dossier public React (`frontend/public/assets/catalogue_verre/`).
  4. Il compile automatiquement le catalogue JSON en un module TypeScript fortement typé (`RawGlassRailingCatalog.ts`) et en inventaire Markdown (`CATALOGUE_MATIERE_PREMIERE_GARDE_CORPS_VERRE.md`).

---

## ⚙️ 2. Comment fonctionne-t-il ? (Sous le capot)

L'outil applique une **Clean Architecture** stricte :
- **Couche Domain (`core/domain/entities_and_ports.py`)** :
  - Entité métier `VisualSyncItemResult` (sku, image_url, local_raw_path, public_frontend_url, path_length_chars, status).
  - Ports abstraits : `IBinaryImageHarvesterPort`, `ICatalogArtifactCompilerPort`.
- **Couche Application / Use Cases (`core/application/use_cases.py`)** :
  - `SyncVisualAssetsUseCase` : Orchestration du téléchargement, de l'assainissement anti-MAX_PATH et de la copie publique.
  - `CompileFrontendCatalogUseCase` : Génération du code source TypeScript et du document Markdown d'inventaire.
- **Couche Infrastructure (`core/infrastructure/`)** :
  - `WindowsSafeImageHarvesterAdapter` : Troncature déterministe et téléchargement binaire sans altération de l'image d'origine.
  - `TypeScriptAndMarkdownCompilerAdapter` : Générateur de code TypeScript avec typage strict et tableaux Markdown documentés.

---

## 🚀 3. Comment l'utiliser ? (Guide Pratique Multi-Canal)

### A. Contrôle Qualité & Tests (Obligatoire avant utilisation)
Double-cliquez sur `run_tests.bat` ou lancez :
```bash
run_tests.bat
# ou avec Python :
python tests/run_all_suites.py
```
*Valide les 4 couches de tests et la compilation TypeScript en moins de 700 ms.*

### B. Canal 1 — Pour les Intelligences Artificielles (MCP)
- **Variante A (MCP JSON-RPC Stdio)** : `python canal_mcp/mcp_classic_stdio/mcp_server.py`. Expose :
  - `sync_visual_assets` : Moissonne et assainit les images.
  - `compile_frontend_catalog` : Génère le fichier TypeScript `RawGlassRailingCatalog.ts`.
  - `sync_and_compile_all` : Exécute le pipeline complet en une seule étape.
  - `run_quality_and_tests_suite` : Exécution autonome des tests par l'IA.
- **Variante B (MCP Agent Coding)** : L'IA consulte [`canal_mcp/mcp_agent_coding/context_llm.json`](./canal_mcp/mcp_agent_coding/context_llm.json) et archive ses comptes rendus dans `history/sessions/` via `context_history_manager.py`.

### C. Canal 2 — Pour les Utilisateurs Humains (Interface Graphique Web UI)
```bash
python canal_ui/server.py --port 5184
```
Ouvrez `http://localhost:5184` dans votre navigateur :
- Visualisez l'état de conformité Windows MAX_PATH (Longueur max : 245 / 260 car.).
- Vérifiez qu'aucune image n'est manquante (`0 manquante`).
- Déclenchez la recompilation TypeScript et Markdown d'un simple clic.

### D. Canal 3 — Pour les Développeurs & Scripts CLI
```bash
python canal_sdk_cli/cli.py --all
```
Ou importez le SDK Python dans votre code :
```python
from canal_sdk_cli.sdk import VisualCatalogSyncSDK
syncer = VisualCatalogSyncSDK()
result = syncer.compile_frontend_catalog()
print(f"TypeScript généré : {result['typescript_module_path']}")
```
