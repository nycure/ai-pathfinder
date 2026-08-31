# Step 24: Phase 6 - Social Cohorts & Public Portfolios

## Overview
Phase 6 introduces social accountability and shareability to AI Pathfinder. By allowing learners to share their dynamic roadmaps publicly and automatically grouping them into peer cohorts, we increase completion rates through public accountability.

## Architectural Changes

### 1. Database Migrations (`supabase_schema_v2_phase6.sql`)
- **`is_public` Flag**: Added to the `roadmaps` table (defaulting to TRUE) to control visibility.
- **Cohorts Tables**: Created `cohorts` and `cohort_members` tables to track peer groups.
- **RLS Policies**: Updated Supabase Row Level Security to allow unauthenticated read access to users and roadmaps where `is_public = true`.

### 2. Backend Enhancements (`routes.py`)
- **`GET /api/public/roadmap/{username}`**: A public endpoint that retrieves a user's active roadmap by their username without requiring a JWT token.
- **Cohort Endpoints**: Added `POST /api/cohort/match` and `GET /api/cohort/me` to handle cohort assignments and retrieve peer progress.

### 3. Public Portfolios & OpenGraph (`frontend/src/app/[username]/page.tsx`)
- Next.js Server Component that fetches the roadmap server-side.
- Uses `generateMetadata()` to inject dynamic **OpenGraph (`og:title`, `og:description`)** tags based on the user's `target_role` and `learner_summary`. This ensures that when the URL is pasted into LinkedIn or X (Twitter), a beautiful preview card is generated.
- The `RoadmapCanvas` is rendered in **Read-Only Mode** (`readOnly={true}`), disabling drag-and-drop and interaction drawers.

### 4. Cohort Dashboard Widget (`LearnerDashboard.tsx`)
- Added a "Your Study Cohort" card.
- Displays a leaderboard of peers (mocked for now until full matchmaking is built), showing usernames and completion percentages side-by-side with the current user.

## Status
- **Implementation**: 🟢 Completed
- **Next Steps**: Phase 7 (Production Infrastructure & Redis Caching).
