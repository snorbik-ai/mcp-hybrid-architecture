#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #05 — VISUAL CATALOG SYNC & TYPESCRIPT COMPILER PIPELINE (CLEAN ARCH)
Couche : Core / Application (Use Cases / Services Métiers assemblés par Injection)
========================================================================================
Rôle :
Orchestre les Services Métiers :
1. SyncVisualAssetsUseCase : Télécharge/vérifie toutes les images produits & accessoires
   en garantissant 0 dépassement de Windows MAX_PATH (260 caractères) et synchronise
   `frontend/public/assets/catalogue_verre/`.
2. CompileFrontendCatalogUseCase : Génère `RawGlassRailingCatalog.ts` et le rapport
   Markdown `CATALOGUE_MATIERE_PREMIERE_GARDE_CORPS_VERRE.md`.
========================================================================================
"""

import os
import json
from typing import Dict, Any, List
from ..domain.entities_and_ports import (
    VisualSyncItemResult,
    IBinaryImageHarvesterPort,
    ICatalogArtifactCompilerPort,
)


class SyncVisualAssetsUseCase:
    """
    Service Métier #1 : Synchronisation idempotente des médias du catalogue et contrôle
    de conformité Windows MAX_PATH (< 260 caractères).
    """

    def __init__(self, image_harvester: IBinaryImageHarvesterPort):
        self._image_harvester = image_harvester

    def execute(
        self,
        catalog_json_path: str,
        raw_base_dir: str,
        public_catalog_dir: str,
        public_url_prefix: str = "/assets/catalogue_verre/",
    ) -> Dict[str, Any]:
        with open(catalog_json_path, "r", encoding="utf-8") as f:
            catalog_data = json.load(f)

        products = catalog_data.get("products", [])
        results: List[VisualSyncItemResult] = []
        max_path_observed = 0
        missing_count = 0
        clean_prefix = public_url_prefix.rstrip("/") + "/"

        for prod in products:
            folder_key = prod.get("category_folder", "02_profils")
            dest_folder = os.path.join(raw_base_dir, "images", folder_key)
            img_url = prod.get("image_url", "")
            local_path = self._image_harvester.download_or_reuse_image(
                image_url=img_url,
                raw_dest_folder=dest_folder,
                public_dest_folder=public_catalog_dir,
            )
            if local_path and os.path.exists(local_path):
                path_len = len(os.path.abspath(local_path))
                if path_len > max_path_observed:
                    max_path_observed = path_len
                fname = os.path.basename(local_path)
                rel_raw = os.path.relpath(local_path, raw_base_dir).replace("\\", "/")
                pub_url = f"{clean_prefix}{fname}"
                prod["local_image"] = rel_raw
                prod["frontend_public_image"] = pub_url
                results.append(
                    VisualSyncItemResult(
                        sku=prod.get("sku", ""),
                        image_url=img_url,
                        local_raw_path=rel_raw,
                        public_frontend_url=pub_url,
                        path_length_chars=path_len,
                        status="SYNCED",
                    )
                )
            else:
                missing_count += 1

        # Sauvegarde du JSON enrichi
        with open(catalog_json_path, "w", encoding="utf-8") as f:
            json.dump(catalog_data, f, ensure_ascii=False, indent=2)

        return {
            "status": "success" if missing_count == 0 else "partial",
            "total_checked": len(products),
            "synced_count": len(results),
            "missing_count": missing_count,
            "max_windows_path_length": max_path_observed,
            "windows_max_path_compliant": max_path_observed < 260,
        }


class CompileFrontendCatalogUseCase:
    """
    Service Métier #2 : Compilation du catalogue JSON en module TypeScript React/Vite
    (`RawGlassRailingCatalog.ts`) et en documentation Markdown.
    """

    def __init__(self, compiler: ICatalogArtifactCompilerPort):
        self._compiler = compiler

    def execute(
        self,
        catalog_json_path: str,
        target_ts_path: str,
        target_md_path: str,
    ) -> Dict[str, Any]:
        with open(catalog_json_path, "r", encoding="utf-8") as f:
            catalog_data = json.load(f)

        ts_out = self._compiler.compile_typescript_module(catalog_data, target_ts_path)
        md_out = self._compiler.compile_markdown_inventory(catalog_data, target_md_path)

        return {
            "status": "success",
            "total_products_compiled": len(catalog_data.get("products", [])),
            "total_vignettes_compiled": len(catalog_data.get("category_vignettes", [])),
            "typescript_module_path": ts_out,
            "markdown_inventory_path": md_out,
        }
