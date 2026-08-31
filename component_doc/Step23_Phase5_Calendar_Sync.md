# Step 23: Phase 5 - Smart Calendar Sync & Recalibration

## Overview
Phase 5 bridges the gap between learning intentions and actual study habits by integrating with personal calendars (Google Calendar, Outlook) and offering a non-guilt recalibration engine.

## Architectural Changes

### 1. Smart Calendar Sync
- **Backend (`calendar_service.py`)**: Takes the user's generated `RoadmapResponse` and `LearnerProfile` to compute estimated study blocks. It calculates the necessary weeks per milestone based on `weekly_hours` and distributes them as blocks. It outputs a standard `.ics` (iCalendar) format string.
- **Frontend Integration (`api.ts` & `LearnerDashboard.tsx`)**: An "Add to Calendar" button in the dashboard triggers a Blob download of the `.ics` file directly into the browser, allowing the user to import it into their preferred calendar app.

### 2. Spaced Repetition Recalibration Engine
- **Backend (`recalibration_agent.py`)**: Implements a non-punitive recalibration function. If the user feels they have fallen behind, they can click "Recalibrate". 
- **Graph Modification**: The agent analyzes the `RoadmapResponse` and dynamically injects a "Warmup / Refresher" node just before the user's currently active (IN_PROGRESS or AVAILABLE) node. This combats the Ebbinghaus forgetting curve by ensuring they review prerequisite concepts before jumping back into complex topics.
- **Frontend**: A "Recalibrate" button in the dashboard seamlessly calls the API and updates the local React Flow state.

## Status
- **Implementation**: 🟢 Completed
- **Dependencies**: No external Python dependencies required (standard library `datetime`, `uuid`).
- **Next Steps**: Phase 6 (Social Cohorts & Public Portfolios).
