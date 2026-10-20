# 🤖 Point d'Entrée Agent IA — MCP Agent Coding (`visual_catalog_sync_pipeline`)

> **Instruction Prioritaire pour l'Agent IA (LLM Coding Agent) :**  
> Avant d'exécuter toute action avec cet outil, **lisez obligatoirement le fichier manifeste GPS** :  
> 👉 [`context_llm.json`](./context_llm.json)

---

## 🔄 Cycle de Vie Obligatoire d'un Tour d'Agent Coding

1. **Étape 1 — Lecture du GPS (`context_llm.json`)** :
   - Prenez connaissance de `system_identity`, `gps_tools_registry`, `static_history` et `dynamic_history` (30 derniers tours).
2. **Étape 2 — Exécution des Services Métiers (Use Cases)** :
   - Lancez `SyncVisualAssetsUseCase` (`--sync`) ou `CompileFrontendCatalogUseCase` (`--compile`) via `../../canal_sdk_cli/cli.py`.
3. **Étape 3 — Compression Sémantique & Compte Rendu de Tour** :
   - Synthétisez le nombre d'images synchronisées, la longueur maximale de chemin Windows et l'état de compilation TypeScript.
4. **Étape 4 — Mise à Jour de l'Historique Mémoire (Fenêtre glissante de 30 tours)** :
   ```bash
   python ../../../mcp_shared/context_history_manager.py --context-file context_llm.json --record-demo
   ```
