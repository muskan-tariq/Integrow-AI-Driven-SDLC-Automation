from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class AmbiguityIssue:
    term: str
    explanation: str
    suggestions: List[str]


@dataclass
class AmbiguityResult:
    issues: List[AmbiguityIssue]
    score: float  # lower is more ambiguous


class AmbiguityAgent:
    def __init__(self) -> None:
        self.groq_enabled = os.getenv("GROQ_API_KEY") is not None
        self._client = None
        if self.groq_enabled:
            try:
                from groq import Groq  # type: ignore

                self._client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            except Exception:
                self.groq_enabled = False

        # Common vague terms to catch locally as fallback
        self._vague_terms = [
            (r"\bfast\b", "'fast' is subjective.", ["<100ms", "<1s", "<5s"]),
            (r"\bquick(ly)?\b", "'quick' is subjective.", ["within 2 seconds"]),
            (r"\bsecure\b", "'secure' needs measures.", ["TLS 1.3", "OWASP ASVS L2"]),
            (r"\breliable\b", "'reliable' needs SLO.", ["99.9% uptime", "MTTR < 1h"]),
            (r"\buser[- ]?friendly\b", "Subjective term.", ["SUS > 80", "task success > 95%"]),
        ]

    async def detect(self, text: str) -> AmbiguityResult:
        if not text or not text.strip():
            return AmbiguityResult(issues=[], score=1.0)

        if self.groq_enabled and self._client is not None:
            try:
                prompt = self._build_prompt(text)
                response = self._client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=400,
                )
                content = response.choices[0].message.content
                issues = self._parse_llm_json(content)
                return self._to_result(issues)
            except Exception:
                # Fall back to local heuristics if API fails
                pass

        issues = self._local_detect(text)
        return self._to_result(issues)

    def _build_prompt(self, text: str) -> str:
        return (
            "Identify ambiguous terms in the requirement and respond with JSON only.\n"
            "Examples of ambiguous terms include subjective words like 'fast', 'secure', 'user-friendly'.\n"
            "Requirement:\n" + text + "\n\n"
            "Output JSON array of objects with keys term, explanation, suggestions (array)."
        )

    def _parse_llm_json(self, content: str) -> List[Dict[str, Any]]:
        try:
            data = json.loads(content)
            if isinstance(data, list):
                return data
        except Exception:
            # Try to extract JSON array substring
            match = re.search(r"\[(.|\n|\r)*\]", content)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    pass
        return []

    def _local_detect(self, text: str) -> List[Dict[str, Any]]:
        found: List[Dict[str, Any]] = []
        seen_terms = set()
        for pattern, explanation, suggestions in self._vague_terms:
            for m in re.finditer(pattern, text, flags=re.IGNORECASE):
                term = m.group(0).lower().strip()
                if term in seen_terms:
                    continue
                seen_terms.add(term)
                found.append({
                    "term": term,
                    "explanation": explanation,
                    "suggestions": suggestions,
                })
        return found

    def _to_result(self, raw_issues: List[Dict[str, Any]]) -> AmbiguityResult:
        issues = [
            AmbiguityIssue(
                term=str(item.get("term", "")).strip(),
                explanation=str(item.get("explanation", "")).strip(),
                suggestions=[str(s) for s in item.get("suggestions", [])],
            )
            for item in raw_issues
            if item.get("term")
        ]
        # Simple score: fewer issues -> closer to 1.0
        score = max(0.0, min(1.0, 1.0 - min(len(issues), 10) / 10.0))
        return AmbiguityResult(issues=issues, score=score)


