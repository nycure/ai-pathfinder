# Step 15: Conversational Goal Intake

## Component Overview
The `GoalChat.tsx` component is the primary entry point for the user. It allows the learner to express their career aspirations, current skill level, and time availability in natural language.

## Architectural Purpose
1. **Frictionless Onboarding**: Traditional forms with endless dropdowns (e.g., "Select your skill level from 1-10 in 50 different technologies") are tedious. By using a single conversational input, we rely on the `ProfilerAgent` on the backend to parse the intent using NLP.
2. **Template Suggestions**: To prevent the blank canvas problem, the UI provides quick-start suggestion chips.
3. **State Linkage**: Submitting the form calls `useRoadmapStore.getState().submitGoal()`, automatically toggling the global loading state and eventually populating the `RoadmapCanvas`.

## Detailed Implementation Specifications
1. **`frontend/src/components/chat/GoalChat.tsx`**:
   - A sticky bottom or centralized card UI.
   - Text input for the user's goal.
   - A set of pre-defined suggestion pills (e.g., "I know basic Python, want to learn AI Engineering for 10 hours a week").
   - A primary "Generate" button wrapped in our glassmorphism styling (`bg-primary/20 border-primary text-primary-foreground`).
   - Displays a loading spinner overlay across the screen when `useRoadmapStore.isLoading` is true.

## Verification
- Can be tested visually by mounting the component on `page.tsx` and ensuring state interactions fire correctly.
