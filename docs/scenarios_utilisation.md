# 🎯 Bibliothèque de Scénarios Pratiques Prêts à l'Emploi

Cette bibliothèque présente des scénarios concrets testés et vérifiés pour chacun des 5 outils de la suite **`mcp-hybrid-architecture`**. Chaque scénario est directement exploitable avec votre assistant IA ou votre agent de coding.

---

## 🧭 Sommaire des Scénarios

* [Outil #01 : Web Assets Manager](#1️⃣-outil-01--web-assets-manager)
  * [Scénario 1.1 (Simple) : Inventaire et Téléchargement des Médias de Maquettes](#scénario-11-simple--inventaire-et-téléchargement-des-médias-de-maquettes)
  * [Scénario 1.2 (Multi-étapes) : Rapatriement et Reliaison Locale dans les Composants React](#scénario-12-multi-étapes--rapatriement-et-reliaison-locale-dans-les-composants-react)
* [Outil #02 : PDF Technical Extractor](#2️⃣-outil-02--pdf-technical-extractor)
  * [Scénario 2.1 (Simple) : Extraction du Texte Technique Markdown pour Base de Connaissances](#scénario-21-simple--extraction-du-texte-technique-markdown-pour-base-de-connaissances)
  * [Scénario 2.2 (Multi-étapes) : Découpage Complet en Pages HD 150 DPI et Extraction CAO](#scénario-22-multi-étapes--découpage-complet-en-pages-hd-150-dpi-et-extraction-cao)
* [Outil #03 : Media Quality Auditor](#3️⃣-outil-03--media-quality-auditor)
  * [Scénario 3.1 (Simple) : Audit de Conformité Résolution et Netteté des Bannières](#scénario-31-simple--audit-de-conformité-résolution-et-netteté-des-bannières)
  * [Scénario 3.2 (Multi-étapes) : Détection, Simulation Dry-Run et Purge des Doublons MD5](#scénario-32-multi-étapes--détection-simulation-dry-run-et-purge-des-doublons-md5)
* [Outil #04 : E-commerce Catalog Scanner (Digest-First)](#4️⃣-outil-04--ecommerce-catalog-scanner)
  * [Scénario 4.1 (Simple) : Scan de Boutique et Génération du Rapport Visuel Interactif](#scénario-41-simple--scan-de-boutique-et-génération-du-rapport-visuel-interactif)
  * [Scénario 4.2 (Multi-étapes) : Exploration d'Arborescence et Audit Ciblé par Référence](#scénario-42-multi-étapes--exploration-darborescence-et-audit-ciblé-par-référence)
* [Outil #05 : Visual Catalog Sync](#5️⃣-outil-05--visual-catalog-sync)
  * [Scénario 5.1 (Simple) : Compilation du Catalogue en Module TypeScript Typé](#scénario-51-simple--compilation-du-catalogue-en-module-typescript-typé)
  * [Scénario 5.2 (Multi-étapes) : Téléchargement Idempotent Safe-Path et Inventaire Markdown](#scénario-52-multi-étapes--téléchargement-idempotent-safe-path-et-inventaire-markdown)
* [Scénario Industriel de Bout en Bout](#🏆-scénario-industriel-complet--la-chaîne-des-5-voitures-autonomes)

---

## 1️⃣ Outil #01 : Web Assets Manager

### Scénario 1.1 (Simple) : Inventaire et Téléchargement des Médias de Maquettes
* **Objectif Utilisateur :** Scanner les maquettes HTML du dossier de design, identifier les images hébergées sur des CDNs distants et les rapatrier dans le dossier d'assets local.
* **Prompt à copier-coller :**
  > *"Utilise l'outil `scan_and_download_maquette_assets` de l'outil 01 pour extraire toutes les images des maquettes HTML locales, les télécharger dans `frontend/public/images/` et me générer le fichier `assets-manifest.json`."*
* **Outils mobilisés :** `scan_and_download_maquette_assets`
* **Résultat attendu :** 
  - Fichier `01_web_assets_manager/data/assets-manifest.json` créé/mis à jour avec les métadonnées (dimensions, URL d'origine, chemin local).
  - Images enregistrées dans `frontend/public/images/`.
* **Critères de vérification :**
  - Ouvrir `assets-manifest.json` et vérifier que la clé `assets` contient la liste des fichiers avec leur statut `DOWNLOADED`.
* **Précautions & autorisations :** Nécessite une connexion Internet active pour télécharger les images distantes depuis les URLs CDN.

---

### Scénario 1.2 (Multi-étapes) : Rapatriement et Reliaison Locale dans les Composants React
* **Objectif Utilisateur :** Remplacer automatiquement les URLs externes dans les fichiers `.tsx` par les chemins locaux sans casser le code existant.
* **Prompt à copier-coller :**
  > *"Étape 1 : Fais une simulation de reliaison (`dry_run: true`) avec l'outil `replace_remote_urls_in_react` pour me lister les fichiers React qui seront modifiés.  
  > Étape 2 : Si la simulation est concluante et ne présente aucune anomalie, applique la modification réelle (`dry_run: false`)."*
* **Outils mobilisés :** `replace_remote_urls_in_react`
* **Résultat attendu :**
  - Étape 1 : Un bilan textuel listant les composants React scannés et le nombre d'occurrences d'URLs distantes trouvées.
  - Étape 2 : Mise à jour des composants dans `frontend/src/` avec les chemins relatifs locaux (`/images/...`).
* **Critères de vérification :**
  - Faire un `git diff frontend/src/` pour constater que seules les URLs ont été modifiées.
* **Précautions & autorisations :** Autorisation d'écriture requise sur le dossier `frontend/src/`. Recommandé d'avoir un arbre Git propre avant de lancer l'étape 2.

---

## 2️⃣ Outil #02 : PDF Technical Extractor

### Scénario 2.1 (Simple) : Extraction du Texte Technique Markdown pour Base de Connaissances
* **Objectif Utilisateur :** Extraire l'intégralité du contenu textuel d'un catalogue PDF technique pour l'indexer ou poser des questions documentaires à l'IA.
* **Prompt à copier-coller :**
  > *"Prends le dossier du document PDF déjà extrait dans `02_pdf_technical_extractor/output/mon_catalogue/` et utilise l'outil `get_pdf_document_text` pour me donner les spécifications de pose et de résistance mécanique."*
* **Outils mobilisés :** `get_pdf_document_text`
* **Résultat attendu :** Texte complet formaté en Markdown avec titres de sections, tableaux et listes à puces.
* **Critères de vérification :** Présence des sections techniques sans caractères corrompus d'encodage.
* **Précautions & autorisations :** Lecture seule, aucun risque de modification de fichiers.

---

### Scénario 2.2 (Multi-étapes) : Découpage Complet en Pages HD 150 DPI et Extraction CAO
* **Objectif Utilisateur :** Traiter un catalogue PDF fournisseur de 20 pages : générer les planches de contrôle en haute définition et isoler les schémas vectoriels.
* **Prompt à copier-coller :**
  > *"Appelle l'outil `process_pdf_document` sur le fichier `data/catalogue_garde_corps.pdf` avec une résolution de 150 DPI et une sortie dans `output/catalogue_hd/`. Affiche-moi ensuite le manifeste technique avec `get_pdf_manifest`."*
* **Outils mobilisés :** `process_pdf_document`, puis `get_pdf_manifest`
* **Résultat attendu :**
  - Dossier `output/catalogue_hd/pages/` contenant les images `page_001.png`, `page_002.png`, etc.
  - Dossier `output/catalogue_hd/images/` avec les visuels isolés.
  - Fichier `manifest.json` référençant l'ensemble des pages et schémas.
* **Critères de vérification :**
  - Vérifier que chaque image PNG a une résolution nette à 150 DPI lisible à l'écran.
* **Précautions & autorisations :** Prévoir de l'espace disque (environ 1 à 2 Mo par page à 150 DPI).

---

## 3️⃣ Outil #03 : Media Quality Auditor

### Scénario 3.1 (Simple) : Audit de Conformité Résolution et Netteté des Bannières
* **Objectif Utilisateur :** Vérifier quelles photos d'un dossier respectent les critères stricts pour servir de bannières Hero (résolution minimale 1200x700).
* **Prompt à copier-coller :**
  > *"Utilise `get_certified_hero_candidates` sur le dossier `frontend/public/images/` pour me lister les visuels validés pour un affichage pleine largeur."*
* **Outils mobilisés :** `get_certified_hero_candidates`
* **Résultat attendu :** Liste des fichiers image répondant au ratio et à la résolution minimale, avec largeur et hauteur réelles.
* **Critères de vérification :** Aucun fichier inférieur à 1200px de large dans la liste des candidats certifiés.
* **Précautions & autorisations :** Lecture seule.

---

### Scénario 3.2 (Multi-étapes) : Détection, Simulation Dry-Run et Purge des Doublons MD5
* **Objectif Utilisateur :** Nettoyer un dossier encombré de copies d'images (suffixes " copy" ou fichiers identiques avec des noms différents).
* **Prompt à copier-coller :**
  > *"Étape 1 : Lance l'outil `clean_duplicate_media` avec `dry_run: true` sur le dossier `frontend/public/images/` pour m'indiquer quels doublons ont été identifiés par empreinte MD5.  
  > Étape 2 : Si la liste ne contient aucun faux positif, exécute la purge avec `dry_run: false`."*
* **Outils mobilisés :** `clean_duplicate_media`
* **Résultat attendu :**
  - Étape 1 : Rapport de simulation indiquant le nombre de doublons et le gain d'espace prévu.
  - Étape 2 : Suppression sécurisée des doublons stricts, préservation de l'exemplaire canonique original.
* **Critères de vérification :**
  - Re-lancer l'audit : le compteur de doublons passe à 0.
* **Précautions & autorisations :** Étape 2 irréversible : l'agent doit demander votre confirmation avant la suppression définitive.

---

## 4️⃣ Outil #04 : E-commerce Catalog Scanner

### Scénario 4.1 (Simple) : Scan de Boutique et Génération du Rapport Visuel Interactif
* **Objectif Utilisateur :** Aspirer les fiches produits d'une boutique (ex: prototype BatiHome), extraire les prix et obtenir un tableau de bord graphique sans saturer le chat.
* **Prompt à copier-coller :**
  > *"Utilise `run_agent_lifecycle` avec le use case `scan_ecommerce_catalog` sur l'URL `https://batihome.snorbik.fr/#P02_solutions`. Donne-moi le résumé compact et le lien vers le rapport HTML interactif."*
* **Outils mobilisés :** `run_agent_lifecycle` (`use_case: "scan_ecommerce_catalog"`)
* **Résultat attendu :**
  - Réponse de l'IA compacte (statut, nombre de références trouvées, fourchette de prix).
  - Fichier `output/catalogue.json` enregistré en local.
  - Fichier `output/rapport_scan_interactif.html` généré pour consultation dans votre navigateur.
* **Critères de vérification :**
  - Double-cliquer sur `rapport_scan_interactif.html` : une interface visuelle s'ouvre avec les vignettes, filtres par famille et calculs de prix TTC/HT.
* **Précautions & autorisations :** Respect des conditions d'utilisation du site cible. L'outil applique une politique de fail-fast en cas de restriction d'accès.

---

### Scénario 4.2 (Multi-étapes) : Exploration d'Arborescence et Audit Ciblé par Référence
* **Objectif Utilisateur :** Explorer les familles de produits puis effectuer une recherche précise par SKU sans recharger l'ensemble des données.
* **Prompt à copier-coller :**
  > *"Étape 1 : Lance `run_agent_lifecycle` avec le use case `audit_scanned_catalog` et filtre sur la famille '04_pinces'.  
  > Étape 2 : Recherche ensuite la référence exacte contenant 'pince au sol 100% inox' pour me donner son prix HT et TTC."*
* **Outils mobilisés :** `run_agent_lifecycle` (`use_case: "audit_scanned_catalog"`)
* **Résultat attendu :** 
  - Synthèse statistique des produits de la famille demandée.
  - Fiche détaillée de l'article ciblé avec son SKU, ses visuels et son calcul de TVA vérifié.
* **Critères de vérification :** Exactitude du prix HT calculé à partir du TTC (ou inversement) selon le taux légal.
* **Précautions & autorisations :** Lecture locale des catalogues précédemment scannés.

---

## 5️⃣ Outil #05 : Visual Catalog Sync

### Scénario 5.1 (Simple) : Compilation du Catalogue en Module TypeScript Typé
* **Objectif Utilisateur :** Générer le code TypeScript prêt à être importé dans une application React/Next.js à partir du fichier `catalogue.json`.
* **Prompt à copier-coller :**
  > *"Appelle l'outil `compile_frontend_catalog` de l'outil 05 pour transformer le fichier `catalogue.json` en module TypeScript typé `RawGlassRailingCatalog.ts`."*
* **Outils mobilisés :** `compile_frontend_catalog`
* **Résultat attendu :**
  - Fichier TypeScript `RawGlassRailingCatalog.ts` généré avec typage strict des interfaces (`ProductItem`, `PricingTTC`, `VariantOptions`).
  - Inventaire Markdown récapitulatif.
* **Critères de vérification :**
  - Ouvrir le fichier TypeScript et vérifier qu'il ne produit aucune erreur de compilation `tsc`.
* **Précautions & autorisations :** Écriture locale d'un fichier source `.ts`.

---

### Scénario 5.2 (Multi-étapes) : Téléchargement Idempotent Safe-Path et Inventaire Markdown
* **Objectif Utilisateur :** Télécharger toutes les photos du catalogue sans dépasser la limite de 260 caractères de Windows (`MAX_PATH`) puis générer l'inventaire.
* **Prompt à copier-coller :**
  > *"Exécute le pipeline complet avec l'outil `sync_and_compile_all` de l'outil 05. Vérifie que la longueur maximale des chemins de fichiers sous Windows reste strictement inférieure à 260 caractères."*
* **Outils mobilisés :** `sync_and_compile_all`
* **Résultat attendu :**
  - Téléchargement idempotent des images manquantes (les fichiers déjà présents ne sont pas retéléchargés).
  - Troncature sécurisée par empreinte de hachage garantissant un nom court (< 43 caractères).
  - Compilation simultanée du module TypeScript et de l'inventaire Markdown.
* **Critères de vérification :**
  - Le rapport indique `max_path_length: < 260` (ex: 136 caractères).
* **Précautions & autorisations :** Connexion Internet requise pour les images non encore mises en cache.

---

## 🏆 Scénario Industriel Complet : La Chaîne des 5 Voitures Autonomes

Voici le scénario d'orchestration qui met en valeur la puissance du **Pattern MCP Hybride** en reliant les 5 outils les uns aux autres :

```markdown
Tu es mon orchestrateur de projet technique. Nous allons exécuter la chaîne industrielle complète des 5 outils de `mcp-hybrid-architecture` sur le cas BatiHome :

1. ÉTAPE 1 (Outil #04) : Scanne le catalogue en ligne BatiHome via `run_agent_lifecycle(use_case="scan_ecommerce_catalog")` et génère le catalogue structuré.
2. ÉTAPE 2 (Outil #03) : Audite la netteté des visuels récupérés via `audit_media_folder` et identifie les images certifiées HD pour la vitrine.
3. ÉTAPE 3 (Outil #05) : Synchronise localement les photos avec troncature safe-path Windows et compile le module TypeScript `RawGlassRailingCatalog.ts` via `sync_and_compile_all`.
4. ÉTAPE 4 (Outil #01) : Intègre les nouveaux médias dans les maquettes React via `replace_remote_urls_in_react`.
5. ÉTAPE 5 (Outil #02) : Découpe la fiche technique PDF associée via `process_pdf_document` pour générer les schémas d'assemblage en 150 DPI.

À chaque étape, affiche un résumé exécutif concis et consigne l'avancement dans le carnet de bord de session.
```
