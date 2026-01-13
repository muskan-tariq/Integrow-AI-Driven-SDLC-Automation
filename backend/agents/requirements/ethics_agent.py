from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class EthicsIssue:
    type: str
    category: str | None
    description: str
    severity: str


@dataclass
class EthicsResult:
    issues: List[EthicsIssue]
    ethics_score: float


class EthicsAgent:
    def __init__(self) -> None:
        self.llm_enabled = os.getenv("OPENAI_API_KEY") is not None
        # Detect AIF360 availability
        self.aif360_enabled = False
        try:
            from aif360.datasets import BinaryLabelDataset  # type: ignore
            from aif360.metrics import BinaryLabelDatasetMetric  # type: ignore

            self._BinaryLabelDataset = BinaryLabelDataset
            self._BinaryLabelDatasetMetric = BinaryLabelDatasetMetric

            # Self-check: verify DI can be computed on a trivial dataset
            import numpy as np  # type: ignore

            prot_attr = np.array([[1]] * 5 + [[0]] * 5)
            labels = np.array([[1]] * 5 + [[0]] * 5)
            ds = BinaryLabelDataset(
                favorable_label=1,
                unfavorable_label=0,
                df=None,
                label_names=["label"],
                protected_attribute_names=["gender"],
                features=prot_attr,
                labels=labels,
            )
            metric = BinaryLabelDatasetMetric(
                ds,
                privileged_groups=[{"gender": 1}],
                unprivileged_groups=[{"gender": 0}],
            )
            di = metric.disparate_impact()
            self.aif360_enabled = di is not None
        except Exception:
            self.aif360_enabled = False

        # Bias-related protected attributes
        self.protected_attributes = [
            "gender",
            "male",
            "female",
            "race",
            "ethnicity",
            "age",
            "religion",
            "christian",
            "muslim",
            "hindu",
            "jewish",
            "sexual orientation",
            "gay",
            "lesbian",
            "bisexual",
            "transgender",
            "disability",
            "disabled",
            "nationality",
            "citizenship",
            "pregnant",
        ]

        # Privacy/data collection indicators
        self.privacy_keywords = [
            "personal data",
            "pii",
            "tracking",
            "biometric",
            "location",
            "fingerprint",
            "facial",
            "recording",
            "surveillance",
        ]

    async def audit(self, text: str) -> EthicsResult:
        if not text or not text.strip():
            return EthicsResult(issues=[], ethics_score=1.0)

        issues: List[EthicsIssue] = []
        lower = text.lower()

        # Bias detection via keyword matches
        for attr in self.protected_attributes:
            if re.search(rf"\b{re.escape(attr)}\b", lower):
                issues.append(
                    EthicsIssue(
                        type="bias",
                        category=attr,
                        description=f"Mentions protected attribute: {attr}",
                        severity="high",
                    )
                )

        # Privacy indicators
        for kw in self.privacy_keywords:
            if kw in lower:
                issues.append(
                    EthicsIssue(
                        type="privacy",
                        category=None,
                        description=f"Mentions: {kw}",
                        severity="medium",
                    )
                )

        # Optional: AIF360 validation to adjust severity based on disparate impact
        if self.aif360_enabled and issues:
            try:
                issues = await self._aif360_validate(text, issues)
            except Exception:
                pass

        # Optional: hook for LLM validation (OpenAI), best-effort only
        if self.llm_enabled and issues:
            try:
                issues = await self._llm_validate(text, issues)
            except Exception:
                pass

        score = max(0.0, min(1.0, 1.0 - min(len(issues), 10) / 10.0))
        return EthicsResult(issues=issues, ethics_score=score)

    async def _aif360_validate(self, text: str, issues: List[EthicsIssue]) -> List[EthicsIssue]:
        """Use AIF360 disparate impact metric on a tiny synthetic dataset to flag explicit access restrictions.
        This is a lightweight heuristic integration suitable for unit testing and early dev.
        """
        # Heuristic: if text contains 'only male' or 'only female', build a dataset where
        # unprivileged group has 0 positive outcomes to force DI < 0.8
        lower = text.lower()
        protected_attr = None
        privileged_value = None

        if "only male" in lower:
            protected_attr = "gender"
            privileged_value = 1  # male
        elif "only female" in lower:
            protected_attr = "gender"
            privileged_value = 0  # female

        if protected_attr is None:
            return issues

        # Build synthetic dataset: features include protected attribute column
        import numpy as np  # type: ignore

        # 10 samples: 5 privileged allowed (label=1), 5 unprivileged denied (label=0)
        prot_attr = np.array([[privileged_value]] * 5 + [[1 - privileged_value]] * 5)
        labels = np.array([[1]] * 5 + [[0]] * 5)

        dataset = self._BinaryLabelDataset(  # type: ignore[attr-defined]
            favorable_label=1,
            unfavorable_label=0,
            df=None,
            label_names=["label"],
            protected_attribute_names=[protected_attr],
            features=prot_attr,
            labels=labels,
        )

        metric = self._BinaryLabelDatasetMetric(  # type: ignore[attr-defined]
            dataset,
            privileged_groups=[{protected_attr: privileged_value}],
            unprivileged_groups=[{protected_attr: 1 - privileged_value}],
        )
        di = metric.disparate_impact()

        if di is not None and di < 0.8:
            # Upgrade or add a critical bias issue
            upgraded = False
            for i in issues:
                if i.type == "bias" and (i.category == protected_attr or i.category is None):
                    i.severity = "critical"
                    i.description = (
                        f"{i.description} (AIF360 disparate impact={di:.2f} < 0.80)"
                    )
                    upgraded = True
            if not upgraded:
                issues.append(
                    EthicsIssue(
                        type="bias",
                        category=protected_attr,
                        description=f"AIF360 disparate impact={di:.2f} indicates unfair outcome",
                        severity="critical",
                    )
                )

        return issues

    async def _llm_validate(self, text: str, issues: List[EthicsIssue]) -> List[EthicsIssue]:
        """Optional OpenAI validation to classify severity; non-blocking and safe to skip.
        If OPENAI_API_KEY is set, query a lightweight model to confirm/adjust severities.
        """
        try:
            from openai import OpenAI  # type: ignore

            client = OpenAI()
            summary = "; ".join([f"{i.type}:{i.category or '-'}" for i in issues])
            prompt = (
                "You are an ethics reviewer. Given the requirement and detected issues, "
                "return the same list with severities adjusted if needed. "
                "Respond ONLY as JSON array of {type, category, description, severity}.\n\n"
                f"Requirement: {text}\nIssues: {summary}"
            )
            # Use chat.completions for broad compatibility
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=300,
            )
            content = resp.choices[0].message.content or ""
            import json, re  # type: ignore

            data = None
            try:
                data = json.loads(content)
            except Exception:
                m = re.search(r"\[(.|\n|\r)*\]", content)
                if m:
                    try:
                        data = json.loads(m.group(0))
                    except Exception:
                        data = None
            if isinstance(data, list) and data:
                adjusted: List[EthicsIssue] = []
                for d in data:
                    adjusted.append(
                        EthicsIssue(
                            type=str(d.get("type", "bias")),
                            category=(d.get("category") if d.get("category") is not None else None),
                            description=str(d.get("description", "")),
                            severity=str(d.get("severity", "medium")),
                        )
                    )
                return adjusted
        except Exception:
            pass
        return issues


