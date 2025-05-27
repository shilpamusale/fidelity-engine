"""
tests/test_rag_grounding.py

Unit test for RAGGroundingSkill using StubRetriever and mocked PaLM.

Author: MedSentinel Team (2025)
"""

from medsentinel.skills.rag_grounding import RAGGroundingSkill
from medsentinel.retrievers.stub import StubRetriever


def test_rag_grounding_skill_runs() -> None:
    skill = RAGGroundingSkill(retriever=StubRetriever())

    input_data = {
        "query": "Why should this diabetic patient reduce processed carbs?",
        "prediction": "The patient should follow a low-gllcemic diet.",
    }

    result = skill.run(input_data)

    assert "grounded_rationale" in result
    assert isinstance(result["grounded_rationale"], str)
    assert "docs_used" in result
    assert isinstance(result["docs_used"], list)
    assert len(result["docs_used"]) > 0
