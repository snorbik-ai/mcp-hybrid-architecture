# 🤖 Guide d'Intégration du Canal MCP : Les 2 Modes de Consommation

Ce guide explique en détail comment consommer les outils internes BatiHome via le **Model Context Protocol (MCP)** selon les deux grands cas d'usage de l'Intelligence Artificielle.

---

## 🎯 Vue d'Ensemble des 2 Modes

```
                               ┌──────────────────────────────────────────────┐
                               │             MOTEUR CORE / SDK                │
                               │  (PdfProcessorSDK / WebAssetsSDK BatiHome)   │
                               └──────────────────────┬───────────────────────┘
                                                      │
                         ┌────────────────────────────┴────────────────────────────┐
                         ▼                                                         ▼
            ┌──────────────────────────┐                              ┌──────────────────────────┐
            │         MODE 1           │                              │         MODE 2           │
            │   UTILISATION DIRECTE    │                              │  AGENT IA AVEC PASSERELLE│
            │      DANS UN IDE         │                              │       INTERMÉDIAIRE      │
            ├──────────────────────────┤                              ├──────────────────────────┤
            │ • Antigravity IDE        │                              │ • Agent Python externe   │
            │ • Cursor                 │                              │ • API Gemini / OpenAI    │
            │ • Claude Desktop         │                              │ • Bot Slack / Webhooks   │
            ├──────────────────────────┤                              ├──────────────────────────┤
            │ Liaison : STDIO direct   │                              │ Liaison : HTTP / REST    │
            │ Aucun intermédiaire      │                              │ via `mcp_http_gateway`   │
            │ requis.                  │                              │ sur port 5185.           │
            └──────────────────────────┘                              └──────────────────────────┘
```

---

## 💻 MODE 1 : Utilisation Directe dans un IDE (Antigravity, Cursor, Claude)

### 1. Comment ça fonctionne ?
Dans ce mode, l'IDE agit lui-même comme **Client MCP natif**. Il lance le processus du serveur MCP en arrière-plan et communique avec lui via les flux standards d'entrée/sortie (`stdin` / `stdout`).
* **Zéro intermédiaire réseau** : Pas besoin de serveur HTTP ou de port réseau.
* **Découverte automatique** : Dès que l'IDE s'ouvre, l'Agent IA interne de l'IDE inspecte les outils disponibles et peut les invoquer de façon transparente.

---

### 2. Configuration pour Antigravity IDE

Le fichier [`outils_internes/mcp_config.json`](../mcp_config.json) déclare l'ensemble des 5 serveurs :

```json
{
  "mcpServers": {
    "01-recuperateur-images-web": {
      "command": "node",
      "args": ["01_web_assets_manager/canal_mcp/mcp_classic_stdio/mcp_server.mjs"],
      "description": "Outil #01 : Récupère les photos d'une maquette web et met à jour les liens d'images React."
    },
    "02-decoupeur-catalogue-pdf": {
      "command": "python",
      "args": ["02_pdf_technical_extractor/canal_mcp/mcp_classic_stdio/mcp_server.py"],
      "description": "Outil #02 : Ingestion, découpage et classification de catalogues PDF techniques."
    },
    "03-controleur-qualite-photos": {
      "command": "python",
      "args": ["03_media_quality_auditor/canal_mcp/mcp_classic_stdio/mcp_server.py"],
      "description": "Outil #03 : Contrôle de résolution HD (>=1200x700) et dédoublonnage cryptographique MD5."
    },
    "04-scanneur-produits-boutique": {
      "command": "python",
      "args": ["04_ecommerce_catalog_scanner/canal_mcp/mcp_classic_stdio/mcp_server.py"],
      "description": "Outil #04 : Scanneur DOM e-commerce et digest de cycle de vie."
    },
    "05-synchroniseur-catalogue-visuels": {
      "command": "python",
      "args": ["05_visual_catalog_sync/canal_mcp/mcp_classic_stdio/mcp_server.py"],
      "description": "Outil #05 : Téléchargement sécurisé MAX_PATH et compilation TypeScript."
    }
  }
}
```

#### Dans Antigravity IDE :
L'agent IA d'Antigravity détecte automatiquement la configuration dans `mcp_config.json` et accède directement à l'ensemble des outils via stdio.

---

### 3. Configuration pour Claude Desktop & Cursor

#### Pour Claude Desktop (`claude_desktop_config.json`) :
Emplacement : `%APPDATA%\Claude\claude_desktop_config.json` (Windows) ou `~/.config/Claude/claude_desktop_config.json` (macOS/Linux) :
```json
{
  "mcpServers": {
    "batihome-pdf": {
      "command": "python",
      "args": [
        "${workspaceFolder}/02_pdf_technical_extractor/canal_mcp/mcp_classic_stdio/mcp_server.py"
      ]
    },
    "batihome-web": {
      "command": "node",
      "args": [
        "${workspaceFolder}/01_web_assets_manager/canal_mcp/mcp_classic_stdio/mcp_server.mjs"
      ]
    }
  }
}
```
> **Astuce de portabilité :** Remplacez `${workspaceFolder}` par le chemin absolu de votre répertoire local `outils_internes` (ex: `C:\\chemin\\vers\\outils_internes`).

---

## 🌐 MODE 2 : Utilisation avec un Agent IA Externe (Via Passerelle Intermédiaire)

### 1. Pourquoi avons-nous besoin d'un intermédiaire ?
Quand vous construisez un agent IA externe qui **ne s'exécute pas dans Antigravity IDE** :
* Par exemple un script Python autonome qui appelle l'API Gemini ou OpenAI.
* Un serveur backend FastAPI ou Node.js qui reçoit des requêtes web.
* Un bot Telegram / Discord ou une tâche planifiée dans le Cloud.

Ces programmes s'exécutent en réseau et ne peuvent pas facilement lancer et piloter des processus terminaux `stdio` sur votre machine locale.

**Solution : La Passerelle Intermédiaire Universelle (`mcp_http_gateway.py`)**.

---

### 2. La Passerelle Intermédiaire : `mcp_http_gateway.py`

Ce service transforme les moteurs MCP locaux en une API HTTP REST standard :

#### Lancement de la passerelle :
```bash
cd outils_internes
npm run mcp:gateway
# Ou : python mcp_shared/mcp_http_gateway.py --port 5185
```

#### Endpoints exposés :
* `GET http://localhost:5185/health` : Statut du service.
* `GET http://localhost:5185/tools` : Liste des outils MCP et leurs schémas JSON (format compatible Function Calling OpenAI & Gemini).
* `POST http://localhost:5185/tools/call` : Exécution d'un outil par l'Agent IA.

---

### 3. Exemple d'Appel HTTP par une IA Externe

#### A. Découverte des outils (`GET /tools`) :
```bash
curl http://localhost:5185/tools
```
Réponse reçue par l'IA :
```json
{
  "tools": [
    {
      "name": "process_pdf_document",
      "description": "Traite un catalogue ou devis PDF : découpe par page, rendu HD 150 DPI, extraction d'images brutes et classification.",
      "parameters": {
        "type": "object",
        "properties": {
          "pdf_path": { "type": "string" },
          "output_dir": { "type": "string" },
          "dpi": { "type": "integer" }
        },
        "required": ["pdf_path"]
      }
    }
  ]
}
```

#### B. Exécution d'un outil par l'IA (`POST /tools/call`) :
```bash
curl -X POST http://localhost:5185/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "get_pdf_document_text", "arguments": {"document_dir": "output/garde_corps_vi_tree"}}'
```
Réponse reçue par l'IA :
```json
{
  "status": "success",
  "tool": "get_pdf_document_text",
  "result": {
    "full_text": "# GARDE CORPS VI_TREE\n\n## Page 1\n..."
  }
}
```

---

### 4. Le Runner d'Agent IA Inclus : `mcp_agent_runner.py`

Pour tester immédiatement le Mode 2, un runner d'agent autonome est fourni dans `mcp_shared/` :

```bash
cd outils_internes
python mcp_shared/mcp_agent_runner.py --demo
```

Ce script simule le cycle complet d'un agent IA :
1. Connexion à la passerelle.
2. Découverte dynamique des outils et de leurs signatures.
3. Décision du LLM sur l'outil à exécuter.
4. Transmission du Tool Call à la passerelle et récupération du résultat structuré.

---

## 📊 Synthèse Comparative

| Critère | Mode 1 : IDE Direct | Mode 2 : Passerelle Intermédiaire |
| :--- | :--- | :--- |
| **Consommateur** | Antigravity IDE, Cursor, Claude Desktop | Agents Python/JS, API LLM, Scripts externes |
| **Protocole** | `stdio` (flux terminal direct) | `HTTP / REST` (requêtes JSON standard) |
| **Configuration** | Déclaration dans `mcp_config.json` | Démarrage de `mcp_http_gateway.py` |
| **Port réseau requis** | Aucun (local pur) | Port 5185 |
| **Interopérabilité** | Réservé aux applications compatibles MCP | Universel (tout langage sachant faire un `fetch` ou `curl`) |
