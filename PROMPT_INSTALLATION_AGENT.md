# 🤖 Procédure d'Installation et Vérification pour Agent IA (Cursor, Claude Code, Windsurf, Devin)

> **Instructions pour l'utilisateur :** Copiez-collez l'intégralité du bloc ci-dessous dans le chat de votre agent de programmation autonome pour qu'il prenne en charge l'installation, la vérification et la démonstration des outils de manière 100 % autonome.

---

```text
Tu es un agent de programmation autonome chargé d'installer, vérifier et configurer la suite d'outils open source "mcp-toolkit".

Emplacement de travail : ./ (racine du dépôt)
Documentation de référence : README.md et INSTALL.md

Suis scrupuleusement la procédure suivante en 6 étapes :

1. LECTURE DE LA DOCUMENTATION :
   - Lis attentivement README.md et INSTALL.md situés à la racine pour comprendre l'architecture des 5 outils, les commandes officielles et les modes disponibles.

2. CONTRÔLE DE L'ENVIRONNEMENT ET DES PRÉREQUIS :
   - Vérifie la présence de Python (>= 3.10, 64-bit recommandé) et de Node.js (>= 18.0 pour l'outil 01).
   - Exécute le script de diagnostic officiel :
     * Sur Windows : lance doctor.bat
     * Sur Linux / macOS : lance python mcp_shared/mcp_doctor.py
   - Analyse le diagnostic renvoyé et identifie les composants manquants éventuels.

3. INSTALLATION DES DÉPENDANCES NÉCESSAIRES :
   - N'installe QUE les dépendances nécessaires déclarées dans le projet.
   - Sur Windows : lance "install.bat" (ou "install.bat <cible>" pour un outil spécifique).
   - Sur Linux / macOS : crée un environnement virtuel .venv et exécute "pip install -r requirements-all.txt".
   - Ne modifie pas arbitrairement les fichiers de configuration (mcp_config.json, requirements.txt).

4. EXÉCUTION DE LA SUITE DE TESTS :
   - Lance la suite complète de non-régression via "run_all_tests.bat" (ou les scripts run_all_suites par outil).
   - Vérifie que les 52 tests sont exécutés et réussis (100% PASS attendu).
   - Distingue clairement dans ton compte-rendu : les tests exécutés avec succès, les éventuels échecs et les tests ignorés. N'invente aucun résultat.

5. DÉMONSTRATION D'UTILISATION :
   - Demande à l'utilisateur quel outil parmi les 5 il souhaite utiliser en priorité :
     * 01 : Récupérateur d'images web et relieur React
     * 02 : Découpeur technique de catalogues PDF
     * 03 : Auditeur qualité d'images HD et dédoublonneur MD5
     * 04 : Scanneur de catalogue e-commerce et extraction tarifaire
     * 05 : Synchroniseur de catalogue visuel et compilateur TypeScript
   - Explique la commande de lancement correspondante (mode MCP Stdio ou passerelle HTTP sur le port 5185).
   - Fournis un exemple d'appel avec les arguments attendus.

6. BILAN D'INSTALLATION :
   - Fournis un compte-rendu synthétique et transparent :
     * Versions Python et Node.js détectées
     * Statut de l'environnement virtuel (.venv)
     * Bilan chiffré des tests (ex: 52/52 PASS)
     * Éventuelles limites ou avertissements restants (ex: port 5185, installation de Node.js si absent).

RÈGLE DE SÉCURITÉ ABSOLUE :
Ne publie rien, ne pousse aucun commit et ne modifie aucun dépôt distant sans validation explicite de l'utilisateur.
```
