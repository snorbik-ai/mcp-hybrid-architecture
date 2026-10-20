#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #04 — PORTE A (MCP STDIO) + PIPELINE CYCLE DE VIE
========================================================================================
L'IA ne voit qu'UNE entrée publique : run_agent_lifecycle.
Le serveur charge context_llm, exécute le use case, digère, record_turn.
========================================================================================
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

current_dir = Path(__file__).resolve().parent
tool_root = current_dir.parent.parent
if str(tool_root) not in sys.path:
    sys.path.insert(0, str(tool_root))

from canal_sdk_cli.sdk import EcommerceCatalogScannerSDK
from core.domain.entities_and_ports import CategoryTargetEntity
from canal_mcp.mcp_agent_coding.context_history_manager import ContextHistoryManager

sdk = EcommerceCatalogScannerSDK()
TEST_RUNNER = tool_root / "tests" / "run_all_suites.py"
CONTEXT_FILE = tool_root / "canal_mcp" / "mcp_agent_coding" / "context_llm.json"
history_mgr = ContextHistoryManager(CONTEXT_FILE) if CONTEXT_FILE.exists() else None

USE_CASES = [
    "scan_ecommerce_catalog",
    "discover_category_tree",
    "audit_scanned_catalog",
    "run_quality_and_tests_suite",
]

# ---------------------------------------------------------------------------
# GPS compact (ce que l'IA doit recevoir au branchement)
# ---------------------------------------------------------------------------

def _load_raw_context() -> Dict[str, Any]:
    if not CONTEXT_FILE.exists():
        return {}
    with open(str(CONTEXT_FILE), "r", encoding="utf-8") as f:
        return json.load(f)


def build_agent_briefing(ctx: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    ctx = ctx if ctx is not None else _load_raw_context()
    identity = ctx.get("system_identity", {})
    rules = ctx.get("agent_turn_lifecycle_rules", {})
    history = ctx.get("context_history", {})
    last_turns = history.get("dynamic_history", [])[-5:]
    return {
        "component": identity.get("tool_id", "04_ecommerce_catalog_scanner"),
        "channel": "Porte_A_MCP_STDIO",
        "mission": identity.get("mission", "Scanner catalogues e-commerce, prix TTC/HT, digests, rapport HTML autonome."),
        "lifecycle": [
            "1. L'IA appelle UNIQUEMENT run_agent_lifecycle",
            "2. Le serveur charge context_llm.json (plan directeur et mémoire glissante)",
            "3. Le serveur exécute le use_case en local (Rendu Playwright SPA / BS4)",
            "4. Le serveur renvoie un digest compact et consigne automatiquement le turn_report",
        ],
        "use_cases_allowed": USE_CASES,
        "rule_do": rules.get("rule_do", "Fournir un résumé exécutif concis et le lien vers le rapport HTML interactif."),
        "rule_dont": rules.get("rule_dont", "NE JAMAIS déverser de JSON ou de HTML brut dans le chat. Ne jamais inventer de prix."),
        "last_turns": [
            {
                "turn_id": t.get("turn_id"),
                "summary": t.get("semantic_summary"),
                "status": t.get("status"),
            }
            for t in last_turns
        ],
    }


def build_initialize_instructions(briefing: Dict[str, Any]) -> str:
    """Texte injecté dans initialize.instructions (Architecture Hybride MCP)."""
    return (
        "04_ecommerce_catalog_scanner (Architecture Hybride MCP Standard).\n"
        "RÈGLE D'OR : N'appelle que 'run_agent_lifecycle'. Ne jamais contourner la pipeline.\n"
        "PIPELINE AUTOMATIQUE : chargement du plan context_llm -> exécution locale déterministe -> digest compact -> archivage mémoire (record_turn).\n"
        "RÈGLE DE RÉPONSE : Donner à l'utilisateur un résumé exécutif concis et le lien vers le rapport HTML interactif. NE JAMAIS DÉVERSER DE JSON OU DE HTML BRUT DANS LE CHAT.\n"
        "BRIEFING_GPS_JSON="
        + json.dumps(briefing, ensure_ascii=False)
    )


TOOLS_SCHEMA = [
    {
        "name": "run_agent_lifecycle",
        "description": (
            "POINT D'ENTRÉE UNIQUE ET OBLIGATOIRE du Scanneur DOM E-Commerce Universel.\n"
            "Cette pipeline exécute le use case demandé de façon déterministe en local (Playwright Chromium Headless pour SPA React/Vue ou BeautifulSoup4 pour SSR), "
            "génère un rapport visuel HTML interactif dans output/, compresse le résultat en un digest compact pour protéger la fenêtre de contexte (pattern digest-first), "
            "et consigne automatiquement le tour dans le carnet de bord de session.\n\n"
            "Use Cases disponibles :\n"
            "- 'scan_ecommerce_catalog' : Extrait fiches produits, prix TTC/HT, références SKU et photos HD. Argument obligatoire : url (ex: https://batihome.snorbik.fr/#P02_solutions ou catalogue local).\n"
            "- 'discover_category_tree' : Découvre l'arborescence des catégories et vignettes. Argument : seed_url ou url.\n"
            "- 'audit_scanned_catalog' : Analyse statistique et recherche dans les catalogues scannés. Arguments : family_filter, search_query.\n"
            "- 'run_quality_and_tests_suite' : Exécute les 4 couches de tests de non-régression.\n\n"
            "RÈGLE DE RÉPONSE : Toujours fournir un résumé concis (nombre d'articles, domaine, prix min/max) et le lien cliquable vers le rapport HTML généré. Ne JAMAIS copier-coller de JSON ou HTML brut dans le chat."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "use_case": {
                    "type": "string",
                    "enum": USE_CASES,
                    "description": "Nom du use case à exécuter : 'scan_ecommerce_catalog' | 'discover_category_tree' | 'audit_scanned_catalog' | 'run_quality_and_tests_suite'.",
                },
                "arguments": {
                    "type": "object",
                    "description": "Arguments spécifiques au use case choisi.",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL cible du site e-commerce à scanner (OBLIGATOIRE pour scan_ecommerce_catalog, ex: https://batihome.snorbik.fr/#P02_solutions ou catalogue local).",
                        },
                        "seed_url": {
                            "type": "string",
                            "description": "URL racine pour discover_category_tree.",
                        },
                        "keywords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Mots-clés de filtrage des catégories (ex: ['garde-corps', 'verre']).",
                        },
                        "family_filter": {
                            "type": "string",
                            "description": "Filtre de famille pour audit_scanned_catalog ('all', '01_kits', '02_profils', '04_pinces', etc.).",
                        },
                        "search_query": {
                            "type": "string",
                            "description": "Texte libre ou référence SKU à rechercher pour audit_scanned_catalog.",
                        },
                        "output_json_path": {
                            "type": "string",
                            "description": "Chemin de sortie personnalisé (optionnel, par défaut dans output/).",
                        },
                    },
                },
            },
            "required": ["use_case"],
        },
    }
]


# ---------------------------------------------------------------------------
# Exécution métier (interne — hors tools/list)
# ---------------------------------------------------------------------------

def _run_use_case(use_case: str, args: Dict[str, Any]) -> Dict[str, Any]:
    if use_case == "discover_category_tree":
        seed = args.get("seed_url") or args.get("base_url") or args.get("url")
        if not seed:
            return {
                "status": "error",
                "error": "URL racine manquante. L'argument 'seed_url' ou 'url' est obligatoire pour 'discover_category_tree'.",
                "categories": [],
            }
        kwargs: Dict[str, Any] = {"keywords": args.get("keywords"), "seed_url": seed}
        return {"categories": sdk.discover_categories(**kwargs), "status": "success"}

    if use_case == "scan_ecommerce_catalog":
        target_url = args.get("url") or args.get("seed_url")
        if target_url:
            return sdk.scan_url(
                url=target_url,
                output_json_path=args.get("output_json_path"),
            )
        raw_targets = args.get("targets")
        if raw_targets:
            targets = [
                CategoryTargetEntity(
                    t.get("folder_key", "01_import"),
                    t.get("category_label", t["url"]),
                    t["url"],
                )
                for t in raw_targets
            ]
            return sdk.scan_custom_catalog(
                targets=targets,
                output_json_path=args.get("output_json_path"),
                source_reference=raw_targets[0]["url"],
            )
        return {
            "status": "error",
            "error": (
                "URL manquante. L'argument 'url' est obligatoire pour 'scan_ecommerce_catalog'. "
                "Exemple : arguments={'url': 'https://batihome.snorbik.fr/#P02_solutions'}"
            ),
            "total_products": 0,
            "products": [],
        }

    if use_case == "audit_scanned_catalog":
        return sdk.audit_and_search_catalog(
            catalog_json_path=args.get("json_path"),
            category_filter=args.get("family_filter") or "all",
            search_query=args.get("search_query"),
        )

    if use_case == "run_quality_and_tests_suite":
        proc = subprocess.run(
            [sys.executable, str(TEST_RUNNER), "--json"],
            capture_output=True,
            text=True,
            check=False,
        )
        return json.loads(proc.stdout) if proc.stdout.strip() else {"stdout": proc.stdout, "stderr": proc.stderr}

    raise ValueError(f"use_case inconnu : {use_case}")


def _digest_result(use_case: str, result: Any) -> Dict[str, Any]:
    """Compresser pour l'IA — pas de dump massif."""
    if not isinstance(result, dict):
        return {"use_case": use_case, "status": "ok", "note": str(type(result))}

    if result.get("status") == "error":
        return {
            "use_case": use_case,
            "status": "error",
            "error_message": result.get("error", "Erreur lors de l'exécution du use case."),
            "total_products": 0,
            "next_recommended_step": "Demander à l'utilisateur de fournir une URL valide pour ce site e-commerce.",
        }

    if use_case == "scan_ecommerce_catalog":
        products = result.get("products") or []
        sample = [
            {
                "sku": p.get("sku"),
                "title": p.get("title"),
                "price_ttc_eur": p.get("price_ttc_eur"),
            }
            for p in products[:5]
            if isinstance(p, dict)
        ]
        return {
            "use_case": use_case,
            "status": result.get("status", "success" if result.get("total_products") else "empty"),
            "source_url": result.get("source_url"),
            "total_products": result.get("total_products", 0),
            "total_vignettes": result.get("total_vignettes", 0),
            "sample_products": sample,
            "html_report_url": result.get("html_report_url") or result.get("saved_html_report_path"),
            "saved_json_path": result.get("saved_json_path"),
            "next_recommended_step": "Présenter un résumé concis à l'utilisateur et fournir le lien cliquable vers le rapport HTML interactif.",
        }

    if use_case == "discover_category_tree":
        cats = result.get("categories", result)
        n = len(cats) if isinstance(cats, list) else (cats.get("total") if isinstance(cats, dict) else 0)
        return {"use_case": use_case, "status": "success", "categories_found": n}

    if use_case == "audit_scanned_catalog":
        return {
            "use_case": use_case,
            "status": "success",
            "total_products": result.get("total_products"),
            "catalog_json_path": result.get("catalog_json_path"),
            "highlights": {
                k: result.get(k)
                for k in ("by_family", "price_stats", "matches")
                if k in result
            },
        }

    return {
        "use_case": use_case,
        "status": result.get("status", "success"),
        "summary_keys": list(result.keys())[:20],
    }


def run_agent_lifecycle(use_case: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Pipeline : GPS → métier → digest → mémoire."""
    args = arguments or {}
    ctx = _load_raw_context()
    briefing = build_agent_briefing(ctx)

    if use_case not in USE_CASES:
        return {
            "context_loaded": bool(ctx),
            "gps_summary": briefing,
            "error": f"use_case invalide: {use_case}. Autorisés: {USE_CASES}",
            "memory": {"recorded": False},
        }

    raw = _run_use_case(use_case, args)
    digest = _digest_result(use_case, raw)

    memory_meta = {"recorded": False, "turn_id": None}
    if history_mgr:
        try:
            errors: List[str] = []
            if isinstance(raw, dict) and raw.get("errors"):
                errors = list(raw["errors"]) if isinstance(raw["errors"], list) else [str(raw["errors"])]
            if digest.get("status") == "error":
                errors = errors or [digest.get("error_message", "error")]
            elif digest.get("status") == "empty":
                errors = errors or ["empty_result"]
            rep = history_mgr.record_turn(
                goal=f"Porte A lifecycle → {use_case}",
                actions_performed=[
                    "Chargement context_llm.json",
                    f"Exécution use_case={use_case}",
                    "Digest + record_turn",
                ],
                semantic_summary=json.dumps(
                    {k: digest.get(k) for k in ("use_case", "status", "total_products", "html_report_url")},
                    ensure_ascii=False,
                ),
                errors_encountered=errors,
                next_recommended_step="Montrer digest + lien HTML à l'utilisateur.",
            )
            memory_meta = {"recorded": True, "turn_id": rep.get("turn_id"), "status": rep.get("status")}
        except Exception as exc:
            memory_meta = {"recorded": False, "error": str(exc)}

    return {
        "context_loaded": bool(ctx),
        "gps_summary": briefing,
        "use_case_result_digest": digest,
        "memory": memory_meta,
        "ai_reply_rules": {
            "do": briefing.get("rule_do"),
            "dont": briefing.get("rule_dont"),
        },
    }


# ---------------------------------------------------------------------------
# JSON-RPC
# ---------------------------------------------------------------------------

def handle_request(req: Dict[str, Any]) -> Dict[str, Any]:
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {}) or {}

    if method == "initialize":
        briefing = build_agent_briefing()
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}, "resources": {}},
                "serverInfo": {
                    "name": "04-ecommerce-catalog-scanner-mcp",
                    "version": "2.0.0",
                },
                "instructions": build_initialize_instructions(briefing),
            },
        }

    if method == "resources/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "resources": [
                    {
                        "uri": "context://plan/context_llm.json",
                        "name": "Plan GPS context_llm.json",
                        "mimeType": "application/json",
                        "description": "Source de vérité complète (plan + mémoire 30 tours).",
                    }
                ]
            },
        }

    if method == "resources/read":
        uri = params.get("uri", "")
        if uri == "context://plan/context_llm.json" and CONTEXT_FILE.exists():
            with open(str(CONTEXT_FILE), "r", encoding="utf-8") as f:
                content = f.read()
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "contents": [
                        {"uri": uri, "mimeType": "application/json", "text": content}
                    ]
                },
            }
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32602, "message": f"Resource non trouvée : {uri}"},
        }

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS_SCHEMA}}

    if method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {}) or {}
        try:
            if tool_name != "run_agent_lifecycle":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "isError": True,
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    f"Tool '{tool_name}' non public. "
                                    "Appelle uniquement run_agent_lifecycle avec use_case=..."
                                ),
                            }
                        ],
                    },
                }

            use_case = args.get("use_case")
            inner = args.get("arguments") or {}
            payload = run_agent_lifecycle(use_case, inner)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(payload, indent=2, ensure_ascii=False),
                        }
                    ]
                },
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "isError": True,
                    "content": [{"type": "text", "text": f"Erreur lifecycle : {str(e)}"}],
                },
            }

    if method == "notifications/initialized":
        return None  # type: ignore

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Méthode non supportée : {method}"},
    }


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            res = handle_request(req)
            if res:
                sys.stdout.write(json.dumps(res, ensure_ascii=False) + "\n")
                sys.stdout.flush()
        except Exception as err:
            sys.stdout.write(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": str(err)},
                    }
                )
                + "\n"
            )
            sys.stdout.flush()


if __name__ == "__main__":
    main()
