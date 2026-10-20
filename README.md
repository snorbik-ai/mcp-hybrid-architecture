# 🛠️ MCP-TOOLKIT — Suite des 5 Outils Métiers Autonomes pour Agents IA

Bienvenue dans **`mcp-toolkit`**, une suite de 5 outils modulaires conçus pour automatiser les tâches d'extraction, d'audit média et de structuration de catalogues e-commerce complexes, exploitable aussi bien par un développeur que par un agent d'intelligence artificielle (Cursor, Claude Desktop, Antigravity IDE, Windsurf, Claude Code).

---

## 🎯 1. Le Problème que ce Projet Cherche à Résoudre

Lors de la construction ou de la migration d'un site e-commerce technique (comme la boutique BatiHome dédiée aux garde-corps et quincaillerie industrielle), les équipes sont confrontées à quatre goulets d'étranglement majeurs :
1. **La dispersion des assets graphiques :** Maquettes HTML dispersées avec des URLs d'images distantes non hébergées localement.
2. **L'hétérogénéité des données techniques :** Fiches produits et plans d'assemblage enfermés dans de volumineux catalogues PDF fabricants.
3. **La disparité de qualité des médias :** Photos de résolution insuffisante pour l'affichage Retina/HD, doublons d'images gaspillant de la bande passante.
4. **La surcharge de contexte des LLMs :** Lorsqu'un agent IA traditionnel tente d'inspecter un catalogue ou un DOM e-commerce, il déverse des milliers de lignes de JSON brut dans sa fenêtre de contexte, provoquant explosion de coûts, amnésie et hallucinations tarifaires.

`mcp-toolkit` résout ces défis en fournissant des moteurs déterministes locaux, rapides et autonomes, capables d'effectuer le travail lourd en millisecondes et de renvoyer à l'IA uniquement des résumés structurés fiables.

---

## 🔌 2. Le Rôle du Protocole MCP et les Limites Pratiques Rencontrées

Le protocole standard **MCP (Model Context Protocol)**, introduit par Anthropic, standardise la connexion entre les modèles de langage et les outils locaux via des échanges JSON-RPC (sur `stdio` ou serveur HTTP).

Toutefois, lors d'une utilisation industrielle intensive sur des données volumineuses, deux constats opérationnels s'imposent :
- **Gestion du volume de données dans la fenêtre de contexte :** Le protocole MCP standard transmet fidèlement les sorties produites par les outils vers le client hôte. Lorsqu'un outil renvoie une charge volumineuse (un arbre DOM complet ou un dump de dizaines de fiches produits avec attributs), la fenêtre de contexte de l'agent est fortement sollicitée, ce qui augmente le coût d'inférence et peut dégrader l'attention du modèle sur ses instructions d'origine.
- **Continuité de contexte et persistance :** Le protocole MCP standard opère comme un protocole de transport de requêtes et de réponses (RPC). La mémoire de travail, l'historique et la persistance entre étapes incombent traditionnellement au client hôte ou à la couche agent. Sur des workflows longs en plusieurs étapes, l'absence de mémoires de travail intermédiaires structurées oblige souvent l'agent à relire ou recalculer des informations déjà traitées.

Pour concilier la standardisation du protocole et la maîtrise du contexte, ce projet propose deux approches complémentaires :
- **En mode MCP standard (Outils 01, 02, 03, 05) :** Les serveurs respectent rigoureusement les spécifications JSON-RPC (`initialize`, `tools/list`, `tools/call`) avec des outils ciblés et sans surcharge.
- **En mode optimisé "Digest-First" (Outil #04) :** L'outil intègre une passerelle de cycle de vie qui sauvegarde le rapport exhaustif et le catalogue sur le disque local, tout en renvoyant à l'agent un résumé exécutif compact (470 octets dans notre cas de référence BatiHome). L'agent consigne ses étapes dans un carnet de bord de session (`turn_report.json`), évitant ainsi la saturation du contexte sans perte d'information pour l'utilisateur.

---

## 💡 3. Contribution Propre de l'Auteur

Ce projet ne prétend pas réinventer le protocole MCP, mais propose une implémentation architecturale rigoureuse articulée autour de 4 principes :
1. **Organisation en "Voitures Autonomes" :** Les 5 outils (`01_` à `05_`) sont découpés en modules indépendants (Clean Architecture : Domain, Application, Infrastructure). Chaque outil possède son propre serveur MCP, sa propre CLI, sa mini-interface Web de visualisation et sa batterie de tests.
2. **Stratégie "Digest-First" :** Renvoi d'un résumé exécutif compact à l'IA avec un lien direct vers un rapport visuel HTML interactif généré localement pour l'utilisateur.
3. **Mémoire Glissante d'Ingénierie :** Gestionnaire de session (`context_history_manager.py`) maintenant un carnet de bord borné à 30 tours pour éviter l'oubli sans surcharger le contexte.
4. **Passerelle Universelle HTTP / REST :** Un reverse proxy local (`mcp_shared/mcp_http_gateway.py` sur le port 5185) unifiant les 17 outils sous un endpoint unique pour les environnements ne supportant pas `stdio`.

---

## 🧭 4. Présentation des 5 MCP

| Répertoire | Rôle Industriel | Prérequis | Sorties Produites |
| :--- | :--- | :--- | :--- |
| [`01_web_assets_manager/`](./01_web_assets_manager/) | **Gestionnaire d'Assets Web & Relieur React** : Scanne les maquettes HTML, télécharge les médias et met à jour les URLs relatives dans les composants React. | Node.js v18+ | `assets-manifest.json`, fichiers React mis à jour |
| [`02_pdf_technical_extractor/`](./02_pdf_technical_extractor/) | **Extracteur Technique PDF** : Découpe les catalogues PDF fabricants, extrait les schémas CAO et génère des rendus de pages HD 150 DPI. | Python 3.10+, PyMuPDF | Images PNG HD, fiches techniques découpées |
| [`03_media_quality_auditor/`](./03_media_quality_auditor/) | **Auditeur Qualité Média & Dédoublonneur** : Analyse la netteté et dimensions réelles ($\ge 1200\times 700$) et supprime les doublons via empreinte MD5. | Python 3.10+, Pillow | Rapport d'audit de conformité, liste des doublons |
| [`04_ecommerce_catalog_scanner/`](./04_ecommerce_catalog_scanner/) | **Scanneur de Catalogue E-commerce** : Analyse le DOM des boutiques (SSR PrestaShop et SPA React BatiHome), extrait SKUs, prix TTC/HT et génère un rapport interactif. | Python 3.10+, BeautifulSoup4 *(Playwright optionnel pour SPAs)* | `catalogue.json`, rapport HTML interactif |
| [`05_visual_catalog_sync/`](./05_visual_catalog_sync/) | **Synchroniseur Visuel & Compilateur TS** : Rapatrie les visuels avec contrainte safe-path (`MAX_PATH < 260`) et compile le catalogue en TypeScript. | Python 3.10+ *(0 dépendance pip)* | `RawGlassRailingCatalog.ts`, assets locaux renommés |

---

## 🚀 5. Prérequis et Parcours d'Installation

### Prérequis Système
- **Python** : Version `3.10` à `3.13` (64-bit recommandé).
- **Node.js** : Version `18.0+` (LTS recommandée) — *Requis uniquement pour l'outil #01*.
- **OS** : Windows 10/11, Linux, macOS.

---

### Parcours 1 — Installation Automatisée sous Windows (Recommandé)
Double-cliquez sur `install.bat` ou lancez dans votre terminal Windows :
```cmd
install.bat
```
*Le script détecte Python, crée automatiquement l'environnement virtuel local `.venv`, met à niveau pip, installe les dépendances requises et exécute un contrôle de santé final.*

> **Si Python n'est pas encore installé sur votre machine :**  
> `install.bat` vous avertit immédiatement et vous propose d'ouvrir la page officielle [python.org/downloads](https://www.python.org/downloads/). Cochez bien `☑ Add Python to PATH` lors de l'installation, puis relancez `install.bat`.

---

### Parcours 2 — Installation Manuelle (Linux / macOS / Développeurs)
```bash
# 1. Créer et activer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate    # Sur Windows : .venv\Scripts\activate

# 2. Installer les dépendances
pip install -r requirements-all.txt
```
*(L'outil #01 utilise les API natives de Node.js et ne requiert aucun `npm install` externe).*

---

### Parcours 3 — Installation Modulaire (Un Seul Outil)
Si vous n'avez besoin que d'un seul outil spécifique, isolez son installation :
```cmd
# Outil #01 uniquement (Node.js) :
install.bat 01

# Outil #02 uniquement (PyMuPDF) :
install.bat 02    # ou : pip install -r 02_pdf_technical_extractor/requirements.txt

# Outil #03 uniquement (Pillow) :
install.bat 03    # ou : pip install -r 03_media_quality_auditor/requirements.txt

# Outil #04 uniquement (BeautifulSoup4) :
install.bat 04    # ou : pip install -r 04_ecommerce_catalog_scanner/requirements.txt

# Outil #05 uniquement (Standard) :
install.bat 05    # Aucune dépendance externe requise
```

---

## 🧪 6. Commandes de Diagnostic, de Test et d'Utilisation

### 🩺 Diagnostic de Santé (`doctor.bat`)
Pour diagnostiquer votre environnement, vérifier les dépendances et s'assurer que le port 5185 est libre :
```cmd
doctor.bat
# Ou sous Linux/macOS :
python mcp_shared/mcp_doctor.py
```

### 🧪 Exécution et Reproduction des Tests de Non-Régression (52/52 Tests)
Le projet intègre une suite stricte de **52 tests automatisés** répartis sur 4 couches (Unitaires avec mocks, Intégration locale sur jeux de données réels, Validation d'architecture et de performance, Smoke tests JSON-RPC & HTTP) :

- **Sur Windows (script global) :**
  ```cmd
  run_all_tests.bat
  ```

- **Sur Linux / macOS (script bash) :**
  ```bash
  chmod +x run_all_tests.sh
  ./run_all_tests.sh
  ```

- **Ou commande par commande (multiplateforme) :**
  ```bash
  node 01_web_assets_manager/tests/run_all_suites.mjs          # 12 tests
  python 02_pdf_technical_extractor/tests/run_all_suites.py    # 10 tests
  python 03_media_quality_auditor/tests/run_all_suites.py      # 10 tests
  python 04_ecommerce_catalog_scanner/tests/run_all_suites.py  # 11 tests
  python 05_visual_catalog_sync/tests/run_all_suites.py        # 9 tests
  ```
*Temps d'exécution global mesuré : ~3,8 secondes. Tous les 52 tests sont exécutables et validés avec succès (0 échec constaté).*

### 🔄 Réinitialisation de l'Environnement (`reset_env.bat`)
Pour supprimer `.venv`, purger les caches temporaires `__pycache__` et réinstaller à neuf :
```cmd
reset_env.bat
```
*(Le script demande une confirmation explicite `[O/N]` avant toute action).*

---

## 📖 7. Documentation d'Utilisation des 5 MCP

Les outils peuvent être utilisés selon deux approches distinctes :
- **Mode MCP (JSON-RPC) :** Connexion directe via stdio (Cursor, Antigravity, Claude Desktop) ou via la passerelle HTTP.
- **Mode Agent Coding (Local) :** Lecture du plan GPS `context_llm.json`, exécution en ligne de commande (CLI) et persistance mémoire dans `ContextHistoryManager`.

### 1️⃣ Outil #01 : Web Assets Manager
- **Rôle :** Scan de maquettes HTML et rapatriement d'images distantes.
- **Lancement MCP Stdio :** `node 01_web_assets_manager/canal_mcp/mcp_classic_stdio/mcp_server.mjs`
- **Outils MCP :** `scan_maquette_html`, `download_web_assets`, `replace_react_image_urls`, `01_run_quality_and_tests_suite`.
- **Exemple d'appel :**
  ```json
  { "name": "scan_maquette_html", "arguments": { "maquette_path": "01_web_assets_manager/data/sample_maquettes/maquette_1/code.html" } }
  ```
- **Résultat attendu :** `{ "found_assets": [...], "count": 71, "status": "scanned" }`
- **Résolution d'erreur :** Si `node` n'est pas trouvé, vérifiez son installation via `node -v` (version 18+ requise).

### 2️⃣ Outil #02 : PDF Technical Extractor
- **Rôle :** Découpage de catalogues PDF industriels et extraction de schémas techniques.
- **Lancement MCP Stdio :** `python 02_pdf_technical_extractor/canal_mcp/mcp_classic_stdio/mcp_server.py`
- **Outils MCP :** `extract_pdf_pages`, `extract_pdf_images`, `get_pdf_manifest`, `02_run_quality_and_tests_suite`.
- **Exemple d'appel :**
  ```json
  { "name": "extract_pdf_pages", "arguments": { "pdf_path": "catalog.pdf", "render_dpi": 150 } }
  ```
- **Résultat attendu :** `{ "extracted_pages": 12, "manifest_path": "output/manifest.json", "status": "success" }`
- **Résolution d'erreur :** Si un PDF est protégé par mot de passe, l'outil lève une exception documentée dans le statut de réponse.

### 3️⃣ Outil #03 : Media Quality Auditor
- **Rôle :** Contrôle de résolution minimale ($\ge 1200\times 700$) et détection de doublons stricts par empreinte MD5.
- **Lancement MCP Stdio :** `python 03_media_quality_auditor/canal_mcp/mcp_classic_stdio/mcp_server.py`
- **Outils MCP :** `audit_media_directory`, `clean_duplicate_media`, `get_certified_hero_candidates`, `03_run_quality_and_tests_suite`.
- **Exemple d'appel :**
  ```json
  { "name": "audit_media_directory", "arguments": { "directory_path": "public/assets", "min_width": 1200, "min_height": 700 } }
  ```
- **Résultat attendu :** `{ "total_audited": 45, "valid_hd": 42, "duplicates_found": 0 }`
- **Résolution d'erreur :** Si des fichiers non-images sont présents, ils sont ignorés avec avertissement sans interrompre l'audit.

### 4️⃣ Outil #04 : E-commerce Catalog Scanner
- **Rôle :** Extraction de fiches produits, prix et références avec rapport visuel HTML interactif.
- **Lancement MCP Stdio :** `python 04_ecommerce_catalog_scanner/canal_mcp/mcp_classic_stdio/mcp_server.py`
- **Capacité Unique :** `run_agent_lifecycle` (avec use cases : `scan_ecommerce_catalog`, `discover_category_tree`, `audit_scanned_catalog`, `run_quality_and_tests_suite`).
- **Exemple d'appel (Test Réel BatiHome) :**
  ```json
  { "name": "run_agent_lifecycle", "arguments": { "use_case": "scan_ecommerce_catalog", "source_url": "https://batihome.snorbik.fr/#P01_home" } }
  ```
- **Résultat attendu (Digest-First) :** Résumé compact extrayant **14 solutions et configurations d'implantation** (Terrasse, Escalier, Balcon, Mezzanine, Garde-corps sur profil...). Le rapport visuel interactif complet est automatiquement généré sur votre machine et consultable dans un navigateur à l'emplacement local :
  `04_ecommerce_catalog_scanner/output/scan_batihome_snorbik_fr_catalogue_view.html`.
- **Précision Playwright :** Playwright Chromium n'est utilisé en secours que si l'URL ciblée utilise un routage par fragment `#` (comme les SPAs React) ou un squelette DOM client vide. Les sites statiques/SSR sont analysés instantanément via `urllib` et `BeautifulSoup4`.

### 5️⃣ Outil #05 : Visual Catalog Sync
- **Rôle :** Synchronisation sécurisée des visuels avec gestion de la limite des chemins longs Windows (`MAX_PATH < 260`) et compilation TypeScript.
- **Lancement MCP Stdio :** `python 05_visual_catalog_sync/canal_mcp/mcp_classic_stdio/mcp_server.py`
- **Outils MCP :** `sync_visual_assets`, `compile_frontend_catalog`, `audit_catalog_sync_status`, `05_run_quality_and_tests_suite`.
- **Exemple d'appel :**
  ```json
  { "name": "compile_frontend_catalog", "arguments": { "catalog_json_path": "data/catalogue_reference.json", "output_ts_path": "output/RawGlassRailingCatalog.ts" } }
  ```
- **Résultat attendu :** `{ "compiled_products": 133, "status": "compiled" }`
- **Résolution d'erreur :** Les noms de fichiers contenant des caractères non autorisés sous Windows (`:`, `*`, `?`, `"`, `<`, `>`, `|`) sont automatiquement normalisés.

---

## 🌐 8. Passerelle Universelle HTTP / REST (Port 5185)

Pour les agents ou clients IA ne gérant pas les processus stdio locaux :
```bash
python mcp_shared/mcp_http_gateway.py --port 5185
```
- **Endpoint de Santé :** `GET http://localhost:5185/health` (renvoie `total_tools: 17`).
- **Découverte des Outils :** `GET http://localhost:5185/tools` (liste complète des 17 outils avec résolution des collisions).
- **Exécution d'Outil :** `POST http://localhost:5185/tools/call` avec `{"name": "...", "arguments": {...}}`.

---

## ⚠️ 9. Limites Connues et Bonnes Pratiques

1. **Rendu dynamique de SPAs complexes :** Le scanner #04 utilise Chromium standard pour les SPAs. Si un site tiers requiert une authentification complexe ou bloque les connexions automatisées, privilégiez le scan d'une exportation HTML locale ou de votre propre plateforme.
2. **Chemins de fichiers Windows :** L'outil #05 tronque préventivement les noms d'images à 42 caractères pour garantir que le chemin absolu total reste toujours inférieur à 260 caractères sous Windows.
3. **Isolement de l'environnement :** Il est fortement conseillé de toujours utiliser l'environnement virtuel `.venv` configuré par `install.bat`.

---

## 🔗 10. Liens vers les Documents Publics Utiles

* 📦 [**Guide d'Installation Détaillé (`INSTALL.md`)**](./INSTALL.md) : Détail des procédures manuelles et dépannage avancé.
* 🤖 [**Prompt d'Installation pour Agent IA (`PROMPT_INSTALLATION_AGENT.md`)**](./PROMPT_INSTALLATION_AGENT.md) : Procédure autonome à copier-coller dans votre agent.
* 📋 [**Configuration MCP Standard (`mcp_config.json`)**](./mcp_config.json) : Fichier de déclaration prêt à importer dans votre IDE.
* 📖 [**Guide d'Intégration MCP & Agents (`docs/GUIDE_INTEGRATION_MCP_ET_AGENTS.md`)**](./docs/GUIDE_INTEGRATION_MCP_ET_AGENTS.md) : Architecture de communication.
* 🏛️ [**Démonstrations d'Architecture (`docs/DEMONSTRATIONS_ARCHITECTURE_MCP_HYBRIDE.md`)**](./docs/DEMONSTRATIONS_ARCHITECTURE_MCP_HYBRIDE.md) : Scénarios réels de bout en bout.
* ⚖️ [**Licence Libre (`LICENSE`)**](./LICENSE) : Licence MIT.
