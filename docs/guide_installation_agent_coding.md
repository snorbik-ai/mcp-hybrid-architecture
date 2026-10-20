# 🤖 Guide d'Installation et d'Utilisation Assistées par Agent de Coding (Variante B)

Ce guide est destiné aux utilisateurs qui souhaitent installer, configurer et utiliser un ou plusieurs outils de la suite **`mcp-hybrid-architecture`** en déléguant l'intégralité des opérations techniques à leur assistant ou agent de coding IA (**Cursor Composer, Claude Code, Devin, Antigravity IDE, Windsurf**).

---

## 🎯 Comment Fonctionne la Variante B ?

1. Vous choisissez l'outil dont vous avez besoin dans la liste ci-dessous.
2. Vous copiez le **Prompt d'Installation de l'Outil** et vous le collez directement dans le chat de votre agent.
3. L'agent applique le protocole d'ingénierie sécurisé :
   - Détection de votre système d'exploitation (Windows, Linux, macOS).
   - Inspection des fichiers réels du dépôt (sans inventer de commandes).
   - Création d'un environnement virtuel isolé `.venv` (sans toucher à vos fichiers personnels).
   - Exécution de la batterie de tests de non-régression du projet.
   - Restitution d'un **Rapport Post-Installation** standardisé.
   - Mise à disposition de **scénarios d'utilisation prêts à l'emploi**.

> 🛡️ **Règle de sécurité stricte :** L'agent a pour instruction formelle de demander votre confirmation explicite avant toute action risquée, écriture sensible ou suppression de fichier.

---

## 📦 Les 5 Prompts d'Installation Clé en Main

---

### 1️⃣ Outil #01 : Web Assets Manager (`01_web_assets_manager`)

* **Rôle :** Scanne les maquettes HTML (`code.html`), télécharge localement les images distantes du CDN dans `frontend/public/images/` et remplace les URLs distantes dans vos composants React (`.tsx`).
* **Prérequis :** Node.js v18+ (LTS recommandé) et npm.

#### 📋 Prompt à Copier-Coller pour votre Agent IA :

```markdown
Tu es mon ingénieur DevOps et agent de coding. Je souhaite installer, vérifier et utiliser l'outil **01_web_assets_manager** du dépôt officiel `https://github.com/snorbik-ai/mcp-hybrid-architecture`.

Applique scrupuleusement le protocole d'ingénierie suivant :

1. ANALYSE ENVIRONNEMENT : Identifie mon système d'exploitation (Windows, Linux ou macOS) et vérifie si Node.js (version 18+ requise) et npm sont installés sur ma machine.
2. RÉCUPÉRATION DU DÉPÔT : Si le dépôt n'est pas encore présent dans mon dossier de travail, clone `https://github.com/snorbik-ai/mcp-hybrid-architecture.git` ou vérifie que le répertoire `01_web_assets_manager` existe.
3. INSPECTION LOCALE : Ne devine aucune commande. Inspecte les fichiers réels de `01_web_assets_manager/` : lis `package.json`, `README.md` et examine les scripts disponibles.
4. INSTALLATION SÉCURISÉE : Installe les dépendances Node.js via `npm install` dans le répertoire `01_web_assets_manager` sans écraser mes fichiers existants. Demande ma confirmation avant toute modification irréversible ou installation globale.
5. CONTRÔLE ET TESTS : Exécute la suite de tests automatisés de l'outil via `node tests/run_all_suites.mjs` (ou `run_tests.bat` sous Windows). Vérifie que les 4 couches de tests (Unitaires, Intégration, Validation/Perf, Smoke) passent sans aucune erreur. Ne dis JAMAIS que l'installation est réussie si les tests échouent.
6. RAPPORT STRUCTURÉ : Une fois les tests validés, affiche le rapport post-installation complet comprenant :
   - Statut de l'installation et versions détectées (Node.js, npm) ;
   - Résumé des tests exécutés et temps de réponse ;
   - Capacités réelles prêtes à l'emploi (extraction d'assets, relieur React, dashboard web port 5181) ;
   - Limites connues ;
   - 3 scénarios d'utilisation avec prompts prêts à copier-coller ;
   - Comment consulter le fichier de sortie `assets-manifest.json` et le carnet de bord de session.
```

---

### 2️⃣ Outil #02 : PDF Technical Extractor (`02_pdf_technical_extractor`)

* **Rôle :** Découpe les catalogues PDF fabricants, extrait les schémas CAO/vectoriels, génère des rendus de page haute définition à 150 DPI et extrait le texte Markdown complet.
* **Prérequis :** Python 3.10+ (avec `PyMuPDF` / `fitz`).

#### 📋 Prompt à Copier-Coller pour votre Agent IA :

```markdown
Tu es mon ingénieur de données et agent de coding. Je souhaite installer, vérifier et utiliser l'outil **02_pdf_technical_extractor** du dépôt officiel `https://github.com/snorbik-ai/mcp-hybrid-architecture`.

Applique scrupuleusement le protocole d'ingénierie suivant :

1. ANALYSE ENVIRONNEMENT : Identifie mon système d'exploitation et vérifie que Python 3.10+ (64-bit) est disponible dans le PATH.
2. RÉCUPÉRATION DU DÉPÔT : Vérifie la présence du dossier `02_pdf_technical_extractor` ou clone `https://github.com/snorbik-ai/mcp-hybrid-architecture.git`.
3. INSPECTION LOCALE : Inspecte `02_pdf_technical_extractor/requirements.txt`, `README.md` et `pdf_processor.py`.
4. ENVIRONNEMENT ISOLÉ : Vérifie si un environnement virtuel `.venv` existe à la racine du dépôt ou crée-le proprement via `python -m venv .venv`. Active-le et installe les dépendances nécessaires (`pip install -r 02_pdf_technical_extractor/requirements.txt` incluant PyMuPDF).
5. CONTRÔLE ET TESTS : Exécute la suite de tests automatisés via `python 02_pdf_technical_extractor/tests/run_all_suites.py` (ou `run_tests.bat` sous Windows). Vérifie que toutes les suites de tests sont validées avec succès.
6. RAPPORT STRUCTURÉ : Affiche le rapport post-installation avec :
   - Statut de l'installation et version de PyMuPDF ;
   - Bilan des tests automatisés ;
   - Capacités réelles (découpage par page, rendu HD 150 DPI, extraction de texte Markdown, dashboard web port 5182) ;
   - 3 scénarios d'utilisation prêts à l'emploi avec prompts (ex: découper un catalogue PDF, extraire le texte technique, générer des vignettes HD) ;
   - Emplacement des fichiers générés (`output/` et `manifest.json`).
```

---

### 3️⃣ Outil #03 : Media Quality Auditor (`03_media_quality_auditor`)

* **Rôle :** Analyse un dossier d'images, calcule les empreintes MD5 pour éliminer les doublons stricts, audite les dimensions minimales (>= 1200x700) et certifie les images candidates pour les bannières Hero.
* **Prérequis :** Python 3.10+ (avec `Pillow`).

#### 📋 Prompt à Copier-Coller pour votre Agent IA :

```markdown
Tu es mon ingénieur qualité et agent de coding. Je souhaite installer, vérifier et utiliser l'outil **03_media_quality_auditor** du dépôt officiel `https://github.com/snorbik-ai/mcp-hybrid-architecture`.

Applique scrupuleusement le protocole d'ingénierie suivant :

1. ANALYSE ENVIRONNEMENT : Identifie mon OS et vérifie la présence de Python 3.10+ 64-bit.
2. RÉCUPÉRATION DU DÉPÔT : Vérifie que le répertoire `03_media_quality_auditor` est accessible.
3. INSPECTION LOCALE : Lis `03_media_quality_auditor/requirements.txt`, `README.md` et les scripts dans `canal_sdk_cli/`.
4. ENVIRONNEMENT ISOLÉ : Utilise l'environnement virtuel `.venv` de la racine et installe les dépendances requises (`Pillow`).
5. CONTRÔLE ET TESTS : Lance la suite de tests via `python 03_media_quality_auditor/tests/run_all_suites.py`. Assure-toi que les 4 couches (dont la détection des doublons MD5 et le test de sécurité dry-run) sont validées à 100 %.
6. RAPPORT STRUCTURÉ : Fournis le rapport post-installation détaillant :
   - Statut et version de Pillow installée ;
   - Résultat des tests ;
   - Capacités réelles (audit par dossier, dédoublonnage MD5 avec sécurité dry-run, qualification VALID_HD / REJECTED_LOW_RES, dashboard web port 5180) ;
   - 3 scénarios pratiques avec prompts copiables (audit d'un dossier média, simulation de purge de doublons, extraction des images certifiées Hero) ;
   - Emplacement des rapports JSON générés.
```

---

### 4️⃣ Outil #04 : E-commerce Catalog Scanner (`04_ecommerce_catalog_scanner`)

* **Rôle :** Scanne le DOM de boutiques en ligne (SSR PrestaShop/Shopify ou SPA React BatiHome), extrait références SKU, prix TTC/HT et visuels, produit un rapport HTML interactif complet sur disque et transmet à l'agent IA un résumé exécutif ultra-compact (*Digest-First*).
* **Prérequis :** Python 3.10+ (avec `BeautifulSoup4` ; support Playwright optionnel pour SPAs complexes).

#### 📋 Prompt à Copier-Coller pour votre Agent IA :

```markdown
Tu es mon architecte d'extraction web et agent de coding. Je souhaite installer, vérifier et utiliser l'outil **04_ecommerce_catalog_scanner** du dépôt officiel `https://github.com/snorbik-ai/mcp-hybrid-architecture`.

Applique scrupuleusement le protocole d'ingénierie suivant :

1. ANALYSE ENVIRONNEMENT : Identifie mon OS et vérifie Python 3.10+.
2. RÉCUPÉRATION DU DÉPÔT : Vérifie l'accès au répertoire `04_ecommerce_catalog_scanner`.
3. INSPECTION LOCALE : Lis `04_ecommerce_catalog_scanner/requirements.txt`, `README.md` et `docs/CAHIER_DES_CHARGES_ET_GUIDE.md`.
4. ENVIRONNEMENT ISOLÉ : Active `.venv` et installe les dépendances requises (`beautifulsoup4`, `requests`, `lxml`).
5. CONTRÔLE ET TESTS : Exécute `python 04_ecommerce_catalog_scanner/tests/run_all_suites.py`. Vérifie que les tests d'extraction de cartes produits, de calculs de prix et d'initialisation du canal MCP Digest-First passent avec succès.
6. RAPPORT STRUCTURÉ : Affiche le bilan post-installation détaillant :
   - Statut et dépendances installées ;
   - Résultats des tests d'extraction ;
   - Capacités réelles (use cases : `scan_ecommerce_catalog`, `discover_category_tree`, `audit_scanned_catalog`, dashboard web interactif sur port 5183) ;
   - Règle Digest-First : explication de la sauvegarde du rapport HTML complet sur disque et de la transmission d'un digest compact pour protéger ma fenêtre de contexte ;
   - 3 scénarios d'utilisation prêts à l'emploi (ex: scan du catalogue BatiHome, recherche par référence SKU, consultation du rapport visuel) ;
   - Emplacement de `output/catalogue.json`, `output/rapport_scan_interactif.html` et `output/turn_report.json`.
```

---

### 5️⃣ Outil #05 : Visual Catalog Sync (`05_visual_catalog_sync`)

* **Rôle :** Synchronise les photos de produits en local de manière idempotente, tronque préventivement les noms d'images pour respecter la contrainte Windows `MAX_PATH < 260`, et compile le catalogue en module TypeScript typé (`RawGlassRailingCatalog.ts`) et en inventaire Markdown.
* **Prérequis :** Python 3.10+ (**0 dépendance externe**, utilise exclusivement la bibliothèque standard Python).

#### 📋 Prompt à Copier-Coller pour votre Agent IA :

```markdown
Tu es mon ingénieur d'intégration frontend et agent de coding. Je souhaite installer, vérifier et utiliser l'outil **05_visual_catalog_sync** du dépôt officiel `https://github.com/snorbik-ai/mcp-hybrid-architecture`.

Applique scrupuleusement le protocole d'ingénierie suivant :

1. ANALYSE ENVIRONNEMENT : Identifie mon OS (attention particulière si Windows en raison de la limite MAX_PATH de 260 caractères) et vérifie la présence de Python 3.10+.
2. RÉCUPÉRATION DU DÉPÔT : Vérifie l'accès au répertoire `05_visual_catalog_sync`.
3. INSPECTION LOCALE : Inspecte `05_visual_catalog_sync/README.md` et `core/domain/`. Note que cet outil fonctionne avec 0 dépendance pip tierce.
4. ENVIRONNEMENT ET TESTS : Exécute directement `python 05_visual_catalog_sync/tests/run_all_suites.py`. Vérifie que les tests de safe-path Windows, de compilation TypeScript et d'idempotence sont validés sans avertissement.
5. RAPPORT STRUCTURÉ : Fournis le rapport post-installation comprenant :
   - Statut de l'outil et confirmation de l'autonomie (0 dépendance pip requise) ;
   - Bilan des tests d'intégration et de compilation ;
   - Capacités réelles (synchronisation d'images safe-path, génération de `RawGlassRailingCatalog.ts`, inventaire Markdown, dashboard web port 5184) ;
   - 3 scénarios prêts à l'emploi avec prompts (ex: synchronisation des visuels, compilation du catalogue TypeScript, vérification des chemins Windows) ;
   - Emplacement des fichiers générés.
```

---

## 📊 Modèle de Rapport Post-Installation Attendu

Lorsque vous soumettez l'un des prompts ci-dessus à votre agent, celui-ci doit impérativement vous répondre sous cette forme standardisée :

```markdown
================================================================================
📋 RAPPORT D'INSTALLATION & VÉRIFICATION — OUTIL #XX
================================================================================
✅ STATUT : Installation Réussie et Vérifiée
🖥️ ENVIRONNEMENT DÉTECTÉ : Windows 11 (ou Linux / macOS) | Python 3.11.x | Node.js v20.x
📦 DÉPENDANCES INSTALLÉES : 
   • .venv actif et isolé
   • Dépendances vérifiées sans conflit
🧪 RÉSULTATS DES TESTS AUTOMATISÉS :
   • Couche 1 (Unitaires) : PASS
   • Couche 2 (Intégration) : PASS
   • Couche 3 (Validation & Performance) : PASS
   • Couche 4 (Smoke Tests Protocolaires) : PASS
   • Bilan : 100 % des tests validés sans échec
⚙️ CAPACITÉS DISPONIBLES :
   • [Liste des fonctionnalités concrètes prêtes à l'emploi]
⚠️ LIMITES CONNUES :
   • [Rappels de sécurité et contraintes du système]
🚀 SCÉNARIOS PRÊTS À L'EMPLOI :
   1. Scénario 1 : [Prompt prêt à copier]
   2. Scénario 2 : [Prompt prêt à copier]
   3. Scénario 3 : [Prompt prêt à copier]
📂 CONSULTATION DES RÉSULTATS :
   • Rapports générés dans : `output/`
   • Carnet de bord horodaté : `turn_report.json`
================================================================================
```

---

## 🔄 Diagnostic Rapide et Désinstallation Propre

* **Diagnostic de santé :** Si vous rencontrez un doute sur l'état de votre installation, demandez à votre agent :  
  `"Lance le diagnostic de santé doctor.bat et vérifie l'intégrité de mes outils."`
* **Désinstallation propre :** Pour réinitialiser ou désinstaller un outil sans laisser de traces résiduelles :  
  `"Supprime l'environnement virtuel .venv et réinitialise les dossiers temporaires output/ en appliquant reset_env.bat."`
