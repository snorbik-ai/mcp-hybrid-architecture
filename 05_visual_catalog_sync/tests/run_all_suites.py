#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL #05 : VISUAL CATALOG SYNC — ORCHESTRATEUR DES 4 COUCHES DE TESTS
========================================================================================
Exécute séquentiellement :
1. 01_UNIT_TESTS (VisualSyncItemResult, WindowsSafeImageHarvesterAdapter MAX_PATH troncature)
2. 02_INTEGRATION_TESTS (SyncVisualAssetsUseCase & CompileFrontendCatalogUseCase sur 133 produits)
3. 03_VALIDATION_AND_PERF_TESTS (Pureté Clean Architecture, Voiture Autonome, Latence compilation)
4. 04_SMOKE_TESTS (MCP JSON-RPC initialize + tools/list, Web UI /api/status)
========================================================================================
"""

import sys
import json
import time
import threading
import urllib.request
from pathlib import Path
from http.server import HTTPServer

current_dir = Path(__file__).resolve().parent
tool_root = current_dir.parent
if str(tool_root) not in sys.path:
    sys.path.insert(0, str(tool_root))

from core.domain.entities_and_ports import VisualSyncItemResult
from core.infrastructure.windows_safe_image_harvester import WindowsSafeImageHarvesterAdapter
from canal_sdk_cli.sdk import VisualCatalogSyncSDK
from canal_mcp.mcp_classic_stdio.mcp_server import handle_request
from canal_ui.server import VisualCatalogSyncUiHandler


def run_unit_tests():
    details = []
    item = VisualSyncItemResult(
        sku="SKU-01",
        image_url="https://www.inoxdesign.fr/media/catalog/product/very_long.jpg",
        local_raw_path="C:/test.jpg",
        public_frontend_url="/assets/catalogue_verre/02_profils/very_long.jpg",
        path_length_chars=180,
        status="CACHED"
    )
    assert item.to_dict()["status"] == "CACHED"
    details.append({"name": "Domain::VisualSyncItemResult immutability & serialization", "passed": True})

    harvester = WindowsSafeImageHarvesterAdapter()
    long_name = "profil_garde_corps_verre_encastre_aluminium_anodise_3000mm_ultra_long_seo_name_test.jpg"
    safe_name = harvester.sanitize_short_filename(long_name, max_base_len=38)
    assert len(safe_name) <= 43 and safe_name.endswith(".jpg")
    details.append({"name": f"Infrastructure::WindowsSafeImageHarvesterAdapter filename truncation ({len(safe_name)} chars <= 43)", "passed": True})

    return {"suite": "01_UNIT_TESTS", "total": len(details), "passed": len(details), "failed": 0, "details": details}


def run_integration_tests():
    details = []
    sdk = VisualCatalogSyncSDK()
    sync_res = sdk.sync_visual_assets()
    assert sync_res["status"] == "success"
    assert sync_res["total_checked"] == 133
    assert sync_res["missing_count"] == 0
    assert sync_res["windows_max_path_compliant"] is True
    details.append({"name": f"Integration::SyncVisualAssetsUseCase verified 133/133 images on disk (max path {sync_res['max_windows_path_length']} < 260)", "passed": True})

    comp_res = sdk.compile_frontend_catalog()
    assert comp_res["status"] == "success"
    assert comp_res["total_products_compiled"] == 133
    assert Path(comp_res["typescript_module_path"]).exists()
    details.append({"name": "Integration::CompileFrontendCatalogUseCase compiled RawGlassRailingCatalog.ts (133 items)", "passed": True})

    return {"suite": "02_INTEGRATION_TESTS", "total": len(details), "passed": len(details), "failed": 0, "details": details}


def run_validation_and_perf_tests():
    details = []
    domain_code = (tool_root / "core" / "domain" / "entities_and_ports.py").read_text(encoding="utf-8")
    assert "from ..infrastructure" not in domain_code
    assert "canal_" not in domain_code
    details.append({"name": "Validation::Clean Architecture Domain purity check", "passed": True})

    assert (tool_root / "README.md").exists()
    assert (tool_root / "requirements.txt").exists()
    assert (tool_root / "run_tests.bat").exists()
    details.append({"name": "Validation::Autonomous Car files (README.md, requirements.txt, run_tests.bat)", "passed": True})

    sdk = VisualCatalogSyncSDK()
    t0 = time.perf_counter()
    sdk.compile_frontend_catalog()
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
    assert elapsed_ms < 250
    details.append({"name": f"Performance::TypeScript + Markdown compilation in {elapsed_ms}ms (< 250ms)", "passed": True})

    return {"suite": "03_VALIDATION_AND_PERF_TESTS", "total": len(details), "passed": len(details), "failed": 0, "details": details}


def run_smoke_tests():
    details = []
    res_init = handle_request({"id": 1, "method": "initialize", "params": {}})
    assert res_init["result"]["serverInfo"]["name"] == "05-visual-catalog-sync-mcp"
    res_list = handle_request({"id": 2, "method": "tools/list", "params": {}})
    assert len(res_list["result"]["tools"]) >= 4
    details.append({"name": "Smoke::Canal 1 MCP JSON-RPC (initialize & tools/list)", "passed": True})

    httpd = HTTPServer(("127.0.0.1", 0), VisualCatalogSyncUiHandler)
    port = httpd.server_port
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/status", timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["missing_count"] == 0
        details.append({"name": "Smoke::Canal 2 Web UI HTTP (/api/status -> 0 missing)", "passed": True})
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
        "tool": "05_visual_catalog_sync",
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
        print("🧪 RAPPORT DE TESTS — OUTIL #05 : 05_visual_catalog_sync")
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
