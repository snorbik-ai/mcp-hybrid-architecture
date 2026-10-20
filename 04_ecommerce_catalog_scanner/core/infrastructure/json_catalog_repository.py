#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #04 — E-COMMERCE CATALOG SCANNER PIPELINE (CLEAN ARCHITECTURE)
Couche : Core / Infrastructure (Adaptateur Persistance JSON)
========================================================================================
Rôle :
Implémente le port ICatalogPersistencePort pour lire et sauvegarder les résultats de
scan du catalogue e-commerce au format JSON structuré.
========================================================================================
"""

import os
import json
from typing import List, Dict, Any
from ..domain.entities_and_ports import (
    ICatalogPersistencePort,
    CategoryVignetteEntity,
    ScannedProductEntity,
)


class JsonCatalogRepositoryAdapter(ICatalogPersistencePort):
    """Adaptateur technique de persistance JSON sur système de fichiers."""

    def save_catalog_json(
        self,
        output_json_path: str,
        source_reference: str,
        vignettes: List[CategoryVignetteEntity],
        products: List[ScannedProductEntity]
    ) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(output_json_path)), exist_ok=True)
        payload = {
            "source_reference": source_reference,
            "total_products": len(products),
            "total_vignettes": len(vignettes),
            "category_vignettes": [v.to_dict() for v in vignettes],
            "products": [p.to_dict() for p in products],
        }
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return os.path.abspath(output_json_path)

    def load_catalog_json(self, json_path: str) -> Dict[str, Any]:
        abs_path = os.path.abspath(json_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Fichier catalogue JSON introuvable : {abs_path}")
        with open(abs_path, "r", encoding="utf-8") as f:
            return json.load(f)
