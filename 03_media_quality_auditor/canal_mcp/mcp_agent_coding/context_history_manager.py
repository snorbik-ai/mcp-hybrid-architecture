#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
GESTIONNAIRE AUTONOME DU CONTEXTE LLM & HISTORIQUE MÉMOIRE D'AGENT CODING (30 TOURS)
Embarqué directement dans 03_media_quality_auditor pour garantir ZÉRO dépendance externe.
"""

import os
import json
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


def _to_os_safe_path(path: Path) -> Path:
    resolved = str(path.resolve())
    if os.name == "nt" and not resolved.startswith("\\\\?\\"):
        return Path("\\\\?\\" + resolved)
    return Path(resolved)


class ContextHistoryManager:
    MAX_HISTORY_TURNS = 30

    def __init__(self, context_file_path: Path):
        self.context_file = _to_os_safe_path(Path(context_file_path))
        self.base_dir = self.context_file.parent
        self.history_dir = self.base_dir / "history" / "sessions"
        os.makedirs(str(self.history_dir), exist_ok=True)

    def load_context(self) -> Dict[str, Any]:
        with open(str(self.context_file), "r", encoding="utf-8") as f:
            return json.load(f)

    def get_todays_session_dir(self) -> Path:
        today_str = datetime.date.today().isoformat()
        session_dir = self.history_dir / today_str
        os.makedirs(str(session_dir), exist_ok=True)
        return session_dir

    def get_next_turn_id(self, session_dir: Path) -> str:
        existing_turns = [
            entry.name
            for entry in os.scandir(str(session_dir))
            if entry.is_dir() and entry.name.startswith("turn_")
        ]
        return f"turn_{len(existing_turns) + 1:02d}"

    def record_turn(
        self,
        goal: str,
        actions_performed: List[str],
        semantic_summary: str,
        errors_encountered: Optional[List[str]] = None,
        next_recommended_step: str = ""
    ) -> Dict[str, Any]:
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

        with open(str(turn_dir / "turn_report.json"), "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        context = self.load_context()
        if "context_history" not in context:
            context["context_history"] = {"static_history": [], "dynamic_history": [], "max_retained_turns": self.MAX_HISTORY_TURNS}
        dynamic_history = context["context_history"].get("dynamic_history", [])
        dynamic_history.append({
            "session_date": report["session_date"],
            "turn_id": report["turn_id"],
            "goal": report["goal"],
            "semantic_summary": report["semantic_summary"],
            "status": report["status"]
        })
        context["context_history"]["dynamic_history"] = dynamic_history[-self.MAX_HISTORY_TURNS:]

        with open(str(self.context_file), "w", encoding="utf-8") as f:
            json.dump(context, f, indent=2, ensure_ascii=False)

        return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--context-file", default=str(Path(__file__).resolve().parent / "context_llm.json"))
    parser.add_argument("--record-demo", action="store_true")
    args = parser.parse_args()

    mgr = ContextHistoryManager(Path(args.context_file))
    if args.record_demo:
        rep = mgr.record_turn(
            goal="Validation autonome de l'historique Agent Coding 30 tours (Outil #03)",
            actions_performed=["Lecture de context_llm.json", "Exécution des 4 couches de tests", "Archivage turn_report.json"],
            semantic_summary="Cycle de vie Agent Coding validé en autonomie complète (0 dépendance externe).",
            next_recommended_step="Prêt pour le prochain tour"
        )
        print(f"✅ Tour autonome enregistré : {rep['turn_id']} ({rep['session_date']})")
