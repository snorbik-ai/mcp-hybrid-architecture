# Canal 1 — Serveur MCP : Media Auditor & Quality Pipeline

Ce serveur MCP implémente le standard officiel Model Context Protocol (JSON-RPC 2.0 sur `stdio`).
Il permet aux agents d'IA (Antigravity, Claude, Cursor) d'exécuter des audits de résolution, de qualifier les images haute définition et de dédoublonner les actifs graphiques sans intervention humaine.

## Outils Exposés

1. `audit_media_folder` : Analyse exhaustive d'un dossier avec retour structuré JSON.
2. `get_certified_hero_candidates` : Retourne la liste des images respectant le standard HD BatiHome (≥ 1200×700 px).
3. `clean_duplicate_media` : Détecte et élimine les fichiers doublons (`MD5` identique ou suffixe ` copy`).

## Lancement
```bash
python mcp_server.py
```
