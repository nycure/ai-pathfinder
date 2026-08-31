import pytest
from services.graph_engine import SkillGraphEngine

@pytest.fixture
def graph_engine():
    return SkillGraphEngine()

def test_graph_loaded_correctly(graph_engine):
    assert len(graph_engine.graph.nodes) > 0
    assert len(graph_engine.graph.edges) > 0
    # Check if a known node exists
    assert "python_basics" in graph_engine.graph.nodes

def test_verify_acyclic(graph_engine):
    assert graph_engine.verify_acyclic() is True

def test_get_prerequisite_chain(graph_engine):
    # To learn deep_learning, one needs calculus and machine_learning_basics
    # To learn machine_learning_basics, one needs python_basics and linear_algebra
    required = graph_engine.get_prerequisite_chain(["deep_learning"])
    
    assert "calculus" in required
    assert "machine_learning_basics" in required
    assert "python_basics" in required
    assert "linear_algebra" in required
    assert "deep_learning" in required

def test_get_prerequisite_chain_with_current_skills(graph_engine):
    # User already knows python and linear algebra
    current = ["python_basics", "linear_algebra"]
    required = graph_engine.get_prerequisite_chain(["deep_learning"], current)
    
    assert "calculus" in required
    assert "machine_learning_basics" in required
    assert "deep_learning" in required
    
    # Should be excluded
    assert "python_basics" not in required
    assert "linear_algebra" not in required

def test_topological_sort(graph_engine):
    skills = ["deep_learning", "machine_learning_basics", "python_basics"]
    sorted_skills = graph_engine.topological_sort(skills)
    
    # python_basics must come before machine_learning_basics
    idx_python = sorted_skills.index("python_basics")
    idx_ml = sorted_skills.index("machine_learning_basics")
    idx_dl = sorted_skills.index("deep_learning")
    
    assert idx_python < idx_ml
    assert idx_ml < idx_dl

def test_calculate_node_coordinates(graph_engine):
    skills = ["python_basics", "machine_learning_basics", "deep_learning"]
    coords = graph_engine.calculate_node_coordinates(skills)
    
    assert "python_basics" in coords
    assert "x" in coords["python_basics"]
    assert "y" in coords["python_basics"]
    
    # python_basics (generation 0) should have smaller X than deep_learning (generation 2)
    assert coords["python_basics"]["x"] < coords["deep_learning"]["x"]
