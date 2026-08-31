# Step 2: Pydantic Data Contracts

## Component Overview
This component defines the strict data schemas used across the entire AI Pathfinder system. Built using **Pydantic v2**, these data models act as the absolute source of truth for how data moves between the Next.js frontend, the FastAPI backend endpoints, the NetworkX graph engine, and the Google Gemini 2.5 Flash LLM.

## Architectural Purpose
By relying on Pydantic v2:
- **LLM Determinism**: Gemini 2.5 Flash's structured JSON output mode integrates natively with Pydantic schemas. This guarantees the LLM returns exactly the keys and types we expect, preventing parsing errors.
- **API Validation**: FastAPI uses these same models to automatically validate incoming JSON payloads and generate Swagger/OpenAPI documentation.
- **Frontend Contract**: These backend schemas inform the TypeScript interfaces that will be created on the frontend, ensuring end-to-end type safety.

## Detailed Implementation Specifications
The file `backend/models/schemas.py` includes the following core schemas:

1. **`LearnerProfile`**
   - Captures normalized inputs: `target_role`, current `skills`, `weekly_hours`, and `learning_pace`.
2. **`LearningResource`**
   - Describes a curated resource from ChromaDB: `title`, `provider`, `url`, `type` (course, video, project), `estimated_hours`, and `difficulty`.
3. **`RoadmapNodeData` & `RoadmapNode`**
   - Defines a single milestone node. It contains the primary resource, hands-on `practical_project`, `why_recommended` (for XAI), and node styling configurations compatible with React Flow (`position`, `status`).
4. **`RoadmapEdge`**
   - Defines directed dependencies (e.g., Node A $\rightarrow$ Node B).
5. **`RoadmapResponse`**
   - The aggregated payload returned to the frontend containing `nodes` and `edges`.
6. **`AdaptationRequest` & `AdaptationResponse`**
   - Contracts for the dynamic path re-routing logic.

## Verification
- Running a test script via `pytest` verifies that all Pydantic schemas correctly instantiate, validate missing or incorrect fields, and successfully dump to valid JSON strings.
