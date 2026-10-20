#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #03 : MEDIA QUALITY AUDITOR — INFRASTRUCTURE ADAPTER
Responsabilité Technique Unique : Inspection d'image via Pillow (PIL), calcul d'empreinte
cryptographique MD5 par blocs de 64 Ko et suppression physique sur le système de fichiers.
========================================================================================
"""

import os
import sys
import hashlib
from pathlib import Path
from typing import Tuple
from PIL import Image

current_dir = Path(__file__).resolve().parent
tool_root = current_dir.parent.parent
if str(tool_root) not in sys.path:
    sys.path.insert(0, str(tool_root))

from core.domain.entities_and_ports import IMediaInspectorPort


class PillowMd5InspectorAdapter(IMediaInspectorPort):
    def compute_file_hash(self, filepath: str) -> str:
        hasher = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def inspect_image_metadata(self, filepath: str) -> Tuple[int, int, str, str]:
        with Image.open(filepath) as img:
            w, h = img.size
            img_format = img.format or "UNKNOWN"
            color_mode = img.mode
            return w, h, img_format, color_mode

    def delete_file(self, filepath: str) -> bool:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
