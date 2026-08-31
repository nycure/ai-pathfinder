import pytest
from unittest.mock import MagicMock, AsyncMock
from agents.github_verifier_agent import GitHubVerifierAgent
from agents.adaptation_agent import AdaptationAgent
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
    GitHubVerificationResponse,
    AdaptationRequest
)

@pytest.mark.anyio
async def test_workflow_5_live_github_verification_and_capstone_mastery():
    """
    Simulates Flow 5: Learner submits GitHub repo -> Verifier Agent inspects tree & README -> Gemini Senior Review -> Passing Approval Unlocks Milestone
    """
    # 1. Setup mock HTTP client for GitHub API
    mock_http_client = MagicMock()
    
    # Mock tree response
    mock_tree_res = MagicMock()
    mock_tree_res.status_code = 200
    mock_tree_res.json.return_value = {
        "tree": [
            {"path": "app/main.py", "type": "blob"},
            {"path": "app/model.py", "type": "blob"},
            {"path": "tests/test_api.py", "type": "blob"},
            {"path": "Dockerfile", "type": "blob"},
            {"path": "requirements.txt", "type": "blob"}
        ]
    }
    
    # Mock readme response (base64 encoded "Transformer Service Readme")
    import base64
    mock_readme_res = MagicMock()
    mock_readme_res.status_code = 200
    mock_readme_res.json.return_value = {
        "content": base64.b64encode(b"# Transformers QA Microservice\nImplements HuggingFace pipelines with FastAPI.").decode("utf-8")
    }
    
    mock_http_client.get = AsyncMock(side_effect=[mock_tree_res, mock_readme_res])
    
    # 2. Setup mock LLM for GitHubVerifierAgent
    mock_llm = MagicMock()
    mock_verifier_output = GitHubVerificationResponse(
        approved=True,
        strengths=[
            "Clean separation between FastAPI endpoint handlers and PyTorch inference models",
            "Includes comprehensive unit tests in tests/test_api.py",
            "Containerized with a production-ready Dockerfile"
        ],
        weaknesses=[
            "Could add GPU quantization via ONNX runtime for sub-10ms latency"
        ],
        feedback_summary="Exceptional project structure! Perfectly demonstrates production LLM microservice patterns."
    )
    mock_llm.generate_structured_output.return_value = mock_verifier_output.model_dump_json()
    
    # 3. Setup Learner Profile and Initial Roadmap
    profile = LearnerProfile(
        target_role="AI Engineer",
        skills={},
        weekly_hours=10,
        learning_pace="medium"
    )
    
    dummy_resource = LearningResource(
        id="res_gh",
        title="Deploying HuggingFace Models",
        provider="HF",
        url="https://huggingface.co",
        type=ResourceType.DOCUMENTATION,
        estimated_hours=8,
        cost="free",
        rating=4.9,
        skills_covered=["transformers_nlp"]
    )
    
    node = RoadmapNode(
        id="transformers_nlp",
        position={"x": 0, "y": 0},
        data=RoadmapNodeData(
            label="Transformers & LLMs",
            phase=2,
            phase_title="Core Concepts",
            description="Build a live FastAPI Transformer model microservice",
            status=NodeStatus.AVAILABLE,
            primary_resource=dummy_resource,
            alternative_resources=[],
            practical_project="Build a REST API service with FastAPI",
            why_recommended="Demonstrates practical AI engineering capstone",
            skills_acquired=["transformers_nlp", "fastapi_deployment"],
            estimated_weeks=2,
            difficulty=SkillLevel.ADVANCED
        )
    )
    
    roadmap = RoadmapResponse(
        roadmap_id="roadmap_gh_test",
        title="Path to AI Engineer",
        target_role="AI Engineer",
        total_estimated_weeks=6,
        total_hours=60,
        learner_summary="AI Engineer Track",
        skill_gap_summary=["transformers_nlp"],
        nodes=[node],
        edges=[]
    )
    
    # 4. Instantiate GitHubVerifierAgent
    verifier_agent = GitHubVerifierAgent(llm_client=mock_llm, http_client=mock_http_client)
    
    # 5. Execute Repository Verification
    review_result = await verifier_agent.verify_project(
        repo_url="https://github.com/developer/transformers-qa-service",
        node_id="transformers_nlp",
        profile=profile,
        roadmap=roadmap
    )
    
    # 6. Verify Senior Engineer Review contents
    assert review_result.approved is True
    assert len(review_result.strengths) == 3
    assert len(review_result.weaknesses) == 1
    assert "FastAPI" in review_result.strengths[0]
    
    # 7. Step 2: Since approved == True, frontend dispatches completeNode -> AdaptationAgent
    mock_roadmap_agent = MagicMock()
    completed_node = node.model_copy(deep=True)
    completed_node.data.status = NodeStatus.COMPLETED
    
    mock_adapted_roadmap = RoadmapResponse(
        roadmap_id="roadmap_gh_test_v2",
        title="Path to AI Engineer",
        target_role="AI Engineer",
        total_estimated_weeks=4,
        total_hours=40,
        learner_summary="AI Engineer Track",
        skill_gap_summary=[],
        nodes=[completed_node],
        edges=[]
    )
    mock_roadmap_agent.generate_roadmap.return_value = mock_adapted_roadmap
    
    adaptation_agent = AdaptationAgent(llm_client=mock_llm, roadmap_agent=mock_roadmap_agent)
    
    adapt_result = adaptation_agent.adapt_path(
        request=AdaptationRequest(roadmap_id=roadmap.roadmap_id, completed_node_id="transformers_nlp"),
        current_profile=profile,
        current_roadmap=roadmap
    )
    
    # 8. Verify skills acquired and milestone status
    assert "transformers_nlp" in adapt_result.updated_profile.skills
    assert "fastapi_deployment" in adapt_result.updated_profile.skills
    assert adapt_result.updated_roadmap.nodes[0].data.status == NodeStatus.COMPLETED
