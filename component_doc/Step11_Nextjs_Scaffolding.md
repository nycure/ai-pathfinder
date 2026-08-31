# Step 11: Next.js 15 & shadcn/ui Scaffolding

## Component Overview
This component represents the foundational setup for the Frontend UI. We are using Next.js 15 (App Router) as our React framework, Tailwind CSS for styling, and `shadcn/ui` for accessible, unstyled components that we can easily customize.

## Architectural Purpose
The frontend needs to be highly interactive to render complex DAGs (React Flow) and handle AI streamed responses.
1. **Next.js App Router**: Provides a modern React architecture with server-side rendering (SSR) capabilities, though we will heavily rely on client components for the interactive dashboard.
2. **Tailwind CSS**: Utility-first CSS allows for rapid prototyping of our sleek, dark-mode prioritized "glassmorphism" aesthetic.
3. **shadcn/ui**: Instead of a bloated component library, `shadcn` gives us the raw source code for components like Modals, Drawers, and Buttons, allowing us to perfectly theme them to our AI Pathfinder brand.
4. **React Flow**: The core engine for rendering our Node/Edge JSON into a pan-and-zoomable learning path.

## Detailed Implementation Specifications
1. **Scaffolding**:
   - Initialized via `create-next-app@latest frontend`.
   - TypeScript enabled.
   - Tailwind CSS enabled.
   - `src/` directory used.
   - App Router enabled.
2. **Dependencies**:
   - `lucide-react`: For sleek iconography.
   - `framer-motion`: For micro-animations when nodes are unlocked.
   - `zustand`: For lightweight global state management (managing the roadmap state without prop drilling).
   - `@xyflow/react` (React Flow): For the interactive graph.
3. **Theming**:
   - Configured `globals.css` with a custom dark theme (deep blacks, neon accents).

## Verification
- Run `npm run dev` in the `frontend` directory. The application should compile successfully and be accessible at `http://localhost:3000`.
