# 🤖 Canal 1 (Variante 2) : MCP Agent Coding Autonome — `01_web_assets_manager`

Ce répertoire contient l'implémentation **100 % autonome** de la variante **MCP Agent Coding** pour l'outil `01_web_assets_manager`. Il n'a aucune dépendance vers un dossier parent externe.

## Cycle de Vie Agent Coding (5 Étapes)
1. **Lecture du GPS** : Lire [`context_llm.json`](./context_llm.json).
2. **Exécution des Tools / Use Cases** : Appeler le SDK, le CLI ou le runner de tests (`node ../../tests/run_all_suites.mjs`).
3. **Compression Sémantique** : Résumer l'action en un compte rendu concis.
4. **Archivage de Session** : Enregistrer `history/sessions/YYYY-MM-DD/turn_XX/turn_report.json`.
5. **Fenêtre Glissante (30 Tours)** : Exécuter le gestionnaire local embarqué :
   ```bash
   python context_history_manager.py --context-file context_llm.json --record-demo
   ```
