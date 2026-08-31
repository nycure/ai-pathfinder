import json
import pytest
from pydantic import ValidationError
from models.schemas import (
    LearnerProfile,
    LearningResource,
    RoadmapNodeData,
    RoadmapNode,
    RoadmapEdge,
    RoadmapResponse,
    SkillLevel,
    ResourceType,
    NodeStatus
)

def test_learner_profile_validation():
    # Valid profile
    profile = LearnerProfile(
        target_role="AI Engineer",
        skills={"python": "intermediate"},
        weekly_hours=10,
        learning_pace="fast"
    )
    assert profile.target_role == "AI Engineer"
    
    # Invalid profile (missing required fields)
    with pytest.raises(ValidationError):
        LearnerProfile(target_role="AI Engineer")

def test_learning_resource_serialization():
    resource = LearningResource(
        id="res_1",
        title="Intro to AI",
        provider="Coursera",
        url="https://coursera.org",
        type="course",
        estimated_hours=5,
        cost="free",
        rating=4.9,
        skills_covered=["ai_basics"]
    )
    # Serialize to JSON string
    resource_json = resource.model_dump_json()
    
    # Deserialize back
    loaded_resource = LearningResource.model_validate_json(resource_json)
    assert loaded_resource.title == "Intro to AI"
    assert loaded_resource.type == ResourceType.COURSE

def test_roadmap_node_validation():
    resource = LearningResource(
        id="res_1",
        title="Intro to AI",
        provider="Coursera",
        url="https://coursera.org",
        type="course",
        estimated_hours=5,
        cost="free",
        rating=4.9,
        skills_covered=["ai_basics"]
    )
    
    node_data = RoadmapNodeData(
        label="Phase 1: Basics",
        phase=1,
        phase_title="Foundations",
        description="Learn the basics.",
        primary_resource=resource,
        why_recommended="You need basics.",
        skills_acquired=["ai_basics"],
        estimated_weeks=1,
        difficulty="beginner"
    )
    
    node = RoadmapNode(
        id="node_1",
        position={"x": 100, "y": 100},
        data=node_data
    )
    assert node.data.status == NodeStatus.LOCKED
    
def test_full_roadmap_response():
    # Create minimal objects to satisfy the schema
    resource = LearningResource(
        id="res_1", title="Intro", provider="Test", url="http", 
        type="course", estimated_hours=1, cost="free", rating=5.0, skills_covered=["test"]
    )
    node_data = RoadmapNodeData(
        label="Label", phase=1, phase_title="Phase", description="Desc",
        primary_resource=resource, why_recommended="Why", skills_acquired=["test"],
        estimated_weeks=1, difficulty="beginner"
    )
    node = RoadmapNode(id="n1", position={"x":0, "y":0}, data=node_data)
    edge = RoadmapEdge(id="e1", source="n0", target="n1")
    
    response = RoadmapResponse(
        roadmap_id="rm_1",
        title="My Roadmap",
        target_role="Developer",
        total_estimated_weeks=10,
        total_hours=100,
        learner_summary="Good learner",
        skill_gap_summary=["Needs python"],
        nodes=[node],
        edges=[edge]
    )
    
    json_data = response.model_dump_json()
    assert "rm_1" in json_data
    loaded_response = RoadmapResponse.model_validate_json(json_data)
    assert loaded_response.nodes[0].data.difficulty == SkillLevel.BEGINNER
