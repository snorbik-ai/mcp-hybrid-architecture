# 🤖 Prompt d'Installation Automatique pour Agent IA (Cursor, Claude Code, Windsurf, Devin)

> Ce fichier est destiné à être copié-collé directement dans le chat de votre agent de programmation autonome pour une installation et une vérification 100 % automatisées en un seul message.

---

```text
Tu es un agent de programmation chargé d'installer et de vérifier ce projet open source.

Dépôt Git : https://github.com/snorbik-ai/mcp-toolkit.git
Dossier cible : ./ (racine du dépôt)

Instructions d'installation et de prise en main :
1. Lis intégralement le README.md et suis les instructions de INSTALL.md situés à la racine du dépôt.
2. Vérifie l'environnement disponible, les prérequis système (Python 3.10+, Node.js 18+), les dépendances et la structure du dépôt avant toute modification.
3. Demande-moi quel mode je souhaite utiliser si je ne l'ai pas déjà précisé :
   - Mode A — MCP Standard (pour Cursor, Claude Desktop ou Antigravity IDE)
   - Mode B — Agent Coding Autonome (pour exécution locale par script, CLI et mémoire glissante 30 tours)
4. Installe uniquement les dépendances nécessaires au mode choisi selon les instructions officielles (pip install -r requirements-all.txt). Ne modifie pas arbitrairement les versions ni les fichiers de configuration.
5. Pour le Mode A, configure les serveurs MCP selon le client et le répertoire de lancement concernés (utilise mcp_config.json). Vérifie que les outils sont découverts et que les appels fonctionnent.
6. Pour le Mode B, suis le parcours Agent Coding documenté. Vérifie la lecture du manifeste context_llm.json, l'exécution d'une tâche locale et la persistance mémoire dans history/sessions/ via ContextHistoryManager.
7. Exécute la suite de tests officielle (run_all_tests.bat ou npm run test:all) et distingue clairement les tests réussis, échoués et non exécutés (52 tests attendus à 100% PASS).
8. N'invente aucun résultat. En cas d'erreur, identifie sa cause probable et propose une correction minimale avant de poursuivre.
9. Termine par un compte-rendu clair indiquant le mode installé, les commandes exécutées, les tests réussis et les éventuelles limites d'environnement.

RÈGLE DE SÉCURITÉ : Ne publie rien, ne pousse aucun commit et ne modifie aucun dépôt distant sans mon autorisation explicite.
```
