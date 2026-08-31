# Step 17: Dynamic Adaptation Loop

## Component Overview
The `AdaptationControls.tsx` component is the bridge between user progress and the backend AI `AdaptationAgent`. It allows users to flag milestones as completed or request a curriculum adjustment if they are struggling.

## Architectural Purpose
1. **Closing the Feedback Loop**: A static curriculum is just a syllabus. A truly personalized path adapts. By providing UI controls, we allow the learner to alter the graph dynamically.
2. **Mastery Progression**: Marking a node as "Mastered" calls `completeNode(nodeId)`. This pings the FastAPI backend, which recalculates downstream edges and unlocks new nodes.
3. **Adaptive Re-routing**: Clicking "Need More Practice" allows the user to submit text feedback. The backend `AdaptationAgent` uses Gemini to generate a bridging prerequisite node to fill the knowledge gap on the fly.

## Detailed Implementation Specifications
1. **`frontend/src/components/roadmap/AdaptationControls.tsx`**:
   - Takes `nodeId` as a prop.
   - Contains a "Mark as Mastered" button connected to `useRoadmapStore.getState().completeNode(nodeId)`.
   - Contains a "Request Adaptation" section that toggles a text input for specific feedback.
   - Submitting feedback calls `submitFeedback()`.
2. **Integration into `NodeInspectorDrawer.tsx`**:
   - Rendered at the bottom of the drawer.
   - Only shown if the node is actively available or in progress (not already completed, or maybe yes, but disabled).

## Verification
- Can be tested visually by mounting the component inside the `NodeInspectorDrawer` and ensuring the state loading UI triggers appropriately.
