# # nli_filtered_agent/nli_verifier.py

# from transformers import pipeline

# # Load NLI model
# nli_model = pipeline("text-classification", model="roberta-large-mnli")

# def classify_nli(premise: str, hypothesis: str):
#     """
#     Classifies the relationship between a premise and hypothesis.
#     Returns: (label, score)
#     """
#     input_text = f"{premise} </s> {hypothesis}"
#     result = nli_model(input_text)[0]
#     label = result["label"]
#     score = result["score"]
#     return label, score


from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

# Load model + tokenizer once
model_name = "roberta-large-mnli"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
model.eval()  # optional: turn off dropout


def classify_nli(premise: str, hypothesis: str):
    """
    Classifies the NLI relationship and returns:
    - final label (with override if enabled)
    - score (confidence for that label)
    - all_probs: dict with all three probabilities
    """
    inputs = tokenizer(premise, hypothesis, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = model(**inputs).logits
        probs = F.softmax(logits, dim=-1)[0]  # shape: (3,)

    label_map = {0: "CONTRADICTION", 1: "NEUTRAL", 2: "ENTAILMENT"}
    all_probs = {
        "CONTRADICTION": probs[0].item(),
        "NEUTRAL": probs[1].item(),
        "ENTAILMENT": probs[2].item(),
    }

    predicted_label = label_map[torch.argmax(probs).item()]
    predicted_score = all_probs[predicted_label]

    return predicted_label, predicted_score, all_probs
