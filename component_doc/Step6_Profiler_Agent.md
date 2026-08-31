# Step 6: Profiler Agent (Gemini 2.5 Flash)

## Component Overview
The Profiler Agent acts as the entry point for the user's conversational goal. It takes natural language input like "I want to become a machine learning engineer, I know some Python and have about 10 hours a week" and translates it into a structured `LearnerProfile` object.

## Architectural Purpose
Natural language is messy and ambiguous. By dedicating an agent specifically to profile extraction, we:
1. **Normalize Data**: We convert vague statements ("I coded a few scripts") into structured, quantifiable enum values (`python_basics: beginner`).
2. **Decouple the Input from the Graph Engine**: The NetworkX Graph Engine expects strict Python dictionaries and Pydantic models, not unstructured text. The Profiler acts as the translation layer.
3. **Set the Target Goal**: Extracting the exact `target_role` helps the downstream RAG service and Roadmap Synthesizer contextualize the curriculum.
4. **Constrain Skill Mapping**: By injecting the full taxonomy skill ID list into the prompt, Gemini is forced to map user skills to exact valid IDs (e.g., `python_basics`, not `python`), preventing silent failures in the graph engine's prerequisite exclusion logic.

## Detailed Implementation Specifications
1. **`backend/agents/profiler_agent.py`**:
   - Contains the `ProfilerAgent` class.
   - `__init__()`: Initializes the `LLMClient` (from Step 5) and the `SkillGraphEngine` (from Step 3) to load the live taxonomy node keys.
   - `extract_profile(user_input: str) -> LearnerProfile`:
     - Reads all valid taxonomy skill IDs from `SkillGraphEngine.graph.nodes.keys()`.
     - Constructs a prompt that includes the full list of valid skill IDs so Gemini can only choose from them.
     - System prompt constrains Gemini: "Map their described skills ONLY to the exact skill IDs from the taxonomy provided in the prompt. Do not invent new skill IDs."
     - Calls `llm_client.generate_structured_output` using the `LearnerProfile` Pydantic schema.
     - Parses the returned JSON string into a validated `LearnerProfile` object and returns it.

## Fixes Applied (Audit Resolution)
| Issue | Fix |
|:---|:---|
| Gemini could invent skill keys (e.g., `python` instead of `python_basics`) | Full taxonomy key list is now embedded in the prompt at runtime |
| System instruction gave only example keys, not the full valid set | System instruction now explicitly prohibits inventing IDs not in the list |
| No validation that extracted skills match taxonomy | Downstream `_normalize_profile_skills()` in `RoadmapAgent` provides a second filter as a safety net |

## Verification
- Unit tests (`backend/tests/test_profiler_agent.py`) pass a sample natural language query to the agent and assert that it correctly instantiates a `LearnerProfile` with:
  - The expected target role.
  - Skill keys that all exist in the skill taxonomy.
  - Valid `weekly_hours` and `learning_pace` values.
