"""
Baseline Agent: No RAG, no retriever,
no context injection. Just pass the
user message to the LLM.
"""

from datetime import datetime
from typing import Optional
import time

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse


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
    Baseline: Just extract the user message and store it for reference.
    """
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
    state["original_user_message"] = original_user_message

    print(
        f"\n=== BASELINE REQUEST STARTED at "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ==="
    )
    print(f"Agent: {agent_name}")
    print(f"Original message: {original_user_message}")
    print("✓ Request approved for processing (no RAG, no context)")
    return None


def after_model_callback(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """
    Optionally, you can post-process the model output here (e.g., positive language),
    but for a true baseline, just return the model's response as-is.
    """
    print("=== BASELINE REQUEST COMPLETED ===")
    return llm_response


# Create the Baseline Agent
root_agent = LlmAgent(
    name="baseline_agent",
    model="gemini-2.0-flash",
    description="A baseline agent that returns the"
    + "LLM's answer to the user question with no RAG or mitigation.",
    instruction="""
    You are a helpful and factual assistant.
    Answer user questions concisely and accurately.
    Do not add any extra context or mitigation.
    """,
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)
