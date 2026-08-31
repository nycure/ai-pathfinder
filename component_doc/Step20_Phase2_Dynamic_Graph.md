# Step 20: Phase 2 - Open-World & Infinite Dynamic Taxonomies

## Overview
In Phase 2 of Version 2, we broke free from the static, hardcoded 15-node JSON taxonomy (`skill_taxonomy.json`) and transformed the application into a truly **Open-World AI Pathfinder**. The system can now dynamically generate learning paths (DAGs) for any domain—ranging from Quantum Physics to Bakery Management—entirely on the fly.

## Architectural Changes

### 1. Dynamic LLM Graph Synthesis (`backend/agents/roadmap_agent.py`)
- **Pydantic Schemas**: We introduced `DynamicNode`, `DynamicEdge`, and `DynamicTaxonomyResponse` to strictly type the LLM's output.
- **Dynamic Prompting**: The `roadmap_agent.py` was refactored to instruct Gemini 2.5 Flash to generate 10-15 highly personalized milestones (nodes) and their exact prerequisite relationships (edges).
- **Personalization**: The prompt injects the user's specific target role, learning pace, weekly commitment, and existing skills (from their DB profile) to ensure the generated graph is hyper-personalized.

### 2. Upgraded Graph Engine (`backend/services/graph_engine.py`)
- **Dynamic Loading**: We added `load_dynamic_graph(nodes, edges)` to allow the engine to instantly wipe its memory and ingest the new AI-generated graph on a per-request basis.
- **DAG Self-Healing (Acyclicity Guard)**: Because Large Language Models can occasionally hallucinate circular logic (e.g., A requires B, and B requires A), we implemented `ensure_acyclic()`.
  - This algorithm uses `networkx.find_cycle()` to detect impossible loops.
  - If a loop is found, it automatically severs the connecting edge, guaranteeing a valid Directed Acyclic Graph (DAG) before sending the payload to the frontend. This prevents React Flow from crashing during the topological layout phase.

### 3. Frontend Compatibility
- Zero changes were required on the frontend! Because the new dynamic LLM output adheres strictly to the existing `RoadmapResponse` schema, React Flow effortlessly parses and renders the new open-world coordinates and nodes.

## Status
- **Implementation**: 🟢 Completed
- **Dependencies**: `google-genai`, `networkx`, `pydantic`
- **Next Steps**: Phase 3 (LLM Cost & Latency Optimization) to implement aggressive semantic caching and streaming for these complex generations.
