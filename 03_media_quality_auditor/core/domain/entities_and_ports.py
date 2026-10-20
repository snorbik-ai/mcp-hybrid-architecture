#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #03 : MEDIA QUALITY AUDITOR — COUCHE DOMAIN (ENTITIES & PORTS)
========================================================================================
Définit les entités immuables et les contrats d'interfaces (Ports) pour l'audit HD,
la certification Hero et le dédoublonnage cryptographique MD5.
========================================================================================
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Dict, Any, Tuple


@dataclass(frozen=True)
class AuditedMediaEntity:
    filename: str
    rel_path: str
    full_path: str
    width: int
    height: int
    aspect_ratio: float
    size_kb: float
    format: str
    mode: str
    md5: str
    status: str
    is_hd: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class IMediaInspectorPort(ABC):
    @abstractmethod
    def compute_file_hash(self, filepath: str) -> str:
        pass

    @abstractmethod
    def inspect_image_metadata(self, filepath: str) -> Tuple[int, int, str, str]:
        pass

    @abstractmethod
    def delete_file(self, filepath: str) -> bool:
        pass
