import pytest
from unittest.mock import MagicMock
from agents.adaptation_agent import AdaptationAgent, ProfileUpdate
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
    AdaptationRequest
)

def test_workflow_6_feedback_and_dynamic_goal_rebalancing_end_to_end():
    """
    Simulates Flow 6: Learner submits feedback / goal pivot -> AdaptationAgent detects role change -> Re-synthesizes DAG with RoadmapAgent
    """
    # 1. Setup mock LLM for AdaptationAgent
    mock_llm = MagicMock()
    mock_profile_update = ProfileUpdate(new_target_role="Frontend Web Developer")
    mock_llm.generate_structured_output.return_value = mock_profile_update.model_dump_json()
    
    # 2. Setup mock RoadmapAgent to return a newly synthesized Frontend curriculum
    mock_roadmap_agent = MagicMock()
    frontend_resource = LearningResource(
        id="res_react",
        title="React & Next.js Docs",
        provider="Vercel",
        url="https://nextjs.org",
        type=ResourceType.DOCUMENTATION,
        estimated_hours=10,
        cost="free",
        rating=4.9,
        skills_covered=["react", "nextjs"]
    )
    
    frontend_node = RoadmapNode(
        id="react_basics",
        position={"x": 0, "y": 0},
        data=RoadmapNodeData(
            label="React & Component State",
            phase=1,
            phase_title="Foundations",
            description="JSX, hooks, component architecture",
            status=NodeStatus.AVAILABLE,
            primary_resource=frontend_resource,
            alternative_resources=[],
            why_recommended="Core frontend foundation",
            skills_acquired=["react"],
            estimated_weeks=2,
            difficulty=SkillLevel.BEGINNER
        )
    )
    
    new_frontend_roadmap = RoadmapResponse(
        roadmap_id="roadmap_frontend_1",
        title="Path to Frontend Web Developer",
        target_role="Frontend Web Developer",
        total_estimated_weeks=8,
        total_hours=80,
        learner_summary="Pivoted to Frontend Web Development",
        skill_gap_summary=["react", "nextjs"],
        nodes=[frontend_node],
        edges=[]
    )
    mock_roadmap_agent.generate_roadmap.return_value = new_frontend_roadmap
    
    # 3. Setup Initial Learner Profile (Data Scientist) and Initial Roadmap
    initial_profile = LearnerProfile(
        target_role="Data Scientist",
        skills={"python_basics": SkillLevel.INTERMEDIATE},
        weekly_hours=10,
        learning_pace="medium"
    )
    
    initial_roadmap = RoadmapResponse(
        roadmap_id="roadmap_ds_1",
        title="Path to Data Scientist",
        target_role="Data Scientist",
        total_estimated_weeks=12,
        total_hours=120,
        learner_summary="Data Science journey",
        skill_gap_summary=["linear_algebra", "pandas"],
        nodes=[],
        edges=[]
    )
    
    # 4. Instantiate AdaptationAgent
    adaptation_agent = AdaptationAgent(llm_client=mock_llm, roadmap_agent=mock_roadmap_agent)
    
    # 5. User submits qualitative feedback expressing a career pivot
    feedback_text = "Regarding milestone 'Python Basics': Actually, I want to build web UIs with React instead of doing data science."
    request = AdaptationRequest(
        roadmap_id="roadmap_ds_1",
        feedback=feedback_text
    )
    
    # 6. Execute Adaptation Pipeline
    response = adaptation_agent.adapt_path(
        request=request,
        current_profile=initial_profile,
        current_roadmap=initial_roadmap
    )
    
    # 7. Verify that target_role was updated
    assert response.updated_profile.target_role == "Frontend Web Developer"
    assert "Changed target role from 'Data Scientist' to 'Frontend Web Developer'" in response.changes_made
    
    # 8. Verify that newly generated roadmap reflects the updated target role and nodes
    assert response.updated_roadmap.target_role == "Frontend Web Developer"
    assert len(response.updated_roadmap.nodes) == 1
    assert response.updated_roadmap.nodes[0].id == "react_basics"
    assert response.updated_roadmap.nodes[0].data.status == NodeStatus.AVAILABLE
    
    # 9. Verify RoadmapAgent was called with the updated profile
    mock_roadmap_agent.generate_roadmap.assert_called_once()
    called_profile = mock_roadmap_agent.generate_roadmap.call_args[0][0]
    assert called_profile.target_role == "Frontend Web Developer"
