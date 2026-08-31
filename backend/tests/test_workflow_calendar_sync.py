import pytest
from services.calendar_service import CalendarService
from models.schemas import (
    LearnerProfile,
    RoadmapResponse,
    RoadmapNode,
    RoadmapNodeData,
    LearningResource,
    ResourceType,
    NodeStatus,
    SkillLevel
)

def test_workflow_8_calendar_schedule_export_end_to_end():
    """
    Simulates Flow 8: Learner clicks 'Add to Calendar' -> Backend generates RFC-5545 iCalendar ICS payload
    """
    # 1. Setup Learner Profile with 15 hours/week
    profile = LearnerProfile(
        target_role="AI Engineer",
        skills={},
        weekly_hours=15,
        learning_pace="medium"
    )
    
    # 2. Setup Roadmap with 2 milestones (one completed, one active/uncompleted)
    res_1 = LearningResource(
        id="r1", title="Python 101", provider="PSF", url="https://docs.python.org",
        type=ResourceType.DOCUMENTATION, estimated_hours=10, cost="free", rating=4.9, skills_covered=["python_basics"]
    )
    res_2 = LearningResource(
        id="r2", title="Deep Learning Book", provider="MIT", url="https://deeplearningbook.org",
        type=ResourceType.DOCUMENTATION, estimated_hours=20, cost="free", rating=4.8, skills_covered=["deep_learning"]
    )
    
    node_completed = RoadmapNode(
        id="python_basics",
        position={"x": 0, "y": 0},
        data=RoadmapNodeData(
            label="Python Fundamentals",
            phase=1,
            phase_title="Foundations",
            description="Syntax, functions, data structures",
            status=NodeStatus.COMPLETED,
            primary_resource=res_1,
            alternative_resources=[],
            why_recommended="Foundational prerequisite",
            skills_acquired=["python_basics"],
            estimated_weeks=2,
            difficulty=SkillLevel.BEGINNER
        )
    )
    
    node_active = RoadmapNode(
        id="deep_learning",
        position={"x": 200, "y": 0},
        data=RoadmapNodeData(
            label="Deep Learning Architectures",
            phase=2,
            phase_title="Core Concepts",
            description="Multi-layer perceptrons, backpropagation, and loss functions",
            status=NodeStatus.AVAILABLE,
            primary_resource=res_2,
            alternative_resources=[],
            why_recommended="Core AI Engineering pillar",
            skills_acquired=["deep_learning"],
            estimated_weeks=3,
            difficulty=SkillLevel.INTERMEDIATE
        )
    )
    
    roadmap = RoadmapResponse(
        roadmap_id="roadmap_cal_test",
        title="Path to AI Engineer",
        target_role="AI Engineer",
        total_estimated_weeks=5,
        total_hours=50,
        learner_summary="AI Engineer Track",
        skill_gap_summary=["deep_learning"],
        nodes=[node_completed, node_active],
        edges=[]
    )
    
    # 3. Generate ICS string via CalendarService
    ics_text = CalendarService.generate_ics(roadmap, profile)
    
    # 4. Verify RFC-5545 format compliance
    assert "BEGIN:VCALENDAR" in ics_text
    assert "VERSION:2.0" in ics_text
    assert "X-WR-CALNAME:AI Pathfinder: Path to AI Engineer" in ics_text
    assert "END:VCALENDAR" in ics_text
    
    # 5. Verify that completed node is excluded and active node is scheduled
    assert "Study: Python Fundamentals" not in ics_text  # Completed node skipped!
    assert "Study: Deep Learning Architectures" in ics_text
    
    # 6. Verify that 3 weeks of events were scheduled for the 3-week milestone
    event_count = ics_text.count("BEGIN:VEVENT")
    assert event_count == 3
    
    # 7. Verify that recommended resource link is embedded in descriptions
    assert "Deep Learning Book" in ics_text
    assert "https://deeplearningbook.org" in ics_text
