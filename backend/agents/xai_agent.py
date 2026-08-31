from services.llm_client import LLMClient
from services.cache_service import CacheService
from models.schemas import LearnerProfile, RoadmapResponse, ExplainabilityResponse

class XAIAgent:
    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()
        self.cache = CacheService()
        
        self.system_instruction = (
            "You are an AI learning path explainer. Your job is to provide transparency to the learner "
            "about WHY they need to learn a specific topic. Keep your explanations highly encouraging, "
            "succinct (2-3 sentences), and directly tied to their ultimate target goal."
        )

    def explain_node(self, node_id: str, profile: LearnerProfile, roadmap: RoadmapResponse) -> ExplainabilityResponse:
        """
        Generates an explanation for why a specific node is in the roadmap.
        """
        
        # Extract node details from roadmap
        target_node = next((n for n in roadmap.nodes if n.id == node_id), None)
        if not target_node:
            raise ValueError(f"Node {node_id} not found in the provided roadmap.")
            
        # Find immediate prerequisites (incoming edges)
        prerequisites = [edge.source for edge in roadmap.edges if edge.target == node_id]
        
        # Find what this node unlocks (outgoing edges)
        unlocks = [edge.target for edge in roadmap.edges if edge.source == node_id]
        
        prompt = (
            f"Learner's Ultimate Goal: {profile.target_role}\n"
            f"Node to Explain: {target_node.data.label} (ID: {node_id})\n"
            f"Direct Prerequisites for this node: {', '.join(prerequisites) if prerequisites else 'None'}\n"
            f"Skills this node unlocks next: {', '.join(unlocks) if unlocks else 'None'}\n\n"
            f"Write a short justification explaining why {target_node.data.label} is essential for achieving their goal."
        )
        
        # Check cache
        cache_key_kwargs = {"node_id": node_id, "target_role": profile.target_role}
        cached_response = self.cache.get("xai_explanation", **cache_key_kwargs)
        if cached_response:
            print("[CacheService] Cache HIT for xai_explanation")
            return ExplainabilityResponse.model_validate_json(cached_response)
        
        print("[CacheService] Cache MISS for xai_explanation")
        response_json_str = self.llm_client.generate_structured_output(
            prompt=prompt,
            response_schema=ExplainabilityResponse,
            system_instruction=self.system_instruction
        )
        
        # Save to cache
        self.cache.set("xai_explanation", response_json_str, ttl_seconds=86400, **cache_key_kwargs)
        
        return ExplainabilityResponse.model_validate_json(response_json_str)
