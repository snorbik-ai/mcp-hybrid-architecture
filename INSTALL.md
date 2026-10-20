# 📦 Guide d'Installation Rapide — Suite des 5 Outils Internes BatiHome / AXESTEEL

Ce guide permet à un utilisateur ou auditeur externe d'installer, configurer et vérifier les 5 outils internes en moins de 3 minutes sur un environnement propre.

---

## 📋 1. Prérequis Système

| Logiciel | Version minimale requise | Rôle |
| :--- | :---: | :--- |
| **Python** | `3.10+` | Moteurs des outils 02, 03, 04, 05 et passerelle HTTP |
| **Node.js** | `18.0+` (LTS recommandé) | Moteur de l'outil 01 (`01_web_assets_manager`) |
| **npm** | `9.0+` | Lanceur de scripts |

---

## 🚀 2. Installation en 3 Étapes

### Étape 1 : Se positionner dans le répertoire
```bash
cd outils_internes
```

### Étape 2 : Créer et activer l'environnement virtuel Python
- **Sur Windows (PowerShell / CMD) :**
  ```powershell
  python -m venv .venv
  .venv\Scripts\activate
  ```
- **Sur Linux / macOS :**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### Étape 3 : Installer les dépendances Python
```bash
pip install -r requirements-all.txt
```
> *Note : L'outil #01 utilise les API Node.js natives et ne nécessite aucun `npm install` (`node_modules` externe = zéro).*

---

## 🧪 3. Validation de l'Installation

Exécutez la batterie complète de non-régression (4 couches de tests) :
```bash
# Sur Windows :
run_all_tests.bat
# Ou via npm :
npm run test:all
```
**Résultat attendu :** Les 5 suites s'exécutent avec succès en ~4 secondes.

---

## 🤖 4. Utilisation du Canal MCP (Model Context Protocol)

### Mode 1 : Connexion Directe STDIO (IDE Antigravity, Cursor, Claude Desktop)
Une configuration déclarative double est fournie pour éliminer toute erreur de répertoire de travail :
* **Depuis la racine du dépôt :** [`./mcp_config.json`](../mcp_config.json) préfixe automatiquement les chemins avec `outils_internes/`.
* **Depuis le dossier `outils_internes/` :** [`./mcp_config.json`](./mcp_config.json) utilise les chemins relatifs directs.
* Les 5 serveurs répondent au protocole MCP standard (`initialize`, `tools/list`, `tools/call`).
* Lancement individuel d'un serveur MCP en console :
  ```bash
  npm run 01:mcp
  npm run 02:mcp
  npm run 03:mcp
  npm run 04:mcp
  npm run 05:mcp
  ```

### Mode 2 : Passerelle Universelle HTTP / REST (Agents Externes, Gemini, OpenAI, Claude API)
Pour consommer les outils sans connexion stdio directe :
```bash
npm run mcp:gateway
# Ou : python mcp_shared/mcp_http_gateway.py --port 5185
```
* **Endpoint de santé :** `GET http://localhost:5185/health` (affiche `total_tools: 17`).
* **Découverte des outils :** `GET http://localhost:5185/tools` (liste les 17 outils avec résolution de collision : les suites de tests sont scopées `01_run_quality_and_tests_suite`, `02_...`, `03_...`, `05_...`).
* **Appel d'outil :** `POST http://localhost:5185/tools/call` avec `{"name": "...", "arguments": {...}}`.
* **Démonstration de l'agent :** `python mcp_shared/mcp_agent_runner.py --demo`.

---

## 🧠 5. Architecture Mémoire : Variante A vs Variante B

| Variante | Périmètre d'application | Fonctionnement |
| :--- | :--- | :--- |
| **Variante A (Porte A — MCP STDIO)** | Serveur `04_ecommerce_catalog_scanner` | Le serveur intercepte les appels via son outil passerelle unique `run_agent_lifecycle`, charge `context_llm.json`, lance le use case localement, compresse en digest, et consigne automatiquement le tour dans le carnet de bord (`turn_report.json` + `dynamic_history`). Les serveurs 01, 02, 03, 05 fonctionnent en MCP pur stateless ultra-rapide. |
| **Variante B (Porte B — Agent Coding Fichier)** | L'ensemble des 5 outils autonomes | L'agent lit le fichier GPS `context_llm.json` dans chaque outil, applique les règles Digest-First et consigne ses tours via `ContextHistoryManager` (mémoire glissante bornée à 30 tours). |
