import pytest
from services.resource_aggregator import ResourceAggregator
from models.schemas import LearningResource, ResourceType

def test_resource_aggregator_official_doc_match():
    aggregator = ResourceAggregator()
    resources = aggregator.fetch_resources("Python", phase_level=1)
    assert len(resources) >= 1
    assert any("Python" in r.title for r in resources)
    assert any(r.type == ResourceType.DOCUMENTATION for r in resources)

def test_resource_aggregator_multi_tier():
    aggregator = ResourceAggregator()
    # Level 5 includes research paper + project + doc/video
    resources = aggregator.fetch_resources("Machine Learning", phase_level=5)
    assert len(resources) >= 2
    types = [r.type for r in resources]
    assert ResourceType.VIDEO in types or ResourceType.DOCUMENTATION in types
