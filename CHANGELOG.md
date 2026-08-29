
# CHANGELOG - Forge Labs Frontier

## [1.0] Baseline - 50%
- Simple RAG, no verification
- Fail: contradiction handling
- Result: 50% accuracy

## [2.0] Improved - 85% (+70%)
- Added Verifier Agent with auto-retry
- Added Retriever with page citations
- Added Compliance Judge with human flag
- Result: 50% -> 85%, Time 45m -> 1.8m (-96%)
- Trajectories: agent_trajectories/trajectory_retry.json proves retry
- Reproduce: python improved/eval_offline.py

## Hot Take
Verification > Better Retrieval for BFSI compliance

