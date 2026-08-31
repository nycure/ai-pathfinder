# Step 7: Roadmap Synthesizer Agent

## Component Overview
The Roadmap Synthesizer Agent is the core orchestration layer of the backend. It merges the extracted `LearnerProfile` (Step 6), the NetworkX topological logic (Step 3), and the curated RAG catalog (Step 4) to produce the final, frontend-ready `RoadmapResponse`.

## Architectural Purpose
Rather than relying on the LLM to blindly generate a curriculum (which is prone to hallucinations and cyclic logic), this agent uses the LLM *only* to select the target end-nodes. The rest of the curriculum generation is deterministic:
1. **Target Selection (LLM)**: Gemini identifies which terminal nodes in our taxonomy map to the user's goal.
2. **Skill Normalization (Deterministic)**: Profile skills are filtered against the live taxonomy to eliminate unrecognized keys before they silently fail in the graph engine.
3. **Path Generation (Deterministic)**: NetworkX calculates all required ancestors, filters out known skills, and topologically sorts the required learning sequence.
4. **Phase Computation (Deterministic)**: `nx.topological_generations()` assigns each node to a numbered learning phase (Foundations → Core Concepts → Applied Learning → Advanced Topics → Specialization).
5. **Difficulty Inference (Deterministic)**: Difficulty (`beginner / intermediate / advanced`) is computed from a node's phase position relative to the total number of phases.
6. **Resource Binding (Deterministic RAG)**: The RAG service performs semantic searches to attach high-quality, verified learning materials to each node. A Google search fallback is used if ChromaDB returns nothing.
7. **UI Preparation**: NetworkX generates (X,Y) coordinates so React Flow can render the graph immediately without complex client-side layout algorithms.

## Detailed Implementation Specifications
1. **`backend/agents/roadmap_agent.py`**:
   - `RoadmapAgent` Class:
     - `__init__()`: Initializes `LLMClient`, `SkillGraphEngine`, and `RAGService`.
     - `_identify_target_skills(profile)`: Uses Gemini to map `profile.target_role` to a subset of node IDs from the `skill_taxonomy`. Filters hallucinated IDs. Returns a validated list of existing taxonomy keys.
     - `_normalize_profile_skills(profile)`: Filters `profile.skills` to only include keys that exist in the graph taxonomy, preventing silent skill-exclusion failures. Returns a new profile via `model_copy()`.
     - `_infer_difficulty(phase, total_phases)`: Returns `SkillLevel` enum based on phase ratio — bottom third = beginner, middle = intermediate, top third = advanced.
     - `generate_roadmap(profile: LearnerProfile)`:
       1. Normalizes profile skills via `_normalize_profile_skills`.
       2. Gets target skills from `_identify_target_skills`.
       3. Calls `graph.get_prerequisite_chain(target_skills, profile.current_skills)`.
       4. Calls `graph.topological_sort()` to order them.
       5. Calls `nx.topological_generations()` to assign phases (1-indexed).
       6. Calls `graph.calculate_node_coordinates()` to prep for React Flow.
       7. Loops through ordered skills. For each skill:
          - Looks up phase number and title from `PHASE_TITLES`.
          - Infers difficulty from phase position.
          - Sets status to `AVAILABLE` for Phase 1 nodes, `LOCKED` for all others.
          - Uses `rag.find_best_resources()` to get courses/docs; falls back to a Google search link.
          - Constructs `RoadmapNodeData` and `RoadmapNode`.
       8. Builds edges from in-edges within the required skill subset.
       9. Generates a unique `roadmap_id` via `uuid4()`.
       10. Builds a personalized `learner_summary` string from profile data.
       11. Returns a validated `RoadmapResponse` object.

## Fixes Applied (Audit Resolution)
| Issue | Fix |
|:---|:---|
| Static `roadmap_id="roadmap_gen_1"` | Replaced with `str(uuid.uuid4())` — unique per generation |
| Hardcoded `difficulty="beginner"` | Computed from `phase / total_phases` ratio using `_infer_difficulty()` |
| All nodes `phase=1, phase_title="Learning Phase"` | Computed from `nx.topological_generations()` with named phase titles |
| Generic `learner_summary` string | Built dynamically from `profile.target_role`, `weekly_hours`, `learning_pace`, skill counts |
| Unrecognized skill keys silently failing | `_normalize_profile_skills()` filters skills to taxonomy before graph operations |

## Verification
- Unit tests (`backend/tests/test_roadmap_agent.py`) verify the end-to-end integration: inputting a `LearnerProfile` results in a fully populated `RoadmapResponse` with nodes, edges, coordinates, RAG resources, valid phases, and correct difficulty levels.
