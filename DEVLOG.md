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