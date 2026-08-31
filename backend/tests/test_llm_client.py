import os
import json
import pytest
from pydantic import BaseModel
from services.llm_client import LLMClient

# Define a simple schema for testing
class DummyUserSchema(BaseModel):
    name: str
    age: int
    is_student: bool

# We will mark this test to be skipped if GEMINI_API_KEY is not set
# to prevent CI/CD failures if keys aren't present.
@pytest.mark.skipif(not os.environ.get("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")
def test_llm_client_structured_output():
    client = LLMClient()
    
    prompt = "Extract the following information: John is 25 years old and he is a student."
    system_instruction = "You are a helpful data extraction assistant."
    
    response_text = client.generate_structured_output(
        prompt=prompt,
        response_schema=DummyUserSchema,
        system_instruction=system_instruction
    )
    
    # Parse the response
    data = json.loads(response_text)
    
    assert data["name"] == "John"
    assert data["age"] == 25
    assert data["is_student"] is True
