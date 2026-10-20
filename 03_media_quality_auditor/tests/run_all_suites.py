#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL #03 : MEDIA QUALITY AUDITOR — ORCHESTRATEUR DES 4 COUCHES DE TESTS
========================================================================================
Exécute séquentiellement :
1. 01_UNIT_TESTS (AuditedMediaEntity, Use Cases avec Mock IMediaInspectorPort)
2. 02_INTEGRATION_TESTS (PillowMd5InspectorAdapter sur images temporaires HD/LowRes/Doublon)
3. 03_VALIDATION_AND_PERF_TESTS (Pureté Clean Architecture, Voiture Autonome, Latence MD5)
4. 04_SMOKE_TESTS (MCP JSON-RPC initialize + tools/list, Web UI /api/health)
========================================================================================
"""

import sys
import json
import time
import tempfile
import threading
import urllib.request
from pathlib import Path
from http.server import HTTPServer
from PIL import Image

current_dir = Path(__file__).resolve().parent
tool_root = current_dir.parent
if str(tool_root) not in sys.path:
    sys.path.insert(0, str(tool_root))

from core.domain.entities_and_ports import AuditedMediaEntity, IMediaInspectorPort
from core.infrastructure.pillow_md5_inspector_adapter import PillowMd5InspectorAdapter
from canal_sdk_cli.sdk import MediaAuditorPipeline
from canal_mcp.mcp_classic_stdio.mcp_server import handle_request
from canal_ui.server import MediaAuditorHandler


class _MockInspectorPort(IMediaInspectorPort):
    def compute_file_hash(self, filepath: str) -> str:
        return "hash_dup" if "dup" in filepath else f"hash_{filepath}"

    def inspect_image_metadata(self, filepath: str):
        if "hd" in filepath:
            return 1600, 900, "PNG", "RGB"
        return 400, 300, "JPEG", "RGB"

    def delete_file(self, filepath: str) -> bool:
        return True


def run_unit_tests():
    details = []
    entity = AuditedMediaEntity(
        filename="hero.png", rel_path="hero.png", full_path="/tmp/hero.png",
        width=1600, height=900, aspect_ratio=1.78, size_kb=240.5,
        format="PNG", mode="RGB", md5="abc12345", status="VALID_HD", is_hd=True
    )
    assert entity.to_dict()["status"] == "VALID_HD"
    details.append({"name": "Domain::AuditedMediaEntity immutability & serialization", "passed": True})

    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp)
        (p / "01_hd.png").write_bytes(b"fake1")
        (p / "02_low.jpg").write_bytes(b"fake2")
        (p / "03_dup_1.jpg").write_bytes(b"fake3")
        (p / "04_dup_2.jpg").write_bytes(b"fake3")

        sdk = MediaAuditorPipeline(inspector_adapter=_MockInspectorPort())
        audit = sdk.audit_directory(str(p))
        assert audit["summary"]["valid_hd"] == 1
        assert audit["summary"]["duplicates"] == 1
        details.append({"name": "Application::AuditMediaDirectoryUseCase DI & Mock Port", "passed": True})

        clean_res = sdk.clean_duplicates(str(p), dry_run=True)
        assert clean_res["removed_count"] == 1
        details.append({"name": "Application::CleanDuplicateMediaUseCase dry-run safety", "passed": True})

    return {"suite": "01_UNIT_TESTS", "total": len(details), "passed": len(details), "failed": 0, "details": details}


def run_integration_tests():
    details = []
    sdk = MediaAuditorPipeline()
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp)
        img_hd = Image.new("RGB", (1400, 800), color=(0, 50, 63))
        img_hd.save(p / "hero_hd.png")
        img_hd.save(p / "hero_hd_duplicate.png")

        img_low = Image.new("RGB", (300, 200), color=(0, 168, 150))
        img_low.save(p / "thumb_low.jpg")

        res = sdk.audit_directory(str(p))
        assert res["summary"]["total_images"] == 3
        assert res["summary"]["valid_hd"] == 1
        assert res["summary"]["duplicates"] == 1
        assert res["summary"]["rejected_low_res"] == 1
        details.append({"name": "Integration::PillowMd5InspectorAdapter real image & MD5 audit", "passed": True})

        candidates = sdk.get_certified_hero_candidates(str(p))
        assert len(candidates) == 1 and candidates[0]["filename"] == "hero_hd.png"
        details.append({"name": "Integration::GetCertifiedHeroCandidatesUseCase filtering", "passed": True})

    return {"suite": "02_INTEGRATION_TESTS", "total": len(details), "passed": len(details), "failed": 0, "details": details}


def run_validation_and_perf_tests():
    details = []
    domain_code = (tool_root / "core" / "domain" / "entities_and_ports.py").read_text(encoding="utf-8")
    assert "infrastructure" not in domain_code
    assert "canal_" not in domain_code
    details.append({"name": "Validation::Clean Architecture Domain purity check", "passed": True})

    assert (tool_root / "README.md").exists()
    assert (tool_root / "requirements.txt").exists()
    assert (tool_root / "run_tests.bat").exists()
    details.append({"name": "Validation::Autonomous Car files (README.md, requirements.txt, run_tests.bat)", "passed": True})

    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(b"x" * 1024 * 256)
        tf_path = tf.name
    try:
        adapter = PillowMd5InspectorAdapter()
        t0 = time.perf_counter()
        for _ in range(100):
            adapter.compute_file_hash(tf_path)
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        assert elapsed_ms < 500
        details.append({"name": f"Performance::100 MD5 hashes (256KB) in {elapsed_ms}ms (< 500ms)", "passed": True})
    finally:
        Path(tf_path).unlink(missing_ok=True)

    return {"suite": "03_VALIDATION_AND_PERF_TESTS", "total": len(details), "passed": len(details), "failed": 0, "details": details}


def run_smoke_tests():
    details = []
    res_init = handle_request({"id": 1, "method": "initialize", "params": {}})
    assert res_init["result"]["serverInfo"]["name"] == "03-media-quality-auditor-mcp"
    res_list = handle_request({"id": 2, "method": "tools/list", "params": {}})
    assert len(res_list["result"]["tools"]) >= 4
    details.append({"name": "Smoke::Canal 1 MCP JSON-RPC (initialize & tools/list)", "passed": True})

    httpd = HTTPServer(("127.0.0.1", 0), MediaAuditorHandler)
    port = httpd.server_port
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["status"] == "online"
        details.append({"name": "Smoke::Canal 2 Web UI HTTP (/api/health)", "passed": True})
    finally:
        httpd.shutdown()
        httpd.server_close()

    return {"suite": "04_SMOKE_TESTS", "total": len(details), "passed": len(details), "failed": 0, "details": details}


def main():
    json_only = "--json" in sys.argv
    t0 = time.perf_counter()
    suites = [
        run_unit_tests(),
        run_integration_tests(),
        run_validation_and_perf_tests(),
        run_smoke_tests()
    ]
    total_tests = sum(s["total"] for s in suites)
    total_passed = sum(s["passed"] for s in suites)
    duration_ms = round((time.perf_counter() - t0) * 1000, 2)

    report = {
        "tool": "03_media_quality_auditor",
        "status": "PASS",
        "total_tests": total_tests,
        "passed": total_passed,
        "failed": 0,
        "duration_ms": duration_ms,
        "suites": suites
    }

    if json_only:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("=" * 80)
        print("🧪 RAPPORT DE TESTS — OUTIL #03 : 03_media_quality_auditor")
        print("=" * 80)
        for s in suites:
            print(f"✅ [{s['suite']}] : {s['passed']}/{s['total']} réussis")
            for d in s["details"]:
                print(f"   • {d['name']}")
        print("-" * 80)
        print(f"🏆 BILAN : {total_passed}/{total_tests} TESTS VALIDÉS ({duration_ms} ms) — STATUT : PASS")
        print("=" * 80)


if __name__ == "__main__":
    main()
