# 🛡️ Sentinel AI — Autonomous DevOps Incident Response Agent

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat&logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_Orchestration-FF6B35?style=flat)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Memory-764ABC?style=flat)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react&logoColor=black)

> **An autonomous, memory-augmented multi-agent system that detects, diagnoses, and remediates DevOps incidents in real-time — with zero human intervention.**

---

## ▶️ Demo

> ⚠️ *Add your dashboard GIF/screenshot here!*
> Record a 2-3 min Loom/YouTube walkthrough showing the memory leak trigger → agent response → ChromaDB post-mortem. Paste the link below.*

[![Watch the Demo](path/to/your/thumbnail.png)](https://www.loom.com/share/4370722728fd49308f54cf38656a8b57)

<img width="1910" height="768" alt="image" src="https://github.com/user-attachments/assets/8f97109c-a69d-4616-9dd8-3ea035dee82a" />


---

## 🔥 The Problem

In modern microservice architectures, memory leaks, CPU spikes, and cascading failures require **manual SRE intervention**. The on-call engineer has to:

1. Get paged at 2am
2. SSH into a service, pull logs, check metrics
3. Diagnose the root cause under pressure
4. Execute a fix (or escalate)
5. Write a post-mortem

This process is slow, error-prone, and expensive. The industry average **Mean Time to Recovery (MTTR)** for a P1 incident is **60-90 minutes**.

## ✅ The Solution

Sentinel AI **automates the full Tier-1 SRE workflow**. When a metric anomaly is detected, a coordinated team of AI agents wakes up, investigates the issue using live metrics and logs, retrieves context from a **long-term memory layer**, executes a safe remediation, and logs a structured post-mortem — all autonomously, in seconds.

---

## 🏗️ Architecture

```mermaid
flowchart TD
    SIM["🖥️ Simulation Environment<br/>(Microservices + Incident Injector)"]
    MON["👁️ Monitor Node<br/>(Threshold Detection)"]
    DIA["🧠 Diagnosis Agent<br/>(LLM + Tool Use)"]
    REM["🔧 Remediation Agent<br/>(LLM + Tool Use)"]
    PM["📝 Post-Mortem Agent<br/>(LLM Summarizer)"]
    MEM[("🗄️ ChromaDB<br/>Vector Memory")]
    API["⚡ FastAPI Backend<br/>(REST + WebSocket)"]
    UI["🖼️ React Dashboard<br/>(Live Agent Stream)"]

    SIM -->|"tick()"| MON
    MON -->|"alert triggered"| DIA
    DIA -->|"query past incidents"| MEM
    MEM -->|"similar cases"| DIA
    DIA -->|"root cause"| REM
    REM -->|"remediation executed"| PM
    PM -->|"save case file"| MEM
    API -->|"WebSocket stream"| UI
    SIM --- API
```

### The 4-Agent Pipeline

| Agent | Role | LLM Used |
|---|---|---|
| **Monitor Node** | Pure Python rule-engine. Checks CPU, Memory, Latency, Error Rate against baselines. Zero LLM cost. | None |
| **Diagnosis Agent** | Queries ChromaDB for historical patterns, then uses tools (`get_metrics`, `get_logs`) to verify root cause. | GPT-5.4 |
| **Remediation Agent** | Reads diagnosis, classifies fix as LOW/MEDIUM/HIGH risk, and executes safe actions autonomously. | GPT-5.4 |
| **Post-Mortem Agent** | Extracts Symptoms, Root Cause, and Resolution from the conversation and persists it to ChromaDB. | GPT-5.4 |

### Memory-First Diagnosis
A key design pattern: the Diagnosis Agent **always checks ChromaDB first** before deep analysis. After several incident cycles, the system recognizes recurring patterns and resolves them significantly faster — a compounding intelligence effect.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Agent Orchestration | LangGraph, LangChain |
| LLM | OpenAI GPT-5.4 |
| Vector Memory | ChromaDB (persistent) |
| Observability | LangSmith (tracing) |
| API Layer | FastAPI, WebSockets |
| Frontend | React 18, Vite, Vanilla CSS |
| Simulation | Custom Python tick-based microservice simulator |
| Evaluation | Custom eval harness over canonical incident scenarios |

---

## 🚀 How to Run

### Prerequisites
- Python 3.10+
- Node.js 18+
- An OpenAI API Key

### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/VnMxMadMax/devops-agent.git
cd devops-agent

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure your API keys
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
# (Optional) add LANGCHAIN_API_KEY to enable LangSmith tracing

# Start the API server
uvicorn api.main:app --port 8000 --reload
```

### 2. Frontend Setup

```bash
# In a second terminal
cd dashboard
npm install
npm run dev
```

Open **`http://localhost:5173`** in your browser.

---

## 🎮 Usage

1. Open the dashboard at `http://localhost:5173`
2. The service health matrix shows all simulated microservices as **healthy**
3. Click **"Trigger Memory Leak"** — the `auth-service` memory begins to climb
4. When memory crosses **65%**, the Monitor Node fires automatically
5. Watch the **Agent Event Stream** as the pipeline runs:
   - 🧠 Diagnosis Agent queries ChromaDB for past incidents
   - 🔧 Remediation Agent restarts the service
   - 📝 Post-Mortem Agent logs the case to vector memory
6. On the next incident, the Diagnosis Agent will recognize the pattern from memory!

> **💡 Cost Note:** The LangGraph pipeline is **event-driven**. LLM calls only happen when an active incident is detected. Healthy ticks are pure Python — zero API cost.

---

## 📊 Observability — LangSmith Tracing

Every Diagnosis, Remediation, and Post-Mortem run is automatically traced when the following keys are present in your `.env`:

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2-...
LANGCHAIN_PROJECT=sentinel-ai
```

LangChain picks these up at import time — no code changes required. Open [smith.langchain.com](https://smith.langchain.com), select the `sentinel-ai` project, and you'll see a full trace per incident: token usage, latency per node, tool calls, and the exact prompt that produced each agent response. This makes debugging agent regressions trivial and is invaluable for tuning system prompts.

---

## 🧪 Evaluation Harness

Sentinel AI ships with a deterministic eval suite under [`evals/`](./evals/) that scores the full LangGraph pipeline against a canonical set of incident scenarios.

### What it measures

For each scenario in `evals/incidents.jsonl`, the harness runs the full pipeline and scores four binary signals:

| Signal | What it checks |
|---|---|
| `memory_query_called` | Did the Diagnosis agent query ChromaDB **first**, as required by the system prompt? |
| `correct_service` | Did the Diagnosis output mention the actually-degraded service? |
| `root_cause_matched` | Did the diagnosis surface at least one expected root-cause keyword (e.g., `heap`, `thread pool`, `circuit breaker`)? |
| `remediation_addressed` | Did the Remediation agent either execute a safe fix (e.g., `restart_service`) **or** explicitly recommend an acceptable mitigation (e.g., circuit-breaker, scaling, escalation)? |

### Run it

```bash
python -m evals.run_evals --verbose
```

Output:
```
  [PASS] eval-001  memory_leak_auth
  [PASS] eval-002  cpu_spike_api_gateway
  [PASS] eval-003  latency_spike_payment
  [PASS] eval-004  error_rate_order

  Passed: 4/4  (100%)
```

A machine-readable summary is written to `evals/last_report.json` after every run — useful for CI integration later.

---

## 🔮 Future Scope

- [ ] **Real Alert Ingestion** — Wire to Prometheus/Datadog webhooks instead of the simulation
- [ ] **Slack / PagerDuty Integration** — Post incident summaries and resolution notices to on-call channels
- [ ] **Kubernetes Support** — Add remediation tools for pod restarts and deployment rollbacks
- [ ] **Local LLM Mode** — Replace OpenAI with Llama 3 / Mistral via Ollama for privacy and zero inference cost
- [ ] **Multi-Incident Concurrency** — Handle parallel incidents across different services simultaneously

---

## 📁 Project Structure

```
devops-agent/
├── agents/
│   ├── orchestrator.py    # LangGraph graph definition & node wiring
│   ├── monitor.py         # Threshold-based alert detection
│   ├── diagnosis.py       # Memory-first root cause analysis
│   ├── remediation.py     # Risk-classified auto-remediation
│   ├── postmortem.py      # Incident summarization & ChromaDB persistence
│   ├── tools.py           # get_metrics, get_logs, restart_service, query_memory
│   └── state.py           # Shared AgentState schema (LangGraph)
├── api/
│   ├── main.py            # FastAPI app, WebSocket endpoint, REST routes
│   └── models.py          # Pydantic request/response schemas
├── memory/
│   └── incident_memory.py # ChromaDB client wrapper
├── simulator/
│   ├── environment.py     # Simulation tick engine
│   ├── incident.py        # Incident definitions & metric impact curves
│   └── service.py         # Microservice model
├── evals/
│   ├── incidents.jsonl    # Canonical eval scenarios (one per incident type)
│   └── run_evals.py       # Eval harness — scores the full pipeline end-to-end
└── dashboard/             # React + Vite frontend
    └── src/
        ├── App.jsx
        └── index.css
```

---

*Built as a portfolio project to demonstrate real-world multi-agent LLM system design, async Python architecture, and full-stack integration.*
