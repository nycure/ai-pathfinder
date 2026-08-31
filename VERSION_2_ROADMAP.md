# AI Pathfinder v2.0 — Production Enhancement Roadmap & Architecture Specification

## 🌟 Executive Vision
AI Pathfinder v1.0 successfully established a verified AI-driven pipeline: conversational profiling $\rightarrow$ deterministic NetworkX Directed Acyclic Graph (DAG) $\rightarrow$ ChromaDB semantic resource binding $\rightarrow$ interactive React Flow UI with Explainable AI (XAI) and adaptive replanning.

**AI Pathfinder v2.0** transforms this prototype into an enterprise-ready, scalable, and personalized lifelong learning platform used by individual students, self-taught professionals, bootcamp cohorts, and enterprise engineering teams.

---

## 🗺️ Enhancement Phases Overview

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               AI PATHFINDER v2.0 PHASES                                │
├────────────────────────────┬────────────────────────────┬──────────────────────────────┤
│ Phase 1: Auth & Database   │ Phase 2: Open-World Graph  │ Phase 3: In-Drawer AI Tutor  │
│ Multi-device Sync & State  │ Infinite Dynamic Taxonomies│ Contextual Q&A & RAG Chat    │
├────────────────────────────┼────────────────────────────┼──────────────────────────────┤
│ Phase 4: Active Validation │ Phase 5: Smart Scheduling  │ Phase 6: Social & Portfolios │
│ Quizzes & GitHub Verifier  │ Calendar Sync & Decay Rem. │ Public URLs & Peer Cohorts   │
├────────────────────────────┴────────────────────────────┴──────────────────────────────┤
│ Phase 7: Production Infrastructure, Redis Caching & Live Course Partner APIs           │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

# 📌 Phase 1: User Authentication & Cloud State Persistence

### 1. Objective
Enable persistent accounts so learners can track multi-month journeys, pause and resume progress, switch between desktop and mobile, and maintain a historical ledger of learning adaptations.

### 2. Architecture & Data Model (PostgreSQL / Supabase)
```sql
-- Core Users Table (managed via Supabase Auth / Clerk)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Persistent Learner Profile
CREATE TABLE learner_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    target_role TEXT NOT NULL,
    weekly_hours INT NOT NULL DEFAULT 10,
    learning_pace TEXT NOT NULL DEFAULT 'medium',
    skills JSONB NOT NULL DEFAULT '{}'::jsonb, -- e.g. {"python_basics": "beginner"}
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Stored Roadmaps (Active & Historical Iterations)
CREATE TABLE roadmaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    target_role TEXT NOT NULL,
    total_estimated_weeks INT NOT NULL,
    total_hours INT NOT NULL,
    learner_summary TEXT NOT NULL,
    skill_gap_summary JSONB NOT NULL,
    graph_payload JSONB NOT NULL, -- Full React Flow nodes & edges
    is_active BOOLEAN DEFAULT TRUE,
    version INT DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Milestone Completion & Engagement Ledger
CREATE TABLE milestone_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    roadmap_id UUID REFERENCES roadmaps(id) ON DELETE CASCADE,
    node_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('locked', 'available', 'in_progress', 'completed')),
    completed_at TIMESTAMP WITH TIME ZONE,
    quiz_score NUMERIC,
    notes TEXT
);
```

### 3. Step-by-Step Flow
1. **User Sign-In:** Learner authenticates via Google/GitHub OAuth through `@clerk/nextjs` or `@supabase/ssr`.
2. **Initial Load:** Frontend fetches the active roadmap (`GET /api/user/active-roadmap`). If none exists, displays the conversational intake.
3. **Save State on Event:** Every node completion or roadmap adaptation automatically persists transactionally to PostgreSQL with version incrementing.

---

# 📌 Phase 2: Open-World & Infinite Dynamic Skill Graph Synthesis

### 1. Objective
Break free from the static 15-node taxonomy. Support any technical or professional domain (Cybersecurity, Cloud Architecture, Mobile Development, Quantum Computing, Product Design, Bio-informatics).

### 2. System Flow & DAG Validation Algorithm
```
User Goal ("Become a Cloud Security Architect specializing in AWS and Kubernetes")
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│              Dynamic Taxonomy Generator (LLM)            │
│  - Generates 10-25 tailored skills & prerequisite tuples │
│  - Returns strictly typed JSON: { nodes: [], edges: [] } │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│              DAG Acyclicity & Validity Guard             │
│  - Loads dynamic graph into NetworkX DiGraph             │
│  - Runs nx.is_directed_acyclic_graph()                   │
│  - If cycles detected: Auto-resolves by edge-reversal    │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│       Topological Ordering & Generation Layout           │
│  - Multi-tier layer assignment (Phase 1, 2, 3...)        │
│  - Computes X, Y coordinates for React Flow              │
└──────────────────────────────────────────────────────────┘
```

### 3. Hierarchical Sub-Milestones
Nodes expand into sub-checklists:
* **Node:** *AWS Identity and Access Management (IAM)*
  * [ ] Sub-topic 1: Least Privilege Policies & RBAC
  * [ ] Sub-topic 2: Multi-Factor Authentication & IAM Roles
  * [ ] Sub-topic 3: Cross-Account Role Assumption & Security Token Service (STS)

---

# 📌 Phase 3: In-Drawer Contextual AI Study Tutor

### 1. Objective
Provide real-time, 24/7 personalized explanations, analogies, and debugging assistance directly inside the `NodeInspectorDrawer` for the active milestone.

### 2. Architectural Flow
```
Learner inside Node Drawer ("Explain Backpropagation with a real-life cooking analogy")
                     │
                     ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                           Context Enrichment Engine                           │
│  - Active Node: "Deep Learning Fundamentals"                                  │
│  - User Profile: Beginner in Math, 10 hrs/week                                │
│  - Active Resource: Coursera Deep Learning Specialization                     │
│  - Retrieved Context: Course Transcript / Documentation Chunk via Vector RAG  │
└──────────────────────────────────────┬────────────────────────────────────────┘
                                       │
                                       ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                       Gemini 3.6 Streaming Agent (SSE)                        │
│  - System Prompt: Socratic, empathetic, practical technical tutor             │
│  - Delivers real-time Server-Sent Events (SSE) stream back to UI              │
└───────────────────────────────────────────────────────────────────────────────┘
```

### 3. Implementation Details
* **Backend Endpoint:** `POST /api/tutor/chat-stream` using FastAPI `StreamingResponse`.
* **Frontend Component:** `MilestoneChatTutor.tsx` embedded into the tabs of `NodeInspectorDrawer.tsx`.

---

# 📌 Phase 4: Active Validation, Micro-Quizzes & GitHub Verification

### 1. Objective
Ensure learners genuinely understand the content before marking milestones as *Mastered*, preventing superficial completion.

### 2. Micro-Quiz Engine
* When clicking *"Mark as Mastered"*, a lightweight 3-question adaptive quiz modal opens.
* **Question Generation:** Gemini generates questions dynamically based on the skill topic and difficulty.
* **Evaluation:** Instant feedback with explanations for incorrect options. Passing threshold: $\ge 66\%$.

### 3. Automated GitHub Capstone Project Verifier
* **Flow:**
  1. Learner pastes their public GitHub repository URL into the project milestone.
  2. Backend fetches repository tree and key code files via GitHub REST API.
  3. LLM analyzes code structure, test coverage, and documentation against the milestone requirements.
  4. Returns structured feedback: *Strengths, Weaknesses, and Verification Status (Approved / Needs Revision)*.

---

# 📌 Phase 5: Smart Calendar Sync & Spaced Repetition Recalibration

### 1. Objective
Bridge the gap between good intentions and actual study habits by integrating with personal calendars and actively combating the Ebbinghaus forgetting curve.

### 2. Calendar Sync Integration
* **Protocol:** Generate standard `.ics` subscription URLs and direct OAuth integration with Google Calendar and Microsoft Outlook.
* **Algorithm:**
  $$\text{Daily Study Slot} = \frac{\text{Weekly Hours Allocated}}{\text{Available Free Days}}$$
  * Distributes 45–90 minute focused study blocks during learner's self-selected peak focus hours.

### 3. Non-Guilt Recalibration Engine
* If a learner misses 14 consecutive days of activity:
  * **No Penalty:** The system recalculates milestone deadlines and shifts subsequent phases forward.
  * **Warmup Milestone:** Inserts a 15-minute refresher checkpoint on the last completed skill before resuming new content.

---

# 📌 Phase 6: Social Cohorts, Public Portfolios & Verified Credentials

### 1. Public Shareable Portfolios
* Public URL: `https://aipathfinder.dev/p/@username/cloud-security`
* **Features:**
  * Interactive read-only React Flow roadmap.
  * OpenGraph Dynamic Card generation for social sharing on LinkedIn and X.
  * Verified badges and project links displayed as proof of competency for recruiters.

### 2. Peer Learning Cohorts
* Group learners with similar goals and timelines into automated study tracks of 5–10 peers.
* Shared cohort leaderboard, milestone celebration feeds, and weekly progress check-ins.

---

# 📌 Phase 7: Production Infrastructure & Real-Time Course Partner APIs

### 1. Infrastructure Architecture
```
                         ┌────────────────────────┐
                         │   Cloudflare CDN/DNS   │
                         └───────────┬────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
         ┌─────────────────────┐           ┌─────────────────────┐
         │  Next.js (Vercel)   │           │ FastAPI (AWS / GCP) │
         │  Frontend & UI      │           │ Scalable Container  │
         └─────────────────────┘           └──────────┬──────────┘
                                                      │
                       ┌──────────────────────────────┼──────────────────────────────┐
                       ▼                              ▼                              ▼
            ┌─────────────────────┐        ┌─────────────────────┐        ┌─────────────────────┐
            │   PostgreSQL (DB)   │        │     Redis Cache     │        │  Qdrant Vector DB   │
            │ User state & graphs │        │  LLM prompts & DAGs │        │ Semantic search RAG │
            └─────────────────────┘        └─────────────────────┘        └─────────────────────┘
```

### 2. Real-Time Resource Aggregators
* Replace static `curated_resources.json` with live integrations:
  * **YouTube Data API v3:** Fetches top-rated, recent tutorials with view counts and durations.
  * **GitHub Search API:** Identifies trending open-source repositories and hands-on starter projects.
  * **ArXiv API:** Connects cutting-edge research papers for advanced milestone nodes.

---

## 📅 Recommended Implementation Roadmap

| Milestone | Deliverables | Target Timeline |
| :--- | :--- | :--- |
| **Sprint 1 (Weeks 1–2)** | Supabase PostgreSQL setup + Clerk Auth + multi-device state saving | Month 1 |
| **Sprint 2 (Weeks 3–4)** | Dynamic Open-Domain Skill Graph synthesis with DAG validation | Month 1 |
| **Sprint 3 (Weeks 5–6)** | In-drawer Gemini SSE Streaming AI Study Tutor | Month 2 |
| **Sprint 4 (Weeks 7–8)** | AI Micro-quizzes + GitHub Capstone Project verification | Month 2 |
| **Sprint 5 (Weeks 9–10)** | Google Calendar `.ics` sync + automated timeline recalibration | Month 3 |
| **Sprint 6 (Weeks 11–12)** | Public portfolio URLs + OpenGraph social cards + Redis caching layer | Month 3 |
