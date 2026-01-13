"""
Requirements Analysis Agents

This module contains specialized agents for analyzing software requirements:
- ParserAgent: Extracts entities, actors, actions from requirements
- AmbiguityAgent: Detects ambiguous terms and suggests clarifications
- CompletenessAgent: Identifies missing aspects and gaps
- EthicsAgent: Evaluates ethical considerations and potential biases
- OrchestratorAgent: Coordinates the entire analysis workflow
"""

from .parser_agent import ParserAgent, ParsedRequirements
from .ambiguity_agent import AmbiguityAgent, AmbiguityIssue, AmbiguityResult
from .completeness_agent import CompletenessAgent, CompletenessItem, CompletenessResult
from .ethics_agent import EthicsAgent, EthicsIssue, EthicsResult
from .orchestrator_agent import OrchestratorAgent, OrchestratorResult

__all__ = [
    # Parser
    "ParserAgent",
    "ParsedRequirements",
    # Ambiguity
    "AmbiguityAgent",
    "AmbiguityIssue",
    "AmbiguityResult",
    # Completeness
    "CompletenessAgent",
    "CompletenessItem",
    "CompletenessResult",
    # Ethics
    "EthicsAgent",
    "EthicsIssue",
    "EthicsResult",
    # Orchestrator
    "OrchestratorAgent",
    "OrchestratorResult",
]
