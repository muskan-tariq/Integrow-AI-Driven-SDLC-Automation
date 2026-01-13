"""
Integrow Agents Package

A modular collection of AI-powered agents for requirements engineering.

Organization:
- requirements/: Requirement analysis agents (parsing, ambiguity, completeness, ethics)
- user_stories/: User story generation and refinement agents
- integration/: External integration agents (Git, GitHub)
- uml/: UML diagram generation agents
"""

# Requirements Analysis Agents
from .requirements import (
    ParserAgent,
    ParsedRequirements,
    AmbiguityAgent,
    AmbiguityIssue,
    AmbiguityResult,
    CompletenessAgent,
    CompletenessItem,
    CompletenessResult,
    EthicsAgent,
    EthicsIssue,
    EthicsResult,
    OrchestratorAgent,
    OrchestratorResult,
)

# User Story Agents
from .user_stories import (
    UserStoryAgent,
    UserStory,
    UserStoryResult,
    StoryRefinementAgent,
    RefinementResult,
)

# Integration Agents
from .integration import (
    GitAgent,
    GitHubAgent,
)

# UML Diagram Agents
from .uml import (
    DiagramAnalyzer,
    DiagramAnalysisResult,
    ClassDiagramAgent,
    ClassDiagramResult,
)

__all__ = [
    # Requirements Analysis
    "ParserAgent",
    "ParsedRequirements",
    "AmbiguityAgent",
    "AmbiguityIssue",
    "AmbiguityResult",
    "CompletenessAgent",
    "CompletenessItem",
    "CompletenessResult",
    "EthicsAgent",
    "EthicsIssue",
    "EthicsResult",
    "OrchestratorAgent",
    "OrchestratorResult",
    # User Stories
    "UserStoryAgent",
    "UserStory",
    "UserStoryResult",
    "StoryRefinementAgent",
    "RefinementResult",
    # Integration
    "GitAgent",
    "GitHubAgent",
    # UML Diagrams
    "DiagramAnalyzer",
    "DiagramAnalysisResult",
    "ClassDiagramAgent",
    "ClassDiagramResult",
]