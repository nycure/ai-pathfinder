# 🚀 AI Pathfinder: Local Setup & Execution Guide

This document provides a clean, step-by-step walkthrough to run **AI Pathfinder** locally from scratch on any machine (Windows, macOS, Linux).

---

## 📋 1. Prerequisites

Make sure the following tools are installed:
- **Node.js**: `v18.0.0` or higher ([Download Node.js](https://nodejs.org/))
- **Python**: `3.11` or higher ([Download Python](https://www.python.org/))
- **Git**: Installed and configured ([Download Git](https://git-scm.com/))
- **Google Gemini API Key**: Free from [Google AI Studio](https://aistudio.google.com/)
- **Supabase Account**: Free project from [Supabase](https://supabase.com/)

---

## 🗄️ 2. Database Setup (Supabase — 30 Seconds)

1. Create a free project at [supabase.com](https://supabase.com).
2. Open the **SQL Editor** on the left menu.
3. Open [`backend/db/schema.sql`](backend/db/schema.sql), copy the entire file contents, paste into the SQL Editor, and click **Run**.
   *(This automatically creates all 6 tables, indexes, Row-Level Security policies, and auth triggers).*
4. Navigate to **Project Settings (⚙️ icon)** -> **API** and copy:
   - **Project URL**
   - **`anon` public key**
   - **`service_role` secret key**
   - **JWT Secret** (under JWT Settings)

---

## ⚙️ 3. Backend Setup (FastAPI + Python)

The backend powers the multi-agent AI system, graph algorithms, and caching engine on port `8000`.

### Step 3.1: Navigate & Create Virtual Environment
Open a terminal in the project root:
```bash
cd backend

# Create Python virtual environment
python -m venv .venv

# Activate the virtual environment:
# On Windows (Command Prompt / PowerShell):
.venv\Scripts\activate
# On macOS / Linux:
source .venv/bin/activate
```

### Step 3.2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3.3: Configure Backend Environment Variables
Create a file named `.env` inside the `backend/` folder:
```env
GEMINI_API_KEY=your_google_ai_studio_api_key_here
PORT=8000
ENVIRONMENT=development

# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_service_role_secret_key_here
SUPABASE_JWT_SECRET=your_supabase_jwt_secret_here
```

### Step 3.4: Start the Backend Server
```bash
uvicorn main:app --reload --port 8000
```
- ✅ **API Health**: Running at `http://localhost:8000`
- 📚 **Interactive Swagger API Docs**: View at `http://localhost:8000/docs`

---

## 💻 4. Frontend Setup (Next.js 15 + TypeScript)

The frontend provides the interactive React Flow canvas, Socratic AI tutor, and analytics dashboard on port `3000`.

### Step 4.1: Open a NEW Terminal & Navigate
```bash
cd frontend
```

### Step 4.2: Install Node.js Dependencies
```bash
npm install
```

### Step 4.3: Configure Frontend Environment Variables
Create a file named `.env.local` inside the `frontend/` folder:
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_public_key_here
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Step 4.4: Start the Next.js Development Server
```bash
npm run dev
```
- 🌐 **Web Application**: Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🪟 5. (Alternative) 1-Click Windows Startup

If you are on Windows, you can start both backend and frontend simultaneously with a single click:
1. Double-click **`run_app.bat`** in the project root directory.
2. It automatically boots both servers and opens your default browser at `http://localhost:3000`.

---

## 🧪 6. Running Automated Tests

Verify that all algorithms, agents, and workflows pass with 100% success rate:

### Run Backend Pytest Suite (38+ Tests)
```bash
cd backend
python -m pytest tests/ -v
```
> Covers: NetworkX DAG cycle detection, topological sort, LLM client, Socratic SSE chat streaming, micro-quiz active validation, GitHub capstone review, calendar export, and all 10 end-to-end user workflows.

### Run Frontend Type Check & Production Build Test
```bash
cd frontend
npx tsc --noEmit
npm run build
```
> Confirms clean production compilation with zero TypeScript errors.

---

## 🎯 7. Quick Smoke Test (Try the App!)

Once running at `http://localhost:3000`:
1. **Sign Up / Log In**: Create an account with any email & password.
2. **Synthesize Roadmap**: Type your career goal in the Goal Chat (e.g., *"I want to learn AI Engineering with 12 hours/week"*).
3. **Explore the DAG**: Pan, zoom, and click any milestone card on the React Flow canvas.
4. **Inspect XAI**: Read why that specific milestone was recommended for your profile.
5. **Chat with Tutor**: Open the in-drawer Socratic AI Tutor and ask questions on the topic.
6. **Take a Quiz**: Click *"Mark as Mastered"* to attempt the 3-question validation micro-quiz.
7. **Export Calendar**: Click *"Add to Calendar"* on the dashboard to download your `.ics` study schedule.

---

## ❓ 8. Troubleshooting FAQ

- **Port 8000 / 3000 Already in Use?**
  - Change backend port: `uvicorn main:app --reload --port 8001` (and update `NEXT_PUBLIC_API_URL=http://localhost:8001/api`).
  - Next.js will automatically prompt to run on port `3001` if `3000` is busy.
- **Gemini API Rate Limits (429)?**
  - The application automatically caches taxonomy, XAI explanations, and resources with MD5-keyed caching (`CacheService`) to minimize token consumption.
- **Supabase Authentication Issues?**
  - Ensure you added `http://localhost:3000/**` to **Authentication -> URL Configuration -> Redirect URLs** in your Supabase Dashboard.
