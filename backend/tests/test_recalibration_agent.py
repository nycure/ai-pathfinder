import pytest
from unittest.mock import MagicMock
from agents.recalibration_agent import RecalibrationAgent
from models.schemas import (
    RoadmapResponse, RoadmapNode, RoadmapEdge, RoadmapNodeData,
    NodeStatus, SkillLevel, LearningResource, ResourceType
)

def test_recalibration_agent_injects_refresher():
    mock_llm = MagicMock()
    mock_llm.generate_structured_output.return_value = '{"title": "Warmup: Python Basics", "description": "Quick review of syntax.", "key_review_topics": ["Variables", "Loops"], "rationale": "Spaced repetition"}'
    
    agent = RecalibrationAgent(llm_client=mock_llm)
    
    node1 = RoadmapNode(
        id="node_1",
        position={"x": 0, "y": 0},
        data=RoadmapNodeData(
            label="FastAPI Basics",
            phase=1,
            phase_title="Foundations",
            description="Building APIs",
            status=NodeStatus.AVAILABLE,
            primary_resource=LearningResource(
                id="res_1", title="FastAPI Docs", provider="FastAPI", url="https://fastapi.tiangolo.com",
                type=ResourceType.DOCUMENTATION, estimated_hours=5, cost="free", rating=4.9, skills_covered=["FastAPI"]
            ),
            why_recommended="Core web backend framework",
            skills_acquired=["FastAPI"],
            estimated_weeks=1,
            difficulty=SkillLevel.BEGINNER
        )
    )

    roadmap = RoadmapResponse(
        roadmap_id="test-roadmap",
        title="Python Web Developer",
        target_role="Backend Developer",
        total_estimated_weeks=4,
        total_hours=40,
        learner_summary="Beginner path",
        skill_gap_summary=["FastAPI"],
        nodes=[node1],
        edges=[]
    )

    recalibrated = agent.recalibrate_roadmap(roadmap)
    assert len(recalibrated.nodes) == 2
    assert "refresher" in recalibrated.nodes[0].id
    assert recalibrated.nodes[0].data.label == "Warmup: Python Basics"
    assert recalibrated.nodes[1].data.status == NodeStatus.LOCKED
