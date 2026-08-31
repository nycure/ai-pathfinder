import json
import uuid
import networkx as nx
from typing import List, Dict
from pydantic import BaseModel
from services.llm_client import LLMClient
from services.graph_engine import SkillGraphEngine
from services.rag_service import RAGService
from services.cache_service import CacheService
from services.resource_aggregator import ResourceAggregator
from models.schemas import (
    LearnerProfile, 
    RoadmapResponse, 
    RoadmapNode,
    RoadmapNodeData, 
    RoadmapEdge,
    LearningResource,
    ResourceType,
    NodeStatus,
    SkillLevel,
    DynamicTaxonomyResponse
)
from database.client import supabase

# Phase title mapping by index (0-based)
PHASE_TITLES = [
    "Foundations",
    "Core Concepts",
    "Applied Learning",
    "Advanced Topics",
    "Specialization",
    "Expert Level"
]

class RoadmapAgent:
    def __init__(self, llm_client: LLMClient = None, graph_engine: SkillGraphEngine = None, rag_service: RAGService = None):
        self.llm_client = llm_client or LLMClient()
        self.graph = graph_engine or SkillGraphEngine()
        self.rag = rag_service or RAGService()
        self.cache = CacheService()
        self.aggregator = ResourceAggregator()
        
        self.system_instruction = (
            "You are an expert technical curriculum designer. Your task is to generate a personalized, "
            "step-by-step learning path (a Directed Acyclic Graph) to help the user achieve their target role. "
            "You must generate 10 to 15 strict milestone skills required. Do not include skills the user already knows well. "
            "Return the nodes (skills) and edges (prerequisites). Node IDs must be lowercase snake_case."
        )

    def _generate_dynamic_graph(self, profile: LearnerProfile) -> DynamicTaxonomyResponse:
        existing_skills = [k for k, v in profile.skills.items()]
        
        prompt = (
            f"User Goal: {profile.target_role}\n"
            f"Weekly Commitment: {profile.weekly_hours} hours/week\n"
            f"Learning Pace: {profile.learning_pace}\n"
            f"Existing Skills (Do not include these in the learning path): {', '.join(existing_skills) if existing_skills else 'None'}\n\n"
            f"Generate a strict DAG of 10 to 15 milestone skills necessary to reach this goal. "
            f"Provide the 'nodes' (id, name, description) and the 'edges' (source, target) where source is a prerequisite for target."
        )
        
        # Check cache before making expensive LLM call
        cache_key_kwargs = {"target_role": profile.target_role, "existing_skills": existing_skills}
        cached_response = self.cache.get("dynamic_taxonomy", **cache_key_kwargs)
        if cached_response:
            print("[CacheService] Cache HIT for dynamic_taxonomy")
            return DynamicTaxonomyResponse.model_validate_json(cached_response)
        
        print("[CacheService] Cache MISS for dynamic_taxonomy")
        response_json_str = self.llm_client.generate_structured_output(
            prompt=prompt,
            response_schema=DynamicTaxonomyResponse,
            system_instruction=self.system_instruction
        )
        
        # Save to cache (TTL: 24 hours)
        self.cache.set("dynamic_taxonomy", response_json_str, ttl_seconds=86400, **cache_key_kwargs)
        
        return DynamicTaxonomyResponse.model_validate_json(response_json_str)

    def _normalize_profile_skills(self, profile: LearnerProfile) -> LearnerProfile:
        """
        Since we are using dynamic open-world graphs, we no longer need to strictly
        filter the user's existing skills against a static taxonomy.
        """
        return profile

    def _infer_difficulty(self, phase: int, total_phases: int) -> SkillLevel:
        """Infers difficulty from a node's phase position in the curriculum."""
        if total_phases <= 1:
            return SkillLevel.BEGINNER
        ratio = (phase - 1) / (total_phases - 1)
        if ratio <= 0.33:
            return SkillLevel.BEGINNER
        elif ratio <= 0.66:
            return SkillLevel.INTERMEDIATE
        else:
            return SkillLevel.ADVANCED

    def generate_roadmap(self, profile: LearnerProfile, user_id: str = None) -> RoadmapResponse:
        profile = self._normalize_profile_skills(profile)

        # 1. LLM dynamically generates the entire taxonomy for this specific user
        dynamic_taxonomy = self._generate_dynamic_graph(profile)
        
        if not dynamic_taxonomy.nodes:
            raise ValueError("LLM failed to generate a learning path.")

        # 2. Load it into the graph engine and enforce Acyclicity
        self.graph.load_dynamic_graph(dynamic_taxonomy.nodes, dynamic_taxonomy.edges)
        self.graph.ensure_acyclic()
        
        # 3. Topologically sort for learning order
        required_skills = list(self.graph.graph.nodes.keys())
        ordered_skills = self.graph.topological_sort(required_skills)
        
        # 4. Compute phases from topological generations
        subgraph = self.graph.graph.subgraph(ordered_skills)
        try:
            generations = list(nx.topological_generations(subgraph))
        except nx.NetworkXUnfeasible:
            generations = [set(ordered_skills)]

        total_phases = len(generations)

        # Build phase lookup maps
        skill_to_phase: Dict[str, int] = {}
        for gen_idx, generation in enumerate(generations):
            for skill_id in generation:
                skill_to_phase[skill_id] = gen_idx + 1  # 1-indexed

        # 5. Calculate React Flow coordinates
        coordinates = self.graph.calculate_node_coordinates(ordered_skills)
        
        # 6. Build personalized learner_summary from profile data
        existing_skill_count = len(profile.skills)
        learner_summary = (
            f"Targeting '{profile.target_role}', committing {profile.weekly_hours} hours/week "
            f"at a {profile.learning_pace} pace. "
            f"{'Starting from scratch' if existing_skill_count == 0 else f'Building on {existing_skill_count} existing skill(s)'}. "
            f"I have mapped out {len(ordered_skills)} critical milestones across {total_phases} learning phase(s) to get you there."
        )

        # 7. Build Nodes and Edges
        nodes = []
        edges = []
        
        for skill_id in ordered_skills:
            skill_node = self.graph.graph.nodes[skill_id]
            
            # Get actual phase and compute difficulty from phase position
            phase_num = skill_to_phase.get(skill_id, 1)
            phase_title = PHASE_TITLES[min(phase_num - 1, len(PHASE_TITLES) - 1)]
            difficulty = self._infer_difficulty(phase_num, total_phases)

            # Phase 7: Use ResourceAggregator instead of static RAG to fetch dynamic API resources
            resources = self.aggregator.fetch_resources(skill_node["name"], phase_level=phase_num)
            
            # Fallback resource if empty
            if not resources:
                resources = [LearningResource(
                    id=f"fallback_{skill_id}",
                    title=f"Learn {skill_node['name']}",
                    provider="Google",
                    url=f"https://google.com/search?q=learn+{skill_id.replace('_', '+')}+tutorial",
                    type=ResourceType.DOCUMENTATION,
                    estimated_hours=10,
                    cost="free",
                    rating=4.5,
                    skills_covered=[skill_id]
                )]



            # Determine initial status: first-phase nodes are AVAILABLE, rest LOCKED
            status = NodeStatus.AVAILABLE if phase_num == 1 else NodeStatus.LOCKED

            # Use the LLM-generated description
            node_desc = skill_node.get("description", f"Learn {skill_node['name']}")

            node_data = RoadmapNodeData(
                label=skill_node["name"],
                phase=phase_num,
                phase_title=phase_title,
                description=node_desc,
                status=status,
                primary_resource=resources[0],
                alternative_resources=resources[1:],
                why_recommended=f"{skill_node['name']} is a required {phase_title} skill that unlocks more advanced milestones on your path.",
                skills_acquired=[skill_id],
                estimated_weeks=2,
                difficulty=difficulty
            )
            
            node = RoadmapNode(
                id=skill_id,
                type="customMilestoneNode",
                position={"x": coordinates[skill_id]["x"], "y": coordinates[skill_id]["y"]},
                data=node_data
            )
            nodes.append(node)
            
        # Create Edges (only include edges where both source and target are in required list)
        for skill_id in ordered_skills:
            in_edges = self.graph.graph.in_edges(skill_id)
            for source, target in in_edges:
                if source in ordered_skills:
                    edge = RoadmapEdge(
                        id=f"e_{source}-{target}",
                        source=source,
                        target=target
                    )
                    edges.append(edge)
                    
        total_weeks = len(ordered_skills) * 2
        total_hours = len(ordered_skills) * 15
        
        roadmap_res = RoadmapResponse(
            roadmap_id=str(uuid.uuid4()),  # FIX: unique ID per generation
            title=f"Path to {profile.target_role}",
            target_role=profile.target_role,
            total_estimated_weeks=total_weeks,
            total_hours=total_hours,
            learner_summary=learner_summary,
            skill_gap_summary=ordered_skills,
            nodes=nodes, 
            edges=edges
        )
        
        # Persist to Supabase if authenticated
        if user_id and supabase:
            try:
                # Upsert learner profile
                supabase.table("learner_profiles").upsert({
                    "user_id": user_id,
                    "target_role": profile.target_role,
                    "weekly_hours": profile.weekly_hours,
                    "learning_pace": profile.learning_pace,
                    "skills": {k: v.value for k, v in profile.skills.items()}
                }, on_conflict="user_id").execute()
                
                # Invalidate old active roadmaps
                supabase.table("roadmaps").update({"is_active": False}).eq("user_id", user_id).execute()
                
                # Insert new roadmap
                graph_payload = {
                    "nodes": [n.model_dump() for n in roadmap_res.nodes],
                    "edges": [e.model_dump() for e in roadmap_res.edges]
                }
                
                # Use the generated ID
                supabase.table("roadmaps").insert({
                    "id": roadmap_res.roadmap_id,
                    "user_id": user_id,
                    "title": roadmap_res.title,
                    "target_role": roadmap_res.target_role,
                    "total_estimated_weeks": roadmap_res.total_estimated_weeks,
                    "total_hours": roadmap_res.total_hours,
                    "learner_summary": roadmap_res.learner_summary,
                    "skill_gap_summary": roadmap_res.skill_gap_summary,
                    "graph_payload": graph_payload,
                    "is_active": True
                }).execute()
                
            except Exception as e:
                print(f"[Supabase Error] Failed to persist roadmap: {e}")

        return roadmap_res
