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
<!-- Copy Day 1 structure and continue logging -->