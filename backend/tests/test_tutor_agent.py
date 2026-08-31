import pytest
from unittest.mock import MagicMock
from agents.tutor_agent import TutorAgent
from models.schemas import LearnerProfile, RoadmapResponse, RoadmapNode, RoadmapNodeData, LearningResource

def test_tutor_agent_stream_chat():
    mock_llm = MagicMock()
    mock_llm.generate_chat_stream.return_value = ["Hello ", "world", "!"]
    
    agent = TutorAgent(llm_client=mock_llm)
    
    dummy_resource = LearningResource(
        id="doc_py",
        title="Python Documentation",
        provider="Python Software Foundation",
        url="https://docs.python.org",
        type="documentation",
        estimated_hours=5,
        cost="free",
        rating=4.9,
        skills_covered=["python_basics"]
    )
    
    node = RoadmapNode(
        id="python_basics",
        position={"x": 0.0, "y": 0.0},
        data=RoadmapNodeData(
            label="Python Basics",
            phase=1,
            phase_title="Foundations",
            description="Variables, loops, functions",
            status="in_progress",
            primary_resource=dummy_resource,
            alternative_resources=[],
            why_recommended="Core prerequisite",
            skills_acquired=["python_basics"],
            estimated_weeks=2,
            difficulty="beginner"
        )
    )
    roadmap = RoadmapResponse(
        roadmap_id="roadmap-123",
        title="AI Engineer Path",
        target_role="AI Engineer",
        total_estimated_weeks=12,
        total_hours=120,
        learner_summary="Beginner journey",
        skill_gap_summary=[],
        nodes=[node],
        edges=[]
    )
    profile = LearnerProfile(
        target_role="AI Engineer",
        skills={},
        weekly_hours=10,
        learning_pace="medium"
    )
    
    messages = [
        {"role": "assistant", "content": "Hi! I am your AI Tutor."},
        {"role": "user", "content": "What is a python dictionary?"}
    ]
    
    stream_output = list(agent.stream_chat(messages, "python_basics", profile, roadmap))
    assert stream_output == ["Hello ", "world", "!"]
    mock_llm.generate_chat_stream.assert_called_once()
