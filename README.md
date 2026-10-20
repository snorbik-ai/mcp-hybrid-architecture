# 🛠️ Suite des 5 Outils Métiers BatiHome / AXESTEEL
## Architecture Hybride pour Agents IA : Un Dépôt Unique, Deux Modes d'Utilisation

> **Philosophie "Voiture Autonome" :**  
> Chaque dossier numéroté (`01_` à `05_`) est une **mini-application 100 % indépendante**. Elle possède ses propres réglages, son propre serveur d'assistance IA (MCP), sa propre interface Web visuelle et ses propres tests de non-régression.

---

## ⚡ Démarrage Rapide en 1 Minute

### 1. Choisissez votre Mode d'Utilisation

```text
               ┌────────────────────────────────────────────────────────┐
               │           DÉPÔT UNIQUE : outils_internes/              │
               │  5 serveurs • documentation • configuration • tests   │
               └───────────────────────────┬────────────────────────────┘
                                           │
                 ┌─────────────────────────┴─────────────────────────┐
                 ▼                                                   ▼
┌───────────────────────────────────┐       ┌───────────────────────────────────┐
│        VARIANTE A — MCP           │       │    VARIANTE B — AGENT CODING      │
│  • Pour Cursor, Claude Desktop,   │       │  • Pour agents autonomes (Devin,  │
│    Antigravity IDE & APIs LLM     │       │    Cline, Windsurf, Claude Code)  │
│  • 17 outils découverts           │       │  • Lecture GPS context_llm.json   │
│  • 5 serveurs stdio légers        │       │  • Exécution locale CLI / SDK     │
│  • Outil #04 avec Gateway         │       │  • Mémoire glissante 30 tours     │
│    Lifecycle & Digest automatique │       │  • 98,8 % d'économie de tokens    │
└───────────────────────────────────┘       └───────────────────────────────────┘
```

### 2. Installation en 2 Commandes
```bash
pip install -r requirements-all.txt
playwright install chromium
```

### 3. Contrôle Qualité Immédiat
```bash
# Windows :
run_all_tests.bat
# Ou multi-plateforme via npm :
npm run test:all
```
*Résultat attendu : **52/52 tests exécutés avec succès (PASS)** sur les 4 couches (Unitaires, Intégration, Validation/Perf, Smoke).*

---

## 🧭 Les 5 Voitures Autonomes

| Répertoire | Rôle Industriel | Mode MCP (Porte A) | Agent Coding (Porte B) | Contrôle Qualité |
| :--- | :--- | :---: | :---: | :---: |
| [`01_web_assets_manager/`](./01_web_assets_manager/) | **Moissonneur d'Assets Web & Relieur React** : Récupère les photos depuis des maquettes HTML et met à jour les liens d'images du site. | 4 outils stdio | GPS + CLI | **12/12 PASS** |
| [`02_pdf_technical_extractor/`](./02_pdf_technical_extractor/) | **Extracteur Catalogues PDF & Découpeur CAO** : Découpe les catalogues PDF fabricants et en extrait fiches, plans techniques et photos HD. | 4 outils stdio | GPS + CLI + Mémoire | **10/10 PASS** |
| [`03_media_quality_auditor/`](./03_media_quality_auditor/) | **Auditeur Qualité Média & Dédoublonneur MD5** : Analyse la résolution réelle ($\ge 1200\times 700$) et purge les doublons par empreinte MD5. | 4 outils stdio | GPS + CLI | **10/10 PASS** |
| [`04_ecommerce_catalog_scanner/`](./04_ecommerce_catalog_scanner/) | **Scanneur DOM Universel & Moissonneur Tarifaire** : Extrait fiches, prix TTC/HT et SKUs sur architectures web modernes (PrestaShop SSR, React SPA BatiHome, catalogues locaux). | **Gateway Lifecycle Unique** | GPS + CLI + Mémoire 30 tours | **11/11 PASS** |
| [`05_visual_catalog_sync/`](./05_visual_catalog_sync/) | **Moissonneur Visuel Safe-Path & Compilateur TS** : Synchronise `public/assets` avec garantie `MAX_PATH < 260` et compile le catalogue TypeScript. | 4 outils stdio | GPS + CLI | **9/9 PASS** |

---

## 📚 Documentation & Prise en Main

* 📖 [**Guide d'Installation Complet (`INSTALL.md`)**](./INSTALL.md) : Procédure pas à pas, double configuration `mcp_config.json` (racine vs local), passerelle HTTP (port 5185) et dépannage.
* 🤖 [**Prompt d'Installation pour Agent IA (`PROMPT_INSTALLATION_AGENT.md`)**](./PROMPT_INSTALLATION_AGENT.md) : Le prompt prêt à l'emploi à copier-coller dans votre assistant (Cursor, Claude Code, Windsurf) pour une installation 100 % autonome.
* 📊 [**Banc d'Essai Comparatif A/B (`docs/BENCHMARK_COMPARATIF_AB_MCP_VS_AGENT_CODING.md`)**](./docs/BENCHMARK_COMPARATIF_AB_MCP_VS_AGENT_CODING.md) : Mesure scientifique de la réduction d'empreinte contextuelle (98,8 % d'économie de tokens mesurée sur catalogue réel).
