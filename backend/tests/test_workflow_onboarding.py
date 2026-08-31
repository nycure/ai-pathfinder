import pytest
from unittest.mock import MagicMock
from agents.profiler_agent import ProfilerAgent
from agents.roadmap_agent import RoadmapAgent
from services.graph_engine import SkillGraphEngine
from services.resource_aggregator import ResourceAggregator
from models.schemas import (
    LearnerProfile,
    DynamicTaxonomyResponse,
    DynamicNode,
    DynamicEdge,
    GenerateRoadmapResponse,
    NodeStatus,
    SkillLevel
)

def test_workflow_1_onboarding_to_graph_synthesis_end_to_end():
    """
    Simulates Flow 1: Conversational Onboarding -> Profiler -> Roadmap Synthesis -> Graph Engine -> Resource Aggregator -> Canvas Ready Graph
    """
    # 1. Mock the LLM calls for determinism
    mock_llm = MagicMock()
    
    # Profiler output
    mock_profile = LearnerProfile(
        target_role="AI Engineer",
        skills={"python_basics": SkillLevel.INTERMEDIATE},
        weekly_hours=12,
        learning_pace="medium"
    )
    
    # Dynamic taxonomy output
    mock_taxonomy = DynamicTaxonomyResponse(
        nodes=[
            DynamicNode(id="math_foundations", name="Mathematics for AI", description="Linear algebra and multivariate calculus"),
            DynamicNode(id="ml_algorithms", name="Classical Machine Learning", description="Scikit-learn, regression, decision trees"),
            DynamicNode(id="deep_learning", name="Deep Learning & PyTorch", description="Neural networks, backpropagation, CNNs"),
            DynamicNode(id="transformers_nlp", name="Transformers & LLMs", description="Attention mechanisms, BERT, GPT architectures"),
            DynamicNode(id="rag_systems", name="RAG & Vector Databases", description="ChromaDB, semantic search, LangChain")
        ],
        edges=[
            DynamicEdge(source="math_foundations", target="ml_algorithms"),
            DynamicEdge(source="ml_algorithms", target="deep_learning"),
            DynamicEdge(source="deep_learning", target="transformers_nlp"),
            DynamicEdge(source="transformers_nlp", target="rag_systems")
        ]
    )
    
    mock_llm.generate_structured_output.side_effect = [
        mock_profile.model_dump_json(),
        mock_taxonomy.model_dump_json()
    ]
    
    # 2. Instantiate Agents
    profiler = ProfilerAgent(llm_client=mock_llm)
    roadmap_agent = RoadmapAgent(llm_client=mock_llm)
    
    # 3. Step 1: User enters raw text into GoalChat
    user_input = "I know some Python. I want to become an AI Engineer with 12 hours a week."
    extracted_profile = profiler.extract_profile(user_input)
    
    assert extracted_profile.target_role == "AI Engineer"
    assert extracted_profile.weekly_hours == 12
    assert "python_basics" in extracted_profile.skills
    
    # 4. Step 2: RoadmapAgent synthesizes the DAG
    roadmap = roadmap_agent.generate_roadmap(extracted_profile)
    
    # 5. Verify the synthesized graph properties
    assert roadmap.target_role == "AI Engineer"
    assert len(roadmap.nodes) == 5
    assert len(roadmap.edges) == 4
    
    # Verify Topological sort and Phase progression
    node_map = {n.id: n for n in roadmap.nodes}
    assert node_map["math_foundations"].data.phase == 1
    assert node_map["math_foundations"].data.status == NodeStatus.AVAILABLE
    
    assert node_map["ml_algorithms"].data.phase == 2
    assert node_map["ml_algorithms"].data.status == NodeStatus.LOCKED
    
    assert node_map["deep_learning"].data.phase == 3
    assert node_map["transformers_nlp"].data.phase == 4
    assert node_map["rag_systems"].data.phase == 5
    
    # Verify 2D Layout Coordinates for React Flow
    for node in roadmap.nodes:
        assert "x" in node.position
        assert "y" in node.position
        assert isinstance(node.position["x"], (int, float))
        assert isinstance(node.position["y"], (int, float))
        # Verify primary and alternative learning resources attached
        assert node.data.primary_resource is not None
        assert node.data.primary_resource.url != ""
        assert len(node.data.skills_acquired) > 0
    
    # Verify Edges map correctly
    edge_pairs = [(e.source, e.target) for e in roadmap.edges]
    assert ("math_foundations", "ml_algorithms") in edge_pairs
    assert ("transformers_nlp", "rag_systems") in edge_pairs
    
    # 6. Verify Full DTO matches frontend expectations
    full_response = GenerateRoadmapResponse(profile=extracted_profile, roadmap=roadmap)
    assert full_response.roadmap.roadmap_id != ""
    assert full_response.profile.target_role == "AI Engineer"
