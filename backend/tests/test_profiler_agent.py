import os
import pytest
from agents.profiler_agent import ProfilerAgent
from models.schemas import SkillLevel

@pytest.mark.skipif(not os.environ.get("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")
def test_profiler_agent_extraction():
    agent = ProfilerAgent()
    
    user_input = "I know basic JavaScript and HTML, want to build fullstack AI apps in 3 months with 10h/week"
    
    profile = agent.extract_profile(user_input)
    
    # Verify the target role is somewhat related
    assert "fullstack" in profile.target_role.lower() or "ai" in profile.target_role.lower()
    
    # Verify time constraints extracted correctly
    assert profile.weekly_hours == 10
    
    # Verify skills dictionary is present
    assert isinstance(profile.skills, dict)
