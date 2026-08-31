# Step 14: Node Inspector & XAI Drawer

## Component Overview
The `NodeInspectorDrawer.tsx` is a slide-over panel that acts as the detailed view for a single milestone on the roadmap. It houses the curated learning resources and the AI's explanation (XAI) for why this node was recommended.

## Architectural Purpose
1. **Declutter the Canvas**: We cannot fit all resource links, video tutorials, and AI explanations on the small `MilestoneNode` cards on the React Flow canvas. The drawer pattern provides maximum space without navigating away from the roadmap context.
2. **Explainable AI (XAI)**: A core tenet of this project is transparency. When a user clicks a node, they don't just see *what* to learn, they see *why* it was chosen for them specifically (e.g., "Recommended because your goal is AI Engineering and you already know basic Python").
3. **Action Hub**: From this drawer, users can adapt the path (e.g., click "Mark as Completed", which we will build in Step 17).

## Detailed Implementation Specifications
1. **`frontend/src/components/roadmap/NodeInspectorDrawer.tsx`**:
   - Subscribes to `activeNodeId` from `useRoadmapStore`.
   - Uses shadcn `Sheet` component for a right-side slide-over panel.
   - Fetches the active node data from `roadmap.nodes.find(n => n.id === activeNodeId)`.
   - Displays the **Primary Resource** using a Card with an external link icon.
   - Displays **Alternative Resources** in a scrollable list.
   - Displays the **"Why Recommended"** rationale from the AI.
   - Calls the `api.explainNode` lazily if deep XAI justification is needed, or just displays the pre-calculated `why_recommended` text.

## Verification
- Can be tested visually by mounting the component on `page.tsx` alongside the Canvas and clicking a node.
