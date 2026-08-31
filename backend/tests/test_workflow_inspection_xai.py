import pytest
from unittest.mock import MagicMock
from agents.xai_agent import XAIAgent
from services.cache_service import CacheService
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
    ExplainabilityResponse
)

def test_workflow_2_milestone_inspection_and_xai_deep_dive_end_to_end():
    """
    Simulates Flow 2: Node Selection -> Inspector Drawer Mount -> XAI Explanation with Caching -> Resource Display
    """
    # 1. Setup mock LLM for XAI agent
    mock_llm = MagicMock()
    mock_xai_response = ExplainabilityResponse(
        justification="Transformers are the backbone of modern LLMs, which directly supports your goal of becoming an AI Engineer.",
        missing_prerequisites_for_this_node=["deep_learning", "neural_networks"]
    )
    mock_llm.generate_structured_output.return_value = mock_xai_response.model_dump_json()
    
    # 2. Setup Learner Profile and Active Roadmap
    profile = LearnerProfile(
        target_role="AI Engineer",
        skills={"python_basics": SkillLevel.INTERMEDIATE},
        weekly_hours=10,
        learning_pace="medium"
    )
    
    doc_resource = LearningResource(
        id="res_hf",
        title="Hugging Face Transformers Documentation",
        provider="Hugging Face",
        url="https://huggingface.co/docs/transformers",
        type=ResourceType.DOCUMENTATION,
        estimated_hours=6,
        cost="free",
        rating=4.9,
        skills_covered=["transformers_nlp"]
    )
    
    node = RoadmapNode(
        id="transformers_nlp",
        position={"x": 300, "y": 100},
        data=RoadmapNodeData(
            label="Transformers & LLMs",
            phase=3,
            phase_title="Advanced Topics",
            description="Attention mechanisms, BERT, and GPT architectures",
            status=NodeStatus.LOCKED,
            primary_resource=doc_resource,
            alternative_resources=[],
            why_recommended="Core milestone for LLMs",
            skills_acquired=["transformers_nlp"],
            estimated_weeks=3,
            difficulty=SkillLevel.ADVANCED
        )
    )
    
    roadmap = RoadmapResponse(
        roadmap_id="test_roadmap_xai",
        title="Path to AI Engineer",
        target_role="AI Engineer",
        total_estimated_weeks=12,
        total_hours=120,
        learner_summary="AI Engineer track",
        skill_gap_summary=["transformers_nlp"],
        nodes=[node],
        edges=[]
    )
    
    # 3. Instantiate XAI Agent
    xai_agent = XAIAgent(llm_client=mock_llm)
    
    # Clear cache for deterministic test
    CacheService().invalidate("xai_explain", node_id="transformers_nlp", target_role=profile.target_role, known_skills=list(profile.skills.keys()))
    
    # 4. User clicks milestone on canvas -> Drawer triggers explainNode
    explanation_1 = xai_agent.explain_node("transformers_nlp", profile, roadmap)
    
    # 5. Verify explanation output
    assert explanation_1.justification != ""
    assert "Transformers" in explanation_1.justification
    assert "deep_learning" in explanation_1.missing_prerequisites_for_this_node
    assert mock_llm.generate_structured_output.call_count == 1
    
    # 6. Second click / repeated drawer inspection -> Must serve from CacheService (0 additional LLM calls)
    explanation_2 = xai_agent.explain_node("transformers_nlp", profile, roadmap)
    assert explanation_2.justification == explanation_1.justification
    assert explanation_2.missing_prerequisites_for_this_node == explanation_1.missing_prerequisites_for_this_node
    assert mock_llm.generate_structured_output.call_count == 1  # Still 1, verified cache hit!
