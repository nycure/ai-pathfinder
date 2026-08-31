# Step 12: API Client & Zustand State Store

## Component Overview
This component acts as the circulatory system for the frontend. It consists of TypeScript definitions mirroring our Python backend, a `fetch` wrapper API client, and a global Zustand state store.

## Architectural Purpose
Instead of passing props down a deep React component tree, we need global state.
1. **Type Safety**: By strictly defining interfaces (`LearnerProfile`, `RoadmapResponse`), we ensure the React Flow canvas doesn't crash from undefined properties.
2. **Centralized Data Fetching**: The `api.ts` file encapsulates the backend URL (`http://localhost:8000`) and handles HTTP errors centrally.
3. **Zustand Store**: The `useRoadmapStore` holds the single source of truth for the active roadmap. It handles loading states automatically while exposing actions (`generateRoadmap`, `adaptRoadmap`) that components can trigger.

## Detailed Implementation Specifications
1. **`frontend/src/lib/types.ts`**:
   - Mirrors all Pydantic schemas: `LearnerProfile`, `RoadmapNode`, `RoadmapEdge`, `RoadmapResponse`, `ExplainabilityResponse`.
2. **`frontend/src/lib/api.ts`**:
   - `BASE_URL = 'http://localhost:8000/api'`
   - `generateRoadmap(userInput: string)`
   - `explainNode(nodeId, profile, roadmap)`
   - `adaptRoadmap(roadmapId, completedNodeId, feedback, currentProfile, currentRoadmap)`
3. **`frontend/src/store/useRoadmapStore.ts`**:
   - State: `profile`, `roadmap`, `isLoading`, `error`, `activeNode`.
   - Actions: 
     - `submitGoal(userInput)`: Calls API and sets profile/roadmap.
     - `completeNode(nodeId)`: Calls API to adapt the path, updates the store with the new roadmap.
     - `submitFeedback(feedback)`: Similar to `completeNode` but with text feedback.
     - `setActiveNode(nodeId)`: Used for opening the XAI side drawer.

## Verification
- Can be verified via browser console once mounted, testing that calling `useRoadmapStore.getState().submitGoal("...")` correctly toggles `isLoading` and updates `roadmap`.
