#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #02 : PDF TECHNICAL EXTRACTOR — CANAL 2 : MINI-APP WEB UI (:5180)
========================================================================================
Serveur HTTP local autonome avec endpoints /api/health, /api/documents, /api/process
et /api/run-tests.
========================================================================================
"""

import sys
import json
import mimetypes
import subprocess
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

current_dir = Path(__file__).resolve().parent
tool_root = current_dir.parent
if str(tool_root) not in sys.path:
    sys.path.insert(0, str(tool_root))

from canal_sdk_cli.sdk import PdfProcessorSDK

WORKSPACE_ROOT = tool_root.parent.parent.resolve()
LOCAL_OUTPUT_DIR = tool_root / "output"
LOCAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SHARED_OUTPUT_DIR = tool_root.parent / "output"
OUTPUT_DIR = LOCAL_OUTPUT_DIR
STATIC_DIR = current_dir / "static"
TEST_RUNNER = tool_root / "tests" / "run_all_suites.py"

sdk = PdfProcessorSDK(default_output_dir=str(OUTPUT_DIR))


class PdfUiRequestHandler(BaseHTTPRequestHandler):
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
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "online", "tool": "02_pdf_technical_extractor", "port": 5180}).encode("utf-8"))
            return

        if path == "/api/documents":
            docs = []
            for base_out in {LOCAL_OUTPUT_DIR, SHARED_OUTPUT_DIR}:
                if base_out.exists():
                    for d in base_out.iterdir():
                        if d.is_dir() and (d / "manifest.json").exists():
                            try:
                                manifest = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
                                docs.append({
                                    "slug": d.name,
                                    "filename": manifest.get("filename", d.name),
                                    "total_pages": manifest.get("total_pages", 0),
                                    "categories": {k: len(v) for k, v in manifest.get("classified_assets", {}).items()}
                                })
                            except Exception:
                                pass
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(docs).encode("utf-8"))
            return

        if path.startswith("/api/document/"):
            slug = path.replace("/api/document/", "").strip()
            for base_out in (LOCAL_OUTPUT_DIR, SHARED_OUTPUT_DIR):
                manifest_file = base_out / slug / "manifest.json"
                if manifest_file.exists():
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(manifest_file.read_bytes())
                    return
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Document non trouve"}')
            return

        if path.startswith("/output/"):
            rel_file = path.replace("/output/", "").lstrip("/")
            for base_out in (LOCAL_OUTPUT_DIR, SHARED_OUTPUT_DIR):
                target_file = base_out / rel_file
                if target_file.exists() and target_file.is_file():
                    mime, _ = mimetypes.guess_type(str(target_file))
                    self.send_response(200)
                    self.send_header("Content-Type", mime or "application/octet-stream")
                    self.end_headers()
                    self.wfile.write(target_file.read_bytes())
                    return

        if path in ("/", "/index.html"):
            index_path = STATIC_DIR / "index.html"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(index_path.read_bytes())
            return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"404 Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/run-tests":
            proc = subprocess.run([sys.executable, str(TEST_RUNNER), "--json"], capture_output=True, text=True, check=False)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(proc.stdout.encode("utf-8"))
            return

        if parsed.path == "/api/process":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            try:
                data = json.loads(body)
                pdf_path = data.get("pdf_path")
                dpi = int(data.get("dpi", 150))
                if pdf_path and not Path(pdf_path).is_absolute():
                    resolved_candidate = WORKSPACE_ROOT / pdf_path
                    if resolved_candidate.exists():
                        pdf_path = str(resolved_candidate)
                res = sdk.process_pdf(pdf_path=pdf_path, output_dir=str(OUTPUT_DIR), dpi=dpi)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(res).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()


def run(port: int = 5180):
    httpd = HTTPServer(("127.0.0.1", port), PdfUiRequestHandler)
    print(f"🌐 [02_pdf_technical_extractor] Web UI active sur http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-p", type=int, default=5180)
    args = parser.parse_args()
    run(args.port)
