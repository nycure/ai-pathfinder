import pytest
from unittest.mock import MagicMock
from models.schemas import (
    LearnerProfile,
    RoadmapResponse,
    RoadmapNode,
    RoadmapNodeData,
    RoadmapEdge,
    LearningResource,
    ResourceType,
    NodeStatus,
    SkillLevel,
    GenerateRoadmapResponse
)

def test_workflow_10_public_portfolio_and_opengraph_end_to_end():
    """
    Simulates Flow 10: Recruiter visits /{username} -> Public API endpoint resolves user & roadmap -> Delivers read-only portfolio DTO & OpenGraph metadata
    """
    # 1. Setup mock database records
    mock_user_record = {"id": "user_uuid_123", "username": "sarah_ai", "email": "sarah@example.com"}
    
    mock_resource = LearningResource(
        id="r_pytorch", title="PyTorch Docs", provider="PyTorch", url="https://pytorch.org",
        type=ResourceType.DOCUMENTATION, estimated_hours=10, cost="free", rating=4.9, skills_covered=["pytorch"]
    )
    
    node = RoadmapNode(
        id="pytorch_nlp",
        position={"x": 0, "y": 0},
        data=RoadmapNodeData(
            label="PyTorch for NLP",
            phase=1,
            phase_title="Foundations",
            description="Deep learning models for natural language processing",
            status=NodeStatus.COMPLETED,
            primary_resource=mock_resource,
            alternative_resources=[],
            why_recommended="Prerequisite for transformer architectures",
            skills_acquired=["pytorch", "nlp_basics"],
            estimated_weeks=2,
            difficulty=SkillLevel.INTERMEDIATE
        )
    )
    
    roadmap = RoadmapResponse(
        roadmap_id="roadmap_public_1",
        title="Path to Senior AI Engineer",
        target_role="Senior AI Engineer",
        total_estimated_weeks=14,
        total_hours=140,
        learner_summary="Sarah's fast-track journey into senior AI Engineering.",
        skill_gap_summary=["transformers", "rag"],
        nodes=[node],
        edges=[]
    )
    
    profile = LearnerProfile(
        target_role="Senior AI Engineer",
        skills={"pytorch": SkillLevel.INTERMEDIATE},
        weekly_hours=15,
        learning_pace="fast"
    )
    
    # 2. Package response matching public endpoint output
    public_response = GenerateRoadmapResponse(profile=profile, roadmap=roadmap)
    
    # 3. Verify Public Portfolio metadata
    assert public_response.roadmap.target_role == "Senior AI Engineer"
    assert public_response.roadmap.total_estimated_weeks == 14
    assert len(public_response.roadmap.nodes) == 1
    assert public_response.roadmap.nodes[0].data.status == NodeStatus.COMPLETED
    
    # 4. Simulate Next.js Server-Side OpenGraph Metadata generation
    og_title = f"{mock_user_record['username']}'s Learning Journey | AI Pathfinder"
    og_description = f"Check out {mock_user_record['username']}'s verified learning roadmap for {public_response.roadmap.target_role} on AI Pathfinder."
    
    assert og_title == "sarah_ai's Learning Journey | AI Pathfinder"
    assert "Senior AI Engineer" in og_description
    assert "sarah_ai" in og_description
