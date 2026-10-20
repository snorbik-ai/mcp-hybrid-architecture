# 🩺 Diagnostic, Dépannage et Procédures de Validation

Ce document regroupe les procédures de contrôle de santé, la matrice de résolution des pannes courantes et les commandes de reproduction des tests de la suite **`mcp-hybrid-architecture`**.

---

## 🩺 1. Contrôle de Santé Automatisé (`doctor.bat`)

Le projet intègre un outil de diagnostic en 6 points qui audite votre environnement d'exécution :

### Comment le lancer ?

* **Sous Windows :**
  ```cmd
  doctor.bat
  ```
* **Sous Linux / macOS :**
  ```bash
  python3 mcp_shared/mcp_doctor.py
  ```

### Les 6 points de contrôle audités :

1. **Moteur Python :** Vérifie que Python est en version $\ge 3.10$ et en architecture 64-bit.
2. **Moteur Node.js :** Vérifie si Node.js v18+ est présent (requis uniquement pour l'outil #01).
3. **Environnement Virtuel :** Confirme la présence et l'isolation du dossier local `.venv`.
4. **Dépendances Métiers :** Contrôle la présence de `PyMuPDF` (Outil 02), `Pillow` (Outil 03), `BeautifulSoup4` (Outil 04) et note que l'Outil 05 tourne avec 0 dépendance.
5. **Configuration MCP :** Valide la syntaxe JSON de `mcp_config.json` et la résolution des chemins.
6. **Disponibilité des Ports Réseau :** Vérifie si les ports des serveurs Web locaux (5180 à 5184) et de la passerelle unifiée (5185) sont libres.

---

## 🚨 2. Matrice de Résolution des Pannes Fréquentes

| Symptôme / Message d'Erreur | Cause Probable | Solution Recommandée |
| :--- | :--- | :--- |
| `'python' n'est pas reconnu en tant que commande interne` | Python n'a pas été ajouté à la variable d'environnement `PATH` lors de son installation sous Windows. | 1. Relancez l'installateur Python officiel.<br>2. Cochez impérativement la case **`☑ Add python.exe to PATH`** en bas de la première fenêtre.<br>3. Cliquez sur **Modify** ou réinstallez, puis rouvrez un nouveau terminal. |
| `Node.js non détecté dans le PATH` | Node.js n'est pas installé sur la machine hôte. | • Si vous n'utilisez que les outils #02, #03, #04 ou #05 : vous pouvez ignorer cet avertissement.<br>• Si vous utilisez l'outil #01 : téléchargez et installez Node.js LTS depuis [nodejs.org](https://nodejs.org/). |
| `No module named 'fitz'` ou `No module named 'PIL'` | Les dépendances n'ont pas été installées dans le `.venv` actif. | Exécutez l'installation automatique des dépendances :<br>`install.bat`<br>ou manuellement :<br>`pip install -r requirements-all.txt` |
| `Server disconnected` ou statut rouge dans Cursor / Claude Desktop | Le client MCP ne parvient pas à lancer le binaire Python avec un chemin relatif. | Dans la configuration MCP de votre client, remplacez les chemins relatifs par des **chemins absolus** complets :<br>`C:/Users/VotreNom/Dev/MCP/.venv/Scripts/python.exe`<br>et pour le script :<br>`C:/Users/VotreNom/Dev/MCP/04_ecommerce_catalog_scanner/canal_mcp/mcp_classic_stdio/mcp_server.py`. |
| `OSError: [WinError 206] Le nom de fichier ou l'extension est trop long` | Windows impose historiquement une limite de 260 caractères (`MAX_PATH`) sur les chemins absolus. | L'outil #05 (`05_visual_catalog_sync`) intègre nativement un coupe-circuit avec hachage court qui tronque les noms de fichiers à 42 caractères pour rester sous 140 caractères au total. Utilisez l'outil #05 pour rapatrier vos médias en toute sécurité. |
| `Address already in use` (Port 5181, 5182, 5183, 5184 ou 5185) | Une précédente instance du dashboard Web ou de la passerelle HTTP est restée active en arrière-plan. | **Sous Windows :**<br>`netstat -ano \| findstr :5185`<br>`taskkill /PID <PID_TROUVE> /F`<br>**Sous Linux / macOS :**<br>`lsof -ti :5185 \| xargs kill -9` |
| `Playwright Host / Browser Not Found` | L'optionnel moteur Playwright n'a pas ses binaires Chromium installés pour les SPAs. | Exécutez :<br>`playwright install chromium`<br>*Note : Pour les sites SSR classiques, BeautifulSoup4 suffit et n'a pas besoin de Playwright.* |

---

## 🔄 3. Procédure de Réinitialisation Complète (`reset_env.bat`)

Si votre environnement virtuel est altéré ou si vous souhaitez repartir d'un état propre :

1. Fermez vos terminaux et éditeurs utilisant le `.venv`.
2. Lancez le script de réinitialisation :
   ```cmd
   reset_env.bat
   ```
3. Ce script réalise les opérations suivantes de manière sécurisée :
   - Suppression intégrale du dossier local `.venv`.
   - Purge des caches temporaires Python (`__pycache__`, `.pytest_cache`).
   - Nettoyage des fichiers temporaires dans les dossiers `output/`.
   - Reconstruction automatique d'un `.venv` vierge et réinstallation des dépendances.

---

## 🗑️ 4. Procédure de Désinstallation Propre

La suite `mcp-hybrid-architecture` respecte rigoureusement la propreté de votre machine hôte :
* Aucune variable d'environnement globale n'est modifiée.
* Aucun service d'arrière-plan permanent n'est enregistré.
* Tous les fichiers générés restent cantonnés dans le dossier du dépôt.

### Pour désinstaller complètement la suite :
1. Supprimez la déclaration des serveurs dans la configuration de votre IDE (`mcp_config.json` ou `claude_desktop_config.json`).
2. Supprimez simplement le dossier racine du projet (`MCP`).  
   Votre système redevient instantanément dans son état initial sans résidu.

---

## 🧪 5. Matrice de Validation et Reproduction des Tests

Pour vérifier que la suite est 100 % opérationnelle sur votre machine :

### Exécution globale (les 5 outils en 1 commande) :
* **Sous Windows :**
  ```cmd
  run_all_tests.bat
  ```
* **Sous Linux / macOS :**
  ```bash
  chmod +x run_all_tests.sh
  ./run_all_tests.sh
  ```

### Exécution ciblée par outil :
* **Outil #01 (Node.js) :**  
  `node 01_web_assets_manager/tests/run_all_suites.mjs`
* **Outil #02 (PyMuPDF) :**  
  `python 02_pdf_technical_extractor/tests/run_all_suites.py`
* **Outil #03 (Pillow) :**  
  `python 03_media_quality_auditor/tests/run_all_suites.py`
* **Outil #04 (BeautifulSoup4) :**  
  `python 04_ecommerce_catalog_scanner/tests/run_all_suites.py`
* **Outil #05 (0 dépendance) :**  
  `python 05_visual_catalog_sync/tests/run_all_suites.py`

Chaque script valide les **4 couches de la Clean Architecture** :
1. **Couche 1 : Tests Unitaires** (Entités du Domain, calculs de TVA, immutabilité).
2. **Couche 2 : Tests d'Intégration** (Parsing de fichiers réels, écriture disque, lecture d'images).
3. **Couche 3 : Tests de Validation et Performance** (Temps de réponse en millisecondes, pureté du Domain).
4. **Couche 4 : Smoke Tests Protocolaires** (Échanges JSON-RPC 2.0 sur `stdio` et points d'accès HTTP).
