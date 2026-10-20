#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #03 : MEDIA QUALITY AUDITOR — CANAL 2 : MINI-APP WEB UI (:5182)
========================================================================================
Serveur HTTP local autonome avec support de --port, résolution de dossier intelligente
(frontend/public/assets/catalogue_verre ou frontend/public/images), /api/health et /api/run-tests.
========================================================================================
"""

import sys
import os
import json
import subprocess
import urllib.parse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

current_dir = Path(__file__).resolve().parent
tool_root = current_dir.parent
if str(tool_root) not in sys.path:
    sys.path.insert(0, str(tool_root))

from canal_sdk_cli.sdk import MediaAuditorPipeline

PIPELINE = MediaAuditorPipeline()
WORKSPACE_ROOT = tool_root.parent.parent.resolve()
TEST_RUNNER = tool_root / "tests" / "run_all_suites.py"


def resolve_folder(folder: str) -> str:
    candidate = os.path.abspath(os.path.join(str(WORKSPACE_ROOT), folder))
    if os.path.exists(candidate):
        return candidate
    fallback = WORKSPACE_ROOT / "frontend" / "public" / "assets" / "catalogue_verre"
    if fallback.exists():
        return str(fallback)
    return str(tool_root)


class MediaAuditorHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

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

        if path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "online", "tool": "03_media_quality_auditor", "port": 5182}).encode("utf-8"))
            return

        if path == "/api/audit":
            folder = query.get("folder", ["frontend/public/assets/catalogue_verre"])[0]
            abs_folder = resolve_folder(folder)
            min_w = int(query.get("min_width", [1200])[0])
            min_h = int(query.get("min_height", [700])[0])

            try:
                res = PIPELINE.audit_directory(abs_folder, min_width=min_w, min_height=min_h)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        if path == "/api/candidates":
            folder = query.get("folder", ["frontend/public/assets/catalogue_verre"])[0]
            abs_folder = resolve_folder(folder)
            try:
                res = PIPELINE.get_certified_hero_candidates(abs_folder)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        if path.startswith("/preview/"):
            rel_file = urllib.parse.unquote(path[len("/preview/"):])
            abs_file = os.path.abspath(os.path.join(str(WORKSPACE_ROOT), rel_file))
            if os.path.exists(abs_file) and os.path.isfile(abs_file):
                self.send_response(200)
                if abs_file.endswith(".png"):
                    self.send_header("Content-Type", "image/png")
                elif abs_file.endswith((".jpg", ".jpeg")):
                    self.send_header("Content-Type", "image/jpeg")
                elif abs_file.endswith(".webp"):
                    self.send_header("Content-Type", "image/webp")
                self.end_headers()
                with open(abs_file, "rb") as f:
                    self.wfile.write(f.read())
                return
            self.send_response(404)
            self.end_headers()
            return

        index_file = current_dir / "static" / "index.html"
        if index_file.exists():
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(index_file.read_bytes())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"index.html non trouve")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/run-tests":
            proc = subprocess.run([sys.executable, str(TEST_RUNNER), "--json"], capture_output=True, text=True, check=False)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(proc.stdout.encode("utf-8"))
            return

        if path == "/api/clean":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body) if body else {}
            folder = data.get("folder", "frontend/public/assets/catalogue_verre")
            abs_folder = resolve_folder(folder)
            dry_run = bool(data.get("dry_run", True))

            try:
                res = PIPELINE.clean_duplicates(abs_folder, dry_run=dry_run)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return


def run(port: int = 5182):
    httpd = HTTPServer(("127.0.0.1", port), MediaAuditorHandler)
    print(f"🌐 [03_media_quality_auditor] Web UI active sur http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-p", type=int, default=5182)
    args = parser.parse_args()
    run(args.port)
