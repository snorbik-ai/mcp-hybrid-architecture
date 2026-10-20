#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
========================================================================================
GESTIONNAIRE DU CONTEXTE LLM & HISTORIQUE MÉMOIRE D'AGENT CODING
========================================================================================
Rôle :
1. Charge le fichier manifeste context_llm.json servant de GPS à l'Agent IA.
2. Archive chaque tour de l'agent dans history/sessions/YYYY-MM-DD/turn_XX/turn_report.json
   (avec support natif Windows Long Path \\?\ pour éviter WinError 206).
3. Maintient une fenêtre glissante stricte de 30 tours dans context_llm.json.
4. Assure la compression sémantique et la persistance entre les sessions de dev.

Auteur : BatiHome / AXESTEEL Engineering Team
========================================================================================
"""

import os
import json
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


def _to_os_safe_path(path: Path) -> Path:
    """
    Convertit un chemin absolu en chemin étendu Windows (\\\\?\\) sur OS Windows
    afin d'éviter l'erreur WinError 206 (limite 248 chars sur CreateDirectoryW).
    """
    resolved = str(path.resolve())
    if os.name == "nt" and not resolved.startswith("\\\\?\\"):
        return Path("\\\\?\\" + resolved)
    return Path(resolved)


class ContextHistoryManager:
    """
    Gestionnaire officiel du cycle de vie du contexte et de la mémoire de l'Agent Coding.
    """

    MAX_HISTORY_TURNS = 30

    def __init__(self, context_file_path: Path):
        self.context_file = _to_os_safe_path(Path(context_file_path))
        self.base_dir = self.context_file.parent
        self.history_dir = self.base_dir / "history" / "sessions"
        self._ensure_structure()

    def _ensure_structure(self):
        """Crée l'arborescence history/sessions si inexistante."""
        os.makedirs(str(self.history_dir), exist_ok=True)

    def load_context(self) -> Dict[str, Any]:
        """Charge le GPS de contexte LLM."""
        if not os.path.exists(str(self.context_file)):
            raise FileNotFoundError(f"Fichier de contexte introuvable : {self.context_file}")
        with open(str(self.context_file), "r", encoding="utf-8") as f:
            return json.load(f)

    def get_todays_session_dir(self) -> Path:
        """Renvoie le chemin du dossier de session daté du jour."""
        today_str = datetime.date.today().isoformat()
        session_dir = self.history_dir / today_str
        os.makedirs(str(session_dir), exist_ok=True)
        return session_dir

    def get_next_turn_id(self, session_dir: Path) -> str:
        """Détermine l'identifiant du prochain tour (ex: turn_01, turn_02)."""
        existing_turns = [
            entry.name
            for entry in os.scandir(str(session_dir))
            if entry.is_dir() and entry.name.startswith("turn_")
        ]
        count = len(existing_turns) + 1
        return f"turn_{count:02d}"

    def record_turn(
        self,
        goal: str,
        actions_performed: List[str],
        semantic_summary: str,
        errors_encountered: Optional[List[str]] = None,
        next_recommended_step: str = ""
    ) -> Dict[str, Any]:
        """
        Enregistre le compte rendu d'un tour dans l'arborescence et met à jour context_llm.json.
        """
        session_dir = self.get_todays_session_dir()
        turn_id = self.get_next_turn_id(session_dir)
        turn_dir = session_dir / turn_id
        os.makedirs(str(turn_dir), exist_ok=True)

        report = {
            "turn_id": turn_id,
            "session_date": datetime.date.today().isoformat(),
            "timestamp": datetime.datetime.now().isoformat(),
            "goal": goal,
            "actions_performed": actions_performed,
            "semantic_summary": semantic_summary,
            "errors_encountered": errors_encountered or [],
            "next_recommended_step": next_recommended_step,
            "status": "ERROR" if errors_encountered else "SUCCESS"
        }

        # 1. Sauvegarde du rapport individuel de tour sur disque
        report_file = turn_dir / "turn_report.json"
        with open(str(report_file), "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # 2. Mise à jour de la mémoire glissante dans context_llm.json (30 tours max)
        self._update_context_dynamic_history(report)

        return report

    def _update_context_dynamic_history(self, new_report: Dict[str, Any]):
        """Injecte le tour dans la liste dynamic_history en tronquant aux 30 derniers."""
        context = self.load_context()
        if "context_history" not in context:
            context["context_history"] = {
                "static_history": [],
                "dynamic_history": [],
                "max_retained_turns": self.MAX_HISTORY_TURNS
            }

        dynamic_history = context["context_history"].get("dynamic_history", [])

        compact_entry = {
            "session_date": new_report["session_date"],
            "turn_id": new_report["turn_id"],
            "goal": new_report["goal"],
            "semantic_summary": new_report["semantic_summary"],
            "status": new_report["status"]
        }

        dynamic_history.append(compact_entry)

        if len(dynamic_history) > self.MAX_HISTORY_TURNS:
            dynamic_history = dynamic_history[-self.MAX_HISTORY_TURNS:]

        context["context_history"]["dynamic_history"] = dynamic_history

        with open(str(self.context_file), "w", encoding="utf-8") as f:
            json.dump(context, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Gestionnaire de contexte et d'historique de tour Agent Coding")
    parser.add_argument("--context-file", required=True, help="Chemin vers context_llm.json")
    parser.add_argument("--record-demo", action="store_true", help="Génère un tour exemple pour valider le pipeline")
    args = parser.parse_args()

    manager = ContextHistoryManager(Path(args.context_file))
    if args.record_demo:
        rep = manager.record_turn(
            goal="Validation du pipeline MCP Agent Coding & archivage de session",
            actions_performed=[
                "Lecture du GPS context_llm.json",
                "Exécution nominale des Use Cases Clean Architecture",
                "Archivage de turn_report.json et mise à jour de dynamic_history (fenêtre 30 tours)"
            ],
            semantic_summary="Pipeline MCP Agent Coding et mémoire glissante 30 tours validés avec succès (0 erreur).",
            next_recommended_step="Prêt pour le prochain tour d'Agent Coding"
        )
        print(f"✅ Tour enregistré avec succès dans {rep['turn_id']} ({rep['session_date']}) !")
