#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #05 — VISUAL CATALOG SYNC & TYPESCRIPT COMPILER PIPELINE
Module : canal_sdk_cli/cli.py (Canal 3 : Interface en Ligne de Commande)
========================================================================================
"""

import json
import argparse
from sdk import VisualCatalogSyncSDK


def main():
    parser = argparse.ArgumentParser(
        description="CLI — Outil Interne #05 : Visual Catalog Sync & TypeScript Compiler Pipeline"
    )
    parser.add_argument("--sync", action="store_true", help="Vérifie et synchronise toutes les images produits avec protection Windows MAX_PATH")
    parser.add_argument("--compile", action="store_true", help="Compile le JSON en module TypeScript (RawGlassRailingCatalog.ts) et rapport Markdown")
    parser.add_argument("--all", action="store_true", help="Exécute la synchronisation visuelle + la compilation TypeScript/Markdown")
    args = parser.parse_args()

    sdk = VisualCatalogSyncSDK()

    if args.sync or args.all or (not args.sync and not args.compile):
        sync_res = sdk.sync_visual_assets()
        print(json.dumps(sync_res, indent=2, ensure_ascii=False))

    if args.compile or args.all or (not args.sync and not args.compile):
        comp_res = sdk.compile_frontend_catalog()
        print(json.dumps(comp_res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
