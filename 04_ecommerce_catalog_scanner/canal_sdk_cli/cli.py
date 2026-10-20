#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #04 — E-COMMERCE CATALOG SCANNER PIPELINE
Module : canal_sdk_cli/cli.py (Canal 3 : Interface en Ligne de Commande)
========================================================================================
Exemples d'utilisation :
  python outils_internes/ecommerce_catalog_scanner_pipeline/canal_sdk_cli/cli.py --audit
  python outils_internes/ecommerce_catalog_scanner_pipeline/canal_sdk_cli/cli.py --search "IN607"
  python outils_internes/ecommerce_catalog_scanner_pipeline/canal_sdk_cli/cli.py --discover "https://www.inoxdesign.fr/pince-a-verre.html"
  python outils_internes/ecommerce_catalog_scanner_pipeline/canal_sdk_cli/cli.py --scan --limit 3
========================================================================================
"""

import json
import argparse
from sdk import EcommerceCatalogScannerSDK


def main():
    parser = argparse.ArgumentParser(
        description="CLI — Outil Interne #04 : E-Commerce Catalog Scanner Pipeline (Sans API)"
    )
    parser.add_argument("--url", type=str, default=None, help="Scanne n'importe quelle URL de site ou catégorie e-commerce (ex: https://www.railingsdesign.com/12-garde-corps-verre)")
    parser.add_argument("--output", type=str, default=None, help="Chemin personnalisé du fichier JSON de sortie")
    parser.add_argument("--audit", action="store_true", help="Affiche le bilan statistique du catalogue scanné")
    parser.add_argument("--category", type=str, default="all", help="Filtre par famille (ex: 02_profils, 04_pinces, 05_points_spider)")
    parser.add_argument("--search", type=str, default=None, help="Recherche par SKU ou mot-clé (ex: IN607, M042, Spider)")
    parser.add_argument("--discover", type=str, default=None, help="Découvre les liens de catégories sur une URL cible")
    parser.add_argument("--scan", action="store_true", help="Lance un scan DOM en direct des catégories garde-corps verre")
    parser.add_argument("--limit", type=int, default=None, help="Limite le nombre de catégories scannées (pour test rapide)")
    parser.add_argument("--json", action="store_true", help="Sortie brute au format JSON")
    args = parser.parse_args()

    sdk = EcommerceCatalogScannerSDK()

    if args.url:
        res = sdk.scan_url(url=args.url, output_json_path=args.output)
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print("=" * 80)
            print("🚀 SCAN UNIVERSEL TERMINÉ AVEC SUCCÈS")
            print("=" * 80)
            print(f"• URL Cible           : {res.get('source_url')}")
            print(f"• Domaine             : {res.get('base_domain')}")
            print(f"• Libellé Catégorie   : {res.get('category_label')}")
            print(f"• Produits extraits   : {res.get('total_products')} références")
            print(f"• Vignettes extraites : {res.get('total_vignettes')} visuels")
            print(f"• Fichier JSON généré : {res.get('saved_json_path')}")
            print(f"• Rapport Visuel HTML : {res.get('saved_html_report_path')}")
            print(f"• Lien cliquable      : {res.get('html_report_url')}")
            print("-" * 80)
            for p in res.get("products", [])[:10]:
                print(f"  • [{p['sku']}] {p['title']} | {p['price_raw']} (TTC: {p['price_ttc_eur']} € / HT: {p['price_ht_eur']} €)")
        return

    if args.discover:
        res = sdk.discover_categories(seed_url=args.discover)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return

    if args.scan:
        res = sdk.scan_glass_railing_catalog(limit_categories=args.limit)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return

    # Par défaut : Audit ou Recherche dans le catalogue
    res = sdk.audit_and_search_catalog(
        category_filter=args.category,
        search_query=args.search,
    )
    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("=" * 80)
        print("🔍 BILAN DU CATALOGUE E-COMMERCE GARDE-CORPS VERRE & ACCESSOIRES")
        print("=" * 80)
        print(f"• Fichier source      : {res['catalog_json_path']}")
        print(f"• Total références    : {res['total_products']} produits & accessoires")
        print(f"• Vignettes catégories: {res['total_vignettes']} vignettes")
        print(f"• Résultats filtrés   : {res['filtered_count']} références")
        print("-" * 80)
        for fam in res["families_breakdown"]:
            pmin = f"{fam['min_price_ttc']:.2f} €" if fam["min_price_ttc"] else "N/A"
            pmax = f"{fam['max_price_ttc']:.2f} €" if fam["max_price_ttc"] else "N/A"
            print(f"  [{fam['folder']}] : {fam['count']} réf. (Prix TTC : de {pmin} à {pmax})")
        if args.search:
            print("-" * 80)
            for item in res["products"][:15]:
                print(f"  • {item['sku']} | {item['title']} | {item['price_raw']} ({item['unit']})")


if __name__ == "__main__":
    main()
