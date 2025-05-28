import pytest
from medsentinel.skills.nli_validation import NLIValidationSkill


@pytest.mark.parametrize(  # type: ignore[misc]
    "premise, hypothesis, expected_verdict",
    [
        (
            "The patient consumes 3500mg of sodium daily.",
            "The patient is within recommended sodium limits.",
            "contradiction",
        ),
        (
            "The patient follows a low-sodium diet.",
            "The patient consumes too much salt.",
            "contradiction",
        ),
        (
            "The patient eats vegetables.",
            "The patient does not eat vegetables.",
            "neutral",
        ),
        ("The patient drinks water.", "The patient stays hydrated.", "entailment"),
    ],
)
def test_nli_validation_stub(premise: str, hypothesis: str, expected_verdict: str) -> None:
    skill = NLIValidationSkill()
    output = skill.run({"premise": premise, "hypothesis": hypothesis})
    assert output["verdict"] == expected_verdict
    assert 0.0 <= output["confidence"] <= 1.0
