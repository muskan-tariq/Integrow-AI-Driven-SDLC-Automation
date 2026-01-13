from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class CompletenessItem:
    category: str
    description: str
    severity: str
    suggestion: str


@dataclass
class CompletenessResult:
    missing_items: List[CompletenessItem]
    completeness_score: float


class CompletenessAgent:
    def __init__(self) -> None:
        self.dev_mode = os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.enabled = self.gemini_key is not None
        self._model = None

        if self.enabled and not self.dev_mode:
            try:
                import google.generativeai as genai  # type: ignore

                genai.configure(api_key=self.gemini_key)
                # Restrict to 2.5 family per project policy
                self._model = genai.GenerativeModel("gemini-2.5-flash")
            except Exception:
                self.enabled = False

    async def check(self, text: str, parsed_entities: Dict[str, Any]) -> CompletenessResult:
        if not text or not text.strip():
            return CompletenessResult(missing_items=[], completeness_score=1.0)

        # Dev mode or disabled – return heuristic-based analysis
        if self.dev_mode or not self.enabled or self._model is None:
            items = self._heuristic_items(text, parsed_entities)
            return self._to_result(items)

        prompt = self._build_prompt(text, parsed_entities)
        try:
            response = self._model.generate_content(prompt)
            content = getattr(response, "text", "") or ""
            items = self._parse_json_array(content)
            return self._to_result(items)
        except Exception:
            # Fallback to heuristic analysis on API errors/quota
            items = self._heuristic_items(text, parsed_entities)
            return self._to_result(items)

    def _build_prompt(self, text: str, parsed: Dict[str, Any]) -> str:
        return (
            "Analyze requirement completeness and output JSON array only with objects: "
            "{category, description, severity, suggestion}.\n\n"
            f"Requirement:\n{text}\n\n"
            f"Parsed: actors={parsed.get('actors')}, actions={parsed.get('actions')}, entities={parsed.get('entities')}\n\n"
            "Check for missing: error_handling, edge_cases, performance, security."
        )

    def _parse_json_array(self, content: str) -> List[Dict[str, Any]]:
        import json, re

        try:
            data = json.loads(content)
            if isinstance(data, list):
                return data
        except Exception:
            pass
        m = None
        try:
            m = re.search(r"\[(.|\n|\r)*\]", content)
        except Exception:
            m = None
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                return []
        return []

    def _heuristic_items(self, text: str, parsed: Dict[str, Any]) -> List[Dict[str, Any]]:
        lower = text.lower()
        items: List[Dict[str, Any]] = []

        def add(cat: str, desc: str, sev: str, sug: str) -> None:
            items.append({
                "category": cat,
                "description": desc,
                "severity": sev,
                "suggestion": sug,
            })

        if "error" not in lower and "fail" not in lower:
            add(
                "error_handling",
                "No error handling specified",
                "high",
                "Define behavior for failures and retries (e.g., 3 attempts).",
            )
        if "timeout" not in lower and "expiry" not in lower and "expire" not in lower:
            add(
                "edge_cases",
                "No session/operation timeout behavior defined",
                "medium",
                "Specify timeout values and what happens on timeout.",
            )
        if "ms" not in lower and "second" not in lower and "performance" not in lower:
            add(
                "performance",
                "No performance targets provided",
                "medium",
                "Add response time/SLA targets (e.g., p95 < 1s).",
            )
        if "auth" not in lower and "oauth" not in lower and "jwt" not in lower and "encrypt" not in lower:
            add(
                "security",
                "No authentication/authorization or data protection specified",
                "high",
                "Specify auth flow and encryption at rest/in transit.",
            )
        return items

    def _to_result(self, items: List[Dict[str, Any]]) -> CompletenessResult:
        parsed_items = [
            CompletenessItem(
                category=str(i.get("category", "")),
                description=str(i.get("description", "")),
                severity=str(i.get("severity", "medium")),
                suggestion=str(i.get("suggestion", "")),
            )
            for i in items
        ]
        # Simple scoring: more missing items => lower score
        score = max(0.0, min(1.0, 1.0 - min(len(parsed_items), 10) / 10.0))
        return CompletenessResult(missing_items=parsed_items, completeness_score=score)


