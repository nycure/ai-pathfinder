# Step 22: Phase 4 - Active Validation & Micro-Quizzes

## Overview
Phase 4 introduces Active Validation to the learning journey. Previously, users could mark a node as mastered with a single click. Now, AI Pathfinder ensures genuine understanding by evaluating learners through AI-generated Micro-Quizzes and GitHub Capstone repository analysis.

## Architectural Changes

### 1. AI Micro-Quiz Engine
- **Backend (`quiz_agent.py`)**: A dedicated `QuizAgent` utilizes `LLMClient.generate_structured_output` to produce 3 highly contextual, multiple-choice questions. It factors in the learner's specific `target_role` to make questions relevant rather than generic.
- **Frontend (`MasteryQuizModal.tsx`)**: Replaced the immediate completion of "Mark as Mastered" with an interactive quiz modal. The user must score $\ge 66\%$ (2/3) to automatically complete the milestone. If they fail, they are given explanations for the correct answers and prompted to review the material.

### 2. GitHub Capstone Repository Verifier
- **Backend (`github_verifier_agent.py`)**: A `GitHubVerifierAgent` built with `httpx` fetches the file structure (`tree`) and `README.md` of any public GitHub repository. 
- **LLM Assessment**: The fetched data is passed to Gemini 2.5 Flash, which acts as a Senior Software Engineer. It evaluates if the codebase meets the specific requirements of the current milestone.
- **Frontend (`GitHubVerificationModal.tsx`)**: A new "Verify Repo" button allows learners to paste a URL. The modal displays structured feedback (strengths, weaknesses, and a final approval decision). If the LLM approves the project, the milestone is automatically marked as Mastered.

### 3. API Endpoints
- `POST /api/verify/quiz/generate`: Generates the structured quiz.
- `POST /api/verify/github`: Analyzes the provided repository URL.

## Status
- **Implementation**: 🟢 Completed
- **Dependencies**: `httpx`, shadcn (`dialog`, `radio-group`)
- **Next Steps**: Phase 5 (Gamification & Social Accountability).
