# Fidelity Engine: A Hierarchical Multi-Agent System for Clinical Trial Analysis

Fidelity Engine is a sophisticated research project that moves beyond standard RAG to build a hierarchical multi-agent system for mitigating hallucinations in the high-stakes domain of clinical trial analysis. The system features an intelligent "Router" agent that delegates complex queries to a suite of specialized agents, ensuring a balance of accuracy, speed, and cost-efficiency.

This project demonstrates an end-to-end workflow from data ingestion and agentic system design to containerization and deployment on Google Cloud.

---

## Live Demo

**Fidelity Engine - Live on Google Cloud Run**  
*(Note: This is a placeholder link. It will be updated upon final deployment.)*

*(Placeholder for a GIF showing the application answering a complex question)*

---

## Project Vision: A Mock Demo

This mock interaction demonstrates the intended functionality of the hierarchical agent system when complete.

---

**User Query:**  
> *Compare the primary outcomes and key exclusion criteria for the two most recent Phase 3 glioblastoma trials involving immunotherapy.*

---

**System Response & Reasoning:**

**ROUTER AGENT THOUGHT PROCESS:**
- The user is asking to "compare" two entities, which suggests a multi-step reasoning process.
- The query involves "primary outcomes" and "exclusion criteria," which are high-stakes medical details where accuracy is critical.
- A simple RAG lookup might miss the comparative nuance, and a standard CoT might hallucinate specific criteria.
- Therefore, the highest-fidelity tool is required.  
  **TOOL SELECTED:** *NLI-Filtered Agent Tool*

---

**Final Answer:**

Based on a review of recent Phase 3 glioblastoma trials involving immunotherapy, here is a comparison of the primary outcomes and key exclusion criteria for the two most recent studies:

---

**Trial NCT04512345 (Active-IMVax Study)**
- **Primary Outcome:** Overall Survival (OS) at 24 months.
- **Key Exclusion Criteria:**
  - Prior treatment with any checkpoint inhibitors.
  - History of autoimmune disease.
  - Presence of brain metastases outside the primary tumor site.

**Trial NCT04876543 (Glio-Boost Trial)**
- **Primary Outcome:** Progression-Free Survival (PFS) at 12 months.
- **Key Exclusion Criteria:**
  - Patients with an ECOG performance status greater than 1.
  - Prior radiation therapy to the brain.
  - Use of systemic corticosteroids within 10 days of enrollment.

---

**VERIFICATION STATUS:** All claims have been verified against the source documents using Natural Language Inference.  
**SOURCES:** NCT04512345_protocol.pdf, NCT04876543_summary.pdf

---

## Key Features

- **Hierarchical Multi-Agent System:**  
  An intelligent "Router" agent analyzes incoming queries and routes them to the most appropriate specialist agent, optimizing for performance and accuracy.

- **Specialized Agentic Tools:**  
  A suite of worker agents, each tailored for a specific task:
    - **RAG Agent:** For fast and efficient factual lookups.
    - **Chain-of-Thought (CoT) Agent:** For complex queries requiring multi-step reasoning or comparisons.
    - **NLI-Filtered Agent:** For high-stakes queries requiring explicit factual verification against source documents.

- **Cost & Latency Aware:**  
  The tiered agent system is inherently efficient, using the most powerful (and expensive) models only when absolutely necessary.

- **Cloud-Native Deployment:**  
  Fully containerized with Docker and deployed as a scalable, public web service on Google Cloud Run.

---

##  Architecture Overview

The system uses a Router agent to intelligently manage a pool of specialist tools. This allows for a dynamic response strategy based on query complexity.

```mermaid
graph TD
    A[User Query] --> B{Router Agent};
    B -- Simple Fact? --> C[RAG Agent Tool];
    B -- Multi-Step Reasoning? --> D[CoT Agent Tool];
    B -- High-Stakes Accuracy? --> E[NLI-Filtered Agent Tool];
    C -- Sourced Answer --> F[Final Response];
    D -- Reasoned Answer --> F;
    E -- Verified Answer --> F;

    subgraph "Knowledge Base"
        G[Clinical Trial Documents <br> (from ClinicalTrials.gov)]
    end

    C --> G;
    D --> G;
    E --> G;

    style A fill:#FFD580,stroke:#333
    style B fill:#A8E6A3,stroke:#333
    style C,D,E fill:#9EC9FF,stroke:#333
    style F fill:#D7B3FF,stroke:#333
```

---

## Tech Stack

<table>
<tr>
<td align="center" width="96">
  <a href="https://www.python.org/">
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="48" height="48" alt="Python" />
  </a><br>Python
</td>
<td align="center" width="96">
  <a href="https://cloud.google.com/vertex-ai/docs/generative-ai/model-garden/gemini-sdk-overview">
    <img src="https://avatars.githubusercontent.com/u/1342004?s=200&v=4" width="48" height="48" alt="Google Gemini" />
  </a><br>Google Gemini
</td>
<td align="center" width="96">
  <a href="https://github.com/google/agent-development-kit">
    <img src="https://avatars.githubusercontent.com/u/1342004?s=200&v=4" width="48" height="48" alt="Google ADK" />
  </a><br>Google ADK
</td>
<td align="center" width="96">
  <a href="https://cloud.google.com/run">
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/googlecloud/googlecloud-original.svg" width="48" height="48" alt="Google Cloud" />
  </a><br>Google Cloud
</td>
<td align="center" width="96">
  <a href="https://www.docker.com/">
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg" width="48" height="48" alt="Docker" />
  </a><br>Docker
</td>
<td align="center" width="96">
  <a href="https://docs.pytest.org/">
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pytest/pytest-original.svg" width="48" height="48" alt="Pytest" />
  </a><br>Pytest
</td>
</tr>
</table>

---

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

- Python 3.11+
- Google Cloud SDK (`gcloud` CLI)
- Docker

### Local Setup

Clone the repository:
```sh
git clone https://github.com/shilpamusale/fidelity-engine.git
cd fidelity-engine
```

Create a virtual environment and install dependencies:
```sh
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Set up your `.env` file:
```sh
cp .env.example .env
# Now, edit the .env file with your key
```

### Running the Data Pipeline

To build the knowledge base from scratch, run the data sourcing script (details to be added):
```sh
python -m data.build_knowledge_base --condition "Type 2 Diabetes"
```

### Running the Application Locally

Start the agent service in one terminal:
```sh
adk web . --port 8001
```

In a second terminal, run the benchmark or a test script:
```sh
python -m tests.run_benchmark
```

---

## Evaluation Results

*(Placeholder for the final results table)*

| Agent Architecture   | TruthfulQA Accuracy | Notes                                         |
|----------------------|--------------------|-----------------------------------------------|
| Baseline LLM         | --                 | Prone to hallucination on complex criteria.   |
| RAG Agent            | --                 | Strong improvement on factual recall.         |
| Hierarchical System  | --                 | Best overall performance and efficiency.      |

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.