#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #04 — E-COMMERCE CATALOG SCANNER PIPELINE (CLEAN ARCHITECTURE)
Couche : Core / Infrastructure (Générateur de Rapport HTML Interactif Autonome)
========================================================================================
Rôle :
Produit une page HTML5 interactive autonome (index_visualisation.html) dans le dossier
de livraison du scan. Permet à un utilisateur humain d'inspecter visuellement tous les
produits extraits (tableau dynamique, filtre instantané, panneau latéral d'aperçu d'image
au clic). 100 % vanilla HTML/CSS/JS (zéro CDN, zéro dépendance externe).
========================================================================================
"""

import os
from typing import List, Dict, Any


class HtmlCatalogReportAdapter:
    """Générateur de tableau de bord HTML autonome pour visualiser les résultats du scan."""

    @staticmethod
    def generate_html_report(
        output_html_path: str,
        catalog_json_rel_path: str,
        source_reference: str,
        vignettes: List[Dict[str, Any]],
        products: List[Dict[str, Any]]
    ) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(output_html_path)), exist_ok=True)

        rows_html = []
        for p in products:
            sku = p.get("sku", "")
            title = p.get("title", "")
            cat = p.get("category_label", p.get("category_folder", ""))
            price_ttc = f"{p['price_ttc_eur']:.2f} €" if p.get("price_ttc_eur") is not None else p.get("price_raw", "Sur devis")
            price_ht = f"{p['price_ht_eur']:.2f} €" if p.get("price_ht_eur") is not None else "—"
            img_url = p.get("image_url", "")
            unit = p.get("unit", "unité")

            img_cell = f'''<button class="preview-btn" onclick="openPreview('{img_url}', '{title.replace("'", "\\'")}')">👁️ Voir photo</button>''' if img_url else '<span class="no-img">Aucune</span>'

            rows_html.append(f'''
            <tr data-title="{title.lower()}" data-sku="{sku.lower()}" data-cat="{cat.lower()}">
                <td class="sku-cell"><code>{sku}</code></td>
                <td class="title-cell"><strong>{title}</strong></td>
                <td><span class="badge">{cat}</span></td>
                <td class="price-cell">{price_ttc}</td>
                <td class="price-ht-cell">{price_ht}</td>
                <td><span class="unit-tag">{unit}</span></td>
                <td class="action-cell">{img_cell}</td>
            </tr>
            ''')

        tbody_content = "\n".join(rows_html)
        total_count = len(products)

        html_template = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport de Scan E-Commerce — {total_count} Produits</title>
    <style>
        :root {{
            --primary: #0284c7;
            --bg: #0f172a;
            --card-bg: #1e293b;
            --text: #f8fafc;
            --muted: #94a3b8;
            --border: #334155;
            --accent: #22c55e;
            --font: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: var(--font);
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        header {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }}
        h1 {{ font-size: 1.4rem; font-weight: 700; color: #fff; }}
        .meta-info {{ font-size: 0.9rem; color: var(--muted); }}
        .stats-badge {{
            background: rgba(34, 197, 94, 0.15);
            color: var(--accent);
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 600;
            border: 1px solid rgba(34, 197, 94, 0.3);
        }}
        .toolbar {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 12px 16px;
            align-items: center;
        }}
        .search-input {{
            flex: 1;
            min-width: 250px;
            padding: 10px 14px;
            background: #0b1329;
            border: 1px solid var(--border);
            border-radius: 8px;
            color: #fff;
            font-size: 0.95rem;
        }}
        .search-input:focus {{ outline: 2px solid var(--primary); }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
            font-size: 0.92rem;
        }}
        th, td {{
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            background: #111c33;
            color: var(--muted);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.78rem;
            letter-spacing: 0.5px;
        }}
        tr:hover td {{ background: rgba(255, 255, 255, 0.02); }}
        .sku-cell code {{
            background: #0b1329;
            padding: 3px 6px;
            border-radius: 4px;
            color: #38bdf8;
            font-family: monospace;
        }}
        .badge {{
            background: #334155;
            color: #e2e8f0;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
        }}
        .price-cell {{ font-weight: 700; color: #fff; }}
        .price-ht-cell {{ color: #38bdf8; font-weight: 600; }}
        .unit-tag {{ color: var(--muted); font-size: 0.82rem; }}
        .preview-btn {{
            background: #0284c7;
            color: #fff;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85rem;
            font-weight: 500;
            transition: background 0.15s ease;
        }}
        .preview-btn:hover {{ background: #0369a1; }}
        .no-img {{ color: #64748b; font-size: 0.85rem; }}

        /* Panneau Latéral d'Aperçu Photo (Modal/Drawer) */
        #preview-drawer {{
            position: fixed;
            top: 0;
            right: -450px;
            width: 420px;
            height: 100vh;
            background: #111c33;
            border-left: 1px solid var(--border);
            box-shadow: -10px 0 30px rgba(0,0,0,0.5);
            transition: right 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            z-index: 1000;
        }}
        #preview-drawer.open {{ right: 0; }}
        .drawer-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 12px;
        }}
        .close-btn {{
            background: transparent;
            border: none;
            color: var(--muted);
            font-size: 1.5rem;
            cursor: pointer;
        }}
        .close-btn:hover {{ color: #fff; }}
        .image-container {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #080e1e;
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            padding: 12px;
        }}
        .image-container img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            border-radius: 4px;
        }}
    </style>
</head>
<body>

    <header>
        <div>
            <h1>📋 Rapport de Moissonnage E-Commerce</h1>
            <p class="meta-info">Source explorée : <code>{source_reference}</code> • Fichier brut : <a href="{catalog_json_rel_path}" style="color: #38bdf8;">{catalog_json_rel_path}</a></p>
        </div>
        <div class="stats-badge">✅ {total_count} Références Consolidées</div>
    </header>

    <div class="toolbar">
        <input type="text" id="searchInput" class="search-input" placeholder="🔍 Rechercher par mot-clé, référence SKU ou catégorie..." onkeyup="filterTable()">
        <span id="matchCount" style="font-size: 0.88rem; color: var(--muted);">{total_count} produits affichés</span>
    </div>

    <table>
        <thead>
            <tr>
                <th>Référence SKU</th>
                <th>Désignation Produit</th>
                <th>Catégorie Métier</th>
                <th>Prix TTC</th>
                <th>Prix Calculé HT</th>
                <th>Unité</th>
                <th>Visuel HD</th>
            </tr>
        </thead>
        <tbody id="catalogBody">
            {tbody_content}
        </tbody>
    </table>

    <div id="preview-drawer">
        <div class="drawer-header">
            <h3 id="drawerTitle" style="font-size: 1rem; color: #fff; line-height: 1.3;">Aperçu Photo</h3>
            <button class="close-btn" onclick="closePreview()">✕</button>
        </div>
        <div class="image-container">
            <img id="drawerImg" src="" alt="Aperçu Produit">
        </div>
        <p id="drawerUrl" style="font-size: 0.8rem; color: var(--muted); word-break: break-all;"></p>
    </div>

    <script>
        function filterTable() {{
            const input = document.getElementById('searchInput').value.toLowerCase();
            const rows = document.querySelectorAll('#catalogBody tr');
            let count = 0;
            rows.forEach(row => {{
                const title = row.getAttribute('data-title');
                const sku = row.getAttribute('data-sku');
                const cat = row.getAttribute('data-cat');
                if (title.includes(input) || sku.includes(input) || cat.includes(input)) {{
                    row.style.display = '';
                    count++;
                }} else {{
                    row.style.display = 'none';
                }}
            }});
            document.getElementById('matchCount').innerText = `${{count}} produits affichés`;
        }}

        function openPreview(url, title) {{
            document.getElementById('drawerTitle').innerText = title;
            document.getElementById('drawerImg').src = url;
            document.getElementById('drawerUrl').innerText = url;
            document.getElementById('preview-drawer').classList.add('open');
        }}

        function closePreview() {{
            document.getElementById('preview-drawer').classList.remove('open');
        }}
    </script>
</body>
</html>'''

        with open(output_html_path, "w", encoding="utf-8") as f:
            f.write(html_template)

        return os.path.abspath(output_html_path)
