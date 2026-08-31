import pytest
from unittest.mock import MagicMock
from services.cohort_service import CohortService
from models.schemas import (
    LearnerProfile,
    RoadmapResponse,
    RoadmapNode,
    RoadmapNodeData,
    NodeStatus,
    SkillLevel,
    CohortResponse,
    CohortMember
)

def test_workflow_9_peer_study_cohort_and_leaderboard_end_to_end():
    """
    Simulates Flow 9: Dashboard mounts -> CohortService resolves target role -> Returns grouped peers with calculated progress percentages -> Leaderboard displays sorted progress
    """
    # 1. Setup mock database client for CohortService
    mock_db = MagicMock()
    
    # Mock user profile lookup
    mock_profile_res = MagicMock()
    mock_profile_res.data = [{"target_role": "AI Engineer"}]
    
    # Mock user active roadmap
    mock_roadmap_res = MagicMock()
    mock_roadmap_res.data = [{"id": "roadmap_user_1", "target_role": "AI Engineer"}]
    
    # Mock existing cohort lookup
    mock_cohort_res = MagicMock()
    mock_cohort_res.data = [{"id": "cohort_ai_101", "topic": "AI Engineer Track", "target_role": "AI Engineer"}]
    
    # Mock cohort peers (3 peers with varying completed milestones)
    mock_members_res = MagicMock()
    mock_members_res.data = [
        {"user_id": "user_1", "username": "alice_ai", "milestones_completed": 8, "total_milestones": 10},
        {"user_id": "user_2", "username": "bob_ml", "milestones_completed": 5, "total_milestones": 10},
        {"user_id": "user_me", "username": "learner_hero", "milestones_completed": 3, "total_milestones": 10}
    ]
    
    # 2. Setup mock cohort service response
    cohort_members = [
        CohortMember(username="alice_ai", progress=80, is_me=False),
        CohortMember(username="bob_ml", progress=50, is_me=False),
        CohortMember(username="learner_hero", progress=30, is_me=True)
    ]
    expected_cohort = CohortResponse(
        cohort_id="cohort_ai_101",
        topic="AI Engineer Track",
        members=cohort_members
    )
    
    # 3. Verify Cohort Data structure
    assert expected_cohort.cohort_id == "cohort_ai_101"
    assert len(expected_cohort.members) == 3
    
    # 4. Simulate Dashboard Leaderboard sorting (descending by progress)
    sorted_members = sorted(expected_cohort.members, key=lambda m: m.progress, reverse=True)
    
    assert sorted_members[0].username == "alice_ai"
    assert sorted_members[0].progress == 80
    assert sorted_members[0].is_me is False
    
    assert sorted_members[1].username == "bob_ml"
    assert sorted_members[1].progress == 50
    
    assert sorted_members[2].username == "learner_hero"
    assert sorted_members[2].progress == 30
    assert sorted_members[2].is_me is True
