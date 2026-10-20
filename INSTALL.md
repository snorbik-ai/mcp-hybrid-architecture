# 📦 Guide d'Installation et d'Utilisation — Suite `mcp-hybrid-architecture`

Ce guide permet à tout développeur, agent IA ou utilisateur d'installer, diagnostiquer et exécuter la suite des 5 serveurs MCP autonomes sur un environnement propre.

---

## 📋 1. Prérequis Système

| Logiciel | Version requise | Rôle | Obligatoire ? |
| :--- | :---: | :--- | :---: |
| **Python** | `3.10` à `3.12+` (64-bit) | Moteurs des MCP 02, 03, 04, 05 et passerelle HTTP | **Oui** (sauf si MCP 01 seul) |
| **Node.js** | `18.0+` (LTS recommandé) | Moteur du MCP 01 (`01_web_assets_manager`) | Uniquement pour l'outil 01 |
| **Windows** / **Linux** / **macOS** | Tout OS récent | Multiplateforme | **Oui** |

---

## 🚀 2. Parcours d'Installation Rapide

### Option A — Installation Automatisée sur Windows (Recommandé)

1. **Lancer l'installateur :**
   Double-cliquez sur `install.bat` ou lancez dans votre terminal :
   ```cmd
   install.bat
   ```
   *Ce script vérifie la présence de Python, crée automatiquement l'environnement virtuel `.venv`, met à niveau pip, installe les dépendances et effectue un contrôle de santé final.*

2. **Si Python n'est pas encore installé sur votre machine :**
   - Le script `install.bat` le détectera immédiatement et vous proposera d'ouvrir la page officielle : [python.org/downloads](https://www.python.org/downloads/).
   - Lors de l'installation de Python sous Windows, cochez impérativement la case :  
     `☑ Add python.exe to PATH`.
   - Relancez ensuite simplement `install.bat`.

---

### Option B — Installation Manuelle (Linux / macOS / Développeurs)

1. **Créer et activer l'environnement virtuel :**
   ```bash
   # Sur Linux / macOS :
   python3 -m venv .venv
   source .venv/bin/activate

   # Sur Windows :
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. **Installer l'ensemble des dépendances :**
   ```bash
   pip install -r requirements-all.txt
   ```
   *(L'outil #01 repose sur les API natives de Node.js et ne requiert aucun `npm install` externe).*

---

## 🧩 3. Installation Modulaire par Outil (Indépendance des MCP)

Vous pouvez installer ou utiliser chaque MCP de façon totalement isolée :

```cmd
# Installer uniquement l'outil 01 (Web Assets - Node.js)
install.bat 01

# Installer uniquement l'outil 02 (PDF Technical Extractor - PyMuPDF)
install.bat 02
# Ou manuellement : pip install -r 02_pdf_technical_extractor/requirements.txt

# Installer uniquement l'outil 03 (Media Quality Auditor - Pillow)
install.bat 03
# Ou manuellement : pip install -r 03_media_quality_auditor/requirements.txt

# Installer uniquement l'outil 04 (E-commerce Catalog Scanner - BeautifulSoup4)
install.bat 04
# Ou manuellement : pip install -r 04_ecommerce_catalog_scanner/requirements.txt

# Installer uniquement l'outil 05 (Visual Catalog Sync - Python Standard)
install.bat 05
# Ou manuellement : 0 dépendance externe requise
```

---

## 🩺 4. Diagnostic de Santé (`doctor.bat`)

Pour vérifier à tout moment l'état de votre machine, vos versions, vos dépendances et la disponibilité des ports :
```cmd
doctor.bat
# Ou sur Linux/macOS :
python mcp_shared/mcp_doctor.py
```
Le diagnostic vérifie :
- La version de Python (>= 3.10) et l'architecture (64-bit).
- La présence de Node.js (v18+ pour l'outil 01).
- La validité de l'environnement virtuel `.venv`.
- L'intégrité des 5 serveurs déclarés dans `mcp_config.json`.
- La disponibilité du port réseau `5185` pour la passerelle HTTP.

---

## 🔄 5. Réinitialisation Complète (`reset_env.bat`)

Si vous souhaitez nettoyer votre environnement virtuel et repartir de zéro :
```cmd
reset_env.bat
```
*Le script demande une confirmation explicite avant d'effacer `.venv`, purge les caches Python temporaires (`__pycache__`) et reconstruit l'environnement proprement.*

---

## 🧪 6. Validation de l'Installation (Tests)

Exécutez la batterie complète des 52 tests non-régression :
```cmd
# Sur Windows :
run_all_tests.bat

# Ou individuellement par outil :
node 01_web_assets_manager/tests/run_all_suites.mjs
python 02_pdf_technical_extractor/tests/run_all_suites.py
python 03_media_quality_auditor/tests/run_all_suites.py
python 04_ecommerce_catalog_scanner/tests/run_all_suites.py
python 05_visual_catalog_sync/tests/run_all_suites.py
```
**Résultat garanti :** Les 5 suites s'exécutent avec succès en ~4 secondes (`52/52 PASS`).

---

## 🌐 7. Connexion aux Agents et IDEs (MCP)

### Mode A : Connexion Directe STDIO (Antigravity IDE, Cursor, Claude Desktop)
Renseignez `mcp_config.json` dans votre configuration IDE :
```json
{
  "mcpServers": {
    "01-web-assets": { "command": "node", "args": ["01_web_assets_manager/canal_mcp/mcp_classic_stdio/mcp_server.mjs"] },
    "02-pdf-extractor": { "command": "python", "args": ["02_pdf_technical_extractor/canal_mcp/mcp_classic_stdio/mcp_server.py"] },
    "03-quality-auditor": { "command": "python", "args": ["03_media_quality_auditor/canal_mcp/mcp_classic_stdio/mcp_server.py"] },
    "04-catalog-scanner": { "command": "python", "args": ["04_ecommerce_catalog_scanner/canal_mcp/mcp_classic_stdio/mcp_server.py"] },
    "05-visual-sync": { "command": "python", "args": ["05_visual_catalog_sync/canal_mcp/mcp_classic_stdio/mcp_server.py"] }
  }
}
```

### Mode B : Passerelle Universelle HTTP / REST (Port 5185)
```bash
python mcp_shared/mcp_http_gateway.py --port 5185
```
- **Santé :** `GET http://localhost:5185/health` (17 outils prêts).
- **Catalogue des outils :** `GET http://localhost:5185/tools`.
- **Appel d'outil :** `POST http://localhost:5185/tools/call` avec `{"name": "...", "arguments": {...}}`.

---

## 💡 8. Évaluation Package Autonome (Non-Techniques)

Pour les utilisateurs ne disposant pas de droits d'installation Python :
- Une distribution sous forme d'exécutable autonome Windows (`.exe` via PyInstaller / Nuitka) est techniquement réalisable pour les outils 02 à 05.
- Cependant, pour des raisons de transparence, de sécurité open-source et d'auditabilité immédiate du code source, la suite est distribuée sous forme de scripts Python/Node.js audités avec installateur guidé `install.bat`.
