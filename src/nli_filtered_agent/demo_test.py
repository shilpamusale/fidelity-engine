# # nli_filtered_agent/demo_test.py

# import json
# from nli_filtered_agent.nli_verifier import classify_nli
# from nli_filtered_agent.kb_mapping import kb

# output = {}

# for prompt, content in kb.items():
#     premise = content["premise"]
#     answers = content["answers"]

#     output[prompt] = {"premise": premise, "results": {}}

#     for label, hypothesis in answers.items():
#         print(f"Running NLI for: {prompt} ({label})")
#         nli_label, score, _ = classify_nli(premise, hypothesis)
#         output[prompt]["results"][label] = {
#             "answer": hypothesis,
#             "nli_label": nli_label,
#             "score": round(score, 4),
#         }

# # Save results to JSON
# with open("nli_results.json", "w") as f:
#     json.dump(output, f, indent=2)

# print("\n NLI results saved to nli_results.json")


# import json
from nli_filtered_agent.nli_verifier import classify_nli
from nli_filtered_agent.kb_mapping import kb


def run_demo():
    output = {}
    for prompt, content in kb.items():
        premise = content["premise"]
        answers = content["answers"]
        output[prompt] = {"premise": premise, "results": {}}
        for label, hypothesis in answers.items():
            nli_label, score, _ = classify_nli(premise, hypothesis)
            output[prompt]["results"][label] = {
                "answer": hypothesis,
                "nli_label": nli_label,
                "score": round(score, 4),
            }
    return output


def test_demo_runs_and_returns_dict():
    result = run_demo()
    # sanity check—must be a dict and not empty
    assert isinstance(result, dict)
    assert result, "Expected at least one prompt in the KB"
