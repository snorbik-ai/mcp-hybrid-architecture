#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #04 — E-COMMERCE CATALOG SCANNER PIPELINE (CLEAN ARCHITECTURE)
Couche : Core / Infrastructure (Adaptateur Parseur DOM BeautifulSoup4)
========================================================================================
Rôle :
Implémente le port IDomCatalogParserPort avec responsabilité technique unique : lire le
HTML d'une page e-commerce et en tirer catégories, vignettes et cartes produits.

Stratégies, essayées dans cet ORDRE (de la plus spécifique à la plus générique) :
  1. Motif historique (images /media/catalog/product/ de type Magento) — c'est le
     comportement qui a produit le catalogue de référence ; il est conservé à l'identique
     pour garantir la non-régression (mêmes SKU, mêmes URLs, mêmes unités).
  2. Microdonnées JSON-LD Schema.org « Product » (Shopify, WooCommerce, PrestaShop...).
  3. Heuristique générique : images produits (/product/, /products/, wp-content/uploads/...)
     ou, en dernier recours, toute image portée par un lien.

Une stratégie plus générique n'est utilisée que si la précédente ne trouve rien : elle ne
peut donc jamais dégrader un résultat déjà obtenu par une stratégie plus spécifique.
========================================================================================
"""

import os
import re
import json
from urllib.parse import urlparse, urljoin
from typing import List, Dict, Set
from bs4 import BeautifulSoup
from ..domain.entities_and_ports import (
    IDomCatalogParserPort,
    CategoryVignetteEntity,
    ScannedProductEntity,
)

LEGACY_PRODUCT_PATTERN = "/media/catalog/product/"
LEGACY_CATEGORY_PATTERN = "/media/catalog/category/"
GENERIC_PRODUCT_PATTERNS = [
    "/product/", "/products/", "/produits/", "cdn.shopify.com", "wp-content/uploads/",
]


class Bs4DomCatalogParserAdapter(IDomCatalogParserPort):
    """Adaptateur d'analyse DOM BeautifulSoup4 : stratégies ordonnées, du spécifique au générique."""

    # ------------------------------------------------------------------ catégories
    def discover_category_links(
        self,
        html: str,
        base_domain: str,
        keywords: List[str]
    ) -> List[Dict[str, str]]:
        """Découvre les liens de catégories du domaine donné qui correspondent aux mots-clés."""
        soup = BeautifulSoup(html, "html.parser")
        discovered = {}
        clean_base = base_domain.replace("https://", "").replace("http://", "").strip("/")

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            txt = a.get_text(" ", strip=True)
            if href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue

            full_url = href if href.startswith("http") else urljoin(f"https://{clean_base}/", href)
            if clean_base not in urlparse(full_url).netloc:
                continue  # lien externe au domaine ciblé

            if not keywords or any(k.lower() in full_url.lower() for k in keywords):
                if full_url not in discovered or (not discovered[full_url]["label"] and txt):
                    discovered[full_url] = {
                        "url": full_url,
                        "label": txt[:90] if txt else os.path.basename(urlparse(full_url).path),
                    }
        return list(discovered.values())

    # -------------------------------------------------------------------- vignettes
    def extract_category_vignettes(
        self,
        html: str,
        source_url: str
    ) -> List[CategoryVignetteEntity]:
        """Vignettes de catégories : motif historique d'abord, sous-catégories CMS, puis repli générique."""
        soup = BeautifulSoup(html, "html.parser")

        def collect(predicate) -> List[CategoryVignetteEntity]:
            found: List[CategoryVignetteEntity] = []
            seen = set()
            for img in soup.find_all("img"):
                src = img.get("data-src") or img.get("src") or ""
                if src and predicate(img, src) and src not in seen:
                    seen.add(src)
                    alt = (img.get("alt") or "").strip()
                    full_src = urljoin(source_url, src)
                    found.append(CategoryVignetteEntity(
                        title=alt or os.path.basename(urlparse(full_src).path),
                        image_url=full_src,
                        source_page_url=source_url,
                    ))
            return found

        # 1. Motif historique (Magento)
        legacy = collect(lambda img, src: LEGACY_CATEGORY_PATTERN in src)
        if legacy:
            return legacy

        # 2. Sous-catégories PrestaShop, Shopify, WooCommerce (.subcategories, #subcategories, .category-card)
        subcat_els = soup.select("#subcategories img, .subcategories img, .subcategory-image img, .category-card img, .sub-categories img")
        if subcat_els:
            sub_found: List[CategoryVignetteEntity] = []
            seen_sub = set()
            for img in subcat_els:
                src = img.get("data-src") or img.get("src") or ""
                if src and src not in seen_sub:
                    seen_sub.add(src)
                    alt = (img.get("alt") or "").strip()
                    parent_a = img.find_parent("a")
                    title = alt
                    if not title and parent_a:
                        title = parent_a.get("title") or parent_a.get_text(strip=True)
                    full_src = urljoin(source_url, src)
                    sub_found.append(CategoryVignetteEntity(
                        title=title or os.path.basename(urlparse(full_src).path),
                        image_url=full_src,
                        source_page_url=source_url,
                    ))
            if sub_found:
                return sub_found

        def generic(img, src) -> bool:
            low = src.lower()
            if "/categories/" in low or "/collections/" in low:
                return True
            classes = " ".join(img.get("class", []) or []).lower()
            return "category" in classes

        return collect(generic)

    # --------------------------------------------------------------------- produits
    def extract_product_cards(
        self,
        html: str,
        folder_key: str,
        category_label: str,
        base_url: str = "",
    ) -> List[ScannedProductEntity]:
        """Cartes produits universelles : (1) motif historique, (2) JSON-LD, (3) conteneurs multi-CMS, (4) heuristique générique."""
        soup = BeautifulSoup(html, "html.parser")
        imgs = soup.find_all("img")

        # 1. Motif historique — comportement strictement identique à la version de référence
        legacy_imgs = [
            img for img in imgs
            if any(LEGACY_PRODUCT_PATTERN in (img.get(a) or "") for a in ("src", "data-src"))
        ]
        legacy = self._cards_from_images(soup, legacy_imgs, folder_key, category_label, strict=True, base_url=base_url)
        if legacy:
            return legacy

        # 2. Microdonnées JSON-LD Schema.org Product
        jsonld = self._cards_from_jsonld(soup, folder_key, category_label, base_url=base_url)
        if jsonld:
            return jsonld

        # 3. Conteneurs e-commerce standards (Prestashop, WooCommerce, Shopify, Magento, etc.)
        containers = soup.select(".ajax_block_product, .product-miniature, .product-container, .product-item, .product-card, .woocommerce-loop-product, article.product, article.offerWrapper, article[data-e2e='offer-item'], [data-e2e='offer-item']")
        if containers:
            cms_cards = self._cards_from_containers(containers, folder_key, category_label, base_url=base_url)
            if cms_cards:
                return cms_cards

        # 4. Heuristique générique d'images e-commerce
        generic_imgs = [
            img for img in imgs
            if any(p in (img.get(a) or "").lower() for a in ("src", "data-src") for p in GENERIC_PRODUCT_PATTERNS)
        ] or [img for img in imgs if img.find_parent("a", href=True)]
        generic_cards = self._cards_from_images(soup, generic_imgs, folder_key, category_label, strict=False, base_url=base_url)
        if generic_cards:
            return generic_cards

        # 5. Heuristique universelle pour SPAs modernes (React, Vue, Next, Tailwind)
        return self._cards_from_spa(soup, folder_key, category_label, base_url=base_url)

    def _cards_from_spa(
        self,
        soup: BeautifulSoup,
        folder_key: str,
        category_label: str,
        base_url: str = "",
    ) -> List[ScannedProductEntity]:
        """Extrait les cartes de solutions/produits depuis les SPAs modernes React/Vue/Tailwind."""
        extracted: List[ScannedProductEntity] = []
        seen_titles: Set[str] = set()

        for heading in soup.find_all(["h4", "h3"]):
            title = heading.get_text(strip=True)
            if not title or len(title) < 4:
                continue
            low_t = title.lower()
            if any(skip in low_t for skip in ["doute", "contact", "newsletter", "estimez", "déjà", "quel est", "nos solutions", "recevez", "vous avez", "un doute", "comment", "étape"]):
                continue
            if title in seen_titles:
                continue

            container = heading.find_parent("div", class_=lambda c: c and any(k in str(c) for k in ["rounded", "shadow", "border", "card", "p-4", "p-6", "bg-"])) or heading.parent
            if not container:
                continue

            card_text = container.get_text(" ", strip=True)
            price_match = re.search(r"([0-9\s]+(?:[,\.][0-9]{2})?)\s*€", card_text)
            price_val = None
            price_raw = "Sur devis"
            if price_match:
                price_raw = price_match.group(0).strip()
                clean_num = price_match.group(1).replace(" ", "").replace("\xa0", "").replace(",", ".")
                try:
                    price_val = float(clean_num)
                except ValueError:
                    price_val = None

            img = container.find("img")
            img_url = ""
            if img:
                img_src = img.get("data-src") or img.get("src") or ""
                if img_src:
                    img_url = urljoin(base_url, img_src) if base_url else img_src

            a_tag = container.find("a", href=True) or container.find_parent("a", href=True)
            source_url = urljoin(base_url, a_tag["href"]) if a_tag and base_url else (a_tag["href"] if a_tag else base_url)

            unit = "unité"
            if "ml" in card_text.lower() or "mètre" in card_text.lower():
                unit = "mètre linéaire (ml)"
            elif "m²" in card_text.lower():
                unit = "m²"

            clean_sku = re.sub(r"[^A-Z0-9\-]", "", title.upper().replace(" ", "-"))[:25]
            if not clean_sku:
                clean_sku = f"SPA_PROD_{len(extracted) + 1:03d}"

            seen_titles.add(title)
            extracted.append(ScannedProductEntity(
                sku=clean_sku,
                title=title,
                category_folder=folder_key,
                category_label=category_label,
                categories=[category_label],
                price_raw=price_raw,
                price_ttc_eur=price_val,
                price_ht_eur=round(price_val / 1.2, 2) if price_val else None,
                unit=unit,
                full_card_text=f"{title} | {price_raw}",
                source_url=source_url,
                image_url=img_url,
            ))

        return extracted

    def _cards_from_containers(
        self,
        containers,
        folder_key: str,
        category_label: str,
        base_url: str = "",
    ) -> List[ScannedProductEntity]:
        """Extrait les cartes produits depuis des conteneurs DOM e-commerce standards multi-CMS."""
        extracted: List[ScannedProductEntity] = []
        seen_urls: Set[str] = set()

        for el in containers:
            name_el = el.select_one(".product-name, .product-title, h2, h3, .name, [itemprop='name']")
            title = name_el.get_text(strip=True) if name_el else ""
            link_el = el.select_one("a.product_img_link, a.product-thumbnail, a[itemprop='url'], a[href*='/']")
            if not title and link_el and link_el.has_attr("title"):
                title = link_el["title"].strip()
            img_el = el.select_one("img[itemprop='image'], img")
            if not title and img_el and img_el.has_attr("alt"):
                title = img_el["alt"].strip()
            if not title or len(title) < 3:
                continue

            price_el = el.select_one(".price.product-price, .product-price, .price, .current-price, [itemprop='price']")
            price_text = price_el.get_text(strip=True) if price_el else ""
            if not price_text and price_el and price_el.has_attr("content"):
                price_text = f"{price_el['content']} €"
            if not price_text:
                price_text = "Sur devis"

            price_match = re.search(r"([0-9\s]+(?:[,\.][0-9]{2})?)\s*€", price_text)
            price_val = None
            if price_match:
                clean_num = price_match.group(1).replace(" ", "").replace("\xa0", "").replace(",", ".")
                try:
                    price_val = float(clean_num)
                except ValueError:
                    price_val = None
            elif price_el and price_el.has_attr("content"):
                try:
                    price_val = float(price_el["content"])
                except ValueError:
                    price_val = None

            link_el = el.select_one("a.product_img_link, a.product-thumbnail, a[itemprop='url'], a[href*='/']")
            source_url = link_el["href"].strip() if link_el and link_el.has_attr("href") else ""
            if not source_url:
                parent_a = el.find_parent("a", href=True)
                if parent_a:
                    source_url = parent_a["href"].strip()

            if source_url:
                if source_url.startswith("//"):
                    source_url = "https:" + source_url
                elif base_url:
                    source_url = urljoin(base_url, source_url)

            if source_url and source_url in seen_urls:
                continue
            if source_url:
                seen_urls.add(source_url)

            img_el = el.select_one("img[itemprop='image'], img")
            img_url = ""
            if img_el:
                img_url = img_el.get("data-src") or img_el.get("src") or ""
                if img_url.startswith("//"):
                    img_url = "https:" + img_url
                elif img_url and base_url:
                    img_url = urljoin(base_url, img_url)

            # Amélioration qualité d'image PrestaShop (remplacement vignette home_default par thickbox_default si dispo)
            if "-home_default" in img_url:
                img_url = img_url.replace("-home_default", "-thickbox_default")

            # SKU déduit du conteneur (data-product-id, data-id-product, itemprop="sku") ou du titre
            sku = el.get("data-product-id") or el.get("data-id-product") or ""
            if not sku and el.select_one("[data-product-id]"):
                sku = el.select_one("[data-product-id]")["data-product-id"]
            if not sku:
                sku = el.select_one("[itemprop='sku']").get_text(strip=True) if el.select_one("[itemprop='sku']") else ""
            if not sku:
                sku = re.sub(r"[^A-Z0-9\-]", "", title.upper().replace(" ", "-"))[:25]
            if not sku:
                sku = f"PROD_{len(extracted) + 1:03d}"

            extracted.append(ScannedProductEntity(
                sku=sku,
                title=title,
                category_folder=folder_key,
                category_label=category_label,
                categories=[category_label],
                price_raw=price_text,
                price_ttc_eur=price_val,
                price_ht_eur=round(price_val / 1.2, 2) if price_val else None,
                unit="mètre linéaire (ml)" if "ml" in title.lower() or "mètre" in title.lower() else "unité",
                full_card_text=f"{title} | {price_text}",
                source_url=source_url,
                image_url=img_url,
            ))

        return extracted

    # ------------------------------------------------------------------ utilitaires
    def _cards_from_images(
        self,
        soup,
        prod_imgs,
        folder_key,
        category_label,
        strict: bool,
        base_url: str = "",
    ) -> List[ScannedProductEntity]:
        """
        Remonte de l'image à sa carte DOM, puis lit titre, prix, unité, SKU.
        strict=True  : reproduit exactement le comportement historique (lien obligatoire,
                       pas de dédoublonnage par SKU — le dédoublonnage est fait par le Use Case).
        strict=False : tolérant (lien facultatif) et dédoublonne les SKU.
        """
        extracted: List[ScannedProductEntity] = []
        seen_skus: Set[str] = set()
        for img in prod_imgs:
            src = img.get("data-src") or img.get("src") or ""
            if not src:
                continue
            p1 = img.parent
            p2 = p1.parent if p1 else None
            p3 = p2.parent if p2 else None
            p4 = p3.parent if p3 else None
            card = (p4 or p3 or p2) if strict else (p4 or p3 or p2 or p1)
            if not card:
                continue

            a_tag = img.find_parent("a") or card.find("a", href=True)
            href = a_tag["href"] if a_tag and a_tag.has_attr("href") else ""
            if strict and not href:
                continue

            raw_parts = [p.strip() for p in card.get_text("\n", strip=True).split("\n") if p.strip()]
            if not raw_parts:
                continue

            title = raw_parts[0]
            for part in raw_parts:
                if len(part) > 8 and "€" not in part and "À partir de" not in part and "TTC" not in part:
                    title = part
                    break

            full_text = " | ".join(raw_parts)
            price_match = re.search(r"([0-9]+(?:[,\.][0-9]{2})?)\s*€", full_text)
            price_str = price_match.group(0) if price_match else "Sur devis"
            price_val = float(price_match.group(1).replace(",", ".")) if price_match else None

            unit = "unité"
            low = full_text.lower()
            if "mètre linéaire" in low or "/ml" in low:
                unit = "mètre linéaire (ml)"
            elif "m²" in low or "m2" in low:
                unit = "m²"

            img_base = os.path.splitext(os.path.basename(urlparse(src).path))[0]
            sku = img_base.upper() or f"ITEM_{len(extracted) + 1:04d}"
            if not strict:
                if sku in seen_skus:
                    continue
                seen_skus.add(sku)

            resolved_href = urljoin(base_url, href) if (href and base_url) else href
            resolved_src = urljoin(base_url, src) if (src and base_url) else src

            extracted.append(ScannedProductEntity(
                sku=sku, title=title, category_folder=folder_key, category_label=category_label,
                categories=[category_label], price_raw=price_str, price_ttc_eur=price_val,
                price_ht_eur=round(price_val / 1.2, 2) if price_val else None, unit=unit,
                full_card_text=full_text, source_url=resolved_href, image_url=resolved_src,
            ))
        return extracted

    def _cards_from_jsonld(self, soup, folder_key, category_label, base_url: str = "") -> List[ScannedProductEntity]:
        """Lit les blocs <script type="application/ld+json"> de type Product."""
        extracted: List[ScannedProductEntity] = []
        seen: Set[str] = set()
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                raw = json.loads(script.string or "{}")
            except (json.JSONDecodeError, TypeError):
                continue
            for item in (raw if isinstance(raw, list) else [raw]):
                if not isinstance(item, dict) or item.get("@type") != "Product":
                    continue
                title = str(item.get("name") or "Produit")
                sku = str(item.get("sku") or item.get("productID") or title).upper()
                if sku in seen:
                    continue
                seen.add(sku)
                offers = item.get("offers", {})
                if isinstance(offers, list) and offers:
                    offers = offers[0]
                try:
                    price_val = float(offers.get("price")) if isinstance(offers, dict) and offers.get("price") else None
                except (TypeError, ValueError):
                    price_val = None
                img_url = item.get("image")
                if isinstance(img_url, list) and img_url:
                    img_url = img_url[0]
                price_str = f"{price_val} €" if price_val is not None else "Sur devis"
                resolved_url = urljoin(base_url, str(item.get("url") or "")) if (item.get("url") and base_url) else str(item.get("url") or "")
                resolved_img = urljoin(base_url, str(img_url or "")) if (img_url and base_url) else str(img_url or "")
                extracted.append(ScannedProductEntity(
                    sku=sku, title=title, category_folder=folder_key, category_label=category_label,
                    categories=[category_label], price_raw=price_str, price_ttc_eur=price_val,
                    price_ht_eur=round(price_val / 1.2, 2) if price_val else None, unit="unité",
                    full_card_text=f"{title} | {price_str}", source_url=resolved_url,
                    image_url=resolved_img,
                ))
        return extracted
