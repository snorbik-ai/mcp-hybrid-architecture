# 📄 Cahier des Charges & Guide — PDF Assets Pipeline

## 📌 1. Introduction & Présentation de l'Outil

Le **PDF Assets Pipeline** est un moteur d'ingestion documentaire haute performance permettant de découper, extraire et classifier automatiquement l'ensemble des éléments contenus dans un catalogue fabricant, une notice de pose ou un devis d'architecte au format PDF.

Il découpe chaque page dans un sous-dossier dédié (`pages/page_XXX/`), produit un rendu pleine page haute fidélité (150 ou 300 DPI), extrait les flux bruts d'images (`XObject`) sans recompression destructive, extrait le texte et les boîtes englobantes géométriques (`blocks.json`), et classe automatiquement les médias dans `classified_assets/`.

---

## 🏛️ 2. Architecture Multi-Canal (3 Canaux)

Ce module expose 3 canaux d'utilisation distincts bâtis autour du moteur `PdfProcessorSDK` :

### 🤖 Canal 1 : Serveur FastMCP (`canal_mcp/mcp_server.py`)
* **Public cible** : Intelligences Artificielles (Claude Desktop, Cursor, Gemini, Antigravity IDE).
* **Protocole** : Standard Model Context Protocol (FastMCP via `stdio`).
* **Outils MCP exposés** :
  1. `process_pdf_document(pdf_path, output_dir, dpi)` : Découpe, extrait et classe un PDF complet.
  2. `get_pdf_manifest(document_dir)` : Lit le manifeste d'un catalogue (pages, dimensions, images).
  3. `get_pdf_document_text(document_dir)` : Retourne le texte complet Markdown d'un catalogue pour alimenter la recherche sémantique ou le RAG d'un agent conversationnel.

### 🖥️ Canal 2 : Interface Graphique Web UI (`canal_ui/server.py`)
* **Public cible** : Utilisateurs humains (acheteurs, chargés de projet, dessinateurs BE).
* **URL d'accès** : `http://localhost:5180` (démarré avec `npm run pdf:ui`).
* **Fonctionnalités** :
  * Sélection de document PDF et réglage interactif de la résolution DPI (120, 150, 300).
  * Bouton "Lancer l'Ingestion" avec retour en temps réel.
  * Compteurs dynamiques (Pages traitées, Photos Produits, Plans & Schémas, Logos).
  * Galerie visuelle à onglets avec zoom sur les images et aperçu des rendus de page.
  * Onglet "Texte OCR & RAG IA" pour visualiser le texte extrait page par page.

### ⚙️ Canal 3 : SDK Programmable & Commandes CLI (`canal_sdk_cli/`)
* **Public cible** : Développeurs Python et pipelines de traitement automatique.
* **Le SDK (`sdk.py`)** :
  ```python
  from canal_sdk_cli.sdk import PdfProcessorSDK

  sdk = PdfProcessorSDK(default_dpi=150)
  result = sdk.process_pdf("documents/catalogue.pdf", output_dir="output")
  print(f"Pages: {result['total_pages']}, Images: {result['total_images_extracted']}")
  ```
* **La commande CLI (`cli.py`)** :
  * `npm run pdf:sample` : Traite l'échantillon fournisseur VI_TREE.
  * `python canal_sdk_cli/cli.py --input "mon_fichier.pdf" --dpi 300` : Commande personnalisée.

---

## 📋 3. Cahier des Charges Fonctionnel & Technique

1. **Rendu Raster Haute Définition** : Rendu des pages sous forme de fichiers PNG à résolution contrôlée par matrice de zoom fitz (`dpi / 72.0`).
2. **Extraction Sans Perte des Flux XObject** : Parcours binaire des objets du document PDF pour extraire les images dans leur format et résolution natives.
3. **Double niveau d'extraction textuelle** :
   - `content.txt` : Texte brut continu par page pour le moteur de recherche plein texte.
   - `blocks.json` : Coordonnées cartésiennes précises `[x0, y0, x1, y1]` des paragraphes et titres.
4. **Classification Heuristique Automatisée** :
   - `plans_et_schemas` : Schémas techniques de profilés et coupes (grande taille, aspect ratio allongé ou format vectoriel).
   - `photos_produits` : Photographies de garde-corps posés (haute résolution, ratio standard).
   - `logos_et_icones` : Logos fournisseurs et pictogrammes de normes (taille < 200px ou aspect ratio très étiré).

---

## 🛠️ 4. Bibliothèques Utilisées

* **`pymupdf` (`fitz`)** : Moteur de rendu et d'analyse PDF en C++ natif avec bindings Python. Il offre une vitesse d'exécution de 10 à 30 fois supérieure aux solutions Pure-Python (comme `pypdf`) ou basées sur `pdf2image` + Poppler, sans nécessiter d'installation externe d'exécutables C++ sous Windows.
* **`mcp` (`mcp.server.fastmcp`)** : Bibliothèque officielle de l'écosystème MCP pour exposer les outils à l'IA en toute sécurité.
* **`http.server` & `json`** : Bibliothèques standards Python pour servir l'interface graphique sans framework lourd.
