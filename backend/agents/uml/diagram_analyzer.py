"""
Diagram Analyzer Agent

Analyzes user stories to extract UML-relevant elements:
- Classes/Entities (nouns)
- Methods/Actions (verbs)
- Relationships (associations, dependencies)
- Attributes (properties, fields)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Dict, Set, Any

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


@dataclass
class EntityInfo:
    """Information about an identified entity/class"""
    name: str
    mentions: int = 0
    methods: Set[str] = field(default_factory=set)
    attributes: Set[str] = field(default_factory=set)
    related_entities: Set[str] = field(default_factory=set)


@dataclass
class RelationshipInfo:
    """Information about a relationship between entities"""
    source: str
    target: str
    relationship_type: str  # "association", "composition", "aggregation", "inheritance"
    description: str = ""


@dataclass
class DiagramAnalysisResult:
    """Result of analyzing user stories for UML elements"""
    entities: Dict[str, EntityInfo]
    relationships: List[RelationshipInfo]
    actions: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class DiagramAnalyzer:
    """
    Analyzes user stories to extract UML class diagram elements.
    Uses NLP (spaCy) to identify entities, actions, and relationships.
    """

    def __init__(self):
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                self.nlp = None

        # Common relationship indicators
        self.relationship_patterns = {
            "composition": ["has", "contains", "owns", "composed of"],
            "aggregation": ["uses", "includes", "comprises"],
            "association": ["relates to", "associated with", "connected to", "works with"],
            "inheritance": ["is a", "extends", "inherits from", "type of"]
        }

    async def analyze(self, user_stories: List[Dict[str, Any]]) -> DiagramAnalysisResult:
        """
        Analyze user stories to extract UML elements.

        Args:
            user_stories: List of user story dicts with 'story', 'acceptance_criteria', etc.

        Returns:
            DiagramAnalysisResult with entities, relationships, and actions
        """
        if not user_stories:
            return DiagramAnalysisResult(entities={}, relationships=[], actions=[])

        entities: Dict[str, EntityInfo] = {}
        all_actions: Set[str] = set()
        relationships: List[RelationshipInfo] = []

        for story in user_stories:
            story_text = story.get("story", "")
            acceptance_criteria = story.get("acceptance_criteria", [])

            # Extract entities and actions from story
            story_entities, story_actions = self._extract_from_text(story_text)

            # Merge entities
            for entity_name in story_entities:
                if entity_name not in entities:
                    entities[entity_name] = EntityInfo(name=entity_name, mentions=1)
                else:
                    entities[entity_name].mentions += 1

            all_actions.update(story_actions)

            # Extract methods from acceptance criteria
            for criterion in acceptance_criteria:
                criterion_entities, criterion_actions = self._extract_from_text(criterion)

                # Associate actions with entities
                for entity_name in criterion_entities:
                    if entity_name in entities:
                        entities[entity_name].methods.update(criterion_actions)

                all_actions.update(criterion_actions)

            # Detect relationships
            story_relationships = self._detect_relationships(story_text, list(entities.keys()))
            relationships.extend(story_relationships)

        return DiagramAnalysisResult(
            entities=entities,
            relationships=relationships,
            actions=list(all_actions),
            metadata={
                "total_stories": len(user_stories),
                "entities_found": len(entities),
                "relationships_found": len(relationships)
            }
        )

    def _extract_from_text(self, text: str) -> tuple[Set[str], Set[str]]:
        """
        Extract entities (nouns) and actions (verbs) from text.

        Returns:
            Tuple of (entities, actions)
        """
        entities: Set[str] = set()
        actions: Set[str] = set()

        if not text:
            return entities, actions

        if self.nlp:
            # Use spaCy for advanced NLP
            doc = self.nlp(text)

            # Extract entities (nouns and proper nouns)
            for token in doc:
                if token.pos_ in ["NOUN", "PROPN"] and len(token.text) > 2:
                    # Capitalize and clean
                    entity = token.lemma_.strip().capitalize()
                    if entity and not entity.lower() in ["a", "an", "the", "this", "that"]:
                        entities.add(entity)

            # Extract actions (verbs, excluding auxiliaries)
            for token in doc:
                if token.pos_ == "VERB" and token.tag_ != "AUX":
                    action = token.lemma_.strip().lower()
                    if action and len(action) > 2:
                        actions.add(action)
        else:
            # Fallback: Simple regex-based extraction
            # Extract capitalized words as potential entities
            entity_matches = re.findall(r'\b[A-Z][a-z]+\b', text)
            entities.update(entity_matches)

            # Extract common verbs (basic pattern)
            verb_patterns = r'\b(create|update|delete|view|manage|add|remove|edit|send|receive|process|validate|login|logout|authenticate|authorize)\b'
            action_matches = re.findall(verb_patterns, text.lower())
            actions.update(action_matches)

        return entities, actions

    def _detect_relationships(self, text: str, entity_names: List[str]) -> List[RelationshipInfo]:
        """
        Detect relationships between entities based on text patterns.

        Args:
            text: Text to analyze
            entity_names: List of known entity names

        Returns:
            List of detected relationships
        """
        relationships: List[RelationshipInfo] = []
        text_lower = text.lower()

        # Check for relationship patterns between each pair of entities
        for i, source in enumerate(entity_names):
            for target in entity_names[i + 1:]:
                # Look for relationship indicators between entities
                for rel_type, patterns in self.relationship_patterns.items():
                    for pattern in patterns:
                        # Check if pattern appears between source and target
                        pattern1 = f"{source.lower()}.*{pattern}.*{target.lower()}"
                        pattern2 = f"{target.lower()}.*{pattern}.*{source.lower()}"

                        if re.search(pattern1, text_lower):
                            relationships.append(RelationshipInfo(
                                source=source,
                                target=target,
                                relationship_type=rel_type,
                                description=f"{source} {pattern} {target}"
                            ))
                            break
                        elif re.search(pattern2, text_lower):
                            relationships.append(RelationshipInfo(
                                source=target,
                                target=source,
                                relationship_type=rel_type,
                                description=f"{target} {pattern} {source}"
                            ))
                            break

        return relationships
