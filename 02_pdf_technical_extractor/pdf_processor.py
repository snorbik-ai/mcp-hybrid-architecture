#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
OUTIL INTERNE : PIPELINE D'INGESTION, DÉCOUPAGE ET EXTRACTION DE PDF VERS ASSETS
=============================================================================
Écosystème : BatiHome E-Commerce & SaaS Garde-Corps
Fichier : outils_internes/pdf_assets_pipeline/pdf_processor.py

OBJECTIF ET CONTEXTE :
Dans l'industrie du bâtiment et du garde-corps sur mesure, une grande partie des
données techniques clés (catalogues fournisseurs, fiches de cotation, plans de
réservation, PV d'essais CSTB) est encapsulée dans des documents PDF statiques.
Cet outil décompose n'importe quel PDF en une arborescence de fichiers exploitables.

ARCHITECTURE DE L'ALGORITHME :
1. Découpage arborescent par page :
   Création automatique d'un sous-dossier `pages/page_XXX/` pour chaque page.
2. Rendu graphique haute fidélité (Rasterization Pixmap) :
   Conversion de chaque page complète en une image PNG (150 ou 300 DPI) permettant
   son affichage plein écran dans une visionneuse web.
3. Extraction textuelle multi-niveaux :
   - Texte brut continu (`content.txt`) pour la recherche indexée / LLM RAG.
   - Blocs géométriques avec boîtes englobantes (`blocks.json`) pour l'analyse
     spatiale et la corrélation texte / schéma.
4. Extraction brute sans perte des flux d'images (XObject) :
   Parcours des flux binaires internes du document PDF sans décompression/recompression
   destructive, préservant la résolution native du capteur ou du logiciel de DAO.
5. Heuristique de classification métier :
   Analyse des dimensions, de l'aspect-ratio et de l'espace colorimétrique pour
   regrouper les images dans `classified_assets/` :
   - `plans_et_schemas` : schémas techniques, coupes vectorielles, plans de pose
   - `photos_produits` : photographies réelles de chantiers, profilés, vitrages
   - `logos_et_icones` : pictogrammes et logos
6. Production d'un manifeste unifié (`manifest.json`) et d'un texte consolidé
   (`full_text.md`) pour alimenter les briques e-commerce et l'Assistant IA BatiHome.
=============================================================================
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path

# Tentative d'import de PyMuPDF (la bibliothèque C haute performance retenue)
try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz  # Fallback sur l'ancien nom de namespace
    except ImportError:
        print("[ERREUR CRITIQUE] PyMuPDF n'est pas installé dans l'environnement Python.")
        print("[SOLUTION] Installez la bibliothèque avec : pip install pymupdf")
        sys.exit(1)


class PdfAssetsProcessor:
    """
    Classe maîtresse responsable de l'ingestion, du découpage et de l'extraction
    d'un document PDF en un ensemble d'assets numériques structurés.
    """

    def __init__(self, pdf_path: str, output_base: str = "output", dpi: int = 150):
        """
        Initialise le processeur avec le fichier cible et les options d'export.
        
        :param pdf_path: Chemin relatif ou absolu vers le document PDF
        :param output_base: Répertoire racine de destination pour les exports
        :param dpi: Résolution de rendu des pages complètes (défaut: 150 DPI)
        """
        self.pdf_path = Path(pdf_path).resolve()
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"Le fichier PDF source '{self.pdf_path}' est introuvable.")
        
        # Normalisation du nom de document pour créer un dossier propre
        self.doc_name = self.pdf_path.stem.replace(" ", "_").lower()
        self.output_dir = Path(output_base).resolve() / self.doc_name
        self.pages_dir = self.output_dir / "pages"
        self.classified_dir = self.output_dir / "classified_assets"
        self.dpi = dpi

        # Répertoires thématiques de classification
        self.cat_schemas = self.classified_dir / "plans_et_schemas"
        self.cat_photos = self.classified_dir / "photos_produits"
        self.cat_logos = self.classified_dir / "logos_et_icones"
        self.cat_autres = self.classified_dir / "autres"

    def _setup_directories(self):
        """
        Crée la structure d'arborescence sur le disque si elle n'existe pas.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pages_dir.mkdir(parents=True, exist_ok=True)
        self.classified_dir.mkdir(parents=True, exist_ok=True)
        self.cat_schemas.mkdir(parents=True, exist_ok=True)
        self.cat_photos.mkdir(parents=True, exist_ok=True)
        self.cat_logos.mkdir(parents=True, exist_ok=True)
        self.cat_autres.mkdir(parents=True, exist_ok=True)

    def _classify_image(self, width: int, height: int, colorspace: str, ext: str, page_num: int) -> str:
        """
        Heuristique de classification d'une image extraite.
        
        Règles d'inférence :
        - Si dimensions < 160x160 px -> Logo, puce, pictogramme ou icône
        - Si espace couleur monochrome/niveaux de gris ou ratio très étiré -> Plan / Schéma / Coupe
        - Si dimensions >= 300x200 px en couleur -> Photo produit ou chantier réel
        - Sinon -> Autre
        """
        aspect_ratio = width / height if height > 0 else 1.0

        # Règle 1 : Petites icônes ou éléments d'interface
        if width < 160 and height < 160:
            return "logos_et_icones"
        
        # Règle 2 : Dessins techniques, schémas, coupes BE
        if colorspace in ["DeviceGray", "Gray"] or (width > 800 and aspect_ratio > 2.2):
            return "plans_et_schemas"
        
        # Règle 3 : Photographies de produits / réalisations de chantiers
        if width >= 300 and height >= 200:
            return "photos_produits"
        
        return "autres"

    def process(self):
        """
        Point d'entrée du pipeline : exécute le traitement complet page par page.
        """
        self._setup_directories()
        print(f"\n=======================================================")
        print(f" [PDF PIPELINE] Démarrage du traitement : {self.pdf_path.name}")
        print(f" [PDF PIPELINE] Dossier d'export : {self.output_dir}")
        print(f"=======================================================")

        # Ouverture du document via le moteur PyMuPDF
        doc = fitz.open(self.pdf_path)
        total_pages = len(doc)
        print(f"[PDF PIPELINE] Document chargé : {total_pages} page(s) détectée(s).")

        # Initialisation de la structure du manifeste JSON global
        manifest = {
            "document_name": self.doc_name,
            "original_file": str(self.pdf_path),
            "total_pages": total_pages,
            "dpi": self.dpi,
            "pages": [],
            "extracted_images": [],
            "summary_classification": {
                "plans_et_schemas": 0,
                "photos_produits": 0,
                "logos_et_icones": 0,
                "autres": 0
            }
        }

        full_document_text = []
        global_img_counter = 0

        # Itération déterministe sur chaque page du PDF
        for page_idx in range(total_pages):
            page_num = page_idx + 1
            page = doc[page_idx]
            page_str = f"page_{page_num:03d}"
            page_folder = self.pages_dir / page_str
            page_images_folder = page_folder / "images"
            
            page_folder.mkdir(parents=True, exist_ok=True)
            page_images_folder.mkdir(parents=True, exist_ok=True)

            print(f"\n-> Traitement de la Page {page_num}/{total_pages}...")

            # -------------------------------------------------------------
            # ÉTAPE 1 : Rendu graphique plein écran (Pixmap PNG)
            # -------------------------------------------------------------
            page_png_name = f"{page_str}.png"
            page_png_path = page_folder / page_png_name
            pix = page.get_pixmap(dpi=self.dpi)
            pix.save(str(page_png_path))
            print(f"   [OK] Rendu HD page généré : {page_png_name} ({pix.width}x{pix.height} px)")

            # -------------------------------------------------------------
            # ÉTAPE 2 : Extraction du texte brut continu
            # -------------------------------------------------------------
            page_text = page.get_text("text").strip()
            text_file_path = page_folder / "content.txt"
            with open(text_file_path, "w", encoding="utf-8") as f:
                f.write(page_text)

            full_document_text.append(f"--- PAGE {page_num} ---\n" + page_text + "\n")

            # -------------------------------------------------------------
            # ÉTAPE 3 : Extraction des blocs typographiques structurés
            # -------------------------------------------------------------
            blocks = page.get_text("blocks")
            structured_blocks = []
            for b in blocks:
                structured_blocks.append({
                    "bbox": [round(x, 1) for x in b[:4]], # [x0, y0, x1, y1]
                    "text": b[4].strip(),
                    "block_type": "text" if b[6] == 0 else "image"
                })
            with open(page_folder / "blocks.json", "w", encoding="utf-8") as f:
                json.dump(structured_blocks, f, indent=2, ensure_ascii=False)

            # -------------------------------------------------------------
            # ÉTAPE 4 : Extraction brute des flux binaires d'images (XObject)
            # -------------------------------------------------------------
            image_list = page.get_images(full=True)
            page_manifest_images = []
            print(f"   [INFO] {len(image_list)} objet(s) image détecté(s) sur la page.")

            for img_idx, img_info in enumerate(image_list):
                xref = img_info[0] # Référence interne de l'objet dans la table PDF
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                width = base_image["width"]
                height = base_image["height"]
                colorspace = base_image.get("colorspace", "RGB")

                # Filtre antibruit : ignorer les masques transparents de quelques pixels
                if width < 30 and height < 30:
                    continue

                global_img_counter += 1
                img_filename = f"img_{page_num:03d}_{img_idx+1:02d}_{width}x{height}.{image_ext}"
                img_path = page_images_folder / img_filename

                # Écriture de l'image originale dans le dossier de la page
                with open(img_path, "wb") as f:
                    f.write(image_bytes)

                # -------------------------------------------------------------
                # ÉTAPE 5 : Classification automatique et copie thématique
                # -------------------------------------------------------------
                category = self._classify_image(width, height, colorspace, image_ext, page_num)
                manifest["summary_classification"][category] += 1

                category_dirs = {
                    "plans_et_schemas": self.cat_schemas,
                    "photos_produits": self.cat_photos,
                    "logos_et_icones": self.cat_logos,
                    "autres": self.cat_autres
                }
                classified_target_dir = category_dirs.get(category, self.cat_autres)
                classified_copy_path = classified_target_dir / img_filename
                shutil.copy2(img_path, classified_copy_path)

                img_data = {
                    "id": f"img_{global_img_counter}",
                    "filename": img_filename,
                    "page": page_num,
                    "width": width,
                    "height": height,
                    "colorspace": colorspace,
                    "format": image_ext,
                    "category": category,
                    "relative_page_path": f"pages/{page_str}/images/{img_filename}",
                    "classified_path": f"classified_assets/{category}/{img_filename}"
                }
                page_manifest_images.append(img_data)
                manifest["extracted_images"].append(img_data)
                print(f"      + Image extraite : {img_filename} [{category}]")

            # Enregistrement des données de la page dans le manifeste global
            manifest["pages"].append({
                "page_number": page_num,
                "rendered_page": f"pages/{page_str}/{page_png_name}",
                "text_content": f"pages/{page_str}/content.txt",
                "blocks": f"pages/{page_str}/blocks.json",
                "images_count": len(page_manifest_images),
                "images": page_manifest_images
            })

        # -----------------------------------------------------------------
        # ÉTAPE 6 : Finalisation & Écriture du Manifeste Consolidé
        # -----------------------------------------------------------------
        with open(self.output_dir / "full_text.md", "w", encoding="utf-8") as f:
            f.write("\n\n".join(full_document_text))

        with open(self.output_dir / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        print(f"\n=======================================================")
        print(f" [PDF PIPELINE] SUCCÈS COMPLET DU TRAITEMENT !")
        print(f" -> {total_pages} page(s) découpée(s) en haute définition (PNG)")
        print(f" -> {global_img_counter} image(s) encapsulée(s) extraite(s) sans perte")
        print(f" -> Répartition : {manifest['summary_classification']}")
        print(f" -> Manifeste JSON généré : {self.output_dir / 'manifest.json'}")
        print(f"=======================================================\n")
        return manifest


def main():
    """
    Interface en ligne de commande (CLI).
    Permet d'appeler le pipeline directement depuis le terminal ou via npm run.
    """
    parser = argparse.ArgumentParser(
        description="BatiHome - Pipeline interne de découpage et d'extraction de PDF vers assets structurés."
    )
    parser.add_argument("--input", "-i", required=True, help="Chemin vers le fichier PDF à traiter.")
    parser.add_argument("--output", "-o", default="output", help="Dossier racine d'exportation (défaut: output).")
    parser.add_argument("--dpi", "-d", type=int, default=150, help="Résolution de rendu des pages (défaut: 150 DPI).")
    args = parser.parse_args()

    processor = PdfAssetsProcessor(args.input, args.output, args.dpi)
    processor.process()


if __name__ == "__main__":
    main()
