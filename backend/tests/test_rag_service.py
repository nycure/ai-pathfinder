import pytest
from services.rag_service import RAGService
from models.schemas import ResourceType

@pytest.fixture
def rag_service():
    # Uses the default curated_resources.json and an ephemeral ChromaDB instance
    return RAGService()

def test_rag_service_initialization(rag_service):
    # Verify collection is created and populated
    assert rag_service.collection.count() > 0

def test_find_best_resources(rag_service):
    # Search for something known to be in the catalog
    results = rag_service.find_best_resources("python_basics", limit=2)
    
    assert len(results) > 0
    # The first result should ideally be the python course
    assert "python" in results[0].title.lower() or "python" in results[0].skills_covered[0].lower()

def test_find_best_resources_with_filter(rag_service):
    # Search specifically for a documentation resource
    results = rag_service.find_best_resources("fastapi_basics", resource_type="documentation", limit=1)
    
    assert len(results) == 1
    assert results[0].type == ResourceType.DOCUMENTATION
    assert "fastapi" in results[0].title.lower()
