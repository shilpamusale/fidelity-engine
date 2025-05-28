"""
Skill Orchestrator - routes user queries through RAG, CoT, and NLI with fallback

This module defines the SkillRouter class which orchestrates the end-to-end execution
of a hallucination-safe QA pipeline by sequentially invoking the following stubbed skills:

This orchestrator handles structured agentic execution of skills:
- RAGGroundingSkill.run(): fetches knowledge
- CoTExplanationSkill.run(): generates reasoning
- NLIValidationSkill.run(): checks factuality
- Fallback: triggers if contradiction detected

Features:
- Modular skill orchestration with type-safe stubs
- Fallback routing when hallucination is suspected
- Logging for traceability and debugging

Intended Use:
- To be integrated with FastAPI and/or Streamlit frontend
- This version uses stubbed methods to validate routing logic

Inputs:
- user_query (str): natural language question from the user

Outputs:
- final_answer (str): validated explanation or fallback response

Functions:
- SkillRouter.route(): Executes the skill chain for a single query

Example Usage:
```python
router = SkillRouter()
answer = router.route("Can I eat salty snacks if I have high blood pressure?")
Author: MedSentinel Team (2025)
"""

import logging
from typing import Dict, Any

from medsentinel.skills.rag_grounding import RAGGroundingSkill
from medsentinel.retrievers.stub import StubRetriever
from medsentinel.skills.cot_explanation import CoTExplanationSkill
from medsentinel.skills.nli_validation import NLIValidationSkill
from medsentinel.skills.fallback import get_fallback_response

# Initialize Logging
logger = logging.getLogger(__name__)


class SkillRouter:
    """
    SkillRouter orchestrates the RAG → CoT → NLI skill pipeline.
    If NLI verdict is 'contradiction', a fallback message is returned.
    Otherwise, the CoT-generated explanation is returned.
    """

    def __init__(self) -> None:
        self.retriever = StubRetriever()
        self.rag = RAGGroundingSkill(self.retriever)
        self.cot = CoTExplanationSkill()
        self.nli = NLIValidationSkill()

    def route(self, user_query: str) -> Any:
        """
        Routes a user query through the agentic reasoning pipeline.
            Args:
                user_query (str): The natural language dietitian-related query.

            Returns:
                str: Final explanation or a fallback warning message.
        """
        logger.info(f"Starting skill routing for query: {user_query}")

        payload: Dict[str, Any] = {"user_query": user_query}

        # Step 1: RAG skill

        payload = self.rag.run(payload)
        logger.debug(f"RAG output: {payload.get('context')}")

        # Step 2: CoT skill
        payload = self.cot.run(payload)
        logger.debug(f"CoT output : {payload.get('explanation')}")

        # Step 3: NLI Skill
        payload = self.nli.run(payload)
        verdict = payload.get("verdict", "")
        logger.info(f"NLI verdict: {verdict}")

        # Fallback if contradiction
        if verdict == "contradiction":
            logger.warning("Contradiction detected. Triggering fallback.")
            return get_fallback_response(user_query)

        return payload.get("explanation", "No explanation generated.")
