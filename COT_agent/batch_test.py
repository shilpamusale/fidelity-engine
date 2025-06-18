import requests
import time
import json
from datetime import datetime
import uuid
import csv
import os

# Configuration
BASE_URL = os.getenv("BASE_URL", "https://dietitian-api-411547369.us-central1.run.app")
# BASE_URL="http://localhost:8000" python COT_agent/batch_test.py
APP_NAME = "COT_agent"
USER_ID = "test1"


def load_questions_from_csv(csv_path):
    questions = []
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row and row[0].strip():
                question = row[0].strip()
                if question.startswith('"') and question.endswith('"'):
                    question = question[1:-1]
                questions.append(question)
    return questions


# Load questions from prompts.csv (relative to this folder)
# INPUT_CSV = "data/modified_prompts.csv"  # Define input file as a variable
INPUT_CSV = "data/prompts.csv"  # Define input file as a variable
QUESTIONS = load_questions_from_csv(INPUT_CSV)
# QUESTIONS = load_questions_from_csv("data/stress_test_prompts.csv")
# QUESTIONS = load_questions_from_csv("data/additional_test_prompts.csv")

# Generate output file name based on agent name and input file
agent_name = os.path.basename(
    os.path.dirname(os.path.abspath(__file__))
)  # Get parent directory name
csv_name = os.path.splitext(os.path.basename(INPUT_CSV))[
    0
]  # Get filename without extension
now_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE = f"{agent_name}_{csv_name}_batch_{now_str}.json"


def create_session():
    url = f"{BASE_URL}/apps/{APP_NAME}/users/{USER_ID}/sessions"
    response = requests.post(url)
    response.raise_for_status()
    return response.json()["id"]


def send_question(session_id, question):
    url = f"{BASE_URL}/run"
    payload = {
        "app_name": APP_NAME,
        "user_id": USER_ID,
        "session_id": session_id,
        "new_message": {"role": "user", "parts": [{"text": question}]},
        "streaming": False,
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def main():
    results = []
    # Create a session for all questions
    session_id = create_session()
    print(f"Created session: {session_id}")

    # Send a warm-up query to handle cold starts
    print("Sending warm-up query...")
    try:
        warm_up_response = send_question(session_id, "hello")
        print("Warm-up complete.")
    except Exception as e:
        print(f"Warm-up query failed: {e}")

    # Now process the actual questions
    for question in QUESTIONS:
        agent_start = time.time()
        agent_start_iso = datetime.utcnow().isoformat() + "Z"
        try:
            response = send_question(session_id, question)
            print("RAW RESPONSE:", json.dumps(response, indent=2))
            agent_end = time.time()
            agent_end_iso = datetime.utcnow().isoformat() + "Z"
            elapsed = agent_end - agent_start

            answer = ""
            initial_answer = None
            retriever_confidence = None
            original_message = None
            enhanced_message = None
            answer_flagged = None
            flagged_reasons = None

            # The response is a list of events, we need to find the one with the model's response
            for event in response:
                if event.get("content") and event["content"].get("parts"):
                    for part in event["content"]["parts"]:
                        if part.get("text"):
                            answer = part["text"]
                state = event.get("actions", {}).get("state_delta", {})
                if "initial_answer" in state:
                    initial_answer = state["initial_answer"]
                if (
                    "retriever_confidence" in state
                    and state["retriever_confidence"] is not None
                ):
                    retriever_confidence = state["retriever_confidence"]
                if (
                    "original_user_message" in state
                    and state["original_user_message"] is not None
                ):
                    original_message = state["original_user_message"]
                if (
                    "enhanced_message" in state
                    and state["enhanced_message"] is not None
                ):
                    enhanced_message = state["enhanced_message"]
                if "answer_flagged" in state:
                    answer_flagged = state["answer_flagged"]
                if "flagged_reasons" in state:
                    flagged_reasons = state["flagged_reasons"]

            timing_info = {
                "agent_start": agent_start_iso,
                "agent_end": agent_end_iso,
                "elapsed": elapsed,
            }
            state_info = {
                "retriever_confidence": retriever_confidence,
                "original_message": original_message,
                "enhanced_message": enhanced_message,
                "answer_flagged": answer_flagged,
                "flagged_reasons": flagged_reasons,
            }
            results.append(
                {
                    "question": question,
                    "initial_answer": initial_answer,
                    "final_answer": answer,
                    "state": state_info,
                    "timing": timing_info,
                }
            )
            print(
                f"Q: {question}\nInitial A: {initial_answer}\nFinal A: {answer}\nConfidence: {retriever_confidence}\nElapsed: {elapsed:.2f}s\n---"
            )
        except Exception as e:
            print(f"Error processing question '{question}': {e}")
            results.append({"question": question, "error": str(e)})

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
