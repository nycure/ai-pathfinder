import pytest
from services.calendar_service import CalendarService
from models.schemas import LearnerProfile, RoadmapResponse, RoadmapNode, RoadmapNodeData, LearningResource

def test_calendar_service_generate_ics():
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
            status="available",
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
    
    ics_content = CalendarService.generate_ics(roadmap, profile)
    assert "BEGIN:VCALENDAR" in ics_content
    assert "END:VCALENDAR" in ics_content
    assert "SUMMARY:Study: Python Basics" in ics_content
    assert "X-WR-CALNAME:AI Pathfinder: AI Engineer Path" in ics_content
