#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #04 — E-COMMERCE CATALOG SCANNER PIPELINE
Module : canal_sdk_cli/sdk.py (Canal 3 : Façade SDK & Conteneur d'Injection de Dépendances)
========================================================================================
Rôle :
Assemble par Injection de Dépendances (Clean Architecture) les adaptateurs techniques
de la couche Infrastructure (UrllibPageFetcherAdapter, Bs4DomCatalogParserAdapter,
JsonCatalogRepositoryAdapter) dans les Services Métiers (Use Cases) de la couche
Application, et expose une API Python simple pour la CLI, le serveur Web UI et les
serveurs MCP.
========================================================================================
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Ajout du dossier racine de l'outil au path pour l'import du Core Clean Architecture
TOOL_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = TOOL_ROOT.parent.parent
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

from core.domain.entities_and_ports import CategoryTargetEntity
from core.infrastructure.urllib_page_fetcher import UrllibPageFetcherAdapter
from core.infrastructure.bs4_dom_catalog_parser import Bs4DomCatalogParserAdapter
from core.infrastructure.json_catalog_repository import JsonCatalogRepositoryAdapter
from core.application.use_cases import (
    DiscoverCategoryTreeUseCase,
    ScanEcommerceCatalogUseCase,
    AuditScannedCatalogUseCase,
    ScanUniversalUrlUseCase,
)


DEFAULT_GLASS_RAILING_TARGETS: List[CategoryTargetEntity] = [
    CategoryTargetEntity("01_kits", "Garde-Corps Verre Complets & Kits", "https://www.inoxdesign.fr/garde-corps/verre.html"),
    CategoryTargetEntity("01_kits", "Garde-Corps Verre sur Profilé", "https://www.inoxdesign.fr/garde-corps/profile.html"),
    CategoryTargetEntity("01_kits", "Barrière Piscine Verre NF P90-306", "https://www.inoxdesign.fr/garde-corps/barriere-piscine.html"),
    CategoryTargetEntity("02_profils", "Tous Systèmes Profils Paroi de Verre", "https://www.inoxdesign.fr/systemes-profil-paroi-de-verre.html"),
    CategoryTargetEntity("02_profils", "Profilé Alu en U Pose au Sol", "https://www.inoxdesign.fr/systemes-profil-paroi-de-verre/profile-alu-en-u-pose-au-sol-pour-garde-corps-en-verre.html"),
    CategoryTargetEntity("02_profils", "Profilé Alu en F Pose au Sol", "https://www.inoxdesign.fr/systemes-profil-paroi-de-verre/profile-alu-en-f-pose-au-sol-pour-garde-corps-verre-terrasse.html"),
    CategoryTargetEntity("02_profils", "Profilé Alu en U Pose en Applique (Anglaise)", "https://www.inoxdesign.fr/systemes-profil-paroi-de-verre/profile-alu-en-u-pose-lateral-pour-garde-corps-verre-en-applique.html"),
    CategoryTargetEntity("02_profils", "Profilé Alu en Y Pose en Applique", "https://www.inoxdesign.fr/systemes-profil-paroi-de-verre/profile-alu-en-y-pose-en-applique.html"),
    CategoryTargetEntity("02_profils", "Profilé Alu en U Encastré Dalle Béton", "https://www.inoxdesign.fr/systemes-profil-paroi-de-verre/profile-alu-en-u-pour-garde-corps-encastre-dalle-beton.html"),
    CategoryTargetEntity("02_profils", "Profil de Sol Pose sur Muret / Acrotère", "https://www.inoxdesign.fr/systemes-profil-paroi-de-verre/profil-de-sol-pose-sur-muret.html"),
    CategoryTargetEntity("03_accessoires", "Accessoires pour Profils Garde-Corps Verre", "https://www.inoxdesign.fr/systemes-profil-paroi-de-verre/accessoires-pour-profils-garde-corps.html"),
    CategoryTargetEntity("04_pinces", "Pinces à Verre de Sol Inox 316", "https://www.inoxdesign.fr/pince-a-verre/pince-a-verre-de-sol.html"),
    CategoryTargetEntity("04_pinces", "Pinces à Verre Fixation sur Plat", "https://www.inoxdesign.fr/pince-a-verre/fixation-sur-plat.html"),
    CategoryTargetEntity("04_pinces", "Pinces à Verre sur Tube Ø33,7 mm", "https://www.inoxdesign.fr/pince-a-verre/fixation-sur-tube-33.html"),
    CategoryTargetEntity("04_pinces", "Pinces à Verre sur Tube Ø42,4 mm", "https://www.inoxdesign.fr/pince-a-verre/fixation-sur-tube-42.html"),
    CategoryTargetEntity("04_pinces", "Pinces à Verre sur Tube Ø48,3 et Ø60 mm", "https://www.inoxdesign.fr/pince-a-verre/pince-verre-pour-tube-48-3mm-et-60mm.html"),
    CategoryTargetEntity("04_pinces", "Pinces à Verre d'Angle 90° Verre/Verre", "https://www.inoxdesign.fr/pince-a-verre/pince-a-verre-d-angle.html"),
    CategoryTargetEntity("04_pinces", "Pinces à Verre Murales", "https://www.inoxdesign.fr/pince-a-verre/pince-a-verre-murale.html"),
    CategoryTargetEntity("05_points_spider", "Points de Fixation Verre, Entretoises & Spider", "https://www.inoxdesign.fr/pince-a-verre/points-de-fixation-garde-corps-verre.html"),
    CategoryTargetEntity("06_verres", "Panneaux Verre Garde-Corps Sur Mesure", "https://www.inoxdesign.fr/pince-a-verre/panneaux-verre-garde-corps.html"),
    CategoryTargetEntity("06_verres", "Verre Feuilleté Trempé HST Clair Sur Mesure", "https://www.inoxdesign.fr/systemes-profil-paroi-de-verre/verre-sur-mesure.html"),
    CategoryTargetEntity("06_verres", "Verre Feuilleté Trempé HST Extra-Clair Sur Mesure", "https://www.inoxdesign.fr/systemes-profil-paroi-de-verre/verre-feuillete-extra-clair-hst.html"),
]


class EcommerceCatalogScannerSDK:
    """
    Conteneur d'Injection de Dépendances et Façade SDK pour l'Outil Interne #04.
    """

    DEFAULT_CATALOG_JSON = str(
        (TOOL_ROOT / "data" / "catalogue_reference.json")
        if (TOOL_ROOT / "data" / "catalogue_reference.json").exists()
        else (WORKSPACE_ROOT / "base_src" / "matiere_premiere_garde_corps_verre" / "catalogue_complet_garde_corps_verre.json")
    )

    def __init__(self):
        # 1. Instanciation des adaptateurs d'Infrastructure (Responsabilité Technique Unique)
        self._page_fetcher = UrllibPageFetcherAdapter()
        self._dom_parser = Bs4DomCatalogParserAdapter()
        self._catalog_repo = JsonCatalogRepositoryAdapter()

        # 2. Injection des dépendances dans les Services Métiers (Use Cases Application)
        self.discover_categories_use_case = DiscoverCategoryTreeUseCase(
            page_fetcher=self._page_fetcher,
            dom_parser=self._dom_parser,
        )
        self.scan_catalog_use_case = ScanEcommerceCatalogUseCase(
            page_fetcher=self._page_fetcher,
            dom_parser=self._dom_parser,
            catalog_repo=self._catalog_repo,
        )
        self.audit_catalog_use_case = AuditScannedCatalogUseCase(
            catalog_repo=self._catalog_repo,
        )
        self.scan_universal_url_use_case = ScanUniversalUrlUseCase(
            page_fetcher=self._page_fetcher,
            dom_parser=self._dom_parser,
            catalog_repo=self._catalog_repo,
        )

    def scan_url(
        self,
        url: str,
        output_json_path: Optional[str] = None,
        folder_key: Optional[str] = None,
        category_label: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Scanne n'importe quelle URL de site ou de catégorie e-commerce universelle."""
        return self.scan_universal_url_use_case.execute(
            url=url,
            output_json_path=output_json_path,
            folder_key=folder_key,
            category_label=category_label,
        )

    def discover_categories(
        self,
        seed_url: str = "https://www.inoxdesign.fr/systemes-profil-paroi-de-verre.html",
        keywords: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Exécute le Service Métier #1 : Découverte d'arborescence e-commerce sans API (tout domaine)."""
        from urllib.parse import urlparse
        base_domain = urlparse(seed_url).netloc or "www.inoxdesign.fr"
        return self.discover_categories_use_case.execute(
            seed_url=seed_url, base_domain=base_domain, keywords=keywords
        )

    def scan_custom_catalog(
        self,
        targets: List[CategoryTargetEntity],
        output_json_path: Optional[str] = None,
        source_reference: str = "custom_ecommerce_source",
    ) -> Dict[str, Any]:
        """Exécute le Service Métier #2 sur n'importe quel site ou liste de catégories e-commerce universelle."""
        dest_json = output_json_path or self.DEFAULT_CATALOG_JSON
        return self.scan_catalog_use_case.execute(
            targets=targets,
            output_json_path=dest_json,
            source_reference=source_reference,
        )

    def scan_glass_railing_catalog(
        self,
        output_json_path: Optional[str] = None,
        limit_categories: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Exécute le Service Métier #2 : Scan complet ou partiel des catégories garde-corps verre."""
        targets = DEFAULT_GLASS_RAILING_TARGETS
        if limit_categories and limit_categories > 0:
            targets = targets[:limit_categories]
        return self.scan_custom_catalog(
            targets=targets,
            output_json_path=output_json_path,
            source_reference="https://www.inoxdesign.fr/garde-corps-verre/",
        )

    def audit_and_search_catalog(
        self,
        catalog_json_path: Optional[str] = None,
        category_filter: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Exécute le Service Métier #3 : Audit statistique et recherche SKU/Prix sur le catalogue JSON."""
        target_json = catalog_json_path or self.DEFAULT_CATALOG_JSON
        return self.audit_catalog_use_case.execute(
            catalog_json_path=target_json,
            category_filter=category_filter,
            search_query=search_query,
        )
