# 🤖 Guide d'Installation et d'Utilisation Assistées par Agent IA (Variante B)

> **Philosophie :** Vous n'avez pas besoin de lire des pages de documentation technique ni de configurer manuellement vos environnements.  
> Choisissez votre outil ci-dessous, copiez son prompt dans votre agent de coding (*Cursor, Claude Code, Windsurf, Antigravity*), et **laissez l'agent préparer l'environnement, tester l'outil et vous guider directement dans la conversation.**

---

## 🎯 Comment Fonctionne le Déploiement Assisté ?

```
[Utilisateur]  ── Copie le prompt ──>  [Agent de Coding]
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       ▼                                           ▼
          1. Détection Environnement                  2. Dépendances & Tests
          (OS, Python/Node, Chemins)                  (Isolation .venv / npm)
                       │                                           │
                       └─────────────────────┬─────────────────────┘
                                             ▼
                               3. Prise en Main Guidée
                        (Commandes exactes, 2-3 exemples,
                         prochaine action prête à lancer)
```

1. **Zéro friction :** L'utilisateur copie-colle un seul prompt dans son agent.
2. **Exécution déterministe :** L'agent inspecte le code réel, configure l'isolation (`.venv` ou `npm`), exécute la suite de tests et rapporte les résultats observés (sans inventer de succès).
3. **Prise en main immédiate en direct :** L'agent ne renvoie pas l'utilisateur vers des documentations externes : il lui donne les commandes exactes, les exemples d'utilisation et une action concrète à lancer immédiatement.

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
5. CONTRÔLE ET TESTS : Exécute la suite de tests automatisés de l'outil via `node tests/run_all_suites.mjs` (depuis le dossier `01_web_assets_manager`) ou `run_tests.bat` sous Windows. Vérifie que les 4 couches de tests (Unitaires, Intégration, Validation/Perf, Smoke) passent sans aucune erreur. Ne dis JAMAIS que l'installation est réussie si les tests échouent ou n'ont pas été lancés.

DERNIÈRE ÉTAPE OBLIGATOIRE — GUIDER L'UTILISATEUR :
Après l'installation et les vérifications, ne me demande pas de parcourir la documentation du projet.
Présente directement dans notre conversation :
- Statut réel : installation réussie, partielle ou échouée, avec les tests réellement exécutés.
- Comment démarrer : la commande exacte à utiliser et le répertoire depuis lequel l'exécuter (ex: serveur web port 5181 ou script CLI).
- Comment utiliser l'outil : deux ou trois exemples concrets, adaptés à ses fonctionnalités réellement disponibles (ex: extraction d'assets d'un code.html, réécriture des imports React).
- Résultats : où trouver les fichiers générés (ex: `assets-manifest.json`, images téléchargées) et comment les consulter.
- Prochaine action : propose un exemple concret que je peux lancer immédiatement.
Si une information manque, inspecte le code et les fichiers du projet avant de répondre. N'invente aucune commande, fonctionnalité ou réussite de test.
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
5. CONTRÔLE ET TESTS : Exécute la suite de tests automatisés via `python 02_pdf_technical_extractor/tests/run_all_suites.py` (ou `run_tests.bat` sous Windows). Vérifie que toutes les suites de tests sont validées avec succès. Ne déclare jamais PASS sans avoir exécuté le test.

DERNIÈRE ÉTAPE OBLIGATOIRE — GUIDER L'UTILISATEUR :
Après l'installation et les vérifications, ne me demande pas de parcourir la documentation du projet.
Présente directement dans notre conversation :
- Statut réel : installation réussie, partielle ou échouée, avec les tests réellement exécutés.
- Comment démarrer : la commande exacte à utiliser et le répertoire depuis lequel l'exécuter (ex: serveur web port 5182 ou CLI).
- Comment utiliser l'outil : deux ou trois exemples concrets (ex: découper un catalogue PDF page par page, extraire les plans CAO, convertir les pages en Markdown technique).
- Résultats : où trouver les fichiers générés (`output/` et `manifest.json`) et comment les inspecter.
- Prochaine action : propose un exemple concret que je peux lancer immédiatement sur un fichier PDF.
Si une information manque, inspecte le code et les fichiers du projet avant de répondre. N'invente aucune commande, fonctionnalité ou réussite de test.
```

---

### 3️⃣ Outil #03 : Media Quality Auditor (`03_media_quality_auditor`)

* **Rôle :** Audite la résolution des visuels e-commerce (seuil minimal 1200 × 700 px), identifie les doublons par empreinte cryptographique MD5 et applique un renommage prédictif sécurisé (`--dry-run`).
* **Prérequis :** Python 3.10+ (avec `Pillow`).

#### 📋 Prompt à Copier-Coller pour votre Agent IA :

```markdown
Tu es mon ingénieur qualité et agent de coding. Je souhaite installer, vérifier et utiliser l'outil **03_media_quality_auditor** du dépôt officiel `https://github.com/snorbik-ai/mcp-hybrid-architecture`.

Applique scrupuleusement le protocole d'ingénierie suivant :

1. ANALYSE ENVIRONNEMENT : Identifie mon système d'exploitation et vérifie la présence de Python 3.10+.
2. RÉCUPÉRATION DU DÉPÔT : Vérifie l'existence du dossier `03_media_quality_auditor` ou clone le dépôt officiel.
3. INSPECTION LOCALE : Lis `03_media_quality_auditor/requirements.txt` et `README.md`. Note que l'outil utilise `Pillow` et dispose d'un canal sécurisé en mode simulation (`dry-run`).
4. ENVIRONNEMENT ISOLÉ : Utilise l'environnement virtuel `.venv` de la racine et installe les dépendances requises (`Pillow`).
5. CONTRÔLE ET TESTS : Lance la suite de tests via `python 03_media_quality_auditor/tests/run_all_suites.py`. Assure-toi que les 4 couches (dont la détection des doublons MD5 et le test de sécurité dry-run) sont validées. Ne valide aucun test sans preuve d'exécution.

DERNIÈRE ÉTAPE OBLIGATOIRE — GUIDER L'UTILISATEUR :
Après l'installation et les vérifications, ne me demande pas de parcourir la documentation du projet.
Présente directement dans notre conversation :
- Statut réel : installation réussie, partielle ou échouée, avec les tests réellement exécutés.
- Comment démarrer : la commande exacte à utiliser et le répertoire depuis lequel l'exécuter (ex: dashboard web port 5180 ou audit CLI).
- Comment utiliser l'outil : deux ou trois exemples concrets (ex: auditer un dossier d'images, détecter les doublons MD5 en mode simulation `--dry-run`, filtrer les visuels rejetés sous 1200×700).
- Résultats : où trouver les rapports d'audit JSON générés dans `output/`.
- Prochaine action : propose un exemple concret que je peux lancer immédiatement sur un dossier d'images.
Si une information manque, inspecte le code et les fichiers du projet avant de répondre. N'invente aucune commande, fonctionnalité ou réussite de test.
```

---

### 4️⃣ Outil #04 : E-commerce Catalog Scanner (`04_ecommerce_catalog_scanner`)

* **Rôle :** Scanne le DOM de boutiques en ligne (SSR PrestaShop/Shopify ou SPA React BatiHome), extrait références SKU, prix TTC/HT et visuels, produit un rapport HTML interactif complet sur disque et transmet à l'agent IA un résumé exécutif ultra-compact (*Digest-First*).
* **Prérequis :** Python 3.10+ (avec `beautifulsoup4`, `requests`, `lxml` ; Playwright optionnel pour SPAs complexes).

#### 📋 Prompt à Copier-Coller pour votre Agent IA :

```markdown
Tu es mon ingénieur extraction e-commerce et agent de coding. Je souhaite installer, vérifier et utiliser l'outil **04_ecommerce_catalog_scanner** du dépôt officiel `https://github.com/snorbik-ai/mcp-hybrid-architecture`.

Applique scrupuleusement le protocole d'ingénierie suivant :

1. ANALYSE ENVIRONNEMENT : Identifie mon système d'exploitation et vérifie que Python 3.10+ est installé.
2. RÉCUPÉRATION DU DÉPÔT : Vérifie la présence du dossier `04_ecommerce_catalog_scanner` ou clone le dépôt officiel.
3. INSPECTION LOCALE : Examine `04_ecommerce_catalog_scanner/requirements.txt`, `README.md` et les handlers MCP dans `server.py` et `core/`.
4. ENVIRONNEMENT ISOLÉ : Active `.venv` et installe les dépendances requises (`beautifulsoup4`, `requests`, `lxml`).
5. CONTRÔLE ET TESTS : Exécute `python 04_ecommerce_catalog_scanner/tests/run_all_suites.py`. Vérifie que les tests d'extraction de cartes produits, de calculs de prix et d'initialisation du canal MCP Digest-First passent avec succès. Ne prétends pas qu'un test est validé sans exécution réelle.

DERNIÈRE ÉTAPE OBLIGATOIRE — GUIDER L'UTILISATEUR :
Après l'installation et les vérifications, ne me demande pas de parcourir la documentation du projet.
Présente directement dans notre conversation :
- Statut réel : installation réussie, partielle ou échouée, avec les tests réellement exécutés.
- Comment démarrer : la commande exacte à utiliser et le répertoire depuis lequel l'exécuter (ex: serveur web interactif sur port 5183 ou commande CLI).
- Comment utiliser l'outil : deux ou trois exemples concrets (ex: scan du catalogue d'une boutique en ligne, extraction par référence SKU, consultation du rapport visuel).
- Règle Digest-First : explique brièvement comment le rapport HTML exhaustif est sauvegardé sur disque tout en me renvoyant un résumé compact pour protéger ma fenêtre de contexte.
- Résultats : où trouver `output/catalogue.json`, `output/rapport_scan_interactif.html` et le carnet de bord `output/turn_report.json`.
- Prochaine action : propose un exemple concret que je peux lancer immédiatement sur un catalogue de démonstration.
Si une information manque, inspecte le code et les fichiers du projet avant de répondre. N'invente aucune commande, fonctionnalité ou réussite de test.
```

---

### 5️⃣ Outil #05 : Visual Catalog Sync (`05_visual_catalog_sync`)

* **Rôle :** Synchronise les médias qualifiés avec le référentiel de composants du frontend e-commerce, génère le code TypeScript typé (`RawGlassRailingCatalog.ts`) et produit l'inventaire Markdown complet.
* **Prérequis :** Python 3.10+ (autonome : **0 dépendance pip tierce requise**).

#### 📋 Prompt à Copier-Coller pour votre Agent IA :

```markdown
Tu es mon ingénieur synchronisation frontend et agent de coding. Je souhaite installer, vérifier et utiliser l'outil **05_visual_catalog_sync** du dépôt officiel `https://github.com/snorbik-ai/mcp-hybrid-architecture`.

Applique scrupuleusement le protocole d'ingénierie suivant :

1. ANALYSE ENVIRONNEMENT : Identifie mon système d'exploitation et vérifie que Python 3.10+ est disponible.
2. RÉCUPÉRATION DU DÉPÔT : Vérifie que le répertoire `05_visual_catalog_sync` est bien accessible.
3. INSPECTION LOCALE : Inspecte `05_visual_catalog_sync/README.md` et `core/domain/`. Note que cet outil fonctionne de manière 100 % autonome sans aucune dépendance pip tierce.
4. ENVIRONNEMENT ET TESTS : Exécute directement `python 05_visual_catalog_sync/tests/run_all_suites.py`. Vérifie que les tests de safe-path Windows, de compilation TypeScript et d'idempotence sont validés. Ne déclare aucun résultat sans exécution.

DERNIÈRE ÉTAPE OBLIGATOIRE — GUIDER L'UTILISATEUR :
Après l'installation et les vérifications, ne me demande pas de parcourir la documentation du projet.
Présente directement dans notre conversation :
- Statut réel : installation réussie, partielle ou échouée, avec les tests réellement exécutés.
- Comment démarrer : la commande exacte à utiliser et le répertoire depuis lequel l'exécuter (ex: dashboard web port 5184 ou CLI).
- Comment utiliser l'outil : deux ou trois exemples concrets (ex: synchronisation safe-path des images, génération de `RawGlassRailingCatalog.ts`, inventaire Markdown).
- Résultats : où trouver le catalogue TypeScript et l'inventaire dans `output/`.
- Prochaine action : propose un exemple concret que je peux lancer immédiatement.
Si une information manque, inspecte le code et les fichiers du projet avant de répondre. N'invente aucune commande, fonctionnalité ou réussite de test.
```

---

## 📊 Modèle de Restitution Attendu dans la Conversation

Lorsque vous soumettez l'un des prompts ci-dessus à votre agent, celui-ci doit répondre **directement dans la conversation** selon cette structure factuelle (sans inventer de succès) :

```markdown
================================================================================
📋 RAPPORT D'INSTALLATION & PRISE EN MAIN — OUTIL #XX
================================================================================
⚙️ STATUT RÉEL CONSTATÉ : [Succès complet / Partiel avec avertissements / Échec]
🖥️ ENVIRONNEMENT DÉTECTÉ : [Système d'exploitation | Version Python / Node.js réellement détectées]
📦 DÉPENDANCES INSTALLÉES : 
   • [.venv isolé ou node_modules configuré sans écrasement de fichiers]
🧪 RÉSULTATS DES TESTS AUTOMATISÉS :
   • Couche 1 (Unitaires) : [PASS / ÉCHEC — consigner l'erreur exacte si échec]
   • Couche 2 (Intégration) : [PASS / ÉCHEC — consigner l'erreur exacte si échec]
   • Couche 3 (Validation & Performance) : [PASS / ÉCHEC — consigner l'erreur exacte si échec]
   • Couche 4 (Smoke Tests Protocolaires) : [PASS / ÉCHEC — consigner l'erreur exacte si échec]
   • Bilan : [Nombre de tests exécutés et validés — Ne jamais prétendre un test réussi sans exécution]

🚀 COMMENT DÉMARRER IMMÉDIATEMENT :
   • Répertoire de travail : [Chemin exact]
   • Commande de démarrage : [Commande exacte CLI ou serveur web]

💡 2 À 3 EXEMPLES CONCRETS D'UTILISATION :
   1. Exemple 1 : [Description et commande exacte]
   2. Exemple 2 : [Description et commande exacte]
   3. Exemple 3 : [Description et commande exacte]

📂 OÙ TROUVER LES RÉSULTATS :
   • Fichiers générés : `output/[nom_du_fichier]`
   • Carnet de bord : `output/turn_report.json`

👉 PROCHAINE ACTION CONCRÈTE :
   « Souhaitez-vous que je lance la commande suivante pour tester immédiatement sur votre premier fichier : [Commande prête à exécuter] ? »
================================================================================
```

---

## 🔄 Diagnostic Rapide et Désinstallation Sécurisée

* **Diagnostic de santé :** Si vous rencontrez un doute sur l'état de votre installation, demandez à votre agent :  
  `"Lance le diagnostic de santé doctor.bat et vérifie l'intégrité de mes outils."`

* **Désinstallation et nettoyage sécurisés :**  
  > ⚠️ **Sécurité des données :** L'agent a pour obligation de demander votre validation explicite avant toute suppression de `.venv` ou réinitialisation du dossier `output/`, afin de vous permettre de sauvegarder au préalable vos rapports et catalogues générés.  
  Demandez à votre agent :  
  `"Demande-moi d'abord confirmation si des rapports dans output/ doivent être conservés, puis supprime proprement .venv et réinitialise les dossiers temporaires."`
