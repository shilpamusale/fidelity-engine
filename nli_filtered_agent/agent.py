from datetime import datetime
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
# from google.adk.models import LlmConfig

# from .nli_verifier import classify_nli
# from .retriever import RAGRetriever

from .nli_verifier import classify_nli
from .rag_wrapper import NliRetrieverWrapper
retriever = NliRetrieverWrapper()


def extract_latest_user_prompt(llm_request: LlmRequest) -> str:
    """
    Extracts the latest user message from the message history.
    """
    for message in reversed(llm_request.contents):
        if message.role == "user":
            for part in message.parts:
                if hasattr(part, "text") and part.text:
                    return part.text.strip()
    return ""


def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest):
    # ✅ Get latest user input correctly
    prompt_text = extract_latest_user_prompt(llm_request)

    # ✅ Get premise using retriever
    top_fact = retriever.retrieve(prompt_text)

    # ✅ Reset and update state
    callback_context.state["original_user_prompt"] = prompt_text
    callback_context.state["premise"] = top_fact
    callback_context.state["llm_answer"] = ""
    callback_context.state["nli_label"] = ""
    callback_context.state["nli_score"] = 0.0
    callback_context.state["hallucination_flag"] = False

    # ✅ Logs
    print(f"\n🔍 New User Prompt: {prompt_text}")
    print(f"📘 New Premise: {top_fact if top_fact else '❌ None found'}")



def after_model_callback(callback_context: CallbackContext, llm_response: LlmResponse):
    hypothesis = ""
    for part in llm_response.content.parts:
        if hasattr(part, "text") and part.text:
            hypothesis = part.text.strip()
            break

    premise = callback_context.state.get("premise", "")

    if not premise:
        print("⚠️ No valid RAG premise — skipping NLI check.")
        callback_context.state["llm_answer"] = hypothesis
        callback_context.state["nli_label"] = "UNKNOWN"
        callback_context.state["nli_score"] = 0.0
        callback_context.state["hallucination_flag"] = True  # assume risky
        return llm_response

    # ✅ New version of classify_nli returns full probabilities
    nli_label, score, all_probs = classify_nli(premise, hypothesis)

    # 🔁 Apply override logic
    if nli_label == "NEUTRAL" and all_probs["ENTAILMENT"] >= 0.85:
        print(f"🔁 Overriding NEUTRAL → ENTAILMENT (Entailment score = {all_probs['ENTAILMENT']:.3f})")
        nli_label = "ENTAILMENT"
        score = all_probs["ENTAILMENT"]

    callback_context.state["llm_answer"] = hypothesis
    callback_context.state["nli_label"] = nli_label
    callback_context.state["nli_score"] = round(score, 4)
    callback_context.state["hallucination_flag"] = nli_label == "CONTRADICTION"

    print(f"\n🧠 NLI Label: {nli_label} | Score: {score:.3f}")
    return llm_response


# Optional custom config
# llm_config = LlmConfig(
#     model="gemini-2.0-flash",
#     max_output_tokens=400
# )

root_agent = LlmAgent(
    name="nli_filtered_agent",
    model="gemini-2.0-flash",
    # llm_config=llm_config,
    description="An agent that uses retrieval + NLI to detect hallucinations.",
    instruction="""
            You are a helpful and factual assistant. Use only known nutrition facts when answering.
            Keep your response concise (within 250 words).
        """,
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)