# Step 5: LLM Client Wrapper (Gemini 2.5 Flash)

## Component Overview
The LLM Client Wrapper is the centralized integration point with the Google Gemini API. It leverages the official `google-genai` Python SDK to interact with the `gemini-2.5-flash` model.

## Architectural Purpose
By centralizing the LLM calls into a single service, we achieve:
1. **Separation of Concerns**: Individual agents (Profiler, Synthesizer, XAI) do not need to manage API keys, HTTP clients, or error handling.
2. **Structured Outputs**: We enforce Pydantic-based structured JSON outputs at the client level, preventing formatting hallucinations.
3. **Resilience**: A central point to implement exponential backoff retries in case of rate limits (HTTP 429) from the API.

## Detailed Implementation Specifications
1. **`backend/services/llm_client.py`**:
   - Imports: `from google import genai` and `from google.genai import types`.
   - `LLMClient` Class:
     - `__init__()`: Initializes the client. If no `api_key` is passed, it uses the environment variable `GEMINI_API_KEY`.
     - `generate_structured_output(prompt: str, response_schema: type[BaseModel], system_instruction: str)`: 
       - Uses `client.models.generate_content`.
       - Passes `response_schema` directly into `types.GenerateContentConfig` for deterministic outputs.
       - Returns the raw JSON string which can be parsed downstream.
     - Includes a `tenacity` retry decorator for robustness against transient API failures.

## Verification
- Unit tests (`backend/tests/test_llm_client.py`) will send a simple prompt and verify that the client correctly respects a provided Pydantic schema and returns valid JSON.
