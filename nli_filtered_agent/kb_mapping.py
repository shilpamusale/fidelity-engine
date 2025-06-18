# # nli_filtered_agent/demo_test.py

# import json
# from nli_filtered_agent.nli_verifier import classify_nli

# # from kb_mapping import kb

# output = {}

# for prompt, content in kb.items():
#     premise = content["premise"]
#     answers = content["answers"]

#     output[prompt] = {"premise": premise, "results": {}}

#     for label, hypothesis in answers.items():
#         print(f"Running NLI for: {prompt} ({label})")
#         nli_label, score = classify_nli(premise, hypothesis)
#         output[prompt]["results"][label] = {
#             "answer": hypothesis,
#             "nli_label": nli_label,
#             "score": round(score, 4),
#         }

# # Save results to JSON
# with open("nli_results.json", "w") as f:
#     json.dump(output, f, indent=2)

# print("\n NLI results saved to nli_results.json")


# nli_filtered_agent/kb_mapping.py

# nli_filtered_agent/kb_mapping.py

import csv
from pathlib import Path
from typing import Any, Sequence  # , Dict

DATA_DIR = Path(__file__).parent / "data"
PROMPTS_CSV = DATA_DIR / "prompts.csv"


# nli_filtered_agent/kb_mapping.py


def load_kb(csv_path: Path = PROMPTS_CSV) -> dict[str, Any]:
    kb: dict[str, Any] = {}
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Assert we actually have headers
        if reader.fieldnames is None:
            raise ValueError(f"No header row found in {csv_path}")
        fieldnames: Sequence[str] = reader.fieldnames

        for row in reader:
            prompt_text = row["Prompt"]
            answers = {col: row[col] for col in fieldnames if col != "Prompt"}
            kb[prompt_text] = {"premise": prompt_text, "answers": answers}
    return kb


# module‐level variable your tests import
kb = load_kb()
