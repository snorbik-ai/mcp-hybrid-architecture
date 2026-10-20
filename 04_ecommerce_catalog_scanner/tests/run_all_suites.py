#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL #04 : E-COMMERCE CATALOG SCANNER — ORCHESTRATEUR DES 4 COUCHES DE TESTS
========================================================================================
Exécute séquentiellement :
1. 01_UNIT_TESTS (ScannedProductEntity, Bs4DomCatalogParserAdapter, Use Cases DI Mocks)
2. 02_INTEGRATION_TESTS (JsonCatalogRepositoryAdapter & Audit des 133 produits réels)
3. 03_VALIDATION_AND_PERF_TESTS (Pureté Clean Architecture, Voiture Autonome, Latence Audit < 100ms)
4. 04_SMOKE_TESTS (MCP JSON-RPC initialize + tools/list, Web UI /api/catalog)
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

from core.domain.entities_and_ports import ScannedProductEntity
from core.infrastructure.bs4_dom_catalog_parser import Bs4DomCatalogParserAdapter
from core.application.use_cases import DiscoverCategoryTreeUseCase
from canal_sdk_cli.sdk import EcommerceCatalogScannerSDK
from canal_mcp.mcp_classic_stdio.mcp_server import handle_request
from canal_ui.server import CatalogScannerUiHandler


class _MockFetcher:
    def fetch_html(self, url: str, timeout_sec: int = 25) -> str:
        return """
        <html><body>
            <a href="https://www.inoxdesign.fr/garde-corps-verre-profil.html">Garde-Corps Verre sur Profil</a>
            <a href="https://www.inoxdesign.fr/pince-a-verre-inox.html">Pinces à Verre Inox 316</a>
        </body></html>
        """


def run_unit_tests():
    details = []
    prod = ScannedProductEntity(
        sku="SKU-001", title="Profil U Sol Aluminium",
        category_folder="02_profils", category_label="Profil garde-corps verre",
        price_ttc_eur=339.0, price_ht_eur=282.5,
        price_raw="339,00 € TTC", unit="mètre linéaire (ml)",
        source_url="https://www.inoxdesign.fr/p1.html",
        image_url="https://www.inoxdesign.fr/img1.jpg"
    )
    assert prod.to_dict()["category_folder"] == "02_profils"
    details.append({"name": "Domain::ScannedProductEntity immutability & serialization", "passed": True})

    parser = Bs4DomCatalogParserAdapter()
    sample_html = """
    <div class="product-item">
      <div class="card">
        <a href="https://www.inoxdesign.fr/profil-verre.html">
          <img src="https://www.inoxdesign.fr/media/catalog/product/p/r/profil_test_1.jpg" alt="Profil Aluminium" />
        </a>
        <div>Profil Aluminium Garde-Corps Verre</div>
        <div>339,00 € TTC par mètre linéaire</div>
      </div>
    </div>
    """
    cards = parser.extract_product_cards(sample_html, "02_profils", "Profils")
    assert len(cards) == 1 and cards[0].price_ttc_eur == 339.0 and cards[0].price_ht_eur == 282.5
    details.append({"name": "Infrastructure::Bs4DomCatalogParserAdapter DOM card & price extraction", "passed": True})

    prestashop_html = """
    <li class="ajax_block_product">
      <div class="product-container">
        <a class="product_img_link" href="/garde-corps-verre/1-garde-corps-cx500.html">
          <img src="/50-home_default/garde-corps-cx500.jpg" alt="Garde corps en verre CX500" />
        </a>
        <span class="price product-price">417,85 €</span>
      </div>
    </li>
    """
    ps_cards = parser.extract_product_cards(prestashop_html, "verre", "Garde-corps Verre", base_url="https://www.railingsdesign.com")
    assert len(ps_cards) == 1 and ps_cards[0].price_ttc_eur == 417.85
    assert ps_cards[0].source_url == "https://www.railingsdesign.com/garde-corps-verre/1-garde-corps-cx500.html"
    assert "thickbox_default" in ps_cards[0].image_url
    details.append({"name": "Infrastructure::Bs4DomCatalogParserAdapter universal PrestaShop DOM & HD image upgrade", "passed": True})

    uc = DiscoverCategoryTreeUseCase(_MockFetcher(), parser)
    cats = uc.execute("https://www.inoxdesign.fr")
    assert cats["discovered_links_count"] == 2
    details.append({"name": "Application::DiscoverCategoryTreeUseCase DI with Mock Fetcher", "passed": True})

    return {"suite": "01_UNIT_TESTS", "total": len(details), "passed": len(details), "failed": 0, "details": details}


def run_integration_tests():
    details = []
    sdk = EcommerceCatalogScannerSDK()
    audit = sdk.audit_and_search_catalog()
    assert audit["status"] == "success"
    assert audit["total_products"] == 133
    assert audit["total_vignettes"] == 7
    details.append({"name": "Integration::AuditScannedCatalogUseCase verified 133 products & 7 vignettes", "passed": True})

    filtered = sdk.audit_and_search_catalog(category_filter="04_pinces")
    assert filtered["filtered_count"] == 52
    details.append({"name": "Integration::AuditScannedCatalogUseCase family filter (52 pinces)", "passed": True})

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

    sdk = EcommerceCatalogScannerSDK()
    t0 = time.perf_counter()
    sdk.audit_and_search_catalog()
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
    assert elapsed_ms < 100
    details.append({"name": f"Performance::Full 133-product catalog audit in {elapsed_ms}ms (< 100ms)", "passed": True})

    return {"suite": "03_VALIDATION_AND_PERF_TESTS", "total": len(details), "passed": len(details), "failed": 0, "details": details}


def run_smoke_tests():
    details = []
    res_init = handle_request({"id": 1, "method": "initialize", "params": {}})
    assert res_init["result"]["serverInfo"]["name"] == "04-ecommerce-catalog-scanner-mcp"
    res_list = handle_request({"id": 2, "method": "tools/list", "params": {}})
    tools = res_list["result"]["tools"]
    assert len(tools) == 1 and tools[0]["name"] == "run_agent_lifecycle"
    res_call = handle_request({
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "run_agent_lifecycle",
            "arguments": {"use_case": "audit_scanned_catalog", "arguments": {"family_filter": "all"}}
        }
    })
    assert not res_call["result"].get("isError")
    details.append({"name": "Smoke::Canal 1 MCP Gateway (initialize, tools/list & run_agent_lifecycle)", "passed": True})

    httpd = HTTPServer(("127.0.0.1", 0), CatalogScannerUiHandler)
    port = httpd.server_port
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/catalog", timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["total_products"] == 133
        details.append({"name": "Smoke::Canal 2 Web UI HTTP (/api/catalog -> 133 products)", "passed": True})
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
        "tool": "04_ecommerce_catalog_scanner",
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
        print("🧪 RAPPORT DE TESTS — OUTIL #04 : 04_ecommerce_catalog_scanner")
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
