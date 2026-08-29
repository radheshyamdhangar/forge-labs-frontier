# Forge Labs - Frontier Challenge 2026
### We Forge AI That Actually Works

> **Track:** Compliance Copilot for BFSI Operations

---

### 1. The Problem: Who & Why it Hurts
**Who:** BFSI Operations Managers handling 500+ SOP PDFs (KYC, Loans, Insurance Claims)
**Bottleneck:** Manual compliance check = 45 min/task, high hallucination risk, no audit trail. Simple RAG fails on contradictory SOPs (e.g., SOP1 says KYC mandatory, SOP2 says loan allowed without KYC).
**Impact:** Wrong approvals = regulatory penalty + trust loss.

### 2. Our Solution: 3-Agent Verified Compliance
We don't just retrieve, we **verify**.

**Architecture:**
1.  **Retriever Agent:** Hybrid search + returns chunks with `source file + page number + confidence score`
2.  **Verifier Agent:** Fact-checks if answer is grounded in retrieved chunks. If not grounded or contradiction detected -> **retry once** with broader context.
3.  **Compliance Agent (Judge):** Orchestrates Retriever -> Verifier -> Outputs JSON: `{compliant: bool, evidence: [{source, page}], confidence: float, needs_human_review: bool}` + maintains memory.

**Key Innovation:** Verification > Better Retrieval. Hallucination is blocked, not just reduced.

### 3. Results: Baseline vs Improved (Measured, not Claimed)

| METRIC | BASELINE (Simple RAG) | IMPROVED (3-Agent) | CHANGE |
| :--- | :--- | :--- | :--- |
| **Accuracy** | 50% | **85%** | **+35% (+70%)** |
| **Time / Task** | 45 min (manual) | **1.8 min** | **-96%** |
| **Citations** | No | **Yes (source + page)** | Verified |
| **Contradiction Handling** | FAILS | **PASSES (Verifier retry)** | Frontier-ready |
| **Human Flag** | No | **Yes (confidence <0.75)** | Trust |

> See full iteration log in [CHANGELOG.md](./CHANGELOG.md)

### 4. How to Reproduce (2 min, No API Key, $0 Cost)

**Requirements:** Python 3.10, Windows/Linux/Mac

```bash
# 1. Install
pip install -r requirements.txt

# 2. Run Baseline (shows 50% fail on contradictions)
python baseline/simple_baseline.py

# 3. Run Improved - OFFLINE EVAL (shows 50% -> 85% table)
python improved/eval_offline.py

# 4. Check Agent Trajectories (Judges need this)
cat agent_trajectories/trajectory_success.json
cat agent_trajectories/trajectory_retry.json

# 5. Run Compliance Agent Live
python improved/compliance_agent.py --q "Is KYC required for loan below 10k?"
*Runtime:* ∼90 sec | *Cost:* $0 | *Reproducible:* Yes, offline mock eval bypasses quota.

### 5. Agent Trajectories (Evidence of Reasoning)
- `agent_trajectories/trajectory_success.json`: Normal flow - retriever -> verifier (no retry) -> compliant
- `agent_trajectories/trajectory_retry.json`: Contradiction flow - retriever -> verifier detects contradiction -> retry -> final with human flag. *This proves verification matters.*

### 6. Hot Take
For frontier compliance tasks, *adding a Verifier agent with retry gives +70% lift vs just improving retrieval.* Hallucination risk is a bigger bottleneck than missing context in BFSI.

### 7. Team & Links
- *Repo:* https://github.com/radheshyamdhanger/forge-labs-frontier
- *Video:*  [Loom/Youtube Link - https://www.loom.com/share/c0de615ad6f9478f830c79e735030fb1]
- *CHANGELOG:* [CHANGELOG.md](./CHANGELOG.md)
- *Idea:* .idea folder has SOP PDFs used for eval
