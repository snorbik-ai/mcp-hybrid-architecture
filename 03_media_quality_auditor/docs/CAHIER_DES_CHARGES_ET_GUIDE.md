# 📖 Cahier des Charges & Guide — Media Auditor & Quality Pipeline
## BatiHome Outil Interne : Audit, Qualification Haute Définition & Dédoublonnage Média

---

## 🧭 1. Introduction & Contexte Métier

Pour un site e-commerce de garde-corps architecturaux haut de gamme comme BatiHome, l'exigence visuelle est absolue.
Lors des phases d'importation de maquettes et de collecte d'actifs :
* Des **vignettes miniatures basse résolution (512×286 px)** sont fréquemment mélangées aux véritables rendus 3D architecturaux.
* Afficher une image de 512 px étirée en plein écran sur un écran d'ordinateur (1920 px) dégrade sévèrement l'image de marque (effet flou et pixelisé).
* Des **doublons** (fichiers renommés avec suffixes ` copy.jpg` ou hachages MD5 identiques) encombrent l'espace disque et créent des incohérences dans les carrousels.

Cet outil interne pérenne fournit une solution automatisée pour auditer, classifier et certifier les images selon les seuils de netteté de BatiHome (seuil de référence : `hero-terrasse.png` à 1536 × 1024 px).

---

## 🏛️ 2. Architecture Multi-Canal (Matrice 3 Canaux)

Conformément à la directive officielle BatiHome (`DIRECTIVE_DEVELOPPEMENT_OUTILS_INTERNES.md`), l'outil s'articule autour d'un **Core SDK Python** et expose 3 canaux d'exploitation :

```
                               ┌────────────────────────────────────────────────────────┐
                               │             MOTEUR CORE PYTHON (Pillow)                │
                               │        canal_sdk_cli/sdk.py (MediaAuditorPipeline)     │
                               └───────────────────────────┬────────────────────────────┘
                                                           │
        ┌──────────────────────────────────────────────────┼──────────────────────────────────────────────────┐
        ▼                                                  ▼                                                  ▼
┌──────────────────────────────┐                ┌──────────────────────────────┐                ┌──────────────────────────────┐
│           CANAL 1            │                │           CANAL 2            │                │           CANAL 3            │
│         SERVEUR MCP          │                │     INTERFACE GRAPHIQUE      │                │          SDK & CLI           │
│       (POUR L'IA & LLM)      │                │       (POUR L'HUMAIN)        │                │       (POUR LE DEV)          │
├──────────────────────────────┤                ├──────────────────────────────┤                ├──────────────────────────────┤
│ canal_mcp/mcp_server.py      │                │ canal_ui/server.py           │                │ canal_sdk_cli/cli.py         │
│ • audit_media_folder         │                │ • Dashboard local HTML5      │                │ • --candidates               │
│ • get_certified_hero_cands   │                │ • Filtres visuels HD         │                │ • --clean-duplicates         │
│ • clean_duplicate_media      │                │ • Port local : 5182          │                │ • --min-width / --min-height │
└──────────────────────────────┘                └──────────────────────────────┘                └──────────────────────────────┘
```

---

## 📋 3. Cahier des Charges Fonctionnel & Règles Métier

### 3.1. Règles de Qualification Visuelle
1. **Seuil Minimal HD pour le Hero** :
   - Largeur minimale : **1200 px**
   - Hauteur minimale : **700 px**
   - Tout fichier inférieur est étiqueté `REJECTED_LOW_RES` et exclu du Hero.
2. **Détection de Doublons** :
   - Calcul de l'empreinte cryptographique **MD5** du fichier binaire.
   - Détection des suffixes de copie du système d'exploitation (` copy.jpg`, ` copy.png`).
3. **Idempotence & Sécurité** :
   - L'audit est purement en lecture seule.
   - Les opérations de nettoyage disposent d'un mode `--dry-run` par défaut pour éviter toute suppression accidentelle.

---

## 🚀 4. Guide d'Exécution par Canal

### Canal 3 : Ligne de Commande (CLI)
```bash
# 1. Lister les candidats certifiés HD pour le Hero
python outils_internes/media_auditor_pipeline/canal_sdk_cli/cli.py --input frontend/public/images/hero --candidates

# 2. Rapport complet d'audit du dossier
python outils_internes/media_auditor_pipeline/canal_sdk_cli/cli.py --input frontend/public/images/hero

# 3. Purger les doublons (avec simulation)
python outils_internes/media_auditor_pipeline/canal_sdk_cli/cli.py --input frontend/public/images/hero --clean-duplicates --dry-run

# 4. Sortie JSON pour intégration dans un script
python outils_internes/media_auditor_pipeline/canal_sdk_cli/cli.py --input frontend/public/images/hero --json
```

### Canal 2 : Interface Web Locale (UI)
```bash
# Démarrer le micro-serveur local
python outils_internes/media_auditor_pipeline/canal_ui/server.py
```
Ouvrir ensuite le navigateur sur `http://localhost:5182`.
L'interface permet de visualiser les vignettes réelles, de filtrer les images par statut (`CERTIFIÉ HD`, `DOUBLON`, `TROP PETIT`) et de déclencher les purges en 1 clic.

### Canal 1 : Serveur MCP (Intelligence Artificielle & Antigravity)
Ajout dans le fichier `mcp_config.json` ou execution directe :
```json
{
  "mcpServers": {
    "batihome-media-auditor": {
      "command": "python",
      "args": [
        "c:/Users/ntpar/Dev_IT/Projet_depo/Projet_IA/ia-pilote-e_commerce_saas/01_e-commerce matériel construction mvp/batihome-ecommerce-garde-corps/outils_internes/media_auditor_pipeline/canal_mcp/mcp_server.py"
      ]
    }
  }
}
```

---

## 🛠️ 5. Bibliothèques Utilisées & Justifications

* **`Pillow (PIL)`** : Standard de référence en Python pour l'analyse d'images (`Image.open`, `.size`, `.format`, `.mode`). Permet de lire les métadonnées sans charger inutilement toute l'image en RAM.
* **`hashlib` (natif Python)** : Calcul d'empreinte MD5 par blocs de 64 Ko pour une détection de doublons ultra-rapide à coût mémoire nul.
* **`http.server` & `urllib.parse` (natifs Python)** : Micro-serveur Web pour le canal UI sans nécessiter Flask ou FastAPI, assurant une portabilité totale.
