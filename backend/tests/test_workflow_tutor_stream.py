import pytest
from unittest.mock import MagicMock
from agents.tutor_agent import TutorAgent
from models.schemas import (
    LearnerProfile,
    RoadmapResponse,
    RoadmapNode,
    RoadmapNodeData,
    LearningResource,
    SkillLevel,
    NodeStatus
)

def test_workflow_3_in_drawer_socratic_tutor_streaming_end_to_end():
    """
    Simulates Flow 3: Learner asks question in MilestoneChatTutor -> TutorAgent streams Socratic response
    """
    # 1. Setup mock LLM stream generator
    mock_llm = MagicMock()
    
    def fake_stream(messages, system_instruction=None):
        chunks = ["Attention ", "mechanisms ", "allow ", "models ", "to weigh ", "tokens ", "dynamically."]
        for chunk in chunks:
            yield chunk
            
    mock_llm.generate_chat_stream.side_effect = fake_stream
    
    # 2. Setup Learner Profile and Milestone Context
    profile = LearnerProfile(
        target_role="AI Engineer",
        skills={},
        weekly_hours=10,
        learning_pace="medium"
    )
    
    dummy_resource = LearningResource(
        id="res_tutor",
        title="Transformers Guide",
        provider="HF",
        url="https://huggingface.co",
        type="documentation",
        estimated_hours=5,
        cost="free",
        rating=5.0,
        skills_covered=["transformers_nlp"]
    )
    
    node = RoadmapNode(
        id="transformers_nlp",
        position={"x": 0, "y": 0},
        data=RoadmapNodeData(
            label="Transformers & LLMs",
            phase=3,
            phase_title="Advanced Topics",
            description="Self-attention and Transformer architectures",
            status=NodeStatus.IN_PROGRESS,
            primary_resource=dummy_resource,
            alternative_resources=[],
            why_recommended="Core AI skill",
            skills_acquired=["transformers_nlp"],
            estimated_weeks=2,
            difficulty=SkillLevel.ADVANCED
        )
    )
    
    roadmap = RoadmapResponse(
        roadmap_id="roadmap_tutor_test",
        title="Path to AI Engineer",
        target_role="AI Engineer",
        total_estimated_weeks=12,
        total_hours=120,
        learner_summary="AI Engineer Track",
        skill_gap_summary=["transformers_nlp"],
        nodes=[node],
        edges=[]
    )
    
    # 3. Instantiate Tutor Agent
    tutor_agent = TutorAgent(llm_client=mock_llm)
    
    # 4. User sends a message in MilestoneChatTutor
    chat_history = [
        {"role": "user", "content": "Can you explain how attention works?"}
    ]
    
    stream_generator = tutor_agent.stream_chat(
        messages=chat_history,
        node_id="transformers_nlp",
        profile=profile,
        roadmap=roadmap
    )
    
    # 5. Consume stream chunks as the frontend getReader() does
    accumulated_response = ""
    chunk_count = 0
    for chunk in stream_generator:
        accumulated_response += chunk
        chunk_count += 1
        
    assert chunk_count == 7
    assert accumulated_response == "Attention mechanisms allow models to weigh tokens dynamically."
    
    # 6. Verify that TutorAgent passed the milestone-specific Socratic instruction
    mock_llm.generate_chat_stream.assert_called_once()
    args, kwargs = mock_llm.generate_chat_stream.call_args
    system_instruction = kwargs.get("system_instruction") or (args[1] if len(args) > 1 else "")
    assert "Transformers & LLMs" in system_instruction
    assert "AI Engineer" in system_instruction
    assert "Socratic" in system_instruction

