#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #03 : MEDIA QUALITY AUDITOR — COUCHE APPLICATION (USE CASES)
========================================================================================
Services Métiers orchestrant l'audit HD, la certification Hero et le dédoublonnage MD5
via Injection de Dépendances (DI).
========================================================================================
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

current_dir = Path(__file__).resolve().parent
tool_root = current_dir.parent.parent
if str(tool_root) not in sys.path:
    sys.path.insert(0, str(tool_root))

from core.domain.entities_and_ports import AuditedMediaEntity, IMediaInspectorPort

SUPPORTED_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")


class AuditMediaDirectoryUseCase:
    def __init__(self, inspector_port: IMediaInspectorPort):
        self._inspector = inspector_port

    def execute(
        self,
        directory_path: str,
        min_width: int = 1200,
        min_height: int = 700
    ) -> Dict[str, Any]:
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Le dossier spécifié n'existe pas : {directory_path}")

        items: List[Dict[str, Any]] = []
        hash_registry: Dict[str, List[str]] = {}
        total_size_bytes = 0

        for root, _, files in os.walk(directory_path):
            for file in sorted(files):
                if not file.lower().endswith(SUPPORTED_EXTENSIONS):
                    continue

                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, directory_path)
                file_size = os.path.getsize(full_path)
                total_size_bytes += file_size

                try:
                    w, h, img_format, color_mode = self._inspector.inspect_image_metadata(full_path)
                except Exception as err:
                    items.append({
                        "filename": file,
                        "rel_path": rel_path,
                        "status": "CORRUPTED",
                        "error": str(err),
                        "width": 0,
                        "height": 0,
                        "size_kb": round(file_size / 1024, 1),
                    })
                    continue

                md5_hash = self._inspector.compute_file_hash(full_path)
                is_duplicate = md5_hash in hash_registry
                if is_duplicate:
                    hash_registry[md5_hash].append(rel_path)
                else:
                    hash_registry[md5_hash] = [rel_path]

                if is_duplicate or " copy" in file:
                    status = "DUPLICATE"
                elif w >= min_width and h >= min_height:
                    status = "VALID_HD"
                else:
                    status = "REJECTED_LOW_RES"

                entity = AuditedMediaEntity(
                    filename=file,
                    rel_path=rel_path,
                    full_path=full_path,
                    width=w,
                    height=h,
                    aspect_ratio=round(w / h, 2) if h > 0 else 0.0,
                    size_kb=round(file_size / 1024, 1),
                    format=img_format,
                    mode=color_mode,
                    md5=md5_hash,
                    status=status,
                    is_hd=(w >= min_width and h >= min_height)
                )
                items.append(entity.to_dict())

        valid_hd_count = sum(1 for i in items if i.get("status") == "VALID_HD")
        rejected_count = sum(1 for i in items if i.get("status") == "REJECTED_LOW_RES")
        duplicate_count = sum(1 for i in items if i.get("status") == "DUPLICATE")

        return {
            "directory": directory_path,
            "thresholds": {"min_width": min_width, "min_height": min_height},
            "summary": {
                "total_images": len(items),
                "valid_hd": valid_hd_count,
                "rejected_low_res": rejected_count,
                "duplicates": duplicate_count,
                "total_size_mb": round(total_size_bytes / (1024 * 1024), 2),
            },
            "items": items,
        }


class CleanDuplicateMediaUseCase:
    def __init__(self, audit_use_case: AuditMediaDirectoryUseCase, inspector_port: IMediaInspectorPort):
        self._audit_uc = audit_use_case
        self._inspector = inspector_port

    def execute(self, directory_path: str, dry_run: bool = True) -> Dict[str, Any]:
        audit = self._audit_uc.execute(directory_path)
        removed_files: List[str] = []

        for item in audit["items"]:
            if item.get("status") == "DUPLICATE" or " copy" in item["filename"]:
                full_path = item["full_path"]
                if not dry_run:
                    self._inspector.delete_file(full_path)
                removed_files.append(item["rel_path"])

        return {
            "dry_run": dry_run,
            "removed_count": len(removed_files),
            "removed_files": removed_files,
        }


class GetCertifiedHeroCandidatesUseCase:
    def __init__(self, audit_use_case: AuditMediaDirectoryUseCase):
        self._audit_uc = audit_use_case

    def execute(self, directory_path: str, min_width: int = 1200, min_height: int = 700) -> List[Dict[str, Any]]:
        audit = self._audit_uc.execute(directory_path, min_width=min_width, min_height=min_height)
        candidates = [
            item for item in audit["items"]
            if item.get("status") == "VALID_HD" and " copy" not in item["filename"]
        ]
        candidates.sort(key=lambda x: (x["width"] * x["height"], x["size_kb"]), reverse=True)
        return candidates
