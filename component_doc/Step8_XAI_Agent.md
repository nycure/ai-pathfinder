# Step 8: Explainability (XAI) Agent

## Component Overview
The Explainability (XAI) Agent provides transparency for the generated learning paths. When a learner clicks on a specific milestone (e.g., "Linear Algebra") in their React Flow dashboard, this agent explains exactly *why* they need to learn it in the context of their specific career goal.

## Architectural Purpose
One of the biggest issues with AI recommendation engines is the "Black Box" effect. Learners lose motivation if they don't understand why a seemingly irrelevant prerequisite is being forced upon them. By adding an XAI layer, we:
1. **Increase Trust**: The system clearly outlines the cause-and-effect relationship between skills.
2. **Contextualize Fundamentals**: It bridges the gap between boring foundational skills (like Calculus) and exciting end goals (like building Deep Learning models).
3. **Structured Justifications**: It outputs an `ExplainabilityResponse` Pydantic model containing the justification and lists of missing prerequisites, keeping the UI data-driven.

## Detailed Implementation Specifications
1. **`backend/agents/xai_agent.py`**:
   - `XAIAgent` Class:
     - `__init__()`: Initializes the `LLMClient`.
     - `explain_node(node_id: str, profile: LearnerProfile, roadmap: RoadmapResponse) -> ExplainabilityResponse`:
       - System prompt assigns a persona: "You are an AI learning path explainer."
       - Extracts context: What is the node? What is the user's ultimate goal? What comes before and after this node in the roadmap?
       - Uses Gemini 2.5 Flash to generate a succinct, 2-3 sentence justification.
       - Returns the validated `ExplainabilityResponse`.

## Verification
- Unit tests (`backend/tests/test_xai_agent.py`) pass a mock roadmap and profile to the XAI agent and assert that the generated justification contextually mentions the user's end goal and the specific skill node.
