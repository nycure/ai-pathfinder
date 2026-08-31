import pytest
from unittest.mock import MagicMock
from agents.quiz_agent import QuizAgent
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
    QuizResponse,
    QuizQuestion,
    AdaptationRequest
)

def test_workflow_4_quiz_validation_and_mastery_progression_end_to_end():
    """
    Simulates Flow 4: Mark as Mastered -> Generate 3-Question Quiz -> Submit Passing Quiz -> Adapt Path & Unlock Next Milestone
    """
    # 1. Setup mock LLM for QuizAgent
    mock_llm_quiz = MagicMock()
    mock_quiz = QuizResponse(
        questions=[
            QuizQuestion(
                text="What is the primary function of self-attention in Transformers?",
                options=[
                    "It downsamples input images",
                    "It calculates dynamic weight coefficients between all tokens in a sequence",
                    "It compresses text into a single integer",
                    "It performs gradient descent"
                ],
                correct_option_index=1,
                explanation="Self-attention computes pairwise relationship scores across all sequence positions."
            ),
            QuizQuestion(
                text="Which embedding is added to word embeddings to preserve sequence order?",
                options=["Positional encoding", "Dropout layer", "Softmax encoding", "Convolutional kernel"],
                correct_option_index=0,
                explanation="Positional encodings inject positional information into permutation-invariant attention layers."
            ),
            QuizQuestion(
                text="Why are multi-head attention mechanisms used?",
                options=[
                    "To multiply execution latency",
                    "To allow the model to jointly attend to information from different representation subspaces",
                    "To replace neural network weights with static lookups",
                    "To encrypt token embeddings"
                ],
                correct_option_index=1,
                explanation="Multiple heads project queries, keys, and values into multiple subspace projections."
            )
        ]
    )
    mock_llm_quiz.generate_structured_output.return_value = mock_quiz.model_dump_json()
    
    # 2. Setup Learner Profile and Initial Roadmap with 2 milestones (one available, one locked)
    profile = LearnerProfile(
        target_role="AI Engineer",
        skills={},
        weekly_hours=10,
        learning_pace="medium"
    )
    
    mock_res_1 = LearningResource(
        id="r1", title="Transformers 101", provider="HF", url="http://hf.co",
        type=ResourceType.DOCUMENTATION, estimated_hours=5, cost="free", rating=5.0, skills_covered=["transformers_nlp"]
    )
    mock_res_2 = LearningResource(
        id="r2", title="RAG Mastery", provider="LangChain", url="http://langchain.com",
        type=ResourceType.DOCUMENTATION, estimated_hours=5, cost="free", rating=5.0, skills_covered=["rag_systems"]
    )
    
    node_1 = RoadmapNode(
        id="transformers_nlp",
        position={"x": 0, "y": 0},
        data=RoadmapNodeData(
            label="Transformers & LLMs",
            phase=1,
            phase_title="Core Concepts",
            description="Transformer architectures",
            status=NodeStatus.AVAILABLE,
            primary_resource=mock_res_1,
            alternative_resources=[],
            why_recommended="Prerequisite for RAG",
            skills_acquired=["transformers_nlp"],
            estimated_weeks=2,
            difficulty=SkillLevel.INTERMEDIATE
        )
    )
    
    node_2 = RoadmapNode(
        id="rag_systems",
        position={"x": 250, "y": 0},
        data=RoadmapNodeData(
            label="RAG & Vector Databases",
            phase=2,
            phase_title="Applied Systems",
            description="ChromaDB and LangChain",
            status=NodeStatus.LOCKED,
            primary_resource=mock_res_2,
            alternative_resources=[],
            why_recommended="Applied LLM specialization",
            skills_acquired=["rag_systems"],
            estimated_weeks=2,
            difficulty=SkillLevel.ADVANCED
        )
    )
    
    initial_roadmap = RoadmapResponse(
        roadmap_id="roadmap_quiz_test",
        title="Path to AI Engineer",
        target_role="AI Engineer",
        total_estimated_weeks=4,
        total_hours=40,
        learner_summary="AI Engineer Track",
        skill_gap_summary=["transformers_nlp", "rag_systems"],
        nodes=[node_1, node_2],
        edges=[RoadmapEdge(id="e1", source="transformers_nlp", target="rag_systems")]
    )
    
    # 3. Step 1: User opens quiz modal -> QuizAgent generates 3 questions
    quiz_agent = QuizAgent(llm_client=mock_llm_quiz)
    quiz_response = quiz_agent.generate_quiz("transformers_nlp", profile, initial_roadmap)
    
    assert len(quiz_response.questions) == 3
    assert quiz_response.questions[0].correct_option_index == 1
    assert quiz_response.questions[1].correct_option_index == 0
    assert quiz_response.questions[2].correct_option_index == 1
    
    # 4. Step 2: User answers 3/3 correctly -> completeNode triggers AdaptationAgent
    mock_roadmap_agent = MagicMock()
    
    # After completion, node_1 is completed, node_2 is unlocked (available)
    updated_node_1 = node_1.model_copy(deep=True)
    updated_node_1.data.status = NodeStatus.COMPLETED
    
    updated_node_2 = node_2.model_copy(deep=True)
    updated_node_2.data.status = NodeStatus.AVAILABLE
    
    adapted_roadmap = RoadmapResponse(
        roadmap_id="roadmap_quiz_test_v2",
        title="Path to AI Engineer",
        target_role="AI Engineer",
        total_estimated_weeks=2,
        total_hours=20,
        learner_summary="AI Engineer Track",
        skill_gap_summary=["rag_systems"],
        nodes=[updated_node_1, updated_node_2],
        edges=[]
    )
    mock_roadmap_agent.generate_roadmap.return_value = adapted_roadmap
    
    adaptation_agent = AdaptationAgent(llm_client=mock_llm_quiz, roadmap_agent=mock_roadmap_agent)
    
    adapt_request = AdaptationRequest(
        roadmap_id=initial_roadmap.roadmap_id,
        completed_node_id="transformers_nlp"
    )
    
    adapt_result = adaptation_agent.adapt_path(
        request=adapt_request,
        current_profile=profile,
        current_roadmap=initial_roadmap
    )
    
    # 5. Verify that profile has acquired the skill and changes summary is clear
    assert "transformers_nlp" in adapt_result.updated_profile.skills
    assert "Marked 'Transformers & LLMs' as completed" in adapt_result.changes_made
    
    # 6. Verify that downstream node is now unlocked in the returned roadmap
    node_map = {n.id: n for n in adapt_result.updated_roadmap.nodes}
    assert node_map["transformers_nlp"].data.status == NodeStatus.COMPLETED
    assert node_map["rag_systems"].data.status == NodeStatus.AVAILABLE
