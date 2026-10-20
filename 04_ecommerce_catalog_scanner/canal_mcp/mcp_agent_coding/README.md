# 🤖 Point d'Entrée Agent IA — MCP Agent Coding (`ecommerce_catalog_scanner_pipeline`)

> **Instruction Prioritaire pour l'Agent IA (LLM Coding Agent) :**  
> Avant d'exécuter toute action avec cet outil, **vous devez obligatoirement lire le fichier manifeste GPS** situé dans ce même répertoire :  
> 👉 [`context_llm.json`](./context_llm.json)

---

## 🔄 Cycle de Vie Obligatoire d'un Tour d'Agent Coding

1. **Étape 1 — Lecture du GPS (`context_llm.json`)** :
   - Lisez `system_identity`, `gps_tools_registry`, `static_history` (exemples de réussite passés) et `dynamic_history` (les 30 derniers tours exécutés).
2. **Étape 2 — Exécution Métier** :
   - Déclenchez le Service Métier (Use Case) approprié via le SDK/CLI (`../../canal_sdk_cli/cli.py`) ou le serveur MCP (`../mcp_classic_stdio/mcp_server.py`).
3. **Étape 3 — Compression Sémantique & Compte Rendu de Tour** :
   - Produisez une synthèse nette, précise et sans bavardage de ce que vous avez accompli durant ce tour.
4. **Étape 4 — Mise à Jour de l'Historique Mémoire (Fenêtre glissante de 30 tours)** :
   - Exécutez `ContextHistoryManager` pour écrire `history/sessions/YYYY-MM-DD/turn_XX/turn_report.json` et rafraîchir automatiquement `context_llm.json` :
   ```bash
   python ../../../mcp_shared/context_history_manager.py --context-file context_llm.json --record-demo
   ```
