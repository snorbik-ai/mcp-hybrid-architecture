#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #05 — VISUAL CATALOG SYNC & TYPESCRIPT COMPILER PIPELINE (CLEAN ARCH)
Couche : Core / Domain (Entités Métier & Ports d'Interface)
========================================================================================
Rôle :
Définit les entités et contrats d'interface (Ports) pour :
1. Le téléchargement idempotent des médias produits/accessoires avec protection contre
   la limite Windows MAX_PATH (260 caractères).
2. La synchronisation vers le dossier public du Frontend React (`public/assets/...`).
3. La compilation automatique du catalogue JSON en module TypeScript fortement typé
   (`RawGlassRailingCatalog.ts`) et en rapport Markdown (`CATALOGUE_MATIERE_PREMIERE.md`).
========================================================================================
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Protocol


@dataclass
class VisualSyncItemResult:
    """Résultat de synchronisation d'une image produit ou accessoire."""
    sku: str
    image_url: str
    local_raw_path: str
    public_frontend_url: str
    path_length_chars: int
    status: str  # CACHED, DOWNLOADED, FAILED

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class IBinaryImageHarvesterPort(Protocol):
    """Port technique unique : Téléchargement binaire d'image et normalisation anti-MAX_PATH."""
    def sanitize_short_filename(self, raw_filename: str, max_base_len: int = 38) -> str:
        ...

    def download_or_reuse_image(
        self,
        image_url: str,
        raw_dest_folder: str,
        public_dest_folder: str,
    ) -> Optional[str]:
        ...


class ICatalogArtifactCompilerPort(Protocol):
    """Port technique unique : Génération des fichiers TypeScript (.ts) et Markdown (.md)."""
    def compile_typescript_module(
        self,
        catalog_data: Dict[str, Any],
        target_ts_path: str,
    ) -> str:
        ...

    def compile_markdown_inventory(
        self,
        catalog_data: Dict[str, Any],
        target_md_path: str,
    ) -> str:
        ...
