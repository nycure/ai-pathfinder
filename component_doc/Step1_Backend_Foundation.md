# Step 1: Backend Foundation & Environment Setup

## Component Overview
The foundation of the intelligent learning path system is built on **Python 3.11+**. We use a dedicated virtual environment to isolate all our AI and backend dependencies. 

## Architectural Purpose
This step ensures that our execution environment is clean, deterministic, and isolated. It prevents dependency conflicts globally on the machine and sets up the configuration files needed to interact with the Google Gemini API securely.

## Detailed Implementation Specifications
1. **Virtual Environment (`.venv`)**: Provides an isolated Python environment.
2. **Dependencies (`requirements.txt`)**: 
   - `fastapi` and `uvicorn`: For the high-performance async web server.
   - `pydantic`: For strict schema validation (critical for structured LLM JSON outputs).
   - `networkx`: For the mathematical prerequisite DAG validation.
   - `google-genai`: The official Google SDK for integrating Gemini 2.5 Flash.
   - `chromadb`: The vector database for hybrid semantic search over curated resources.
   - `python-dotenv`: To securely load API keys from the `.env` file without hardcoding them in the repository.
   - `pytest`: For automated testing.
3. **Environment Secrets (`.env.example`)**: A template for required secrets, specifically `GEMINI_API_KEY`.
4. **Source Control Ignore (`.gitignore`)**: Ensures we do not commit `.venv` environments, cache files, or `.env` files containing actual API keys to the GitHub repository.

## Verification
- Running `pip install -r requirements.txt` must succeed without conflicts.
- Activating the virtual environment should isolate `pip freeze` to just the required dependencies.
