#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
CANAL 3 : CLI (COMMAND LINE INTERFACE) — PDF ASSETS PIPELINE
========================================================================================
Qu'est-ce que le CLI ?
Le CLI (Command Line Interface) est le point d'entrée pour le terminal. Il consomme le
SDK Python `PdfProcessorSDK` et offre une expérience interactive ou automatisée en
ligne de commande avec parsing d'arguments (`--input`, `--output`, `--dpi`).

Utilisation :
  python cli.py --input "mon_document.pdf" --output "output" --dpi 150

Auteur : BatiHome Dev Team
========================================================================================
"""

import sys
import argparse
from pathlib import Path

# Permet d'importer le SDK même si le script est lancé depuis un dossier différent
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from sdk import PdfProcessorSDK


def main():
    parser = argparse.ArgumentParser(
        description="BatiHome PDF Assets Pipeline (CLI) : Découpage, Extraction et Classification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple d'utilisation :
  python cli.py --input "../../documents/catalogue.pdf" --output "output" --dpi 150
        """
    )
    parser.add_argument("--input", "-i", required=True, help="Chemin vers le fichier PDF à traiter")
    parser.add_argument("--output", "-o", default="output", help="Dossier de destination (défaut: output)")
    parser.add_argument("--dpi", "-d", type=int, default=150, help="Résolution en DPI des rendus (défaut: 150)")
    parser.add_argument("--no-classify", action="store_true", help="Désactive le tri automatique des images")

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("🚀 BATIHOME PDF ASSETS PIPELINE — CANAL CLI")
    print("=" * 70)
    print(f"📄 Fichier source : {args.input}")
    print(f"📁 Destination    : {args.output}")
    print(f"🎯 Résolution DPI : {args.dpi}")
    print("-" * 70)

    sdk = PdfProcessorSDK(default_output_dir=args.output, default_dpi=args.dpi)

    try:
        results = sdk.process_pdf(
            pdf_path=args.input,
            output_dir=args.output,
            dpi=args.dpi,
            classify=not args.no_classify
        )
        print("✅ Traitement terminé avec succès !")
        print(f"   • Pages traitées       : {results['total_pages']}")
        print(f"   • Images extraites     : {results['total_images_extracted']}")
        print(f"   • Répartition classée  : {results['classified_counts']}")
        print(f"   • Dossier d'export     : {results['document_dir']}")
        print(f"   • Index manifeste      : {results['manifest_file']}")
        print("=" * 70 + "\n")
    except Exception as e:
        print(f"\n❌ ERREUR lors du traitement : {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
