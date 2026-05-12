# Sentinel AI: Agentic DevOps Pipeline

Sentinel AI is a fully autonomous, multi-agent AI system designed to simulate, detect, diagnose, and remediate DevOps incidents in a microservices environment. It leverages large language models (LLMs), long-term memory, and an event-driven architecture to act as a virtual Site Reliability Engineer (SRE).

## 🚀 Architecture

The system is built on an orchestrator using **LangGraph**, consisting of four primary components in an iterative loop:

1. **Monitor Node**: Acts as the system's watchtower. It continuously tracks CPU, Memory, Latency, and Error Rates against defined baselines. If a threshold is breached, it raises an alert.
2. **Diagnosis Agent**: The brains of the operation. Triggered by an alert, it queries **ChromaDB** for similar past incidents (Memory-First design) to speed up resolution. It then utilizes custom tools to retrieve live logs and metrics to pinpoint the root cause.
3. **Remediation Agent**: The hands of the system. Once the root cause is established, it formulates an action plan and safely executes low-risk remediation tools (e.g., `restart_service`).
4. **Post-Mortem Agent**: The memory builder. After an incident is resolved, it summarizes the Symptoms, Root Cause, and Resolution, and persists the "case file" to ChromaDB to train the Diagnosis Agent for the future.

### Tech Stack
- **Backend**: FastAPI, Python, WebSockets
- **Agent Orchestration**: LangChain, LangGraph
- **Vector Database (Memory)**: ChromaDB
- **Frontend Dashboard**: React, Vite, Vanilla CSS
- **LLM**: OpenAI GPT models

## 🛠️ How to Run

### 1. Backend Setup
Create a virtual environment and install dependencies:
```bash
python -m venv venv
# Activate the venv (Windows)
venv\Scripts\activate
# Activate the venv (Mac/Linux)
source venv/bin/activate

pip install -r requirements.txt
```

Set up your environment variables:
Create a `.env` file in the root directory and add your OpenAI API key:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

Start the FastAPI server:
```bash
uvicorn api.main:app --port 8000 --reload
```

### 2. Frontend Dashboard Setup
In a second terminal, navigate to the dashboard directory and run the React app:
```bash
cd dashboard
npm install
npm run dev
```

Open your browser to `http://localhost:5173/`.

## 🎮 Usage
Once the frontend and backend are running, open the Sentinel AI Dashboard. You will see a grid of healthy services polling via WebSockets in real-time.

1. Click **Trigger Memory Leak** in the dashboard.
2. Watch the `auth-service` memory start to steadily climb.
3. When memory crosses the 65% threshold, the Monitor Node fires.
4. Watch the **Agent Event Stream** on the right side of the dashboard as the Diagnosis, Remediation, and Post-Mortem agents spin up, investigate logs, restart the service, and log the incident to ChromaDB autonomously!
