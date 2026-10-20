#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #05 — VISUAL CATALOG SYNC & TYPESCRIPT COMPILER PIPELINE (CLEAN ARCH)
Couche : Core / Infrastructure (Adaptateur Téléchargement Binaire & Anti-MAX_PATH)
========================================================================================
Rôle :
Implémente le port IBinaryImageHarvesterPort avec responsabilité technique unique :
sanitiser et tronquer intelligemment les noms de fichiers pour ne jamais dépasser la
limite Windows MAX_PATH (260 caractères), télécharger l'image si absente, et la copier
dans le répertoire public du Frontend React.
========================================================================================
"""

import os
import re
import shutil
import urllib.request
from urllib.parse import urlparse
from typing import Optional
from ..domain.entities_and_ports import IBinaryImageHarvesterPort


class WindowsSafeImageHarvesterAdapter(IBinaryImageHarvesterPort):
    """Adaptateur de téléchargement d'images idempotent et compatible Windows MAX_PATH."""

    HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    def sanitize_short_filename(self, raw_filename: str, max_base_len: int = 38) -> str:
        base, ext = os.path.splitext(raw_filename)
        clean_base = re.sub(r"[^a-zA-Z0-9_-]", "_", base)[:max_base_len]
        return clean_base + ext.lower()

    def download_or_reuse_image(
        self,
        image_url: str,
        raw_dest_folder: str,
        public_dest_folder: str,
    ) -> Optional[str]:
        if not image_url or not image_url.startswith("http"):
            return None

        os.makedirs(raw_dest_folder, exist_ok=True)
        os.makedirs(public_dest_folder, exist_ok=True)

        parsed = urlparse(image_url)
        base_name = os.path.basename(parsed.path)
        if not base_name:
            return None

        fname = self.sanitize_short_filename(base_name)
        raw_dest_path = os.path.join(raw_dest_folder, fname)
        pub_dest_path = os.path.join(public_dest_folder, fname)

        # 1. Si déjà présent dans public_dest_folder mais pas dans raw_dest_folder, copie locale
        if os.path.exists(pub_dest_path) and not os.path.exists(raw_dest_path):
            shutil.copy2(pub_dest_path, raw_dest_path)

        # 2. Téléchargement distant uniquement si absent sur disque (Idempotence)
        if not os.path.exists(raw_dest_path):
            req = urllib.request.Request(image_url, headers=self.HEADERS)
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
            with open(raw_dest_path, "wb") as f:
                f.write(data)

        # 3. Synchronisation vers le répertoire public Frontend
        if os.path.exists(raw_dest_path) and not os.path.exists(pub_dest_path):
            shutil.copy2(raw_dest_path, pub_dest_path)

        return raw_dest_path
