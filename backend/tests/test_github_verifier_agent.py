import pytest
from unittest.mock import MagicMock, AsyncMock
from agents.github_verifier_agent import GitHubVerifierAgent
from models.schemas import (
    LearnerProfile,
    RoadmapResponse,
    RoadmapNode,
    RoadmapNodeData,
    LearningResource,
    GitHubVerificationResponse,
)

@pytest.mark.anyio
async def test_github_verifier_agent():
    mock_llm = MagicMock()
    mock_response = GitHubVerificationResponse(
        approved=True,
        strengths=["Clean directory structure", "Comprehensive README with usage instructions"],
        weaknesses=["Missing unit tests"],
        feedback_summary="Excellent demonstration of fullstack principles."
    )
    mock_llm.generate_structured_output.return_value = mock_response.model_dump_json()
    
    mock_http = MagicMock()
    # Mock tree response
    mock_tree_res = MagicMock()
    mock_tree_res.status_code = 200
    mock_tree_res.json.return_value = {
        "tree": [
            {"path": "src/main.py", "type": "blob"},
            {"path": "requirements.txt", "type": "blob"}
        ]
    }
    # Mock readme response
    mock_readme_res = MagicMock()
    mock_readme_res.status_code = 200
    mock_readme_res.json.return_value = {
        "content": "IyBNeSBQcm9qZWN0CgpBIGdyZWF0IEFJIEFwcGxpY2F0aW9uLg==" # "# My Project\n\nA great AI Application."
    }
    
    mock_http.get = AsyncMock(side_effect=[mock_tree_res, mock_readme_res])
    
    agent = GitHubVerifierAgent(llm_client=mock_llm, http_client=mock_http)
    
    dummy_resource = LearningResource(
        id="res-1",
        title="FastAPI Guide",
        provider="FastAPI",
        url="https://fastapi.tiangolo.com",
        type="documentation",
        estimated_hours=4,
        cost="free",
        rating=4.9,
        skills_covered=["fastapi"]
    )
    
    node = RoadmapNode(
        id="fastapi_api",
        position={"x": 0.0, "y": 0.0},
        data=RoadmapNodeData(
            label="FastAPI Backend",
            phase=2,
            phase_title="Core Services",
            description="Build scalable async REST APIs",
            status="in_progress",
            primary_resource=dummy_resource,
            alternative_resources=[],
            practical_project="Build a REST API service with FastAPI",
            why_recommended="Backend development skill",
            skills_acquired=["fastapi"],
            estimated_weeks=2,
            difficulty="intermediate"
        )
    )
    roadmap = RoadmapResponse(
        roadmap_id="roadmap-123",
        title="Fullstack Path",
        target_role="Fullstack Engineer",
        total_estimated_weeks=10,
        total_hours=100,
        learner_summary="FastAPI and React journey",
        skill_gap_summary=[],
        nodes=[node],
        edges=[]
    )
    profile = LearnerProfile(
        target_role="Fullstack Engineer",
        skills={},
        weekly_hours=10,
        learning_pace="medium"
    )
    
    res = await agent.verify_project(
        repo_url="https://github.com/octocat/Hello-World",
        node_id="fastapi_api",
        profile=profile,
        roadmap=roadmap
    )
    
    assert res.approved is True
    assert len(res.strengths) == 2
    assert "Missing unit tests" in res.weaknesses
