import os
import pytest
from agents.xai_agent import XAIAgent
from models.schemas import (
    LearnerProfile, RoadmapResponse, RoadmapNode, RoadmapNodeData, 
    RoadmapEdge, SkillLevel, LearningResource, ResourceType, NodeStatus
)

@pytest.mark.skipif(not os.environ.get("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")
def test_xai_agent_explain_node():
    agent = XAIAgent()
    
    # Mock Profile
    profile = LearnerProfile(
        target_role="Fullstack AI App Developer",
        skills={},
        weekly_hours=10,
        learning_pace="medium"
    )
    
    # Mock primary resource to satisfy schema
    mock_resource = LearningResource(
        id="r1", title="Python 101", provider="Mock", url="http://mock",
        type=ResourceType.COURSE, estimated_hours=10, cost="free", rating=5.0, skills_covered=["python_basics"]
    )
    
    # Mock Roadmap
    roadmap = RoadmapResponse(
        roadmap_id="roadmap_1",
        title="Path to Fullstack AI App Developer",
        target_role="Fullstack AI App Developer",
        total_estimated_weeks=12,
        total_hours=120,
        learner_summary="Beginner with 10h/week.",
        skill_gap_summary=["python_basics", "fastapi_basics"],
        nodes=[
            RoadmapNode(
                id="python_basics",
                type="customMilestoneNode",
                position={"x": 0, "y": 0},
                data=RoadmapNodeData(
                    label="Python Fundamentals",
                    phase=1,
                    phase_title="Basics",
                    description="Learn Python",
                    status=NodeStatus.LOCKED,
                    primary_resource=mock_resource,
                    why_recommended="",
                    skills_acquired=["python_basics"],
                    estimated_weeks=2,
                    difficulty=SkillLevel.BEGINNER
                )
            ),
            RoadmapNode(
                id="fastapi_basics",
                type="customMilestoneNode",
                position={"x": 100, "y": 0},
                data=RoadmapNodeData(
                    label="FastAPI",
                    phase=2,
                    phase_title="Backend",
                    description="Learn FastAPI",
                    status=NodeStatus.LOCKED,
                    primary_resource=mock_resource,
                    why_recommended="",
                    skills_acquired=["fastapi_basics"],
                    estimated_weeks=3,
                    difficulty=SkillLevel.INTERMEDIATE
                )
            )
        ],
        edges=[
            RoadmapEdge(id="e1", source="python_basics", target="fastapi_basics")
        ]
    )
    
    response = agent.explain_node("python_basics", profile, roadmap)
    
    # Verify the structure
    assert response.justification != ""
    assert isinstance(response.missing_prerequisites_for_this_node, list)

def test_xai_agent_mocked_explain_node():
    from unittest.mock import MagicMock
    from models.schemas import ExplainabilityResponse
    
    mock_llm = MagicMock()
    mock_llm.generate_structured_output.return_value = ExplainabilityResponse(
        justification="Python is required before FastAPI",
        missing_prerequisites_for_this_node=[]
    ).model_dump_json()
    
    agent = XAIAgent(llm_client=mock_llm)
    
    profile = LearnerProfile(
        target_role="Fullstack AI App Developer",
        skills={},
        weekly_hours=10,
        learning_pace="medium"
    )
    mock_resource = LearningResource(
        id="r1", title="Python 101", provider="Mock", url="http://mock",
        type=ResourceType.COURSE, estimated_hours=10, cost="free", rating=5.0, skills_covered=["python_basics"]
    )
    roadmap = RoadmapResponse(
        roadmap_id="roadmap_1",
        title="Path to Fullstack AI App Developer",
        target_role="Fullstack AI App Developer",
        total_estimated_weeks=12,
        total_hours=120,
        learner_summary="",
        skill_gap_summary=[],
        nodes=[
            RoadmapNode(
                id="python_basics",
                position={"x": 0, "y": 0},
                data=RoadmapNodeData(
                    label="Python Fundamentals",
                    phase=1,
                    phase_title="Basics",
                    description="Learn Python",
                    status=NodeStatus.LOCKED,
                    primary_resource=mock_resource,
                    why_recommended="",
                    skills_acquired=["python_basics"],
                    estimated_weeks=2,
                    difficulty=SkillLevel.BEGINNER
                )
            )
        ],
        edges=[]
    )
    
    res = agent.explain_node("python_basics", profile, roadmap)
    assert "Python is required" in res.justification

