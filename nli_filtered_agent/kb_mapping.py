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
from typing import Any, Dict

DATA_DIR = Path(__file__).parent / "data"
PROMPTS_CSV = DATA_DIR / "prompts.csv"

def load_kb(csv_path: Path = PROMPTS_CSV) -> Dict[str, Any]:
    kb: Dict[str, Any] = {}
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 1) Get the prompt text from the "Prompt" column
            prompt_text = row["Prompt"]

            # 2) Build answers dict from *all* other columns
            answers = {
                col_name: row[col_name]
                for col_name in reader.fieldnames
                if col_name != "Prompt"
            }

            kb[prompt_text] = {
                "premise": prompt_text,  # we only have one text column
                "answers": answers,
            }
    return kb

# module‐level variable your tests import
kb = load_kb()
