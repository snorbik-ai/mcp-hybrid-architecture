#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #04 — E-COMMERCE CATALOG SCANNER PIPELINE (CLEAN ARCHITECTURE)
Couche : Core / Domain (Entités Métier & Ports d'Interface)
========================================================================================
Rôle :
Définit les structures de données immuables (Entités et Value Objects) ainsi que les
contrats d'interface (Ports) que la couche Infrastructure doit implémenter et qui sont
injectés par Inversion de Dépendance (DIP) dans les Use Cases (Services Métiers).
========================================================================================
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any, Protocol


@dataclass
class CategoryTargetEntity:
    """Représente une catégorie ou sous-catégorie cible à scanner sur un site e-commerce."""
    folder_key: str
    category_label: str
    url: str


@dataclass
class CategoryVignetteEntity:
    """Représente une vignette visuelle de catégorie extraite du mégamenu ou d'une page hub."""
    title: str
    image_url: str
    source_page_url: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ScannedProductEntity:
    """
    Entité Métier centrale représentant un produit ou accessoire extrait sans API
    depuis le DOM d'un site e-commerce de référence.
    """
    sku: str
    title: str
    category_folder: str
    category_label: str
    categories: List[str] = field(default_factory=list)
    price_raw: str = "Sur devis"
    price_ttc_eur: Optional[float] = None
    price_ht_eur: Optional[float] = None
    unit: str = "unité"
    full_card_text: str = ""
    source_url: str = ""
    image_url: str = ""
    local_image: str = ""
    frontend_public_image: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ======================================================================================
# PORTS D'INTERFACE (INVERSION DE DÉPENDANCE — CLEAN ARCHITECTURE)
# ======================================================================================

class IHttpPageFetcherPort(Protocol):
    """Port technique unique : Récupération du flux HTML brut d'une URL externe sans API."""
    def fetch_html(self, url: str, timeout_sec: int = 25) -> str:
        ...


class IDomCatalogParserPort(Protocol):
    """Port technique unique : Analyse syntaxique du DOM HTML pour extraire catégories et produits."""
    def discover_category_links(self, html: str, base_domain: str, keywords: List[str]) -> List[Dict[str, str]]:
        ...

    def extract_category_vignettes(self, html: str, source_url: str) -> List[CategoryVignetteEntity]:
        ...

    def extract_product_cards(
        self,
        html: str,
        folder_key: str,
        category_label: str,
        base_url: str = "",
    ) -> List[ScannedProductEntity]:
        ...


class ICatalogPersistencePort(Protocol):
    """Port technique unique : Sauvegarde et lecture du catalogue scanné sur le système de fichiers."""
    def save_catalog_json(
        self,
        output_json_path: str,
        source_reference: str,
        vignettes: List[CategoryVignetteEntity],
        products: List[ScannedProductEntity]
    ) -> str:
        ...

    def load_catalog_json(self, json_path: str) -> Dict[str, Any]:
        ...
