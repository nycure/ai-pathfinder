import os
import pytest
from agents.adaptation_agent import AdaptationAgent
from models.schemas import (
    LearnerProfile, RoadmapResponse, RoadmapNode, RoadmapNodeData, 
    AdaptationRequest, SkillLevel, NodeStatus, LearningResource, ResourceType
)

@pytest.mark.skipif(not os.environ.get("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")
def test_adaptation_agent_node_completion():
    agent = AdaptationAgent()
    
    profile = LearnerProfile(
        target_role="Data Scientist",
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
        title="Path to Data Scientist",
        target_role="Data Scientist",
        total_estimated_weeks=12,
        total_hours=120,
        learner_summary="",
        skill_gap_summary=[],
        nodes=[
            RoadmapNode(
                id="python_basics",
                type="customMilestoneNode",
                position={"x":0, "y":0},
                data=RoadmapNodeData(
                    label="Python Fundamentals",
                    phase=1,
                    phase_title="Basics",
                    description="",
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
    
    request = AdaptationRequest(
        roadmap_id="roadmap_1",
        completed_node_id="python_basics"
    )
    
    response = agent.adapt_path(request, profile, roadmap)
    
    # Profile should now have python_basics
    assert "python_basics" in response.updated_profile.skills
    
    # The new roadmap should exclude python_basics since it's known
    new_node_ids = [n.id for n in response.updated_roadmap.nodes]
    assert "python_basics" not in new_node_ids

@pytest.mark.skipif(not os.environ.get("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")
def test_adaptation_agent_feedback():
    agent = AdaptationAgent()
    
    profile = LearnerProfile(
        target_role="Data Scientist",
        skills={},
        weekly_hours=10,
        learning_pace="medium"
    )
    
    roadmap = RoadmapResponse(
        roadmap_id="roadmap_1",
        title="Path to Data Scientist",
        target_role="Data Scientist",
        total_estimated_weeks=0,
        total_hours=0,
        learner_summary="",
        skill_gap_summary=[],
        nodes=[],
        edges=[]
    )
    
    request = AdaptationRequest(
        roadmap_id="roadmap_1",
        feedback="Actually, I think I want to do Frontend Web Development instead."
    )
    
    response = agent.adapt_path(request, profile, roadmap)
    
    # Target role should have changed
    assert response.updated_profile.target_role != "Data Scientist"
    assert "frontend" in response.updated_profile.target_role.lower() or "web" in response.updated_profile.target_role.lower()

def test_adaptation_agent_mocked_completion():
    from unittest.mock import MagicMock
    mock_llm = MagicMock()
    mock_roadmap_agent = MagicMock()
    
    mock_resource = LearningResource(
        id="r1", title="Python 101", provider="Mock", url="http://mock",
        type=ResourceType.COURSE, estimated_hours=10, cost="free", rating=5.0, skills_covered=["python_basics"]
    )
    
    mock_new_roadmap = RoadmapResponse(
        roadmap_id="roadmap_2",
        title="Path to Data Scientist",
        target_role="Data Scientist",
        total_estimated_weeks=10,
        total_hours=100,
        learner_summary="",
        skill_gap_summary=[],
        nodes=[],
        edges=[]
    )
    mock_roadmap_agent.generate_roadmap.return_value = mock_new_roadmap
    
    agent = AdaptationAgent(llm_client=mock_llm, roadmap_agent=mock_roadmap_agent)
    
    profile = LearnerProfile(
        target_role="Data Scientist",
        skills={},
        weekly_hours=10,
        learning_pace="medium"
    )
    
    initial_roadmap = RoadmapResponse(
        roadmap_id="roadmap_1",
        title="Path to Data Scientist",
        target_role="Data Scientist",
        total_estimated_weeks=12,
        total_hours=120,
        learner_summary="",
        skill_gap_summary=[],
        nodes=[
            RoadmapNode(
                id="python_basics",
                type="customMilestoneNode",
                position={"x":0, "y":0},
                data=RoadmapNodeData(
                    label="Python Fundamentals",
                    phase=1,
                    phase_title="Basics",
                    description="",
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
    
    request = AdaptationRequest(
        roadmap_id="roadmap_1",
        completed_node_id="python_basics"
    )
    
    res = agent.adapt_path(request, profile, initial_roadmap)
    assert "python_basics" in res.updated_profile.skills
    assert "Marked 'Python Fundamentals' as completed" in res.changes_made
    mock_roadmap_agent.generate_roadmap.assert_called_once()

