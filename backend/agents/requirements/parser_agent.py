from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Dict, Any

import spacy


@dataclass
class ParsedRequirements:
    actors: List[str]
    actions: List[str]
    entities: List[str]
    constraints: List[str]
    dependencies: List[str]


class ParserAgent:
    def __init__(self) -> None:
        self.nlp = spacy.load("en_core_web_sm")
        self.hf_pipeline = None
        self._hf_loaded = False

    def _ensure_hf_pipeline(self):
        if self._hf_loaded:
            return

        # Optional HuggingFace NER pipeline
        self.enable_hf = False
        try:
            from transformers import pipeline  # type: ignore

            # Enable only if token provided to avoid rate limits in CI
            if os.getenv("HUGGINGFACE_API_KEY"):
                self.hf_pipeline = pipeline(
                    "ner",
                    model="dslim/bert-base-NER",
                    aggregation_strategy="simple",
                )
                self.enable_hf = True
        except Exception:
            self.enable_hf = False
        
        self._hf_loaded = True

    async def parse(self, text: str) -> ParsedRequirements:
        if not text or not text.strip():
            raise ValueError("Requirement text cannot be empty")

        doc = self.nlp(text)

        spacy_entities = [ent.text for ent in doc.ents]

        # Heuristic actor detection using common nouns and grammatical subjects
        actor_keywords = {
            "user",
            "admin",
            "administrator",
            "customer",
            "client",
            "manager",
            "operator",
            "moderator",
            "guest",
            "system",
        }
        noun_lemmas = [t.lemma_.lower() for t in doc if t.pos_ in {"NOUN", "PROPN"}]
        subject_lemmas = [t.lemma_.lower() for t in doc if t.dep_ in {"nsubj", "nsubjpass"}]
        actors_list: List[str] = []
        for lemma in noun_lemmas + subject_lemmas:
            if lemma in actor_keywords and lemma not in actors_list:
                actors_list.append(lemma)

        # Actions from verbs (lemmas), exclude auxiliaries and common nouns accidentally tagged
        action_exclude = actor_keywords
        actions_list = [
            t.lemma_.lower()
            for t in doc
            if t.pos_ == "VERB" and t.tag_ != "AUX" and t.lemma_.lower() not in action_exclude
        ]
        actions_list = list(dict.fromkeys(actions_list))

        # Entities: combine spaCy named entities and noun chunks
        noun_chunks = [chunk.text for chunk in doc.noun_chunks]
        entities: List[str] = list(
            dict.fromkeys([e.lower() for e in (spacy_entities + noun_chunks)])
        )

        # Optionally enrich entities with HF NER
        self._ensure_hf_pipeline()
        if self.enable_hf:
            try:
                hf_results: List[Dict[str, Any]] = self.hf_pipeline(text)  # type: ignore[attr-defined]
                hf_entities = [r.get("word", "").lower() for r in hf_results if r.get("word")]
                for ent in hf_entities:
                    if ent and ent not in entities:
                        entities.append(ent)
            except Exception:
                # Best-effort enrichment; ignore HF errors
                pass

        # Naive extraction for constraints/dependencies as placeholders
        constraints: List[str] = []
        dependencies: List[str] = []

        return ParsedRequirements(
            actors=actors_list,
            actions=actions_list,
            entities=entities,
            constraints=constraints,
            dependencies=dependencies,
        )


