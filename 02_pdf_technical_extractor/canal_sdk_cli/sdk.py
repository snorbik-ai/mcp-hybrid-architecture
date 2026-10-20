#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #02 : PDF TECHNICAL EXTRACTOR — CANAL 3 : SDK (CONTENEUR DI)
========================================================================================
Assemble les adaptateurs d'Infrastructure dans les Use Cases de la couche Application.
========================================================================================
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

current_dir = Path(__file__).resolve().parent
tool_root = current_dir.parent
if str(tool_root) not in sys.path:
    sys.path.insert(0, str(tool_root))

from core.infrastructure.heuristic_asset_classifier_adapter import HeuristicPdfAssetClassifierAdapter
from core.infrastructure.pdf_manifest_repository_adapter import PdfManifestRepositoryAdapter
from core.application.use_cases import (
    ProcessPdfDocumentUseCase,
    GetPdfManifestUseCase,
    GetPdfDocumentTextUseCase
)


class PdfProcessorSDK:
    """
    Conteneur d'Injection de Dépendances & Façade SDK pour 02_pdf_technical_extractor.
    """

    def __init__(
        self,
        default_output_dir: Optional[str] = None,
        default_dpi: int = 150,
        classifier_adapter=None,
        repository_adapter=None
    ):
        self.tool_root = tool_root
        self.default_output_dir = default_output_dir or str(tool_root / "output")
        self.default_dpi = default_dpi

        # Injection de Dépendances (Infrastructure -> Use Cases)
        self._classifier = classifier_adapter or HeuristicPdfAssetClassifierAdapter()
        self._repository = repository_adapter or PdfManifestRepositoryAdapter()

        self._process_uc = ProcessPdfDocumentUseCase(self._classifier, self._repository)
        self._manifest_uc = GetPdfManifestUseCase(self._repository)
        self._text_uc = GetPdfDocumentTextUseCase(self._repository)

    def process_pdf(
        self,
        pdf_path: str,
        output_dir: Optional[str] = None,
        dpi: Optional[int] = None,
        classify: bool = True
    ) -> Dict[str, Any]:
        return self._process_uc.execute(
            pdf_path=pdf_path,
            output_dir=output_dir or self.default_output_dir,
            dpi=dpi or self.default_dpi,
            classify=classify
        )

    def get_manifest(self, document_dir: str) -> Dict[str, Any]:
        return self._manifest_uc.execute(document_dir)

    def get_document_text(self, document_dir: str) -> str:
        return self._text_uc.execute(document_dir)

    @staticmethod
    def _classify_image(width: int, height: int, ext: str) -> str:
        return HeuristicPdfAssetClassifierAdapter().classify_image(width, height, ext)
