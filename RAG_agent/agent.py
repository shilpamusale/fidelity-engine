"""
Model Callbacks Example with Before and After Processing
"""

import copy
from datetime import datetime
from typing import Optional
import time
import numpy as np

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types
from .rag.retriever import Retriever

retriever = Retriever(
    csv_path="RAG_agent/data/embeddings.csv", model_name="BAAI/bge-large-en-v1.5"
)


def print_state_debug(label, state):
    print(f"[DEBUG] {label}:")
    try:
        for k, v in state._value.items():
            try:
                print(f"  {k}: {v!r}")
            except Exception as e:
                print(f"  {k}: <unprintable: {e}>")
    except Exception as e:
        print(f"  <Could not print state: {e}>")


def before_agent_callback(callback_context):
    now = time.time()
    callback_context.state["agent_start_time"] = now
    callback_context.state["agent_start_time_str"] = datetime.fromtimestamp(
        now
    ).isoformat()
    print("Agent processing started.")
    print_state_debug("State at end of before_agent_callback", callback_context.state)
    return None


def after_agent_callback(callback_context):
    now = time.time()
    callback_context.state["agent_end_time"] = now
    callback_context.state["agent_end_time_str"] = datetime.fromtimestamp(
        now
    ).isoformat()
    agent_start = callback_context.state.get("agent_start_time")
    if agent_start:
        elapsed = now - agent_start
        callback_context.state["agent_elapsed_time"] = elapsed
        print(f"Agent processing took {elapsed:.2f} seconds.")
    print_state_debug("State at end of after_agent_callback", callback_context.state)
    return None


def before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Before model callback that:
    1. Logs request information
    2. RAG with multi-chunk prompt
    """
    # Get the state and agent name
    state = callback_context.state
    agent_name = callback_context.agent_name

    # Extract the last user message
    original_user_message = ""
    if llm_request.contents and len(llm_request.contents) > 0:
        for content in reversed(llm_request.contents):
            if content.role == "user" and content.parts and len(content.parts) > 0:
                if hasattr(content.parts[0], "text") and content.parts[0].text:
                    original_user_message = content.parts[0].text
                    break

    # Store original message
    state["original_user_message"] = original_user_message

    # 1. Retrieve up to 10 best chunks (hybrid dense + BM25, already reranked)
    retrieved_chunks = retriever.retrieve(original_user_message, top_k=10)
    # Drop all chunks if the best cross‑encoder score is too low (recall guard)
    # if retrieved_chunks and retrieved_chunks[0][2] < -1.0:
    #     retrieved_chunks = []
    BOOK_TITLE = "Food & Nutrition Handbook"

    # 2. Build a numbered SOURCE block with book title and page
    if retrieved_chunks:
        numbered_chunks = "\n\n".join(
            f"[{i+1}] ({BOOK_TITLE}) {txt}"
            for i, (txt, page, _) in enumerate(retrieved_chunks)
        )
        state["retriever_confidence"] = float(retrieved_chunks[0][2])
    else:
        numbered_chunks = ""
        state["retriever_confidence"] = None

    # 3. Compose the full prompt
    prompt_text = (
        f"### SOURCE\n{numbered_chunks}\n\n"
        f"### QUESTION\n{original_user_message}\n\n"
        f"### ANSWER\n"
    )
    state["enhanced_message"] = prompt_text  # keep for post-filter

    # 4. Overwrite the *actual* user message that the model will see
    llm_request.contents = [
        types.Content(role="user", parts=[types.Part(text=prompt_text)])
    ]

    # Log the request
    print(
        f"\n=== REQUEST STARTED at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ==="
    )
    print(f"Agent: {agent_name}")
    print(f"Original message: {original_user_message}")
    print(f"Enhanced message: {prompt_text[:100]}...")
    print("✓ Request approved for processing")

    return None


def after_model_callback(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """
    Post-process the model output to flag answers that use values or cite sources not present in the context.
    If answer_flagged is True, override the answer with 'I don't know.'
    """
    state = callback_context.state
    context = state.get("enhanced_message", "")
    flagged = False
    flagged_reasons = []

    # Extract the model's answer
    response_text = ""
    if llm_response and llm_response.content and llm_response.content.parts:
        for part in llm_response.content.parts:
            if hasattr(part, "text") and part.text:
                response_text += part.text
    state["initial_answer"] = response_text  # Store the initial answer
    state["llm_raw_response"] = response_text

    # Check for citations not in context
    import re

    citations = re.findall(r"\(([^)]+)\)", response_text)
    for citation in citations:
        if citation.lower() not in context.lower():
            flagged = True
            flagged_reasons.append(f"Citation '{citation}' not found in context.")

    # Allow common metric-to-English conversions
    ALLOWED_CONVERSIONS = {
        "2.2",
        "0.45",
        "0.454",
        "0.4536",
        "0.5",
        "1.61",
        "3.28",
    }  # kg<->lb, g/lb, km/mi, m/ft, etc.

    # Check for numbers not in context (simple heuristic)
    numbers_in_answer = re.findall(r"\b\d+(?:\.\d+)?\b", response_text)
    for number in numbers_in_answer:
        if number not in context and number not in ALLOWED_CONVERSIONS:
            flagged = True
            flagged_reasons.append(f"Number '{number}' not found in context.")

    if flagged:
        print(f"[GUARD] Answer flagged: {flagged_reasons}")
        state["answer_flagged"] = True
        state["flagged_reasons"] = flagged_reasons
        # Override the answer with abstention
        abstain_text = "I don't know."
        from google.genai.types import Content, Part

        return LlmResponse(
            content=Content(role="model", parts=[Part(text=abstain_text)])
        )
    else:
        state["answer_flagged"] = False
        state["flagged_reasons"] = []  # Clear flagged reasons when not flagged

    print(f"=== REQUEST COMPLETED ===")
    return llm_response


# Create the Agent
root_agent = LlmAgent(
    name="RAG_agent",
    model="gemini-2.0-flash",
    description="A Dietitian RAG agent that uses the context to answer the user question.",
    instruction="""
    You are a helpful, empathetic, and positive assistant.

    Your job is to:
    - Answer user questions concisely
    - Provide factual information
    - Be friendly, empathetic, and respectful
    - Only answer using the provided context. If the answer is clearly stated or can be directly inferred from the context, use it in your answer.
    - If the answer cannot be found or inferred from the context, respond with: "I'm here to help with nutrition and diet questions. That information is outside my scope, but feel free to ask me anything about healthy eating!"
    - Do NOT use any information, numbers, or sources from outside the context, even if you know them.
    - If the context provides a value in a different unit than the question, you may convert units only if the conversion is straightforward and commonly known (e.g., kilograms to pounds, 1 kg ≈ 2.2 lbs). Show your calculation.
    - If multiple valid answers appear in the context (e.g., different age groups), list them all, citing the source, instead of saying 'I don't know.'
    - If the context lists several valid values (e.g., children vs. adults), list them all with their labels instead of saying 'I don't know.'
    - If the context gives a guideline that depends on body weight, state that guideline and explain how the user can calculate their own number.
    - Cite the source from the context when possible. Do NOT cite any other sources.
    - When citing, include only the book title and chunk number as shown in the SOURCE block, e.g., (Food & Nutrition Handbook) [1]. Do not include page numbers.
    - Never invent page numbers or cite any other sources.
    - When citing, use the exact string from SOURCE, one per parenthesis; e.g. (Food & Nutrition Handbook) [1].
    - When citing, list exactly one chunk per parenthesis, copied verbatim from the SOURCE block. Do not combine multiple chunks in a single citation.

    Example:
    SOURCE:
    [1] (Food & Nutrition Handbook) ...brown rice...
    [2] (Food & Nutrition Handbook) ...porridge...
    [3] (Food & Nutrition Handbook) ...porridge...

    QUESTION:
    What can you tell me about brown rice and porridge?

    ANSWER:
    Brown rice is a source of selenium (Food & Nutrition Handbook) [1]. It can be used as an ingredient for enriched porridges (Food & Nutrition Handbook) [2] and (Food & Nutrition Handbook) [3].
    """,
    generate_content_config=types.GenerateContentConfig(
        temperature=2.0,
        # top_p=0.9,
        top_p=0.5,
        max_output_tokens=512,
    ),
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)
