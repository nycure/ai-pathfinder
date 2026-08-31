# Step 3: NetworkX DAG Prerequisite Engine

## Component Overview
The NetworkX Graph Engine provides the mathematical backbone for the learning path generator. It manages skills and their prerequisites as a Directed Acyclic Graph (DAG) using the `networkx` Python library.

## Architectural Purpose
Standard recommendation systems output flat lists of courses. In an educational context, learning topics must be strictly ordered (e.g., Linear Algebra *must* precede Deep Learning). By using a DAG, we mathematically guarantee that:
1. No circular dependencies exist (A requires B, B requires A).
2. Advanced skills are never scheduled before their foundational prerequisites.
3. The layout algorithm can assign predictable `(x, y)` coordinates for rendering in the React Flow frontend.

## Detailed Implementation Specifications
The implementation consists of two core files:
1. **`backend/data/skill_taxonomy.json`**: 
   - A JSON configuration file defining the global skill graph. It lists nodes (skills) and directed edges (prerequisites). For example: `"source": "python_basics", "target": "data_structures"`.
2. **`backend/services/graph_engine.py`**:
   - Contains the `SkillGraphEngine` class.
   - `build_graph()`: Initializes a `networkx.DiGraph()` and populates it from the taxonomy file.
   - `verify_acyclic()`: Checks `nx.is_directed_acyclic_graph(G)` to prevent logical errors in curriculum design.
   - `get_prerequisite_chain(target_skills, current_skills)`: Extracts all required ancestors (`nx.ancestors()`) for the target skills, excluding those the learner already possesses.
   - `topological_sort(subgraph)`: Outputs the final, linear or grouped sequence of milestones in valid chronological order.
   - `calculate_node_coordinates()`: Basic algorithm to assign phases (X-axis) and vertical spacing (Y-axis) for the frontend graph.

## Verification
- Unit tests (`backend/tests/test_graph_engine.py`) verify the DAG is acyclic.
- Tests assert that foundational skills always appear earlier in the topological sort than their dependent skills.
