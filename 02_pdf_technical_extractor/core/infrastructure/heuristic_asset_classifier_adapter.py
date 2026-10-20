#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #02 : PDF TECHNICAL EXTRACTOR — INFRASTRUCTURE ADAPTER #1
Responsabilité Technique Unique : Classification géométrique et heuristique des images
extraites (plans_et_schemas, photos_produits, logos_et_icones, autres).
========================================================================================
"""

import sys
from pathlib import Path

current_dir = Path(__file__).resolve().parent
tool_root = current_dir.parent.parent
if str(tool_root) not in sys.path:
    sys.path.insert(0, str(tool_root))

from core.domain.entities_and_ports import IPdfAssetClassifierPort


class HeuristicPdfAssetClassifierAdapter(IPdfAssetClassifierPort):
    def classify_image(self, width: int, height: int, ext: str) -> str:
        ratio = max(width, height) / max(min(width, height), 1)
        if width <= 200 and height <= 200:
            return "logos_et_icones"
        if ratio >= 2.2 and min(width, height) < 250:
            return "logos_et_icones"
        if width >= 500 and height >= 500 and (ext.lower() in ("png", "svg") or ratio >= 1.7):
            return "plans_et_schemas"
        if width >= 300 and height >= 200:
            return "photos_produits"
        return "autres"
