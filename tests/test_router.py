import pytest
from medsentinel.router.skill_orchestrator import SkillRouter


def test_skill_router_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    router = SkillRouter()

    monkeypatch.setattr(router.rag, "run", lambda d: {**d, "context": "Stubbed RAG context"})
    monkeypatch.setattr(router.cot, "run", lambda d: {**d, "explanation": "Stubbed CoT reasoning"})
    monkeypatch.setattr(router.nli, "run", lambda d: {**d, "verdict": "contradiction"})

    result = router.route("Can I eat salty snacks if I have high blood pressure?")
    assert "not be reliable" in result


def test_skill_router_success(monkeypatch: pytest.MonkeyPatch) -> None:
    router = SkillRouter()

    monkeypatch.setattr(router.rag, "run", lambda d: {**d, "context": "Stubbed RAG context"})
    monkeypatch.setattr(router.cot, "run", lambda d: {**d, "explanation": "Stubbed CoT reasoning"})
    monkeypatch.setattr(router.nli, "run", lambda d: {**d, "verdict": "entailment"})

    result = router.route("Can I eat salty snacks if I have high blood pressure?")
    assert result == "Stubbed CoT reasoning"
