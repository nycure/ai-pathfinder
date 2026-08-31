# Step 16: Learner Analytics & Radar Chart

## Component Overview
The `LearnerDashboard.tsx` component provides a high-level summary of the learner's journey. It tracks milestone completion progress and visualizes the learner's skill distribution using a Recharts Radar Chart.

## Architectural Purpose
1. **Gamification and Motivation**: A visual progress bar and time estimates help keep the learner motivated by showing exactly how much they've completed vs. how much remains.
2. **Skill Gap Visualization**: The backend `ProfilerAgent` extracts a `skill_gap_summary` (an array of strings indicating missing skills). We parse this array to populate a Radar chart. This visual feedback loop proves to the learner *why* the curriculum contains certain topics—it fills in the "dents" in their radar chart.

## Detailed Implementation Specifications
1. **`frontend/src/components/dashboard/LearnerDashboard.tsx`**:
   - Subscribes to `roadmap` from `useRoadmapStore`.
   - Uses `recharts` (`Radar`, `RadarChart`, `PolarGrid`, `PolarAngleAxis`, `PolarRadiusAxis`) to render the skill distribution.
   - We map the `roadmap.skill_gap_summary` (which is an array of strings like `["Missing deep learning fundamentals", "Needs MLOps practice"]`) into a generalized set of core skills for the radar chart, giving lower scores to missing skills and higher scores to existing ones (derived from `profile.skills`).
   - Uses shadcn `Progress` to show the percentage of completed nodes out of total nodes.
   - Displays textual summaries (e.g., total hours, total weeks).

## Verification
- Can be tested visually by mounting the component on `page.tsx` alongside the Canvas and verifying that the Recharts graph renders without throwing DOM errors.
