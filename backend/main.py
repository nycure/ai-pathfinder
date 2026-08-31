from dotenv import load_dotenv
load_dotenv()  # Load .env FIRST before any other imports read env vars

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(
    title="AI Pathfinder API",
    description="Backend API for the Personalized Learning Path Recommender",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for local development (e.g. localhost:3000, 3001, 127.0.0.1)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Pathfinder API"}
