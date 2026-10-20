#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #05 — VISUAL CATALOG SYNC & TYPESCRIPT COMPILER PIPELINE
Module : canal_sdk_cli/sdk.py (Canal 3 : Façade SDK & Conteneur d'Injection de Dépendances)
========================================================================================
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

TOOL_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = TOOL_ROOT.parent.parent
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

from core.infrastructure.windows_safe_image_harvester import WindowsSafeImageHarvesterAdapter
from core.infrastructure.ts_markdown_compiler import TypeScriptAndMarkdownCompilerAdapter
from core.application.use_cases import (
    SyncVisualAssetsUseCase,
    CompileFrontendCatalogUseCase,
)


class VisualCatalogSyncSDK:
    """
    Conteneur d'Injection de Dépendances (Clean Architecture) et Façade SDK pour l'Outil #05.
    """

    _EMBEDDED_JSON = TOOL_ROOT / "data" / "catalogue_reference.json"
    DEFAULT_JSON = str(_EMBEDDED_JSON if _EMBEDDED_JSON.exists() else (WORKSPACE_ROOT / "base_src" / "matiere_premiere_garde_corps_verre" / "catalogue_complet_garde_corps_verre.json"))
    DEFAULT_RAW_DIR = str((TOOL_ROOT / "data") if _EMBEDDED_JSON.exists() else (WORKSPACE_ROOT / "base_src" / "matiere_premiere_garde_corps_verre"))
    DEFAULT_PUBLIC_DIR = str((TOOL_ROOT / "output" / "public_assets") if _EMBEDDED_JSON.exists() else (WORKSPACE_ROOT / "frontend" / "public" / "assets" / "catalogue_verre"))
    DEFAULT_TS_OUT = str((TOOL_ROOT / "output" / "RawGlassRailingCatalog.ts") if _EMBEDDED_JSON.exists() else (WORKSPACE_ROOT / "frontend" / "src" / "core" / "domain" / "invariants" / "RawGlassRailingCatalog.ts"))
    DEFAULT_MD_OUT = str((TOOL_ROOT / "output" / "CATALOGUE_MATIERE_PREMIERE_GARDE_CORPS_VERRE.md") if _EMBEDDED_JSON.exists() else (WORKSPACE_ROOT / "base_src" / "matiere_premiere_garde_corps_verre" / "CATALOGUE_MATIERE_PREMIERE_GARDE_CORPS_VERRE.md"))

    def __init__(self):
        # 1. Adaptateurs d'Infrastructure (Responsabilité Technique Unique)
        self._image_harvester = WindowsSafeImageHarvesterAdapter()
        self._artifact_compiler = TypeScriptAndMarkdownCompilerAdapter()

        # 2. Injection de Dépendances dans les Services Métiers (Use Cases)
        self.sync_visual_assets_use_case = SyncVisualAssetsUseCase(
            image_harvester=self._image_harvester
        )
        self.compile_frontend_catalog_use_case = CompileFrontendCatalogUseCase(
            compiler=self._artifact_compiler
        )

    def sync_visual_assets(
        self,
        catalog_json_path: Optional[str] = None,
        raw_base_dir: Optional[str] = None,
        public_catalog_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Exécute le Service Métier #1 : Téléchargement, contrôle anti-MAX_PATH et copie publique."""
        return self.sync_visual_assets_use_case.execute(
            catalog_json_path=catalog_json_path or self.DEFAULT_JSON,
            raw_base_dir=raw_base_dir or self.DEFAULT_RAW_DIR,
            public_catalog_dir=public_catalog_dir or self.DEFAULT_PUBLIC_DIR,
        )

    def compile_frontend_catalog(
        self,
        catalog_json_path: Optional[str] = None,
        target_ts_path: Optional[str] = None,
        target_md_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Exécute le Service Métier #2 : Génération TypeScript (.ts) et Markdown (.md)."""
        return self.compile_frontend_catalog_use_case.execute(
            catalog_json_path=catalog_json_path or self.DEFAULT_JSON,
            target_ts_path=target_ts_path or self.DEFAULT_TS_OUT,
            target_md_path=target_md_path or self.DEFAULT_MD_OUT,
        )
