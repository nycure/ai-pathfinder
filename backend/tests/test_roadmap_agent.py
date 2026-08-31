import os
import pytest
from agents.roadmap_agent import RoadmapAgent
from models.schemas import LearnerProfile

@pytest.mark.skipif(not os.environ.get("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")
def test_roadmap_agent_generation():
    agent = RoadmapAgent()
    
    # Mock a learner profile
    profile = LearnerProfile(
        target_role="I want to learn how to build large language models from scratch",
        skills={"python_basics": "beginner"},
        weekly_hours=10,
        learning_pace="medium"
    )
    
    response = agent.generate_roadmap(profile)
    
    # Since they want to build LLMs, the LLM should pick deep_learning or transformers as target
    # Because they know python_basics, it should be excluded, but linear_algebra, calculus etc should be included
    
    assert len(response.nodes) > 0
    
    # Check if python_basics is excluded
    node_ids = [n.id for n in response.nodes]
    assert "python_basics" not in node_ids
    
    # Verify structure of nodes
    for node in response.nodes:
        assert "x" in node.position
        assert "y" in node.position
        assert node.data.primary_resource is not None
        
    # Check if edges are created
    assert len(response.edges) > 0

def test_roadmap_agent_mocked_generation():
    from unittest.mock import MagicMock
    from models.schemas import DynamicTaxonomyResponse, DynamicNode, DynamicEdge
    
    mock_llm = MagicMock()
    mock_taxonomy = DynamicTaxonomyResponse(
        nodes=[
            DynamicNode(id="math_foundations", name="Mathematics Foundations", description="Linear algebra and calculus"),
            DynamicNode(id="ml_fundamentals", name="Machine Learning Fundamentals", description="Supervised and unsupervised models"),
            DynamicNode(id="neural_networks", name="Neural Networks", description="Deep learning architectures")
        ],
        edges=[
            DynamicEdge(source="math_foundations", target="ml_fundamentals"),
            DynamicEdge(source="ml_fundamentals", target="neural_networks")
        ]
    )
    mock_llm.generate_structured_output.return_value = mock_taxonomy.model_dump_json()
    
    agent = RoadmapAgent(llm_client=mock_llm)
    
    profile = LearnerProfile(
        target_role="AI Engineer",
        skills={},
        weekly_hours=10,
        learning_pace="medium"
    )
    
    response = agent.generate_roadmap(profile)
    assert len(response.nodes) == 3
    assert len(response.edges) == 2
    assert response.nodes[0].data.phase == 1
    assert response.nodes[0].data.status == "available"
    assert response.nodes[1].data.phase == 2
    assert response.nodes[1].data.status == "locked"
    mock_llm.generate_structured_output.assert_called_once()

