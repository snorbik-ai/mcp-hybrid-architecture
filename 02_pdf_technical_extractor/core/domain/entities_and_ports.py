#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #02 : PDF TECHNICAL EXTRACTOR — COUCHE DOMAIN (ENTITIES & PORTS)
========================================================================================
Définit les entités immuables et les contrats d'interfaces (Ports) pour l'ingestion,
le découpage HD et la classification des catalogues techniques PDF.
========================================================================================
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Any


@dataclass(frozen=True)
class PdfAssetEntity:
    id: str
    page: int
    filename: str
    raw_relative_path: str
    width: int
    height: int
    format: str
    category: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PdfPageEntity:
    page_number: int
    render_relative_path: str
    width: float
    height: float
    has_text: bool
    images_count: int
    images: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class IPdfAssetClassifierPort(ABC):
    @abstractmethod
    def classify_image(self, width: int, height: int, ext: str) -> str:
        pass


class IPdfManifestRepositoryPort(ABC):
    @abstractmethod
    def save_manifest_and_text(self, doc_output_dir: Path, manifest: Dict[str, Any], full_text_md: str) -> Dict[str, str]:
        pass

    @abstractmethod
    def load_manifest(self, document_dir: Path) -> Dict[str, Any]:
        pass

    @abstractmethod
    def load_full_text(self, document_dir: Path) -> str:
        pass
