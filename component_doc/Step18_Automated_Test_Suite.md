# Step 18: Automated Test Suite

## Component Overview
The automated test suite uses Playwright for End-to-End (E2E) testing of the frontend application. It verifies that the critical user journeys—such as goal intake, API integration, and rendering the DAG—function as expected in a real browser environment.

## Architectural Purpose
1. **Confidence in Delivery**: The AI Pathfinder relies heavily on asynchronous state (FastAPI -> Zustand -> React Flow). E2E tests are the only way to ensure the whole chain works perfectly from the user's perspective.
2. **Mocked Resiliency**: By mocking the FastAPI backend in our tests, we can verify the frontend's loading states and error handling without needing to spin up the actual Python backend or expend Gemini API tokens during CI/CD runs.

## Detailed Implementation Specifications
1. **Setup**: Installed `@playwright/test`.
2. **`frontend/playwright.config.ts`**:
   - Configured to run against `http://localhost:3000`.
   - Setup for Chromium, Firefox, and WebKit (standard).
3. **`frontend/e2e/pathfinder.spec.ts`**:
   - **Test 1: Initial Render**: Verifies the `GoalChat` component renders correctly and accepts text input.
   - **Test 2: Loading State Simulation**: Intercepts the `/api/generate-roadmap` route using `page.route()`, artificially delays the response, and verifies the "Synthesizing your personalized roadmap..." loading spinner appears.
   - **Test 3: Canvas Render**: Mocks a successful JSON response and verifies the `<ReactFlow>` canvas successfully mounts and displays the roadmap title.

## Verification
- Can be tested by running `npx playwright test` inside the `frontend/` directory (requires `npm run dev` to be running first).
