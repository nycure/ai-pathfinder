import pytest
from services.cohort_service import CohortService
from models.schemas import CohortResponse

def test_cohort_service_standalone():
    # Tests that CohortService produces a valid CohortResponse even without external DB
    cohort = CohortService.get_or_match_cohort("test-user-123", "AI Engineer")
    assert isinstance(cohort, CohortResponse)
    assert cohort.topic is not None
    assert len(cohort.members) > 0
    assert cohort.members[0].username is not None

def test_cohort_service_match_new():
    res = CohortService.match_new_cohort("test-user-456", "DevOps Specialist")
    assert res["status"] in ("success", "error")
