from medsentinel.skills.cot_explanation import CoTExplanationSkill


def test_cot_explanation_stub_output() -> None:
    skill = CoTExplanationSkill()
    input_data = {
        "grounded_text": "Patient consumes 3,000 kcal/day, "
        + " high sodium intake, BMI 32, glucose 112 mg/dL."
    }

    result = skill.run(input_data)

    assert isinstance(result, dict)
    assert "reasoning_steps" in result
    assert isinstance(result["reasoning_steps"], list)
    assert "final_answer" in result
    assert isinstance(result["final_answer"], str)
    assert "citations" in result
    assert isinstance(result["citations"], list)
