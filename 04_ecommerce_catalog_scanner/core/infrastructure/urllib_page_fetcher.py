#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #04 — E-COMMERCE CATALOG SCANNER PIPELINE (CLEAN ARCHITECTURE)
Couche : Core / Infrastructure (Adaptateur HTTP — Responsabilité Technique Unique)
========================================================================================
Rôle :
Implémente le port IHttpPageFetcherPort en utilisant urllib.request avec gestion des
en-têtes User-Agent standard et bascule Chromium Playwright pour le rendu SPA React/Vue.
========================================================================================
"""

import re
import urllib.request
from urllib.parse import urlparse
from ..domain.entities_and_ports import IHttpPageFetcherPort


class UrllibPageFetcherAdapter(IHttpPageFetcherPort):
    """Adaptateur technique de téléchargement : HTTP standard avec rendu headless Chromium pour SPAs React."""

    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    }

    def fetch_html(self, url: str, timeout_sec: int = 25) -> str:
        """Récupère le code source HTML d'une URL publique (avec support dynamique SPA React/Vue)."""
        needs_headless = "#" in url
        raw_html = ""

        if not needs_headless:
            try:
                req = urllib.request.Request(url, headers=self.DEFAULT_HEADERS)
                with urllib.request.urlopen(req, timeout=min(timeout_sec, 8)) as response:
                    raw_bytes = response.read()
                raw_html = raw_bytes.decode("utf-8", errors="ignore")
                
                is_spa_skeleton = bool(re.search(r'<div\s+id=["\'](?:root|app|__next)["\'][^>]*>\s*</div>', raw_html, re.I))
                if not is_spa_skeleton:
                    return raw_html
            except Exception:
                pass

        # Rendu Chromium Headless standard pour les frameworks clients (React / Vue / Vite)
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=self.DEFAULT_HEADERS["User-Agent"],
                    viewport={"width": 1920, "height": 1080},
                    locale="fr-FR",
                    timezone_id="Europe/Paris"
                )
                page = context.new_page()
                page.goto(url, timeout=timeout_sec * 1000, wait_until="domcontentloaded")
                try:
                    page.wait_for_load_state("networkidle", timeout=4000)
                except Exception:
                    pass
                rendered_html = page.content()
                browser.close()
                if rendered_html and len(rendered_html) > 500:
                    return rendered_html
        except Exception:
            pass

        return raw_html
