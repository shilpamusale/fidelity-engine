"""
medsentinel/skills/rag_grounding.py

Agent skill for retrieval-augmented grounding of predictions using clinical context.

Inherits:
    - BaseSkill

Uses:
    - RetrieverInterface to fetch grounding docs
    - PaLM (mocked) for explanation
    - PromptLayer for trace logging
Responsibilities:
    - Use retriever to fetch grounding docs
    - Compose a RAG-style prompt
    - Call LLM with constructed prompt
    - Log inputs/outputs to PromptLayer
    - Return structured {"grounded_rationale": ..., "docs_used": ...}

Author: MedSentinel Team (2025)
"""

import logging
from typing import Dict, Any, List
from medsentinel.skills.base import BaseSkill
from medsentinel.retrievers.base import RetrieverInterface
from medsentinel.llm.vertex_palm import call_palm_api
from medsentinel.logs.prompt_logger import log_prompt

# Initialize Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGGroundingSkill(BaseSkill):
    """
    Uses RAG to ground a clinical prediction in retrieved context.
    """

    def __init__(self, retriever: RetrieverInterface):
        super().__init__(skill_name="RAGGroundingSkill")
        self.retriever = retriever

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        query = input_data.get("query", "")
        prediction = input_data.get("prediction", "")

        logger.info("Running RAGGroundingSkill.")
        logger.debug(f"Received input query: {query}")
        logger.debug(f"Received input prediction: {prediction}")

        # Step 1: Retrieve documents
        docs: List[str] = self.retriever.retrieve(query, top_k=3)
        logger.debug(f"Retrieved documents: {docs}")

        # Step 2: Compose prompt
        context = "\n".join(docs)
        prompt = (
            f"You are a clinical reasoning assistant.\n"
            f"Given the following context:\n{context}\n\n"
            f"And the prediction: '{prediction}', explain why this prediction makes sense "
            f"based on the context above.\n\nExplanation:"
        )

        # step 3: Log prompt
        logger.debug(f"Constructed LLM prompt:\n{prompt}")
        log_prompt(skill=self.skill_name, prompt=prompt)

        # Step 4: Call LLM(mocked)
        explanatoion = call_palm_api(prompt)
        logger.info("LLM call complete. Explanation received.")

        return {"grounded_rationale": explanatoion, "docs_used": docs}
