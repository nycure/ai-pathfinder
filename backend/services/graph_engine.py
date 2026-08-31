import json
import os
import networkx as nx
from typing import List, Dict, Any, Tuple

class SkillGraphEngine:
    def __init__(self, taxonomy_path: str = None):
        if taxonomy_path is None:
            # Default to the data directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            taxonomy_path = os.path.join(current_dir, "..", "data", "skill_taxonomy.json")
            
        self.taxonomy_path = taxonomy_path
        self.graph = nx.DiGraph()
        self._load_taxonomy()

    def _load_taxonomy(self):
        """Loads the taxonomy JSON and builds the NetworkX Directed Graph."""
        if not os.path.exists(self.taxonomy_path):
            # Instead of failing, start with an empty graph if file doesn't exist
            # since we are moving to dynamic graphs in Phase 2
            return
            
        with open(self.taxonomy_path, "r") as f:
            data = json.load(f)
            
        for skill in data.get("skills", []):
            self.graph.add_node(skill["id"], **skill)
            
        for edge in data.get("edges", []):
            self.graph.add_edge(edge["source"], edge["target"])

    def load_dynamic_graph(self, nodes: List[Any], edges: List[Any]):
        """Loads a dynamically generated graph from LLM output, replacing the current graph."""
        self.graph.clear()
        
        for node in nodes:
            # node could be a dict or a Pydantic model (DynamicNode)
            node_dict = node if isinstance(node, dict) else node.model_dump()
            self.graph.add_node(node_dict["id"], **node_dict)
            
        for edge in edges:
            edge_dict = edge if isinstance(edge, dict) else edge.model_dump()
            # Ensure the source and target exist before adding the edge
            if edge_dict["source"] in self.graph and edge_dict["target"] in self.graph:
                self.graph.add_edge(edge_dict["source"], edge_dict["target"])

    def ensure_acyclic(self) -> bool:
        """
        Verifies that the graph is a Directed Acyclic Graph. 
        If cycles are found, automatically removes the necessary edges to break them.
        Returns True if cycles were removed, False if it was already acyclic.
        """
        cycles_removed = False
        while not nx.is_directed_acyclic_graph(self.graph):
            cycles_removed = True
            try:
                # Find one cycle and remove its last edge
                cycle = nx.find_cycle(self.graph)
                # cycle is a list of tuples like [('A', 'B'), ('B', 'C'), ('C', 'A')]
                edge_to_remove = cycle[-1]
                print(f"[GraphEngine] Cycle detected! Removing edge {edge_to_remove} to enforce DAG.")
                self.graph.remove_edge(*edge_to_remove)
            except nx.NetworkXNoCycle:
                break
        return cycles_removed

    def verify_acyclic(self) -> bool:
        """Returns True if the graph is a Directed Acyclic Graph (no circular dependencies)."""
        return nx.is_directed_acyclic_graph(self.graph)

    def get_prerequisite_chain(self, target_skills: List[str], current_skills: List[str] = None) -> List[str]:
        """
        Gets all prerequisite skills required to learn the target skills, 
        excluding those the user already has.
        """
        if current_skills is None:
            current_skills = []
            
        required_skills = set(target_skills)
        
        for target in target_skills:
            if target in self.graph:
                # nx.ancestors returns all nodes that have a path to target
                ancestors = nx.ancestors(self.graph, target)
                required_skills.update(ancestors)
                
        # Remove skills the user already has
        needed_skills = required_skills - set(current_skills)
        return list(needed_skills)

    def topological_sort(self, skills_subset: List[str]) -> List[str]:
        """
        Sorts a subset of skills topologically. 
        Ensures foundational skills come before dependent skills.
        """
        subgraph = self.graph.subgraph(skills_subset)
        if not nx.is_directed_acyclic_graph(subgraph):
            raise ValueError("The subgraph contains cycles and cannot be topologically sorted.")
            
        return list(nx.topological_sort(subgraph))

    def calculate_node_coordinates(self, skills_ordered: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Calculates simple (x, y) coordinates for React Flow rendering.
        Basic algorithm: Assigns X based on topological generation/layer, Y based on spacing.
        """
        coordinates = {}
        subgraph = self.graph.subgraph(skills_ordered)
        
        # Calculate topological generations (layers)
        try:
            generations = list(nx.topological_generations(subgraph))
        except nx.NetworkXUnfeasible:
             # Fallback if there are cycles (shouldn't happen with our checks)
             generations = [skills_ordered]

        x_spacing = 300
        y_spacing = 150
        
        for x_idx, generation in enumerate(generations):
            for y_idx, node_id in enumerate(generation):
                coordinates[node_id] = {
                    "x": x_idx * x_spacing,
                    # Center the Y axis slightly depending on how many nodes are in this generation
                    "y": (y_idx - len(generation)/2.0) * y_spacing
                }
                
        return coordinates
