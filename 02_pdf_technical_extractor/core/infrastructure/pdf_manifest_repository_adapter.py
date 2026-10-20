#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #02 : PDF TECHNICAL EXTRACTOR — INFRASTRUCTURE ADAPTER #2
Responsabilité Technique Unique : Lecture et écriture atomique de manifest.json et full_text.md.
========================================================================================
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

current_dir = Path(__file__).resolve().parent
tool_root = current_dir.parent.parent
if str(tool_root) not in sys.path:
    sys.path.insert(0, str(tool_root))

from core.domain.entities_and_ports import IPdfManifestRepositoryPort


class PdfManifestRepositoryAdapter(IPdfManifestRepositoryPort):
    def save_manifest_and_text(self, doc_output_dir: Path, manifest: Dict[str, Any], full_text_md: str) -> Dict[str, str]:
        doc_output_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = doc_output_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

        full_text_path = doc_output_dir / "full_text.md"
        full_text_path.write_text(full_text_md, encoding="utf-8")
        return {
            "manifest_file": str(manifest_path),
            "full_text_file": str(full_text_path)
        }

    def load_manifest(self, document_dir: Path) -> Dict[str, Any]:
        manifest_file = Path(document_dir) / "manifest.json"
        if not manifest_file.exists():
            raise FileNotFoundError(f"Manifeste introuvable dans : {document_dir}")
        return json.loads(manifest_file.read_text(encoding="utf-8"))

    def load_full_text(self, document_dir: Path) -> str:
        text_file = Path(document_dir) / "full_text.md"
        if not text_file.exists():
            raise FileNotFoundError(f"Fichier texte introuvable dans : {document_dir}")
        return text_file.read_text(encoding="utf-8")
