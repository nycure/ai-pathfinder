# Step 21: Phase 3 - In-Drawer Contextual AI Study Tutor

## Overview
Phase 3 introduces an intelligent, context-aware AI tutor directly embedded into the milestone inspector drawer. It enables learners to ask highly specific questions, request analogies, and get tailored debugging assistance without ever leaving the context of their learning roadmap.

## Architectural Changes

### 1. Server-Sent Events (SSE) Backend Endpoint (`backend/api/routes.py`)
- Added `POST /api/tutor/chat`, a dedicated streaming endpoint returning a `StreamingResponse`.
- Leverages the `google-genai` Python SDK's `generate_content_stream` method to yield LLM chunks instantly to the client, drastically improving perceived latency.
- Validates requests using the robust `supabase.auth.get_user()` verification flow to ensure multi-tenant security.

### 2. Contextual AI Agent (`backend/agents/tutor_agent.py`)
- Created `TutorAgent` which constructs a rich system instruction block by combining:
  1. The user's `LearnerProfile` (Target Role, Time Commitment).
  2. The specific `DynamicNode` they are studying (Milestone Title, Phase, Description).
- Instructs the Gemini 2.5 Flash model to act as a Socratic, empathetic mentor that ties explanations directly back to the learner's long-term career goals.

### 3. Frontend Chat Component (`frontend/src/components/roadmap/MilestoneChatTutor.tsx`)
- Built a bespoke streaming UI utilizing `fetch` and `ReadableStream` to parse the chunked text directly from the FastAPI endpoint.
- Avoided the overhead of a WebSocket or third-party AI UI library, maintaining a lightweight Vercel-friendly architecture.
- Included real-time auto-scrolling to ensure the latest tokens are always visible.

### 4. Tabbed Node Inspector (`frontend/src/components/roadmap/NodeInspectorDrawer.tsx`)
- Refactored the `NodeInspectorDrawer` to use Shadcn UI `Tabs`.
- The user can toggle between the static **Overview** (XAI rationale, resources, micro-quizzes) and the interactive **AI Tutor**.

## Status
- **Implementation**: 🟢 Completed
- **Dependencies**: `google-genai`, FastAPI `StreamingResponse`, Next.js `ReadableStream`
- **Next Steps**: Phase 4 (Active Validation & Micro-quizzes) to enforce mastery before progressing to the next node.
