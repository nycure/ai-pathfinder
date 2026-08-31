import json
import pytest
from unittest.mock import MagicMock
from agents.quiz_agent import QuizAgent
from models.schemas import LearnerProfile, RoadmapResponse, RoadmapNode, RoadmapNodeData, LearningResource, QuizResponse, QuizQuestion

def test_quiz_agent_generate_quiz():
    mock_llm = MagicMock()
    mock_quiz = QuizResponse(
        questions=[
            QuizQuestion(
                text="What is a Python list?",
                options=["An immutable tuple", "A mutable ordered sequence", "A hash set", "A binary tree"],
                correct_option_index=1,
                explanation="Lists in Python are mutable ordered sequences."
            ),
            QuizQuestion(
                text="Which keyword defines a function in Python?",
                options=["func", "function", "def", "lambda"],
                correct_option_index=2,
                explanation="The 'def' keyword defines functions."
            ),
            QuizQuestion(
                text="How do you add an element to a list?",
                options=["list.push()", "list.append()", "list.add()", "list.insert_end()"],
                correct_option_index=1,
                explanation="The 'append' method adds an item to the end of a list."
            )
        ]
    )
    mock_llm.generate_structured_output.return_value = mock_quiz.model_dump_json()
    
    agent = QuizAgent(llm_client=mock_llm)
    
    dummy_resource = LearningResource(
        id="doc_py",
        title="Python Documentation",
        provider="Python Software Foundation",
        url="https://docs.python.org",
        type="documentation",
        estimated_hours=5,
        cost="free",
        rating=4.9,
        skills_covered=["python_basics"]
    )
    
    node = RoadmapNode(
        id="python_basics",
        position={"x": 0.0, "y": 0.0},
        data=RoadmapNodeData(
            label="Python Basics",
            phase=1,
            phase_title="Foundations",
            description="Variables, loops, functions",
            status="in_progress",
            primary_resource=dummy_resource,
            alternative_resources=[],
            why_recommended="Core prerequisite",
            skills_acquired=["python_basics"],
            estimated_weeks=2,
            difficulty="beginner"
        )
    )
    roadmap = RoadmapResponse(
        roadmap_id="roadmap-123",
        title="AI Engineer Path",
        target_role="AI Engineer",
        total_estimated_weeks=12,
        total_hours=120,
        learner_summary="Beginner journey",
        skill_gap_summary=[],
        nodes=[node],
        edges=[]
    )
    profile = LearnerProfile(
        target_role="AI Engineer",
        skills={},
        weekly_hours=10,
        learning_pace="medium"
    )
    
    quiz_res = agent.generate_quiz("python_basics", profile, roadmap)
    assert len(quiz_res.questions) == 3
    assert quiz_res.questions[0].correct_option_index == 1
    assert quiz_res.questions[1].correct_option_index == 2
    mock_llm.generate_structured_output.assert_called_once()
