from services.llm_client import LLMClient
from services.cache_service import CacheService
from models.schemas import LearnerProfile, RoadmapResponse, QuizResponse

class QuizAgent:
    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()
        self.cache = CacheService()

    def generate_quiz(
        self, 
        node_id: str, 
        profile: LearnerProfile, 
        roadmap: RoadmapResponse, 
        force_refresh: bool = False,
        user_id: str = None
    ) -> QuizResponse:
        active_node = next((n for n in roadmap.nodes if n.id == node_id), None)
        if not active_node:
            raise ValueError("Node not found in roadmap.")

        cache_key_kwargs = {"node_id": node_id, "target_role": profile.target_role}
        
        # Check cache if not explicitly forcing a fresh retake
        if not force_refresh:
            cached_quiz_str = self.cache.get("quiz_v2", **cache_key_kwargs)
            if cached_quiz_str:
                print(f"[CacheService] Cache HIT for quiz_v2 (node: {node_id})")
                return QuizResponse.model_validate_json(cached_quiz_str)

        print(f"[CacheService] Generating quiz via AI (node: {node_id}, force_refresh={force_refresh})")
        system_instruction = (
            "You are an expert technical AI tutor. Your goal is to evaluate if a learner has genuinely mastered a specific topic. "
            "Generate exactly 3 multiple-choice questions that test their conceptual understanding. "
            "When writing questions that include code, always format the code with clean multi-line indentation "
            "using standard newlines (\\n) and enclose it in a markdown code block with the language identifier (e.g. ```javascript\\n...\\n```). "
            "Never compress code into a single line. Keep the introductory question prompt separated from the code block."
        )

        diff_str = active_node.data.difficulty.value if hasattr(active_node.data.difficulty, 'value') else str(active_node.data.difficulty)

        prompt = f"""
Learner Profile:
Target Role: {profile.target_role}
Experience Level: {diff_str}

Topic to Test:
Milestone Title: {active_node.data.label}
Description: {active_node.data.description}
Skills Acquired: {', '.join(active_node.data.skills_acquired)}

Generate exactly 3 multiple-choice questions to test the learner's understanding of this topic.
Ensure the questions are applied and conceptual, not just rote memorization.
Formatting Requirements:
1. If a question involves code, place the question prompt first, followed by a multi-line formatted code block using ```<language>\\n...\\n``` with proper indentation.
2. Options must be an array of exactly 4 strings. If an option refers to code identifiers, values, or errors, use single backticks (e.g. `undefined`, `TypeError`).
3. correct_option_index must be between 0 and 3.
4. explanation must clearly explain why the correct answer is right and why the others are wrong.
"""

        response_str = self.llm_client.generate_structured_output(
            prompt=prompt,
            response_schema=QuizResponse,
            system_instruction=system_instruction
        )
        
        # Save to cache (TTL: 24 hours)
        self.cache.set("quiz_v2", response_str, ttl_seconds=86400, **cache_key_kwargs)
        
        return QuizResponse.model_validate_json(response_str)
