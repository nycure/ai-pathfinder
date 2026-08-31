# Step 9: Dynamic Path Adaptation Agent

## Component Overview
The Path Adaptation Agent allows the learning roadmap to be a living, breathing entity rather than a static document. It takes user feedback (e.g., "This topic is too hard") or state changes (e.g., node completed) and dynamically adjusts the downstream path.

## Architectural Purpose
Learning is non-linear. A static path fails if the learner gets stuck or their goals evolve. 
1. **Feedback Loop**: By allowing free-text feedback, we can use the LLM to extract intent (e.g., pivot from "Deep Learning" to "Frontend Web Dev").
2. **State Management**: It updates the `LearnerProfile` (e.g., adding newly acquired skills) and delegates the heavy lifting of path regeneration back to the `RoadmapAgent`.
3. **Immutability**: It uses `model_copy()` to produce a new updated profile rather than mutating the original, preventing Pydantic v2 validation side effects. The returned roadmap always has a new unique ID.

## Detailed Implementation Specifications
1. **`backend/agents/adaptation_agent.py`**:
   - `AdaptationAgent` Class:
     - `__init__()`: Initializes `LLMClient` and `RoadmapAgent`.
     - `adapt_path(request: AdaptationRequest, current_profile: LearnerProfile, current_roadmap: RoadmapResponse) -> AdaptationResponse`:
       - Collects all mutations into local variables (`updated_skills`, `updated_target_role`) rather than directly mutating the Pydantic model.
       - If a node was completed, adds the `skills_acquired` from that node to `updated_skills` using `SkillLevel.BEGINNER` (enum value, not raw string).
       - If the user provided feedback, uses Gemini to parse how the feedback should alter the `target_role`.
       - Uses `profile.model_copy(update={...})` to safely construct the updated profile — compatible with Pydantic v2's mutation model.
       - Calls `RoadmapAgent.generate_roadmap()` with the updated profile to get the newly calculated subgraph.
       - Returns the `AdaptationResponse` containing the new roadmap and a string summary of the changes made.

## Fixes Applied (Audit Resolution)
| Issue | Fix |
|:---|:---|
| `current_profile.skills[skill] = "beginner"` — raw string, unsafe mutation | Changed to `SkillLevel.BEGINNER` enum; mutations collected in a local dict |
| Direct attribute mutation on Pydantic v2 model | Replaced with `profile.model_copy(update={...})` for safe immutable-style updates |
| Both `skills` and `target_role` changes scattered | Consolidated into a single `model_copy()` call with all updates at once |

## Verification
- Unit tests (`backend/tests/test_adaptation_agent.py`) pass an `AdaptationRequest` marking a node as completed, and verify that:
  1. The returned roadmap excludes that completed node.
  2. The `LearnerProfile` in the regenerated roadmap correctly contains the newly acquired skills.
  3. No `ValidationError` is raised during profile mutation.
