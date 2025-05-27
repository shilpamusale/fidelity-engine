"""
Module: medsentinel/skills/base.py

Base class for agentic skills in the MedSentinel hallucination-safe QA system.

Features:
- Abstract `run()` method for executing skill logic
- Optional metadata tagging and prompt logging hooks
- Designed for RAG, CoT, NLI, Fallback skill composition

Intended Use:
Subclass this base to implement skill modules that take in structured inputs
and produce agent-safe outputs (text, JSON, confidence scores, etc.).

Author: MedSentinel Team (2025)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseSkill(ABC):
    """
    Abstract base class for agentic skill modules.
    """

    def __init__(self, skill_name: str):
        self.skill_name = skill_name

    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the skill on input data and return structured output.
        Args:
            input_data: Dict containing structured inputs (e.g., patient context, prediction).
        Returns:
            Dict containing structured outputs (e.g., grounded rationale, CoT explanation).
        """
        pass

    def log_metadata(self, meta: Optional[Dict[str, Any]] = None) -> None:
        """
        Optional metadata logging hook. Override if needed.
        """
        if meta:
            print(f"[{self.skill_name}] Metadata: {meta}")
