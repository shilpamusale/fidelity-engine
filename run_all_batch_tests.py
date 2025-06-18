#!/usr/bin/env python3
import requests
import time
import json
from datetime import datetime
import os
import csv
import sys
import glob
import subprocess

# Configuration
BASE_URL = os.getenv("BASE_URL", "https://dietitian-api-411547369.us-central1.run.app")

# List of all agents to test
AGENTS = ["baseline_agent", "COT_agent", "RAG_agent", "nli_filtered_agent"]

# List of CSV files to test with each agent
CSV_FILES = ["prompts.csv", "modified_prompts.csv"]

USER_ID = "test1"


def cleanup_old_files():
    """Clean up old .json and .csv batch test result files."""
    print("Cleaning up old batch test results...")
    cleanup_count = 0
    
    for agent_name in AGENTS:
        # Clean up JSON files
        json_pattern = os.path.join(agent_name, f"{agent_name}_*_batch_*.json")
        json_files = glob.glob(json_pattern)
        for file in json_files:
            os.remove(file)
            cleanup_count += 1
            print(f"  Removed: {file}")
        
        # Clean up CSV files
        csv_pattern = os.path.join(agent_name, f"{agent_name}_*_batch_*.csv")
        csv_files = glob.glob(csv_pattern)
        for file in csv_files:
            os.remove(file)
            cleanup_count += 1
            print(f"  Removed: {file}")
    
    print(f"Cleaned up {cleanup_count} old files.\n")


def convert_json_to_csv(json_file):
    """Convert JSON results to CSV format."""
    csv_file = json_file.replace('.json', '.csv')
    subprocess.run(['python', 'json_to_csv.py', json_file, csv_file], check=True)
    print(f"Converted {json_file} to {csv_file}")
    return csv_file


def load_questions_from_csv(csv_path):
    """Load questions from a CSV file."""
    questions = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row and row[0].strip():
                question = row[0].strip()
                if question.startswith('"') and question.endswith('"'):
                    question = question[1:-1]
                questions.append(question)
    return questions


def create_session(agent_name):
    """Create a new session for the given agent."""
    url = f"{BASE_URL}/apps/{agent_name}/users/{USER_ID}/sessions"
    response = requests.post(url)
    response.raise_for_status()
    return response.json()["id"]


def send_question(agent_name, session_id, question):
    """Send a question to the agent."""
    url = f"{BASE_URL}/run"
    payload = {
        "app_name": agent_name,
        "user_id": USER_ID,
        "session_id": session_id,
        "new_message": {
            "role": "user",
            "parts": [{"text": question}]
        },
        "streaming": False
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def test_agent_with_csv(agent_name, csv_file):
    """Test a single agent with a single CSV file."""
    print(f"\n{'='*80}")
    print(f"Testing {agent_name} with {csv_file}")
    print(f"{'='*80}")
    
    # Load questions from the agent's data directory
    csv_path = os.path.join(agent_name, "data", csv_file)
    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} not found, skipping...")
        return None
    
    questions = load_questions_from_csv(csv_path)
    print(f"Loaded {len(questions)} questions from {csv_file}")
    
    # Create output filename
    csv_name = os.path.splitext(csv_file)[0]
    now_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(agent_name, f"{agent_name}_{csv_name}_batch_{now_str}.json")
    
    results = []
    
    try:
        # Create a session
        session_id = create_session(agent_name)
        print(f"Created session: {session_id}")
        
        # Send warm-up query
        print("Sending warm-up query...")
        try:
            warm_up_response = send_question(agent_name, session_id, "hello")
            print("Warm-up complete.")
        except Exception as e:
            print(f"Warm-up query failed: {e}")
        
        # Process actual questions
        for i, question in enumerate(questions, 1):
            print(f"\nProcessing question {i}/{len(questions)}: {question[:50]}...")
            agent_start = time.time()
            agent_start_iso = datetime.utcnow().isoformat() + "Z"
            
            try:
                response = send_question(agent_name, session_id, question)
                agent_end = time.time()
                agent_end_iso = datetime.utcnow().isoformat() + "Z"
                elapsed = agent_end - agent_start
                
                # Extract answer and state information
                answer = ""
                initial_answer = None
                retriever_confidence = None
                original_message = None
                enhanced_message = None
                answer_flagged = None
                flagged_reasons = None
                
                for event in response:
                    if event.get("content") and event["content"].get("parts"):
                        for part in event["content"]["parts"]:
                            if part.get("text"):
                                answer = part["text"]
                    state = event.get("actions", {}).get("state_delta", {})
                    if "initial_answer" in state:
                        initial_answer = state["initial_answer"]
                    if "retriever_confidence" in state and state["retriever_confidence"] is not None:
                        retriever_confidence = state["retriever_confidence"]
                    if "original_user_message" in state and state["original_user_message"] is not None:
                        original_message = state["original_user_message"]
                    if "enhanced_message" in state and state["enhanced_message"] is not None:
                        enhanced_message = state["enhanced_message"]
                    if "answer_flagged" in state:
                        answer_flagged = state["answer_flagged"]
                    if "flagged_reasons" in state:
                        flagged_reasons = state["flagged_reasons"]
                
                timing_info = {
                    "agent_start": agent_start_iso,
                    "agent_end": agent_end_iso,
                    "elapsed": elapsed
                }
                state_info = {
                    "retriever_confidence": retriever_confidence,
                    "original_message": original_message,
                    "enhanced_message": enhanced_message,
                    "answer_flagged": answer_flagged,
                    "flagged_reasons": flagged_reasons
                }
                results.append({
                    "question": question,
                    "initial_answer": initial_answer,
                    "final_answer": answer,
                    "state": state_info,
                    "timing": timing_info
                })
                print(f"Elapsed: {elapsed:.2f}s")
                
            except Exception as e:
                print(f"Error processing question: {e}")
                results.append({
                    "question": question,
                    "error": str(e)
                })
        
        # Save results
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {output_file}")
        
        # Convert to CSV
        csv_file = convert_json_to_csv(output_file)
        
        return output_file
        
    except Exception as e:
        print(f"Fatal error testing {agent_name}: {e}")
        return None


def main():
    """Main function to run all batch tests."""
    print("Starting comprehensive batch testing for all agents...")
    print(f"Base URL: {BASE_URL}")
    
    # Clean up old files first
    cleanup_old_files()
    
    all_results = []
    
    # Test each agent with each CSV file
    for csv_file in CSV_FILES:
        print(f"\n\n{'#'*80}")
        print(f"# Running all agents with {csv_file}")
        print(f"{'#'*80}")
        
        for agent_name in AGENTS:
            result_file = test_agent_with_csv(agent_name, csv_file)
            if result_file:
                all_results.append({
                    "agent": agent_name,
                    "csv_file": csv_file,
                    "output_file": result_file
                })
    
    # Print summary
    print(f"\n\n{'='*80}")
    print("BATCH TESTING COMPLETE")
    print(f"{'='*80}")
    print(f"\nTotal test runs: {len(all_results)}")
    for result in all_results:
        print(f"- {result['agent']} with {result['csv_file']}: {result['output_file']}")
    
    print("\nAll batch tests completed!")


if __name__ == "__main__":
    main() 