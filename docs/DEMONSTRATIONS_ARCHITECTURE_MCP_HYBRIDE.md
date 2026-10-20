# Démonstrations Techniques de l'Architecture MCP Hybride
## Validation Opérationnelle sur le Prototype Contrôlé BatiHome & Données Étalons

> **Directive de référence :** DIRECTIVE CANONIQUE — Nettoyage des risques et validation (v1.0 - 20 octobre 2026)  
> **Prototype officiel de démonstration :** [https://batihome.snorbik.fr/#P01_home](https://batihome.snorbik.fr/#P01_home)  
> **Auteur :** Équipe d'Ingénierie BatiHome / AXESTEEL  
> **Statut :** Conforme aux règles d'accès éthiques, reproductible sans dépendance non autorisée  

---

## 🧭 Vue d'Ensemble des 5 Démonstrations

Les cinq exemples ci-dessous illustrent les mécanismes complémentaires de l'architecture hybride construite autour de MCP. Ils démontrent la valeur d'assemblage (déterminisme local, sorties digest-first, mémoire glissante, passerelle unifiée, intégration agent coding) sans prétendre modifier le protocole MCP standard.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   5 DÉMONSTRATIONS CANONIQUES                         │
│                                                                        │
│ 1. Exécution Déterministe Locale (Calcul TVA & Invariants Métier)       │
│ 2. Sortie Compacte « Digest-First » (Prototype BatiHome React SPA)     │
│ 3. Mémoire de Travail Glissante (Persistance & Rotation 30 Tours)      │
│ 4. Passerelle MCP Universelle (Découverte 17 Outils & Résolution Conflit)│
│ 5. Intégration Agent Coding Bout-en-Bout (Capitaine au Volant)         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📐 Démonstration 1 — Exécution Déterministe Locale

### 1. Objectif
Démontrer qu'une opération mathématique et métier (calculs de TVA à 20 %, prix HT/TTC, extraction de dimensions et métrés) est exécutée à coût nul de tokens par le moteur Python local, éliminant tout risque d'hallucination arithmétique par le LLM.

### 2. Entrée Contrôlée
* **Donnée d'entrée brute :** Chaîne textuelle non structurée issue du catalogue : `"Garde-corps Profil Aluminium Sol 2,5m - 289,00 € TTC / mètre"`.
* **Règle de calcul déterministe (Domain entity) :**
  $$\text{Prix HT} = \frac{\text{Prix TTC}}{1 + 0{,}20} = \frac{289{,}00}{1{,}20} = 240{,}8333... \rightarrow 240{,}83\text{ €}$$
  $$\text{Montant TVA} = \text{Prix TTC} - \text{Prix HT} = 48{,}17\text{ €}$$

### 3. Procédure & Commande
```bash
python outils_internes/04_ecommerce_catalog_scanner/tests/test_domain_product_card.py
```

### 4. Résultat Observé
* **Exactitude :** 100 % des calculs de conversion sont conformes aux arrondis bancaires ISO.
* **Consommation de tokens LLM pour le calcul :** **0 token**.
* **Tests unitaires associés :** 11/11 tests validés dans `tests/test_domain_product_card.py` et `tests/test_calculateur_metres.py`.

### 5. Limite Identifiée
Le moteur déterministe applique les règles codées dans le Domain. Si une devise exotique ou un taux de TVA réduit (10 % en rénovation) s'applique sans que l'invariant ne soit paramétré, le calcul par défaut reste à 20 %.

---

## ⚡ Démonstration 2 — Sortie Compacte « Digest-First »

### 1. Objectif
Comparer le volume d'informations transmis au modèle de langage entre une approche brute conventionnelle et l'approche hybride *Digest-First* sur le prototype contrôlé BatiHome.

### 2. Périmètre de Test
* **URL officielle :** `https://batihome.snorbik.fr/#P01_home` (Application monopage React + Vite).
* **Données extraites :** 14 fiches solutions et composants de garde-corps verre.

### 3. Procédure & Commande
```bash
python outils_internes/04_ecommerce_catalog_scanner/canal_sdk_cli/cli.py --url https://batihome.snorbik.fr/#P01_home
```

### 4. Mesures Comparatives

| Grandeur mesurée | Approche Conventionnelle (Dump Brut) | Approche Hybride Digest-First | Écart / Réduction |
| :--- | :---: | :---: | :---: |
| **Charge utile transmise au LLM** | 8 146 caractères (JSON complet) | 284 caractères (Digest sémantique) | **-96,5 %** |
| **Tokens estimés (`cl100k_base` $\approx 3,8$ car/token)** | ~2 143 tokens | ~75 tokens | **-2 068 tokens** |
| **Informations conservées dans le Digest** | Toutes (avec bruit) | Statut, domaine, total fiches (14), aperçu de 3 SKUs, lien vers rapport HTML | Essentiel décisionnel |
| **Accès aux données complètes** | Dans le contexte | Persistées sur disque (`output/scan_batihome_snorbik_fr_catalogue.json`) | Traçabilité physique |

### 5. Nuance Méthodologique
L'économie de tokens est estimée via le ratio standard `cl100k_base` de 3,8 caractères par token. Ce test prouve qu'un digest de décision soulage le contexte du modèle sans perdre la disponibilité physique des données complètes sur disque.

---

## 🧠 Démonstration 3 — Mémoire de Travail Glissante

### 1. Objectif
Démontrer la persistance et la continuité d'un chantier entre plusieurs étapes d'un agent, via un historique glissant limité à 30 tours, indépendant de la mémoire volatile de session du client.

### 2. Procédure & Commande
```bash
python outils_internes/04_ecommerce_catalog_scanner/canal_mcp/mcp_agent_coding/context_history_manager.py
```

### 3. Propriétés Vérifiées
1. **Persistance physique :** Chaque tour génère un fichier structuré `history/sessions/YYYY-MM-DD/turn_XX/turn_report.json` contenant :
   * Le but (`goal`),
   * Les actions effectuées (`actions_taken`),
   * Le résumé sémantique compact (`semantic_summary`),
   * Les anomalies éventuelles (`errors_detected`),
   * L'étape recommandée suivante (`next_recommended_step`).
2. **Rotation de la fenêtre glissante :** Le tableau `dynamic_history` dans `context_llm.json` est borné à 30 entrées. Le 31e tour archive le plus ancien sur disque, maintenant l'empreinte mémoire du prompt système constante (~100 tokens).
3. **Comportement après redémarrage :** À l'initialisation, le module recharge l'état à partir du disque. Si le fichier est absent, un fichier vierge conforme au schéma est créé sans crash.

### 4. Limite Identifiée
Cette mémoire de travail est une solution applicative hébergée sur le système de fichiers local ; elle ne constitue pas une fonctionnalité native du protocole réseau MCP.

---

## 🚪 Démonstration 4 — Passerelle MCP & Résolution de Collisions

### 1. Objectif
Démontrer l'exposition standardisée des outils via MCP (`stdio` et passerelle Streamable HTTP) et la résolution automatique des collisions de noms entre les différents serveurs de l'architecture.

### 2. Procédure & Commande
```bash
# Lancement de la passerelle HTTP universelle
python outils_internes/mcp_shared/mcp_http_gateway.py --port 5185
```

Vérification de la découverte des outils :
```bash
python -c "
import urllib.request, json
req = urllib.request.Request('http://127.0.0.1:5185/mcp/v1/tools')
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())
    print('Total outils découverts :', len(data.get('tools', [])))
"
```

### 3. Résultat Observé
* **Résolution de collision :** 4 serveurs partageaient un outil de même nom (`run_quality_and_tests_suite`). La passerelle a scopé automatiquement ces outils (`01_run_quality_and_tests_suite`, `02_...`).
* **Catalogue unifié :** Exactement **17 outils distincts** sont découverts, documentés avec leur `inputSchema` JSON valide et exécutables par requête JSON-RPC.

---

## 🤖 Démonstration 5 — Intégration Agent Coding Bout-en-Bout

### 1. Objectif
Démontrer le fonctionnement en conditions réelles où un agent IA externe consomme le plan directeur (`context_llm.json`), invoque l'outil via la Porte A (MCP Gateway Lifecycle) ou la Porte B (CLI), reçoit la télémétrie de décision, et poursuit sa tâche.

### 2. Scénario de Test
1. **Étape 1 (Initialisation) :** L'agent lit `context_llm.json` et découvre les use cases autorisés.
2. **Étape 2 (Scan) :** L'agent exécute `run_agent_lifecycle` avec `use_case="scan_ecommerce_catalog"` et l'URL du prototype BatiHome.
3. **Étape 3 (Digest & Persistance) :** Le moteur exécute le scan en local, persiste le rapport HTML autonome, consigne `turn_report.json`, et renvoie le digest (75 tokens).
4. **Étape 4 (Audit Ciblé) :** L'agent demande des statistiques détaillées sans réinjecter le HTML (`use_case="audit_scanned_catalog"`).
5. **Étape 5 (Validation) :** L'état du chantier est préservé, avec traçabilité complète sur disque.

### 3. Statut de Validation
* **Suite de non-régression locale :** **52/52 tests réussis** sur l'environnement de développement.
* **Validation en environnement conteneurisé vierge :** Documentée comme étape ultérieure dans la feuille de route.

---

## 📋 Synthèse de Conformité Éthique & Juridique

| Règle de la Directive Canonique | Statut d'implémentation | Preuve |
| :--- | :---: | :--- |
| **Zéro tentative de contournement anti-bot tiers** | **Conforme** | Retrait de tout test intrusif ou non autorisé. Utilisation exclusive du prototype contrôlé BatiHome et de jeux de données locaux. |
| **Données de test autorisées et reproductibles** | **Conforme** | `https://batihome.snorbik.fr/#P01_home` et `data/catalogue_reference.json`. |
| **Précision des benchmarks** | **Conforme** | Les tokens sont explicitement indiqués comme des estimations calculées via le ratio 3,8 car/token `cl100k_base`. |
| **Absence de chemins machine locaux** | **Conforme** | Chemins relatifs standardisés pour toute la suite documentaire. |
