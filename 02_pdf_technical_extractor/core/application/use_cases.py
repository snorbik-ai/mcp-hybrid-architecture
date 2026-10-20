#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #02 : PDF TECHNICAL EXTRACTOR — COUCHE APPLICATION (USE CASES)
========================================================================================
Services Métiers orchestrant l'extraction PDF via Injection de Dépendances (DI).
========================================================================================
"""

import json
import shutil
import sys
from pathlib import Path
from typing import Dict, Any, Optional

current_dir = Path(__file__).resolve().parent
tool_root = current_dir.parent.parent
if str(tool_root) not in sys.path:
    sys.path.insert(0, str(tool_root))

from core.domain.entities_and_ports import (
    PdfAssetEntity,
    PdfPageEntity,
    IPdfAssetClassifierPort,
    IPdfManifestRepositoryPort
)


class ProcessPdfDocumentUseCase:
    def __init__(self, classifier_port: IPdfAssetClassifierPort, repository_port: IPdfManifestRepositoryPort):
        self._classifier = classifier_port
        self._repository = repository_port

    def execute(
        self,
        pdf_path: str,
        output_dir: str = "output",
        dpi: int = 150,
        classify: bool = True
    ) -> Dict[str, Any]:
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz

        input_file = Path(pdf_path).resolve()
        if not input_file.exists():
            raise FileNotFoundError(f"Le fichier PDF source est introuvable : {input_file}")

        target_base = Path(output_dir).resolve()
        doc_slug = input_file.stem.lower().replace(" ", "_").replace("-", "_")
        doc_output_dir = target_base / doc_slug

        pages_dir = doc_output_dir / "pages"
        classified_dir = doc_output_dir / "classified_assets"
        pages_dir.mkdir(parents=True, exist_ok=True)

        categories = {
            "plans_et_schemas": classified_dir / "plans_et_schemas",
            "photos_produits": classified_dir / "photos_produits",
            "logos_et_icones": classified_dir / "logos_et_icones",
            "autres": classified_dir / "autres",
        }
        if classify:
            for cat_path in categories.values():
                cat_path.mkdir(parents=True, exist_ok=True)

        doc = fitz.open(str(input_file))
        zoom = dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)

        manifest: Dict[str, Any] = {
            "source_file": str(input_file),
            "filename": input_file.name,
            "total_pages": len(doc),
            "dpi": dpi,
            "pages": [],
            "classified_assets": {k: [] for k in categories.keys()}
        }

        full_text_parts = []
        global_image_counter = 0

        try:
            for page_index in range(len(doc)):
                page_num = page_index + 1
                page = doc[page_index]
                page_folder_name = f"page_{page_num:03d}"
                page_folder = pages_dir / page_folder_name
                page_images_folder = page_folder / "images"
                page_folder.mkdir(parents=True, exist_ok=True)
                page_images_folder.mkdir(parents=True, exist_ok=True)

                page_render_filename = f"{page_folder_name}.png"
                pix = page.get_pixmap(matrix=matrix, alpha=False)
                pix.save(str(page_folder / page_render_filename))

                page_text = page.get_text("text").strip()
                (page_folder / "content.txt").write_text(page_text, encoding="utf-8")

                text_blocks = page.get_text("blocks")
                formatted_blocks = [
                    {"bbox": [round(c, 2) for c in b[:4]], "text": b[4].strip(), "block_no": b[5], "type": b[6]}
                    for b in text_blocks if len(b) >= 7 and b[4].strip()
                ]
                (page_folder / "blocks.json").write_text(
                    json.dumps(formatted_blocks, indent=2, ensure_ascii=False), encoding="utf-8"
                )

                full_text_parts.append(
                    f"## Page {page_num}\n\n{page_text if page_text else '*[Page sans texte direct]*'}\n"
                )

                image_list = page.get_images(full=True)
                page_images_metadata = []

                for img_idx, img_info in enumerate(image_list):
                    xref = img_info[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    width = base_image["width"]
                    height = base_image["height"]

                    if width < 30 or height < 30:
                        continue

                    global_image_counter += 1
                    img_filename = f"img_{page_num:03d}_{img_idx+1:02d}_{width}x{height}.{image_ext}"
                    raw_img_path = page_images_folder / img_filename
                    raw_img_path.write_bytes(image_bytes)

                    category = self._classifier.classify_image(width, height, image_ext)
                    entity = PdfAssetEntity(
                        id=f"asset_{global_image_counter:04d}",
                        page=page_num,
                        filename=img_filename,
                        raw_relative_path=f"pages/{page_folder_name}/images/{img_filename}",
                        width=width,
                        height=height,
                        format=image_ext,
                        category=category
                    )
                    asset_meta = entity.to_dict()
                    page_images_metadata.append(asset_meta)

                    if classify:
                        classified_dest = categories[category] / img_filename
                        shutil.copy2(raw_img_path, classified_dest)
                        manifest["classified_assets"][category].append({
                            **asset_meta,
                            "classified_relative_path": f"classified_assets/{category}/{img_filename}"
                        })

                page_entity = PdfPageEntity(
                    page_number=page_num,
                    render_relative_path=f"pages/{page_folder_name}/{page_render_filename}",
                    width=page.rect.width,
                    height=page.rect.height,
                    has_text=bool(page_text),
                    images_count=len(page_images_metadata),
                    images=page_images_metadata
                )
                manifest["pages"].append(page_entity.to_dict())
        finally:
            doc.close()

        full_text_content = f"# {input_file.stem}\n\n" + "\n---\n\n".join(full_text_parts)
        paths = self._repository.save_manifest_and_text(doc_output_dir, manifest, full_text_content)

        return {
            "status": "success",
            "document_dir": str(doc_output_dir),
            "manifest_file": paths["manifest_file"],
            "full_text_file": paths["full_text_file"],
            "total_pages": manifest["total_pages"],
            "total_images_extracted": global_image_counter,
            "classified_counts": {k: len(v) for k, v in manifest["classified_assets"].items()}
        }


class GetPdfManifestUseCase:
    def __init__(self, repository_port: IPdfManifestRepositoryPort):
        self._repository = repository_port

    def execute(self, document_dir: str) -> Dict[str, Any]:
        return self._repository.load_manifest(Path(document_dir))


class GetPdfDocumentTextUseCase:
    def __init__(self, repository_port: IPdfManifestRepositoryPort):
        self._repository = repository_port

    def execute(self, document_dir: str) -> str:
        return self._repository.load_full_text(Path(document_dir))
