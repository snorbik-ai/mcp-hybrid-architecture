#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #03 : MEDIA QUALITY AUDITOR — CANAL 3 : SDK (CONTENEUR DI)
========================================================================================
Assemble l'adaptateur d'Infrastructure Pillow/MD5 dans les Use Cases de la couche Application.
========================================================================================
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

current_dir = Path(__file__).resolve().parent
tool_root = current_dir.parent
if str(tool_root) not in sys.path:
    sys.path.insert(0, str(tool_root))

from core.infrastructure.pillow_md5_inspector_adapter import PillowMd5InspectorAdapter
from core.application.use_cases import (
    AuditMediaDirectoryUseCase,
    CleanDuplicateMediaUseCase,
    GetCertifiedHeroCandidatesUseCase
)


class MediaAuditorPipeline:
    """
    Conteneur d'Injection de Dépendances & Façade SDK pour 03_media_quality_auditor.
    """

    def __init__(self, default_min_width: int = 1200, default_min_height: int = 700, inspector_adapter=None):
        self.default_min_width = default_min_width
        self.default_min_height = default_min_height

        self._inspector = inspector_adapter or PillowMd5InspectorAdapter()
        self._audit_uc = AuditMediaDirectoryUseCase(self._inspector)
        self._clean_uc = CleanDuplicateMediaUseCase(self._audit_uc, self._inspector)
        self._candidates_uc = GetCertifiedHeroCandidatesUseCase(self._audit_uc)

    @staticmethod
    def compute_file_hash(filepath: str) -> str:
        return PillowMd5InspectorAdapter().compute_file_hash(filepath)

    def audit_directory(
        self,
        directory_path: str,
        min_width: Optional[int] = None,
        min_height: Optional[int] = None,
    ) -> Dict[str, Any]:
        return self._audit_uc.execute(
            directory_path=directory_path,
            min_width=min_width if min_width is not None else self.default_min_width,
            min_height=min_height if min_height is not None else self.default_min_height
        )

    def clean_duplicates(self, directory_path: str, dry_run: bool = True) -> Dict[str, Any]:
        return self._clean_uc.execute(directory_path=directory_path, dry_run=dry_run)

    def get_certified_hero_candidates(self, directory_path: str) -> List[Dict[str, Any]]:
        return self._candidates_uc.execute(
            directory_path=directory_path,
            min_width=self.default_min_width,
            min_height=self.default_min_height
        )
