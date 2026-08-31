# Step 10: FastAPI Routes & Server Scaffold

## Component Overview
The FastAPI app serves as the API Gateway, exposing our backend agent logic over standard REST endpoints. This is what the Next.js frontend will communicate with.

## Architectural Purpose
By placing a FastAPI layer on top of our Python agents, we achieve:
1. **Frontend-Backend Decoupling**: The Next.js client does not need to know about NetworkX, ChromaDB, or the Gemini SDK. It simply sends JSON and receives React Flow compatible JSON.
2. **Asynchronous Handling**: Generating the roadmap involves multiple LLM calls and vector searches. FastAPI's async nature handles this efficiently.
3. **CORS Configuration**: Securely allows requests originating from the `localhost:3000` Next.js development server.

## Detailed Implementation Specifications
1. **`backend/api/routes.py`**:
   - `GenerateRoadmapRequest`: Pydantic model for incoming `POST /api/generate-roadmap` (takes `user_input` string).
   - `ExplainNodeRequest`: Takes `node_id`, `profile`, and `roadmap`.
   - `POST /api/generate-roadmap`: 
     - Instantiates `ProfilerAgent` to get `LearnerProfile`.
     - Instantiates `RoadmapAgent` to get `RoadmapResponse`.
     - Returns `{ profile: ..., roadmap: ... }`.
   - `POST /api/explain-node`:
     - Instantiates `XAIAgent` and returns `ExplainabilityResponse`.
   - `POST /api/adapt-roadmap`:
     - Instantiates `AdaptationAgent` and returns `AdaptationResponse`.
2. **`backend/main.py`**:
   - Initializes `FastAPI()`.
   - Adds `CORSMiddleware` configured for `http://localhost:3000`.
   - Includes the router from `routes.py`.

## Verification
- Unit tests (`backend/tests/test_api.py`) use FastAPI's `TestClient` to send mock JSON payloads to the endpoints and verify standard `200 OK` responses and structural integrity.
