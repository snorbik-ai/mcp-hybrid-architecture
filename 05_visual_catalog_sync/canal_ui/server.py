#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #05 — VISUAL CATALOG SYNC & TYPESCRIPT COMPILER PIPELINE
Module : canal_ui/server.py (Canal 2 : Mini-Application Web Graphique sur port 5184)
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

from sdk import VisualCatalogSyncSDK

SYNC_SDK = VisualCatalogSyncSDK()


class VisualCatalogSyncUiHandler(BaseHTTPRequestHandler):
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

        if path == "/api/status":
            try:
                res = SYNC_SDK.sync_visual_assets()
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
        if parsed.path == "/api/compile":
            try:
                res = SYNC_SDK.compile_frontend_catalog()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            except Exception as exc:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(exc)}).encode("utf-8"))


def run(port: int = 5184):
    httpd = HTTPServer(("127.0.0.1", port), VisualCatalogSyncUiHandler)
    print(f"🚀 Dashboard Web Visual Catalog Sync & TS Compiler actif sur http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5184)
    args = parser.parse_args()
    run(args.port)
