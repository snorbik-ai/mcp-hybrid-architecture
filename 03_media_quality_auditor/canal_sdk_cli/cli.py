#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
BatiHome Internal Tool — Media Auditor & Quality Pipeline
Module : canal_sdk_cli/cli.py
===============================================================================
Point d'entrée Terminal / CLI pour auditer les médias, éliminer les doublons
et filtrer les images sous les seuils de résolution (ex: 1200x700).
"""

import sys
import os
import argparse
import json

# Permet d'importer le sdk du même dossier
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sdk import MediaAuditorPipeline

def main():
    parser = argparse.ArgumentParser(
        description="BatiHome CLI — Audit de Qualité Média & Détection de Doublons"
    )
    parser.add_argument(
        "-i", "--input",
        default="frontend/public/images/hero",
        help="Chemin du dossier d'images à analyser (défaut: frontend/public/images/hero)"
    )
    parser.add_argument(
        "--min-width",
        type=int,
        default=1200,
        help="Largeur minimale exigée en pixels (défaut: 1200)"
    )
    parser.add_argument(
        "--min-height",
        type=int,
        default=700,
        help="Hauteur minimale exigée en pixels (défaut: 700)"
    )
    parser.add_argument(
        "--clean-duplicates",
        action="store_true",
        help="Supprimer les doublons (MD5 identique ou suffixe ' copy')"
    )
    parser.add_argument(
        "--candidates",
        action="store_true",
        help="Afficher uniquement les candidats certifiés HD pour le Hero"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Exécution à blanc (n'altère aucun fichier sur le disque)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Sortie au format JSON structuré"
    )

    args = parser.parse_args()

    # Normalisation du chemin
    target_dir = os.path.abspath(args.input)
    if not os.path.exists(target_dir):
        print(f"❌ Erreur : Dossier introuvable : {target_dir}", file=sys.stderr)
        sys.exit(1)

    pipeline = MediaAuditorPipeline(
        default_min_width=args.min_width,
        default_min_height=args.min_height
    )

    if args.clean_duplicates:
        res = pipeline.clean_duplicates(target_dir, dry_run=args.dry_run)
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            mode_str = "[SIMULATION / DRY-RUN]" if args.dry_run else "[ACTION RÉELLE]"
            print(f"🧹 {mode_str} Nettoyage des doublons dans : {args.input}")
            print(f"   Fichiers traités : {res['removed_count']}")
            for f in res["removed_files"]:
                print(f"   - {f}")
        return

    if args.candidates:
        cands = pipeline.get_certified_hero_candidates(target_dir)
        if args.json:
            print(json.dumps(cands, indent=2, ensure_ascii=False))
        else:
            print(f"\n🏆 CANDIDATS CERTIFIÉS HD (Seuil >= {args.min_width}x{args.min_height}) :")
            print(f"{'Fichier':40} | {'Résolution':12} | {'Poids':8} | {'Statut'}")
            print("-" * 75)
            for c in cands:
                print(f"{c['filename']:40} | {c['width']}x{c['height']:<6} | {c['size_kb']} KB | ✅ CERTIFIÉ HD")
            print(f"\nTotal : {len(cands)} images certifiées éligibles.\n")
        return

    # Mode Audit par défaut
    audit = pipeline.audit_directory(target_dir, min_width=args.min_width, min_height=args.min_height)

    if args.json:
        print(json.dumps(audit, indent=2, ensure_ascii=False))
        return

    summary = audit["summary"]
    print("\n" + "=" * 75)
    print(f"📊 RAPPORT D'AUDIT QUALITÉ MÉDIA BATIHOME")
    print(f"📁 Dossier analysé : {audit['directory']}")
    print(f"🎯 Seuils requis    : Largeur >= {args.min_width}px | Hauteur >= {args.min_height}px")
    print("=" * 75)
    print(f"Total images scannées : {summary['total_images']}")
    print(f"✅ Images Valides HD  : {summary['valid_hd']}")
    print(f"⚠️ Rejetées (Trop bas): {summary['rejected_low_res']}")
    print(f"🔄 Doublons détectés  : {summary['duplicates']}")
    print(f"📦 Poids total        : {summary['total_size_mb']} Mo")
    print("-" * 75)
    print(f"{'Statut':16} | {'Résolution':12} | {'Poids':8} | {'Fichier'}")
    print("-" * 75)

    for item in audit["items"]:
        stat = item["status"]
        stat_icon = "✅ VALIDE HD" if stat == "VALID_HD" else ("🔄 DOUBLON" if stat == "DUPLICATE" else "❌ TROP BAS")
        res_str = f"{item['width']}x{item['height']}"
        print(f"{stat_icon:16} | {res_str:12} | {item['size_kb']:>6.1f}KB | {item['filename']}")
    print("=" * 75 + "\n")

if __name__ == "__main__":
    main()
