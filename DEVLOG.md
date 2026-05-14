# Sentinel AI — Dev Log

> A daily log of progress, blockers, and learnings while building the DevOps Incident Response Agent.

---

## Quick Stats
- **Project Start:** 25 April 2026  
- **Target Completion:** 10 May 2026  
- **Current Phase:** Phase 1 — Foundation  

---

## Log

---

### Day 1 — `25 April 2026`
**Phase:** Foundation  
**Time Spent:** 1 hour  

#### What I Did
- Initialized project structure (directories, `.env`, `requirements.txt`)
- Designed **service simulation layer**
  - Implemented `Service`, `Metrics`, and `Thresholds` using Pydantic
  - Defined baseline metrics and alert thresholds for each service
- Built **log generation module**
  - Created structured log generator with:
    - ISO timestamps
    - Service-specific messages
    - Log levels (`INFO`, `DEBUG`)
  - Introduced randomness for realistic system behavior
- Performed basic testing
  - Verified service initialization
  - Validated log generation output

---

#### Challenges & How I Solved Them
- **Challenge:** Defining realistic system metrics and thresholds  
- **Solution:**  
  - Researched standard production ranges  
  - Used AI tools and documentation to approximate real-world values  

---

#### Stuck On / Unresolved
- None  

---

#### Key Learnings
- Importance of **structured logging**
- Modeling microservices using Pydantic
- Basics of system observability simulation

---

#### Impact
- Established the foundation for simulating service health and generating logs  

---

#### Tomorrow's Goal
- Implement **incident scenarios**
  - Memory leak  
  - Cascading failure  
- Build **metric generator**
  - Continuous metric updates  
  - Controlled randomness around baseline values  

---

### Day 2 — `26 April 2026`
**Phase:** Foundation  
**Time Spent:** 2.5 hours  

#### What I Did
- Implemented **metric generation system**
  - Built `generate_normal_metrics()` for continuous updates
- Refactored logic from **random reset → baseline + jitter model**
  - Metrics now fluctuate around stable baseline values
- Added **baseline field** to `Service` model
  - Prevents long-term drift in metrics
- Implemented **bounded updates**
  - CPU & Memory clamped between `0–100`
  - Latency & Error Rate constrained to `>= 0`
- Improved realism in simulation:
  - Introduced **small jitter ranges** instead of full random values
  - Adjusted latency to allow **spike-like behavior**
- Fixed multiple issues during testing:
  - Incorrect `round()` usage
  - Removed unnecessary imports

---

#### Challenges & How I Solved Them
- **Challenge:** Metrics behaving unrealistically (sudden jumps like 30% → 95%)  
- **Solution:**  
  - Replaced full random generation with **delta-based jitter**

- **Challenge:** Metrics drifting over time (random walk problem)  
- **Solution:**  
  - Introduced **baseline metrics** and recalculated values relative to it  

- **Challenge:** Keeping values within valid bounds  
- **Solution:**  
  - Implemented `clamp()` function using `min()` and `max()`  

---

#### Stuck On / Unresolved
- Status is still **static ("healthy")**
- No **threshold comparison logic** implemented yet  

---

#### Key Learnings
- Difference between **random noise vs realistic simulation**
- Importance of **baseline in time-series systems**
- Understanding of **random walk problem**
- How to enforce constraints using **clamping**
- Small design decisions significantly impact **system realism**

---

#### Impact
- Upgraded system from **static + random → controlled dynamic simulation**
- Metrics now behave like **real production telemetry**
- Established foundation for:
  - Alerting system
  - Incident simulation
  - Anomaly detection

---

#### Tomorrow's Goal
- Design and implement **Incident system**
  - Create `Incident` Pydantic model in `simulator/incidents.py`
  - Define attributes such as:
    - incident name
    - affected service(s)
    - root cause
    - severity
    - duration / active state
- Plan integration with system components:
  - Modify `metric_generator.py`
    - Support **incident-driven metric behavior** (e.g., memory leak → gradual increase)
  - Modify `log_generator.py`
    - Inject **ERROR logs and stack traces** during incidents
- Prepare architecture for:
  - Switching between **normal vs incident states**
  - Simulating real-world failures (memory leak, cascading failure)

---

### Day 3 — `27 April 2026`
**Phase:** Foundation  
**Time Spent:** ~3–4 hours  

#### What I Did
- Designed and implemented **Incident system**
  - Created `Incident` Pydantic model with:
    - identity (name, service, severity, status)
    - timeline (start_time, end_time)
    - root cause and description
    - behavior overrides (`metric_impact`, `log_impact`)
- Implemented **incident-driven metric behavior**
  - Built `apply_incident_to_metrics()`
  - Introduced **baseline-shifting mechanism**
    - Instead of modifying metrics directly, incidents modify `service.baseline`
    - Enables realistic degradation when combined with jitter
- Implemented **incident-driven log injection**
  - Built `apply_incident_to_logs()`
  - Added probabilistic error log generation using:
    - `frequency`
    - service-specific error messages
    - dynamic log levels (`ERROR`)
- Created first prebuilt incident:
  - **Memory Leak in auth-service**
    - Gradual memory increase (`+0.5 per tick`)
    - Injects JWT-related memory failure logs
- Built **SimulationEnvironment (core orchestrator)**
  - Manages:
    - services
    - active incidents
  - Implemented:
    - `trigger_incident()`
    - `resolve_incident()`
    - `tick()` → system heartbeat
- Integrated full system flow inside `tick()`:
  1. Apply incident → modify baseline  
  2. Generate metrics → baseline + jitter  
  3. Generate normal logs  
  4. Inject incident logs  
  5. Return system state  
- Updated `main.py` to run real-time simulation:
  - Added infinite loop (`while True`)
  - Introduced 1-second heartbeat using `time.sleep(1)`
  - Enabled live monitoring of:
    - metric degradation
    - error log generation  

---

#### Challenges & How I Solved Them
- **Challenge:** Incident effects getting overwritten by metric jitter  
- **Solution:**  
  - Shifted design from **direct metric modification → baseline modification**  

- **Challenge:** Designing flexible incident behavior  
- **Solution:**  
  - Used **config-driven approach** (`metric_impact`, `log_impact`) instead of hardcoding logic  

- **Challenge:** Integrating multiple components (metrics, logs, incidents)  
- **Solution:**  
  - Introduced **SimulationEnvironment as a central orchestrator**  

- **Challenge:** Ensuring realistic log behavior (not too frequent / not too rare)  
- **Solution:**  
  - Used **probabilistic log injection** via `random.random()` and `frequency`  

---

#### Stuck On / Unresolved
- No **incident recovery logic** implemented yet  
- Baseline may **drift indefinitely** during long-running incidents  
- No **threshold-based alerting system** yet  
- No **incident scheduling (automatic triggering)**  

---

#### Key Learnings
- Importance of **baseline-driven simulation in time-series systems**
- Difference between:
  - **state mutation (bad)** vs **state evolution (good)**
- How to design **config-driven systems** for flexibility
- Role of **probability in realistic system behavior**
- Understanding of **system orchestration layer**
- How real-world systems simulate:
  - failures
  - degradation
  - observability signals  

---

#### Impact
- Transitioned system from:
  - **passive simulation → active failure simulation**
- Built a **fully functioning incident simulation engine**
- Enabled real-time visualization of:
  - system degradation
  - error propagation
- Established strong foundation for:
  - anomaly detection (ML/LLM)
  - root cause analysis
  - automated incident response agents  

---

#### Tomorrow's Goal
- Begin preparation for **Phase 2 (LangGraph Agents)**
  - Use logs + metrics as input for reasoning agents  

---

### Day 4 — `30 April 2026`
**Phase:** Phase 2 — LangGraph Agents (Foundation)  
**Time Spent:** ~3–4 hours  

#### What I Did
- Designed **AgentState (shared state for LangGraph pipeline)**
  - Defined structured data flow between agents:
    - `services`, `logs` → input
    - `alert` → Monitor output
    - `messages` → LLM conversation memory
    - `root_cause`, `remediation_plan` → future outputs
  - Ensured compatibility with LangGraph’s state-passing mechanism

- Implemented **LLM Tools (agents/tools.py)**
  - Created tool interfaces using `@tool` decorator:
    - `get_service_metrics`
    - `get_service_logs`
    - `restart_service`
  - Wrote **detailed docstrings** with:
    - Input / Output schema
    - Usage conditions (“Use this tool when…”)
    - Contextual notes for reasoning
  - Focused on making tools **LLM-readable and self-explanatory**

- Built **Monitor Agent (rule-based)**
  - Implemented `monitor_node(state)`
  - Compared real-time metrics vs thresholds
  - Generated structured `alert` object on breach:
    - service name
    - metric
    - current value vs threshold
    - severity level
  - Added `_calculate_severity()` helper for realistic alert classification
  - Designed early-exit logic (first alert only) to simplify V1 pipeline

- Implemented **Diagnosis Agent (LLM-based)**
  - Created `diagnosis_node(state)`
  - Integrated `ChatOpenAI` with tool binding (`llm.bind_tools`)
  - Designed system prompt for:
    - root cause investigation
    - tool-guided reasoning
  - Passed `messages` as conversation history
  - Appended LLM response back into state for downstream agents

---

#### Challenges & How I Solved Them
- **Challenge:** Designing a clean data contract between agents  
- **Solution:**  
  - Created a well-structured `AgentState` to standardize communication  

- **Challenge:** Making tools usable by LLM (not just code functions)  
- **Solution:**  
  - Focused heavily on **docstring quality and clarity**  
  - Added explicit “when to use” instructions  

- **Challenge:** Preventing LLM from hallucinating without context  
- **Solution:**  
  - Injected structured alert data into system prompt  
  - Grounded reasoning using real metrics and logs  

- **Challenge:** Avoiding overly complex alert handling in V1  
- **Solution:**  
  - Implemented **single-alert early exit strategy** in Monitor Agent  

---

#### Stuck On / Unresolved
- No **structured parsing of root cause** from LLM output yet  
- No **tool execution loop (ReAct / LangGraph orchestration)** implemented  
- Remediation agent not implemented yet  
- No **multi-alert handling (batch processing)**  

---

#### Key Learnings
- Importance of **state design in agent-based systems**
- How LangGraph uses **shared state instead of direct function calls**
- Role of **tools as interfaces for LLM reasoning**
- Difference between:
  - **LLM capability** vs **LLM guidance via prompts**
- How structured prompts + tools enable **controlled reasoning**
- Early understanding of **agent pipelines (Monitor → Diagnosis → Remediation)**  

---

#### Impact
- Transitioned system from:
  - **simulation engine → intelligent agent system**
- Built foundation for:
  - autonomous incident detection
  - AI-driven root cause analysis
- Established core architecture for:
  - LangGraph orchestration
  - tool-based reasoning agents
- System is now ready for:
  - full agent pipeline execution  

---

#### Tomorrow's Goal
- Implement **Remediation Agent**
  - Generate actionable recovery steps
- Build **LangGraph Orchestrator**
  - Define nodes and edges (Monitor → Diagnosis → Remediation)
  - Implement execution flow
- Add **tool execution loop**
  - Enable LLM to call tools dynamically
- Begin **structured output parsing**
  - Extract root cause and remediation plan from LLM responses

---

### Day 5 — `10 May 2026 (LAtE NIGHT 2AM)`
**Phase:** Phase 2 — LangGraph Agent Orchestration  
**Time Spent:** ~3 hours  

#### What I Did
- Implemented initial **LangGraph workflow orchestration**
  - Created `StateGraph(AgentState)`
  - Registered core agent nodes:
    - `monitor`
    - `diagnosis`
    - `remediation`
  - Compiled the graph into an executable workflow pipeline

- Designed **agent execution flow**
  - Connected:
    - Monitor → Diagnosis → Remediation
  - Added graph entry point and finish point
  - Refactored architecture toward event-driven execution

- Implemented **conditional routing logic**
  - Added `route_after_monitor()` function
  - Enabled dynamic branching:
    - If alert exists → continue investigation
    - If no alert → terminate workflow
  - Prevented unnecessary diagnosis/remediation execution during healthy system states

- Learned and integrated **LangGraph ToolNode execution model**
  - Studied how tool execution loops work in ReAct-style agents
  - Understood distinction between:
    - LLM requesting tools
    - LangGraph executing tools
  - Explored AIMessage → ToolNode → ToolMessage lifecycle

- Designed **ReAct reasoning loop architecture**
  - Planned iterative investigation flow:
    - Diagnosis Agent
    - Tool Execution
    - Return to Diagnosis
  - Added conceptual design for:
    - `should_continue()` conditional routing
    - tool-based recursive reasoning
  - Established architecture for multi-step root cause analysis

- Planned integration of shared tool execution system
  - Centralized tools:
    - `get_service_logs`
    - `get_service_metrics`
    - `restart_service`
  - Prepared graph structure for:
    - ToolNode execution
    - dynamic investigation loops

---

#### Challenges & How I Solved Them
- **Challenge:** Understanding how LangGraph actually executes tools  
- **Solution:**  
  - Learned that `llm.bind_tools()` only exposes tools to the LLM  
  - Real execution requires a dedicated `ToolNode`

- **Challenge:** Understanding ReAct loop behavior  
- **Solution:**  
  - Broke the flow into:
    - AI reasoning
    - tool request
    - tool execution
    - iterative reasoning continuation

- **Challenge:** Avoiding unnecessary pipeline execution during healthy states  
- **Solution:**  
  - Implemented conditional graph routing after Monitor Agent

- **Challenge:** Understanding message-driven state transitions  
- **Solution:**  
  - Studied how LangGraph appends:
    - `AIMessage`
    - `ToolMessage`
    - conversation history
    into shared state automatically

---

#### Stuck On / Unresolved
- ToolNode execution loop not fully integrated yet
- Tools still use dummy/static data instead of simulator state
- No structured root cause extraction implemented yet
- No remediation verification loop yet
- Diagnosis and remediation tools are not separated yet

---

#### Key Learnings
- Deep understanding of **LangGraph orchestration**
- Difference between:
  - static pipelines
  - conditional agent workflows
- How ReAct agents perform:
  - iterative reasoning
  - evidence gathering
  - tool-assisted investigation
- Internal lifecycle of:
  - `AIMessage`
  - `ToolNode`
  - `ToolMessage`
- Importance of conditional routing in autonomous systems
- How agent memory/state evolves across graph execution

---

#### Impact
- Transitioned architecture from:
  - standalone agents
  → orchestrated multi-agent workflow
- Established foundation for:
  - autonomous investigations
  - iterative root cause analysis
  - dynamic tool execution
- System is now approaching:
  - fully autonomous incident response behavior

---

#### Tomorrow's Goal
- Fully integrate ToolNode execution loop
- Connect tools to live simulator state
- Implement real dynamic tool responses
- Add structured root cause extraction
- Execute first complete end-to-end autonomous incident workflow

---

### Day 6 — `10 May 2026 MORNING`
**Phase:** Phase 3 — Memory & Intelligence  
**Time Spent:** ~2–3 hours  

#### What I Did
- Implemented the foundation of the **long-term memory system** using ChromaDB
  - Created `memory/incident_memory.py`
  - Initialized persistent local vector database using:
    - `chromadb.PersistentClient(path="./chroma_db")`
  - Created / loaded `incident_history` collection
- Built memory helper functions:
  - `save_incident()`
    - Stores resolved incidents into vector memory
    - Combines:
      - symptoms
      - root cause
      - remediation
    - Stores metadata for structured retrieval
  - `search_past_incidents()`
    - Performs semantic similarity search using incident symptoms
    - Retrieves related historical incidents
- Learned and implemented **semantic vector search concepts**
  - Understood difference between:
    - keyword matching
    - embedding similarity search
  - Learned how ChromaDB automatically:
    - embeds text
    - compares semantic meaning
    - retrieves closest matches
- Integrated memory into the **Diagnosis Agent**
  - Imported memory search into `agents/tools.py`
  - Created new tool:
    - `query_incident_memory(symptoms)`
  - Added formatting logic to convert retrieved ChromaDB documents into LLM-readable context
  - Implemented empty-result handling:
    - returns `"No past incidents found."`
- Updated Diagnosis Agent behavior
  - Added `query_incident_memory` to tool list
  - Modified system prompt to enforce:
    - memory lookup before investigation
    - historical RCA guidance
    - validation of past incidents using logs and metrics
- Improved understanding of:
  - Retrieval-Augmented Generation (RAG)
  - memory-augmented agents
  - operational knowledge systems
  - AI-assisted incident response workflows

---

#### Challenges & How I Solved Them
- **Challenge:** Confusion about how symptoms are searched inside stored documents  
- **Solution:**  
  - Learned that ChromaDB performs:
    - semantic embedding search
    - not manual keyword search
  - Understood that the current symptoms themselves become the search query  

- **Challenge:** Understanding ChromaDB query response structure  
- **Solution:**  
  - Explored nested result format:
    - `results["documents"][0]`
  - Learned that Chroma supports multi-query retrieval, which is why results are nested arrays  

- **Challenge:** Formatting vector search results for LLM reasoning  
- **Solution:**  
  - Converted retrieved incidents into structured readable context:
    - `Past Incident #1`
    - `Past Incident #2`

- **Challenge:** Debugging tool implementation  
- **Solution:**  
  - Fixed typo bug:
    - `appen()` → `append()`

---

#### Stuck On / Unresolved
- Memory currently stores incidents as raw concatenated text only
- No similarity threshold filtering implemented yet
- No automatic memory write-back after remediation success
- No incident summarization/compression pipeline yet

---

#### Key Learnings
- Difference between:
  - traditional databases
  - vector databases
- Fundamentals of:
  - embeddings
  - semantic similarity
  - vector retrieval
- How memory transforms an LLM workflow into an:
  - adaptive
  - learning
  - agentic system
- Importance of:
  - retrieval before reasoning
  - evidence validation after retrieval
- How production-grade RCA systems combine:
  - memory retrieval
  - hypothesis generation
  - evidence verification

---

#### Impact
- Transitioned the system from:
  - **stateless diagnosis → memory-augmented intelligence**
- Enabled historical incident recall and reuse
- Established the foundation for:
  - self-improving agents
  - operational learning
  - incident knowledge reuse
  - future RAG workflows
- System can now:
  - remember past failures
  - retrieve similar incidents
  - guide future diagnosis using historical evidence

---

#### Tomorrow's Goal
- Automatically save successful remediations into memory
- Connect remediation success → memory write-back loop
- Begin building:
  - Post-Mortem Agent
  - incident timeline generation
  - structured incident reports
- Explore similarity score filtering for higher-quality memory retrieval

### Day 7 — `11 May 2026`
**Phase:** Phase 4 — API & Real-Time Infrastructure  
**Time Spent:** ~2–3 hours  

#### What I Did
- Began implementation of the **FastAPI backend layer**
  - Created foundational API architecture for Sentinel AI
  - Structured backend into:
    - `api/models.py`
    - `api/main.py`

- Designed **Pydantic API schemas**
  - Implemented:
    - `TriggerIncidentRequest`
    - `ServiceStatus`
    - `SimulationStatusResponse`
  - Standardized request/response contracts between backend and future frontend dashboard

- Built initial **REST API endpoints**
  - `GET /health`
    - Simple health verification endpoint
  - `GET /status`
    - Returns:
      - live service states
      - metrics snapshot
      - active incidents
  - `POST /incident/trigger`
    - Dynamically triggers simulated incidents
  - `POST /incident/resolve`
    - Resolves active incidents

- Integrated **SimulationEnvironment** into FastAPI
  - Created module-level shared environment instance
  - Enabled persistent in-memory simulation state across API requests

- Implemented first **WebSocket simulation endpoint**
  - Added:
    - `@app.websocket("/ws/simulation")`
  - Established real-time communication pipeline between:
    - simulation environment
    - LangGraph agent system
    - frontend dashboard (future phase)

- Integrated **LangGraph execution pipeline** into WebSocket loop
  - Built continuous simulation heartbeat:
    1. Advance simulation (`tick()`)
    2. Build `initial_state`
    3. Execute LangGraph agent workflow
    4. Stream agent messages over WebSocket
  - Added 1-second async simulation cycle

- Implemented **threadpool offloading** for LangGraph execution
  - Used:
    ```python
    asyncio.get_event_loop().run_in_executor()
    ```
  - Prevented FastAPI event loop blocking from synchronous `graph.invoke()`

- Streamed agent reasoning over WebSocket
  - Sent structured JSON messages:
    - message type
    - content
  - Prepared architecture for:
    - live agent workflow visualization
    - real-time dashboard updates

---

#### Challenges & How I Solved Them
- **Challenge:** Understanding async vs sync execution in FastAPI  
- **Solution:**  
  - Learned why `graph.invoke()` blocks the event loop
  - Used `run_in_executor()` to offload blocking LangGraph execution into worker threads

- **Challenge:** Designing shared vs isolated simulation state  
- **Solution:**  
  - Used:
    - module-level `env` for REST APIs
    - dedicated `ws_env` per WebSocket client
  - Prevented multi-client simulation collisions

- **Challenge:** Converting Pydantic service models into API-safe JSON  
- **Solution:**  
  - Used:
    ```python
    model_dump()
    ```
  - Standardized serialization for frontend consumption

- **Challenge:** Structuring the LangGraph initial state correctly  
- **Solution:**  
  - Built complete runtime state including:
    - services
    - logs
    - messages
    - active incidents
    - timestamp metadata

---

#### Stuck On / Unresolved
- Frontend dashboard not implemented yet
- WebSocket currently streams only agent messages
- No real-time metrics visualization yet
- No WebSocket reconnection handling
- Incident lifecycle events are not yet broadcast separately

---

#### Key Learnings
- Difference between:
  - synchronous AI execution
  - asynchronous web servers
- Importance of threadpool offloading in AI-powered APIs
- Real-world FastAPI WebSocket architecture patterns
- How stateful simulation environments behave inside API servers
- API schema design using Pydantic
- Building event-driven real-time systems
- How backend observability systems stream live operational data

---

#### Impact
- Transitioned Sentinel AI from:
  - standalone backend simulation
  → real-time observable platform
- Established foundation for:
  - live dashboards
  - streaming agent workflows
  - real-time incident visualization
- Created production-style architecture combining:
  - FastAPI
  - WebSockets
  - LangGraph
  - AI agents
  - simulation systems

---

### Day 8 — `12 May 2026`
**Phase:** Phase 5 — Frontend Dashboard Initialization  
**Time Spent:** ~2 hours  

#### What I Did
- Initialized **React + Vite Frontend**
  - Scaffolded a new project in the `dashboard/` directory
  - Set up standard frontend tooling and package dependencies
- Configured **FastAPI CORS Middleware**
  - Added `http://localhost:5173` to the backend origins whitelist
  - Enabled cross-origin requests for local frontend development
- Built foundational **React State Management**
  - Created `App.jsx`
  - Implemented state for:
    - services
    - active incidents
    - messages stream
- Integrated **WebSocket Client**
  - Connected React to `ws://localhost:8000/ws/simulation`
  - Began parsing `SystemMessage`, `AIMessage`, and `ToolMessage` payloads
- Developed **REST API Polling**
  - Added a 1-second interval to fetch system health via `/status`

---

#### Challenges & How I Solved Them
- **Challenge:** Cross-Origin Resource Sharing (CORS) blocking frontend requests
- **Solution:** 
  - Implemented FastAPI's `CORSMiddleware`
  - Explicitly mapped the Vite dev server port to the allowed origins list

---

#### Tomorrow's Goal
- Focus on UI/UX design and dashboard styling
- Build the Service Health Matrix visualization
- Implement the Agent Event Stream pane
- Add interactive controls to trigger/resolve incidents

---

### Day 9 — `13 May 2026`
**Phase:** Phase 5 — UI/UX Polish & Interactivity  
**Time Spent:** ~3 hours  

#### What I Did
- Engineered **Premium Dashboard Aesthetics**
  - Developed a dark mode, glassmorphism design in `index.css`
  - Integrated `lucide-react` for modern iconography
- Built the **Service Health Matrix**
  - Created dynamic service cards that change styling based on health status
  - Displayed live CPU, Memory, Latency, and Error Rate metrics
- Developed the **Agent Event Stream**
  - Created an auto-scrolling log pane
  - Added distinct styling for different LangGraph message types
- Implemented **Interactive Controls**
  - Added UI buttons to execute `POST /incident/trigger` and `POST /incident/resolve`
  - Connected the buttons directly to the simulation environment

---

#### Challenges & How I Solved Them
- **Challenge:** Managing real-time DOM updates without performance jitter
- **Solution:** 
  - Abstracted styling entirely to vanilla CSS classes
  - Utilized React `useRef` to implement smooth auto-scrolling on the event stream

---

#### Tomorrow's Goal
- Conduct end-to-end testing of the full system
- Fix edge-cases and harden the backend logic
- Finalize documentation and repository hygiene
- Complete the Sentinel AI project

---

### Day 10 — `14 May 2026`
**Phase:** Phase 6 — Testing, Hardening & Project Finalization  
**Time Spent:** ~2 hours  

#### What I Did
- Engineered **WebSocket Resilience**
  - Wrapped `graph.invoke` in a `try/except` block inside the async worker thread
  - Prevented LLM API timeouts/errors from crashing the WebSocket loop
- Addressed **Codebase Technical Debt**
  - Removed misleading `ws_env = env` alias variables
  - Explicitly documented the V1 shared environment design constraints
- Hardened **Repository Hygiene**
  - Overhauled `.gitignore` to strictly exclude local artifacts (`chroma_db/`, `node_modules/`, `.cache/`)
- Finalized **Project Documentation**
  - Authored a comprehensive `README.md`
  - Documented the multi-agent architecture, tech stack, and execution instructions
- Conducted **Final E2E Validation**
  - Successfully ran a full, end-to-end autonomous incident response cycle from the web UI

---

#### Challenges & How I Solved Them
- **Challenge:** Avoiding silent WebSocket failures on LLM API errors
- **Solution:** 
  - Caught synchronous exceptions in the thread pool and forwarded them as styled `SystemMessage` strings to the frontend, keeping the loop alive.

---

### PROJECT COMPLETED 

**Sentinel AI** is now a fully functional, autonomous, memory-augmented DevOps agent pipeline with a real-time observability dashboard!