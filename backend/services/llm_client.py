import os
import json
from pydantic import BaseModel
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential

class LLMClient:
    def __init__(self, api_key: str = None):
        # The client will automatically pick up GEMINI_API_KEY from the environment
        # if api_key is not explicitly provided.
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-3.6-flash"

    @retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=2, min=3, max=60))
    def generate_structured_output(self, prompt: str, response_schema: type[BaseModel], system_instruction: str = None) -> str:
        """
        Calls Gemini 2.5 Flash and enforces a structured JSON output.

        Instead of passing response_schema directly to the API (which triggers
        additionalProperties — unsupported in Developer API mode), we embed
        the JSON schema description in the prompt and request JSON-only output
        via response_mime_type. Pydantic validation is then done by the caller.
        """

        # Get human-readable schema and embed it in the prompt
        schema_description = json.dumps(response_schema.model_json_schema(), indent=2)
        full_prompt = (
            f"{prompt}\n\n"
            f"You MUST respond ONLY with a valid JSON object that strictly conforms to this schema:\n"
            f"```json\n{schema_description}\n```\n"
            f"Do not include any explanation or markdown formatting — return the raw JSON object only."
        )

        config_args = {
            "response_mime_type": "application/json",
            "temperature": 0.2,  # Low temperature for deterministic outputs
        }

        if system_instruction:
            config_args["system_instruction"] = system_instruction

        config = types.GenerateContentConfig(**config_args)

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=full_prompt,
            config=config,
        )

        return response.text

    def generate_chat_stream(self, messages: list[dict], system_instruction: str = None):
        """
        Generates a streaming response using Gemini's generate_content_stream.
        Expects messages as [{"role": "user"|"assistant", "content": "..."}]
        """
        contents = []
        for msg in messages:
            content_str = msg.get("content", "").strip()
            if not content_str:
                continue
            # Map 'assistant' to 'model' for Gemini
            role = "model" if msg["role"] == "assistant" else "user"
            contents.append(
                types.Content(role=role, parts=[types.Part.from_text(text=content_str)])
            )

        # Gemini requires multi-turn contents to start with a 'user' turn
        while contents and contents[0].role == "model":
            contents.pop(0)

        if not contents:
            return

        config_args = {}
        if system_instruction:
            config_args["system_instruction"] = system_instruction
            
        config = types.GenerateContentConfig(**config_args)

        response = self.client.models.generate_content_stream(
            model=self.model_name,
            contents=contents,
            config=config,
        )

        for chunk in response:
            if chunk.text:
                yield chunk.text
