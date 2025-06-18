# nli_filtered_agent/demo_test.py

import json
from nli_verifier import classify_nli
from kb_mapping import kb

output = {}

for prompt, content in kb.items():
    premise = content["premise"]
    answers = content["answers"]

    output[prompt] = {
        "premise": premise,
        "results": {}
    }

    for label, hypothesis in answers.items():
        print(f"Running NLI for: {prompt} ({label})")
        nli_label, score = classify_nli(premise, hypothesis)
        output[prompt]["results"][label] = {
            "answer": hypothesis,
            "nli_label": nli_label,
            "score": round(score, 4)
        }

# Save results to JSON
with open("nli_results.json", "w") as f:
    json.dump(output, f, indent=2)

print("\n✅ NLI results saved to nli_results.json")