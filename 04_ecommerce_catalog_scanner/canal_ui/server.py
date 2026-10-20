#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #04 — E-COMMERCE CATALOG SCANNER PIPELINE
Module : canal_ui/server.py (Canal 2 : Mini-Application Web Graphique Locale)
========================================================================================
Rôle :
Micro-serveur HTTP sur le port 5183 servant un Dashboard Web au Design System AXESTEEL
pour explorer, filtrer, rechercher et lancer des scans DOM sur les 133 références du
catalogue e-commerce garde-corps verre.
========================================================================================
"""

import os
import sys
import json
import argparse
import urllib.parse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

CURRENT_DIR = Path(__file__).resolve().parent
SDK_DIR = CURRENT_DIR.parent / "canal_sdk_cli"
WORKSPACE_ROOT = CURRENT_DIR.parent.parent.parent
if str(SDK_DIR) not in sys.path:
    sys.path.insert(0, str(SDK_DIR))

from sdk import EcommerceCatalogScannerSDK

SCANNER_SDK = EcommerceCatalogScannerSDK()


class CatalogScannerUiHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/api/catalog":
            cat = query.get("category", ["all"])[0]
            q = query.get("search", [""])[0]
            custom_file = query.get("file", [None])[0]
            try:
                res = SCANNER_SDK.audit_and_search_catalog(
                    catalog_json_path=custom_file,
                    category_filter=cat,
                    search_query=q or None,
                )
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            except Exception as exc:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(exc)}).encode("utf-8"))
            return

        if path.startswith("/assets/catalogue_verre/"):
            rel_name = os.path.basename(urllib.parse.unquote(path))
            img_file = WORKSPACE_ROOT / "frontend" / "public" / "assets" / "catalogue_verre" / rel_name
            if img_file.exists() and img_file.is_file():
                self.send_response(200)
                ext = img_file.suffix.lower()
                ctype = "image/png" if ext == ".png" else "image/jpeg"
                self.send_header("Content-Type", ctype)
                self.end_headers()
                self.wfile.write(img_file.read_bytes())
                return

        index_file = CURRENT_DIR / "static" / "index.html"
        if index_file.exists():
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(index_file.read_bytes())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/scan_url":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            url = body.get("url")
            if not url:
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Paramètre 'url' obligatoire"}).encode("utf-8"))
                return
            try:
                res = SCANNER_SDK.scan_url(url=url)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            except Exception as exc:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(exc)}).encode("utf-8"))
            return

        if parsed.path == "/api/discover":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            seed_url = body.get("seed_url", "https://www.inoxdesign.fr/systemes-profil-paroi-de-verre.html")
            try:
                res = SCANNER_SDK.discover_categories(seed_url=seed_url)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            except Exception as exc:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(exc)}).encode("utf-8"))


def run(port: int = 5183):
    httpd = HTTPServer(("127.0.0.1", port), CatalogScannerUiHandler)
    print(f"🚀 Dashboard Web E-Commerce Catalog Scanner actif sur http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5183)
    args = parser.parse_args()
    run(args.port)
