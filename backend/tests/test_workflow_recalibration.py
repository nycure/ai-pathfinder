import pytest
from unittest.mock import MagicMock
from agents.recalibration_agent import RecalibrationAgent
from models.schemas import (
    RoadmapResponse,
    RoadmapNode,
    RoadmapNodeData,
    RoadmapEdge,
    LearningResource,
    ResourceType,
    NodeStatus,
    SkillLevel
)

def test_workflow_7_spaced_recalibration_and_absence_catchup_end_to_end():
    """
    Simulates Flow 7: Learner returns after absence -> Clicks Recalibrate -> RecalibrationAgent injects warmup refresher node & rewires DAG
    """
    # 1. Setup initial roadmap with 1 completed node and 1 available node
    mock_resource = LearningResource(
        id="r_pytorch",
        title="PyTorch Docs",
        provider="PyTorch",
        url="https://pytorch.org",
        type=ResourceType.DOCUMENTATION,
        estimated_hours=6,
        cost="free",
        rating=4.9,
        skills_covered=["pytorch_basics"]
    )
    
    node_completed = RoadmapNode(
        id="pytorch_basics",
        position={"x": 0, "y": 0},
        data=RoadmapNodeData(
            label="PyTorch Basics",
            phase=1,
            phase_title="Foundations",
            description="Tensors, autograd, and simple neural networks",
            status=NodeStatus.COMPLETED,
            primary_resource=mock_resource,
            alternative_resources=[],
            why_recommended="Prerequisite for deep learning",
            skills_acquired=["pytorch_basics"],
            estimated_weeks=2,
            difficulty=SkillLevel.BEGINNER
        )
    )
    
    node_target = RoadmapNode(
        id="transformers_nlp",
        position={"x": 300, "y": 0},
        data=RoadmapNodeData(
            label="Transformers & LLMs",
            phase=2,
            phase_title="Core Concepts",
            description="Self-attention mechanisms and HuggingFace models",
            status=NodeStatus.AVAILABLE,
            primary_resource=mock_resource,
            alternative_resources=[],
            why_recommended="Core AI Engineering milestone",
            skills_acquired=["transformers_nlp"],
            estimated_weeks=3,
            difficulty=SkillLevel.ADVANCED
        )
    )
    
    initial_roadmap = RoadmapResponse(
        roadmap_id="roadmap_recal_test",
        title="Path to AI Engineer",
        target_role="AI Engineer",
        total_estimated_weeks=5,
        total_hours=50,
        learner_summary="AI Engineer track",
        skill_gap_summary=["transformers_nlp"],
        nodes=[node_completed, node_target],
        edges=[RoadmapEdge(id="e1", source="pytorch_basics", target="transformers_nlp")]
    )
    
    # 2. Instantiate RecalibrationAgent with mock LLM
    mock_llm = MagicMock()
    mock_refresher_content = {
        "title": "Warmup & Recall: PyTorch Foundations",
        "description": "Quick 15-minute refresher on prerequisite concepts.",
        "key_review_topics": ["pytorch_basics"],
        "rationale": "Combating the Ebbinghaus forgetting curve with spaced retrieval practice."
    }
    import json
    mock_llm.generate_structured_output.return_value = json.dumps(mock_refresher_content)
    
    recalibration_agent = RecalibrationAgent(llm_client=mock_llm)
    
    # 3. Learner returns and clicks "Recalibrate" on LearnerDashboard
    recalibrated_roadmap = recalibration_agent.recalibrate_roadmap(initial_roadmap)
    
    # 4. Verify that a Refresher Node was injected
    node_ids = [n.id for n in recalibrated_roadmap.nodes]
    refresher_nodes = [n for n in recalibrated_roadmap.nodes if "refresher_" in n.id]
    assert len(refresher_nodes) == 1
    refresher_node = refresher_nodes[0]
    
    # Verify Refresher Node attributes
    assert "Warmup & Recall" in refresher_node.data.label
    assert refresher_node.data.status == NodeStatus.AVAILABLE
    assert refresher_node.data.difficulty == SkillLevel.BEGINNER
    assert refresher_node.data.primary_resource is not None
    
    # 5. Verify that the target node is now dependent on the refresher node
    edge_pairs = [(e.source, e.target) for e in recalibrated_roadmap.edges]
    assert (refresher_node.id, "transformers_nlp") in edge_pairs
    
    # 6. Verify that running recalibration again does not duplicate refresher nodes
    second_recalibration = recalibration_agent.recalibrate_roadmap(recalibrated_roadmap)
    refresher_count = sum(1 for n in second_recalibration.nodes if "refresher_" in n.id)
    assert refresher_count == 1

