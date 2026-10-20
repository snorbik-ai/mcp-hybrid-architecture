#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #04 — E-COMMERCE CATALOG SCANNER PIPELINE (CLEAN ARCHITECTURE)
Couche : Core / Application (Use Cases / Services Métiers assemblés par Injection)
========================================================================================
Rôle :
Chaque Use Case (Service Métier) orchestre une fonctionnalité métier complète en
utilisant exclusivement les Ports d'Interface injectés dans son constructeur
(Inversion de Dépendance — Clean Architecture).
========================================================================================
"""

import os
from typing import List, Dict, Any, Optional
from ..domain.entities_and_ports import (
    CategoryTargetEntity,
    CategoryVignetteEntity,
    ScannedProductEntity,
    IHttpPageFetcherPort,
    IDomCatalogParserPort,
    ICatalogPersistencePort,
)


class DiscoverCategoryTreeUseCase:
    """
    Service Métier #1 : Découverte automatique des catégories et sous-catégories
    sur un site e-commerce externe sans API.
    """

    def __init__(
        self,
        page_fetcher: IHttpPageFetcherPort,
        dom_parser: IDomCatalogParserPort,
    ):
        self._page_fetcher = page_fetcher
        self._dom_parser = dom_parser

    def execute(
        self,
        seed_url: str,
        base_domain: str = "www.inoxdesign.fr",
        keywords: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Scanne une page racine et extrait tous les liens de catégories pertinents."""
        target_keywords = keywords or [
            "verre", "profil", "pince", "point", "entretoise", "spider", "main-courante", "piscine"
        ]
        html = self._page_fetcher.fetch_html(seed_url)
        links = self._dom_parser.discover_category_links(html, base_domain, target_keywords)
        vignettes = self._dom_parser.extract_category_vignettes(html, seed_url)
        return {
            "status": "success",
            "seed_url": seed_url,
            "discovered_links_count": len(links),
            "discovered_links": links,
            "vignettes_count": len(vignettes),
            "vignettes": [v.to_dict() for v in vignettes],
        }


class ScanEcommerceCatalogUseCase:
    """
    Service Métier #2 : Scan multi-catégories d'un catalogue e-commerce sans API,
    extraction des cartes produits (SKU, Titre, Prix TTC/HT, Unité, Image URL),
    fusion dédoublonnée et persistance JSON.
    """

    def __init__(
        self,
        page_fetcher: IHttpPageFetcherPort,
        dom_parser: IDomCatalogParserPort,
        catalog_repo: ICatalogPersistencePort,
    ):
        self._page_fetcher = page_fetcher
        self._dom_parser = dom_parser
        self._catalog_repo = catalog_repo

    def execute(
        self,
        targets: List[CategoryTargetEntity],
        output_json_path: str,
        source_reference: str = "https://www.inoxdesign.fr/garde-corps-verre/",
    ) -> Dict[str, Any]:
        merged_products: Dict[str, ScannedProductEntity] = {}
        vignettes: List[CategoryVignetteEntity] = []
        scanned_urls: List[str] = []
        errors: List[str] = []

        for target in targets:
            try:
                html = self._page_fetcher.fetch_html(target.url)
                scanned_urls.append(target.url)

                if not vignettes:
                    vignettes = self._dom_parser.extract_category_vignettes(html, target.url)

                cards = self._dom_parser.extract_product_cards(
                    html=html,
                    folder_key=target.folder_key,
                    category_label=target.category_label,
                    base_url=target.url,
                )

                for card in cards:
                    key = card.source_url or card.sku
                    if key not in merged_products:
                        merged_products[key] = card
                    else:
                        existing = merged_products[key]
                        if target.category_label not in existing.categories:
                            existing.categories.append(target.category_label)
                        if card.price_ttc_eur and not existing.price_ttc_eur:
                            existing.price_raw = card.price_raw
                            existing.price_ttc_eur = card.price_ttc_eur
                            existing.price_ht_eur = card.price_ht_eur
            except Exception as exc:
                errors.append(f"{target.url}: {str(exc)}")

        products_list = list(merged_products.values())
        actual_source = source_reference or (targets[0].url if targets else "https://www.inoxdesign.fr/garde-corps-verre/")
        saved_path = self._catalog_repo.save_catalog_json(
            output_json_path=output_json_path,
            source_reference=actual_source,
            vignettes=vignettes,
            products=products_list,
        )

        # Génération du Rapport HTML Interactif Autonome avec Panneau d'Aperçu Photo
        saved_html_path = None
        try:
            from ..infrastructure.html_catalog_report import HtmlCatalogReportAdapter
            html_dest = os.path.splitext(output_json_path)[0] + "_visualisation.html"
            saved_html_path = HtmlCatalogReportAdapter.generate_html_report(
                output_html_path=html_dest,
                catalog_json_rel_path=os.path.basename(output_json_path),
                source_reference=actual_source,
                vignettes=[v.to_dict() for v in vignettes],
                products=[p.to_dict() for p in products_list],
            )
        except Exception as html_err:
            errors.append(f"Erreur génération rapport HTML : {str(html_err)}")

        return {
            "status": "success" if products_list else "empty",
            "scanned_categories_count": len(scanned_urls),
            "total_unique_products": len(products_list),
            "total_vignettes": len(vignettes),
            "saved_json_path": saved_path,
            "saved_html_report_path": saved_html_path,
            "html_report_url": f"file:///{saved_html_path.replace(os.sep, '/')}" if saved_html_path else None,
            "errors": errors,
        }


class ScanUniversalUrlUseCase:
    """
    Service Métier #4 : Scan universel à chaud de n'importe quel site ou URL e-commerce
    (PrestaShop, Shopify, WooCommerce, Magento ou site sur mesure).
    Inversion de dépendance complète : déduit le domaine, extrait les cartes DOM,
    génère le catalogue JSON dédié et le rapport visuel HTML autonome.
    """

    def __init__(
        self,
        page_fetcher: IHttpPageFetcherPort,
        dom_parser: IDomCatalogParserPort,
        catalog_repo: ICatalogPersistencePort,
    ):
        self._page_fetcher = page_fetcher
        self._dom_parser = dom_parser
        self._catalog_repo = catalog_repo

    def execute(
        self,
        url: str,
        output_json_path: Optional[str] = None,
        folder_key: Optional[str] = None,
        category_label: Optional[str] = None,
    ) -> Dict[str, Any]:
        from urllib.parse import urlparse
        from pathlib import Path
        import re

        parsed = urlparse(url)
        base_domain = parsed.netloc or "site_inconnu"
        raw_slug = os.path.basename(parsed.path.rstrip("/")).replace(".html", "").replace(".php", "") or "catalogue"
        
        target_folder = folder_key or re.sub(r"[^a-zA-Z0-9_]", "_", raw_slug.lower())[:30] or "custom_category"
        target_label = category_label or raw_slug.replace("-", " ").replace("_", " ").title()

        merged_products: Dict[str, ScannedProductEntity] = {}
        vignettes: List[CategoryVignetteEntity] = []
        errors: List[str] = []

        try:
            html = self._page_fetcher.fetch_html(url)
            vignettes = self._dom_parser.extract_category_vignettes(html, url)
            cards = self._dom_parser.extract_product_cards(
                html=html,
                folder_key=target_folder,
                category_label=target_label,
                base_url=url,
            )
            for card in cards:
                key = f"{card.source_url}_{card.sku}" if card.sku else (card.source_url or "PROD")
                if key not in merged_products:
                    merged_products[key] = card
                else:
                    existing = merged_products[key]
                    if target_label not in existing.categories:
                        existing.categories.append(target_label)
                    if card.price_ttc_eur and not existing.price_ttc_eur:
                        existing.price_raw = card.price_raw
                        existing.price_ttc_eur = card.price_ttc_eur
                        existing.price_ht_eur = card.price_ht_eur
        except Exception as exc:
            errors.append(f"{url}: {str(exc)}")

        products_list = list(merged_products.values())
        
        # Détermination du fichier de sortie : strictement confiné à l'intérieur du projet autonome de l'outil 04
        if not output_json_path:
            tool_root = Path(__file__).resolve().parent.parent.parent
            out_dir = tool_root / "output"
            out_dir.mkdir(parents=True, exist_ok=True)
            clean_domain = re.sub(r"^www\.", "", base_domain)
            clean_host = re.sub(r"[^a-zA-Z0-9]", "_", clean_domain)[:25].strip("_")
            clean_folder = target_folder[:30].strip("_")
            dest_json = str(out_dir / f"scan_{clean_host}_{clean_folder}.json")
        else:
            dest_json = output_json_path

        saved_path = self._catalog_repo.save_catalog_json(
            output_json_path=dest_json,
            source_reference=url,
            vignettes=vignettes,
            products=products_list,
        )

        saved_html_path = None
        try:
            from ..infrastructure.html_catalog_report import HtmlCatalogReportAdapter
            html_dest = os.path.splitext(dest_json)[0] + "_view.html"
            saved_html_path = HtmlCatalogReportAdapter.generate_html_report(
                output_html_path=html_dest,
                catalog_json_rel_path=os.path.basename(dest_json),
                source_reference=url,
                vignettes=[v.to_dict() for v in vignettes],
                products=[p.to_dict() for p in products_list],
            )
        except Exception as html_err:
            errors.append(f"Erreur rapport HTML: {html_err}")

        return {
            "status": "success" if products_list else "empty",
            "source_url": url,
            "base_domain": base_domain,
            "folder_key": target_folder,
            "category_label": target_label,
            "total_products": len(products_list),
            "total_vignettes": len(vignettes),
            "products": [p.to_dict() for p in products_list],
            "vignettes": [v.to_dict() for v in vignettes],
            "saved_json_path": str(saved_path),
            "saved_html_report_path": str(saved_html_path) if saved_html_path else None,
            "html_report_url": f"file:///{saved_html_path.replace(os.sep, '/')}" if saved_html_path else None,
            "errors": errors,
        }


class AuditScannedCatalogUseCase:
    """
    Service Métier #3 : Analyse statistique, filtrage et recherche sur un catalogue
    scanné (couverture par famille, fourchettes de prix HT/TTC, recherche SKU).
    """

    def __init__(self, catalog_repo: ICatalogPersistencePort):
        self._catalog_repo = catalog_repo

    def execute(
        self,
        catalog_json_path: str,
        category_filter: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> Dict[str, Any]:
        data = self._catalog_repo.load_catalog_json(catalog_json_path)
        products = data.get("products", [])
        vignettes = data.get("category_vignettes", [])

        # Calcul des statistiques par dossier de catégorie
        by_folder: Dict[str, Dict[str, Any]] = {}
        for p in products:
            folder = p.get("category_folder", "unknown")
            if folder not in by_folder:
                by_folder[folder] = {
                    "folder": folder,
                    "count": 0,
                    "priced_count": 0,
                    "min_price_ttc": None,
                    "max_price_ttc": None,
                }
            stats = by_folder[folder]
            stats["count"] += 1
            price = p.get("price_ttc_eur")
            if isinstance(price, (int, float)) and price > 0:
                stats["priced_count"] += 1
                if stats["min_price_ttc"] is None or price < stats["min_price_ttc"]:
                    stats["min_price_ttc"] = price
                if stats["max_price_ttc"] is None or price > stats["max_price_ttc"]:
                    stats["max_price_ttc"] = price

        # Filtrage optionnel
        filtered = products
        if category_filter and category_filter != "all":
            filtered = [p for p in filtered if p.get("category_folder") == category_filter]
        if search_query:
            q = search_query.strip().lower()
            filtered = [
                p for p in filtered
                if q in p.get("sku", "").lower()
                or q in p.get("title", "").lower()
                or any(q in c.lower() for c in p.get("categories", []))
            ]

        return {
            "status": "success",
            "catalog_json_path": catalog_json_path,
            "total_products": len(products),
            "total_vignettes": len(vignettes),
            "filtered_count": len(filtered),
            "families_breakdown": list(by_folder.values()),
            "products": filtered,
            "category_vignettes": vignettes,
        }
