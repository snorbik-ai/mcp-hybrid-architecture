# 🚗 Outil Interne #02 : Extracteur de Catalogues Techniques BTP & Découpeur CAO (`02_pdf_technical_extractor`)

> **Nom Industriel Évocateur Officiel :** Extracteur de Catalogues Techniques BTP & Découpeur CAO  
> **Répertoire Autonome :** `02_pdf_technical_extractor`  
> **Type d'architecture :** "Voiture Autonome" (100 % autonome, zéro dépendance externe)  
> **Conception :** Clean Architecture (`core/domain/` $\leftarrow$ `core/application/` $\leftarrow$ `core/infrastructure/`)  
> **Qualité & Tests :** 4 couches de tests (Unitaires, Intégration, Validation/Perf, Smoke) $\rightarrow$ **10/10 PASS**

---

## 📌 1. À quoi sert cet outil ? (Rôle & Vision)

Le **PDF Technical Extractor** est un moteur d'ingestion documentaire haute performance conçu pour transformer des catalogues fournisseurs volumineux (50 à 300 pages), des notices de pose ou des devis d'architectes PDF en **données exploitables et structurées** :
- **Avant cet outil** : Les schémas de coupe des profilés de garde-corps, les photos commerciales et le texte technique étaient enfermés dans des fichiers PDF binaires impossibles à requêter par une IA ou à afficher dynamiquement sur le Web.
- **Grâce à cet outil** :
  1. Il découpe chaque page dans un sous-dossier dédié (`page_001/`, `page_002/`).
  2. Il génère un rendu haute définition pleine page au format PNG (150 ou 300 DPI).
  3. Il extrait sans aucune compression destructive les flux d'images bruts (`XObject`).
  4. Il extrait le texte brut (`content.txt`) ainsi que les coordonnées géométriques des blocs (`blocks.json`).
  5. Il classe automatiquement les images en 4 répertoires : `plans_et_schemas`, `photos_produits`, `logos_et_icones`, `autres`.
  6. Il compile l'intégralité du document dans un fichier Markdown structuré (`full_text.md`) pour alimenter le RAG de l'Agent IA.

---

## ⚙️ 2. Comment fonctionne-t-il ? (Sous le capot)

L'outil applique une **Clean Architecture** stricte :
- **Couche Domain (`core/domain/entities_and_ports.py`)** :
  - Entités métier : `PdfAssetEntity` (id, page, format, dimensions, catégorie) et `PdfPageEntity` (numéro, statut texte, compteur d'images, dimensions).
  - Interfaces abstraites (*Ports*) : `IPdfAssetClassifierPort`, `IPdfManifestRepositoryPort`.
- **Couche Application / Use Cases (`core/application/use_cases.py`)** :
  - `ProcessPdfDocumentUseCase` : Traitement de bout en bout du fichier PDF avec PyMuPDF.
  - `GetPdfManifestUseCase` : Lecture et chargement du `manifest.json`.
  - `GetPdfDocumentTextUseCase` : Lecture du texte intégral `full_text.md`.
- **Couche Infrastructure (`core/infrastructure/`)** :
  - `HeuristicPdfAssetClassifierAdapter` : Classification géométrique selon le ratio largeur/hauteur et la résolution (ex: ratio > 1.7 et grande taille = plan/schéma technique).
  - `PdfManifestRepositoryAdapter` : Persistance atomique des métadonnées JSON et des synthèses Markdown.

---

## 🚀 3. Comment l'utiliser ? (Guide Pratique Multi-Canal)

### A. Contrôle Qualité & Tests (Obligatoire avant utilisation)
Double-cliquez sur `run_tests.bat` ou lancez :
```bash
run_tests.bat
# ou avec Python :
python tests/run_all_suites.py
```
*Valide les 4 couches de tests en moins de 600 ms.*

### B. Canal 1 — Pour les Intelligences Artificielles (MCP)
- **Variante A (MCP JSON-RPC Stdio)** : `python canal_mcp/mcp_classic_stdio/mcp_server.py`. Expose :
  - `process_pdf_document` : Découpe, extrait et classe un PDF.
  - `get_pdf_manifest` : Charge le manifeste JSON d'un document traité.
  - `get_pdf_document_text` : Récupère le texte complet Markdown pour l'analyse IA.
  - `run_quality_and_tests_suite` : Exécution autonome des tests par l'IA.
- **Variante B (MCP Agent Coding)** : L'IA consulte [`canal_mcp/mcp_agent_coding/context_llm.json`](./canal_mcp/mcp_agent_coding/context_llm.json) et archive ses comptes rendus de session via son `context_history_manager.py` local.

### C. Canal 2 — Pour les Utilisateurs Humains (Interface Graphique Web UI)
```bash
python canal_ui/server.py --port 5180
```
Ouvrez `http://localhost:5180` dans votre navigateur :
- Réglez la résolution DPI (120, 150, 300 DPI).
- Sélectionnez un PDF et lancez l'ingestion d'un clic.
- Explorez la galerie d'images classées et l'onglet d'analyse textuelle OCR/RAG.

### D. Canal 3 — Pour les Développeurs & Scripts CLI
```bash
python canal_sdk_cli/cli.py --input "chemin/vers/catalogue.pdf" --output "output" --dpi 150
```
Ou importez le SDK Python dans votre code :
```python
from canal_sdk_cli.sdk import PdfProcessorSDK
sdk = PdfProcessorSDK(default_dpi=150)
result = sdk.process_pdf("documents/catalogue.pdf")
print(f"Pages extraites : {result['total_pages']}, Images : {result['total_images_extracted']}")
```
