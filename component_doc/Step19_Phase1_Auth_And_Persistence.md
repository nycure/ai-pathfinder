# Step 19: Phase 1 — User Authentication & Database Persistence

## Objective
Implement Phase 1 of AI Pathfinder v2.0. Transition the application from an ephemeral, stateless memory model into a persistent, multi-device capable platform. This step introduces user accounts, authentication, and a relational database (PostgreSQL) to store learner profiles, generated roadmaps, and milestone progress.

## Architecture

### 1. Technology Stack
*   **Authentication**: Supabase Auth (or Clerk) integrated with Next.js App Router for frontend session management.
*   **Database**: PostgreSQL (hosted on Supabase or locally).
*   **Backend ORM**: SQLAlchemy (Async) or direct Supabase Python Client to interface with the database from FastAPI.

### 2. Data Models (Schema)
*   **Users**: Manages core identities (Email, OAuth providers).
*   **Learner Profiles**: Stores the user's `target_role`, `weekly_hours`, `learning_pace`, and a JSONB mapping of their `skills`. One-to-one relationship with Users.
*   **Roadmaps**: Stores generated roadmap configurations (`graph_payload`, `total_hours`, `skill_gap_summary`). One-to-many relationship with Users.
*   **Milestone Progress**: Tracks individual node status (`locked`, `available`, `completed`) for a specific roadmap.

### 3. Component Flow
1.  **Auth Guarding**: The Next.js frontend wraps protected routes with authentication guards. Unauthenticated users are redirected to a login page.
2.  **API Authorization**: FastAPI endpoints enforce authentication via JWT verification (Bearer tokens passed from the frontend).
3.  **State Hydration**: When a user logs in, `useRoadmapStore` fetches their active profile and roadmap from the database instead of requiring a new goal input.
4.  **Transactional Updates**: When an adaptation occurs (e.g., node completed), the backend updates the PostgreSQL records first, then returns the fresh state to the frontend.

## Implementation Details

### Frontend (`frontend/src`)
*   Integrate Auth provider SDK (e.g., `@supabase/ssr` or `@clerk/nextjs`).
*   Update `api.ts` to attach the Authorization header (JWT) to all FastAPI requests.
*   Update `useRoadmapStore.ts` with a new `fetchInitialState` action that runs on component mount to load existing data.

### Backend (`backend/`)
*   Add database dependencies: `supabase`, `psycopg2-binary`, `sqlalchemy` (if using ORM).
*   Create a new module `backend/database/` with connection logic and schema definitions.
*   Update `backend/api/routes.py` to inject database sessions and verify user tokens.
*   Modify `RoadmapAgent` and `AdaptationAgent` to read/write from the database instead of relying solely on the request payload.

## Success Criteria
*   Users can sign up and log in.
*   Generated roadmaps are saved to the database and tied to the user's account.
*   Progress (marking a node as mastered) persists across page reloads.
*   The application gracefully handles the absence of an active roadmap by prompting the user for a new goal.
