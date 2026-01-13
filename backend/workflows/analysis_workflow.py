from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Optional

import importlib


@dataclass
class AnalysisState:
    project_id: Optional[str]
    text: str
    parsed: Optional[Dict[str, Any]] = None
    analysis: Optional[Dict[str, Any]] = None
    user_stories: Optional[Dict[str, Any]] = None


class AnalysisWorkflow:
    """Minimal orchestrator-like workflow: sequential parser, parallel detectors, user story generation, aggregate."""

    def __init__(self) -> None:
        # Lazy import to avoid heavy deps failing during simple imports
        try:
            ParserAgent = importlib.import_module("agents.requirements.parser_agent").ParserAgent
            self.parser = ParserAgent()
        except Exception:
            # Minimal stub parser if spaCy is unavailable
            class _StubParser:
                async def parse(self, text: str):
                    return type("Parsed", (), {
                        "actors": [],
                        "actions": [],
                        "entities": []
                    })()
            self.parser = _StubParser()

        AmbiguityAgent = importlib.import_module("agents.requirements.ambiguity_agent").AmbiguityAgent
        CompletenessAgent = importlib.import_module("agents.requirements.completeness_agent").CompletenessAgent
        EthicsAgent = importlib.import_module("agents.requirements.ethics_agent").EthicsAgent
        UserStoryAgent = importlib.import_module("agents.user_stories.user_story_agent").UserStoryAgent

        self.ambiguity = AmbiguityAgent()
        self.completeness = CompletenessAgent()
        self.ethics = EthicsAgent()
        self.user_story = UserStoryAgent()

    async def run(self, project_id: Optional[str], text: str) -> AnalysisState:
        state = AnalysisState(project_id=project_id, text=text)

        # Step 1: Parse (sequential)
        parsed = await self.parser.parse(text)
        state.parsed = {
            "actors": parsed.actors,
            "actions": parsed.actions,
            "entities": parsed.entities,
        }

        # Step 2: Parallel detection
        amb_task = asyncio.create_task(self.ambiguity.detect(text))
        comp_task = asyncio.create_task(self.completeness.check(text, state.parsed))
        eth_task = asyncio.create_task(self.ethics.audit(text))

        amb_res, comp_res, eth_res = await asyncio.gather(amb_task, comp_task, eth_task)

        # Calculate overall quality score (weighted average)
        # Ambiguity: 35%, Completeness: 40%, Ethics: 25%
        overall_quality = (
            amb_res.score * 0.35 +
            comp_res.completeness_score * 0.40 +
            eth_res.ethics_score * 0.25
        )

        state.analysis = {
            "ambiguity": {
                "score": amb_res.score,
                "issues": [
                    {
                        "term": i.term,
                        "explanation": i.explanation,
                        "suggestions": i.suggestions,
                    }
                    for i in amb_res.issues
                ],
            },
            "completeness": {
                "score": comp_res.completeness_score,
                "missing": [
                    {
                        "category": i.category,
                        "description": i.description,
                        "severity": i.severity,
                        "suggestion": i.suggestion,
                    }
                    for i in comp_res.missing_items
                ],
            },
            "ethics": {
                "score": eth_res.ethics_score,
                "issues": [
                    {
                        "type": i.type,
                        "category": i.category,
                        "description": i.description,
                        "severity": i.severity,
                    }
                    for i in eth_res.issues
                ],
            },
            "overall_quality_score": overall_quality,
            "api_used": {
                "parser": getattr(parsed, 'api_used', 'groq'),
                "ambiguity": getattr(amb_res, 'api_used', 'groq'),
                "completeness": getattr(comp_res, 'api_used', 'groq'),
                "ethics": getattr(eth_res, 'api_used', 'groq'),
            }
        }

        # Step 3: Generate user stories (after analysis is complete)
        try:
            story_res = await self.user_story.generate(
                requirement_text=text,
                parsed_entities=state.parsed,
                analysis_findings=state.analysis
            )
            
            state.user_stories = {
                "stories": [
                    {
                        "title": s.title,
                        "story": s.story,
                        "acceptance_criteria": s.acceptance_criteria,
                        "priority": s.priority,
                        "story_points": s.story_points,
                        "tags": s.tags,
                    }
                    for s in story_res.user_stories
                ],
                "total_stories": story_res.total_stories,
            }
            
            # Track API usage for user stories
            state.analysis["api_used"]["user_stories"] = "groq"
        except Exception:
            # Non-blocking: if user story generation fails, continue with analysis
            state.user_stories = {
                "stories": [],
                "total_stories": 0,
            }
            state.analysis["api_used"]["user_stories"] = "fallback"

        return state





