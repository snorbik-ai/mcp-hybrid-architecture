# 🚗 Outil Interne #03 : Auditeur Qualité Média HD & Moteur Dédoublonneur MD5 (`03_media_quality_auditor`)

> **Nom Industriel Évocateur Officiel :** Auditeur Qualité Média HD & Moteur Dédoublonneur MD5  
> **Répertoire Autonome :** `03_media_quality_auditor`  
> **Type d'architecture :** "Voiture Autonome" (100 % autonome, zéro dépendance externe)  
> **Conception :** Clean Architecture (`core/domain/` $\leftarrow$ `core/application/` $\leftarrow$ `core/infrastructure/`)  
> **Qualité & Tests :** 4 couches de tests (Unitaires, Intégration, Validation/Perf, Smoke) $\rightarrow$ **10/10 PASS**

---

## 📌 1. À quoi sert cet outil ? (Rôle & Vision)

Le **Media Quality Auditor** est le gardien de la qualité graphique et de la netteté visuelle du site e-commerce :
- **Avant cet outil** : Lors de la récupération d'images depuis des maquettes ou des flux tiers, des vignettes minuscules (300×200 px ou 512×286 px) étaient insérées par erreur dans les bannières Hero plein écran (1920 px), provoquant un rendu flou et dégradant l'image de marque. De plus, des doublons de fichiers (suffixés ` copy.jpg` ou strictement identiques en octets) saturaient l'espace disque.
- **Grâce à cet outil** :
  1. Il inspecte les dimensions réelles (largeur × hauteur), le mode de couleur et le format de chaque image via Pillow.
  2. Il certifie les images répondant aux exigences architecturales du Hero ($\ge 1200\times 700\text{px}$).
  3. Il classe les visuels en `VALID_HD`, `REJECTED_LOW_RES` ou `DUPLICATE`.
  4. Il calcule l'empreinte cryptographique **MD5** par blocs de 64 Ko pour détecter les doublons exacts et propose un nettoyage sécurisé (avec mode `--dry-run`).

---

## ⚙️ 2. Comment fonctionne-t-il ? (Sous le capot)

L'outil applique une **Clean Architecture** stricte :
- **Couche Domain (`core/domain/entities_and_ports.py`)** :
  - Entité métier `AuditedMediaEntity` (dimensions, aspect_ratio, poids Ko, statut, hash MD5, indicateur is_hd).
  - Port abstrait `IMediaInspectorPort`.
- **Couche Application / Use Cases (`core/application/use_cases.py`)** :
  - `AuditMediaDirectoryUseCase` : Audit exhaustif d'un dossier avec calcul des métriques et détection des doublons.
  - `CleanDuplicateMediaUseCase` : Purge sécurisée des doublons (avec simulation `dry_run` par défaut).
  - `GetCertifiedHeroCandidatesUseCase` : Sélection des meilleures images haute résolution triées par surface en pixels.
- **Couche Infrastructure (`core/infrastructure/`)** :
  - `PillowMd5InspectorAdapter` : Lecture des en-têtes d'images sans charger l'intégralité des pixels en mémoire, et hachage MD5 optimisé.

---

## 🚀 3. Comment l'utiliser ? (Guide Pratique Multi-Canal)

### A. Contrôle Qualité & Tests (Obligatoire avant utilisation)
Double-cliquez sur `run_tests.bat` ou lancez :
```bash
run_tests.bat
# ou avec Python :
python tests/run_all_suites.py
```
*Valide les 4 couches de tests et le benchmark de 100 hachages MD5 en moins de 70 ms.*

### B. Canal 1 — Pour les Intelligences Artificielles (MCP)
- **Variante A (MCP JSON-RPC Stdio)** : `python canal_mcp/mcp_classic_stdio/mcp_server.py`. Expose :
  - `audit_media_folder` : Analyse et qualifie les images d'un dossier.
  - `get_certified_hero_candidates` : Retourne la liste des images certifiées pour le Hero.
  - `clean_duplicate_media` : Nettoie les fichiers en doublon (avec `dry_run` activable).
  - `run_quality_and_tests_suite` : Exécution autonome des tests par l'IA.
- **Variante B (MCP Agent Coding)** : L'IA consulte [`canal_mcp/mcp_agent_coding/context_llm.json`](./canal_mcp/mcp_agent_coding/context_llm.json) et archive ses comptes rendus dans `history/sessions/` via `context_history_manager.py`.

### C. Canal 2 — Pour les Utilisateurs Humains (Interface Graphique Web UI)
```bash
python canal_ui/server.py --port 5182
```
Ouvrez `http://localhost:5182` dans votre navigateur :
- Visualisez les statistiques globales du dossier audité (Total, Valides HD, Rejetées, Doublons).
- Prévisualisez chaque image avec ses dimensions et son statut coloré.
- Nettoyez les doublons en 1 clic.

### D. Canal 3 — Pour les Développeurs & Scripts CLI
```bash
python canal_sdk_cli/cli.py --folder "frontend/public/assets/catalogue_verre" --min-width 1200 --min-height 700
```
Ou importez le SDK Python dans votre code :
```python
from canal_sdk_cli.sdk import MediaAuditorPipeline
auditor = MediaAuditorPipeline(default_min_width=1200, default_min_height=700)
report = auditor.audit_directory("frontend/public/assets/catalogue_verre")
print(f"Valides HD : {report['summary']['valid_hd']}, Doublons : {report['summary']['duplicates']}")
```
