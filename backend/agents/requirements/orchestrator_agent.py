from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Optional

from workflows.analysis_workflow import AnalysisWorkflow


@dataclass
class OrchestratorResult:
    parsed: Dict[str, Any]
    analysis: Dict[str, Any]
    user_stories: Dict[str, Any]


class OrchestratorAgent:
    """Coordinates the analysis workflow. Adds simple retries for robustness."""

    def __init__(self, max_retries: int = 2) -> None:
        self.workflow = AnalysisWorkflow()
        self.max_retries = max_retries

    async def analyze(self, project_id: Optional[str], text: str) -> OrchestratorResult:
        last_err: Optional[Exception] = None
        for _ in range(self.max_retries + 1):
            try:
                state = await self.workflow.run(project_id, text)
                return OrchestratorResult(
                    parsed=state.parsed or {}, 
                    analysis=state.analysis or {},
                    user_stories=state.user_stories or {}
                )
            except Exception as e:
                last_err = e
                await asyncio.sleep(0.2)
                continue
        raise RuntimeError(f"Orchestration failed: {last_err}")



