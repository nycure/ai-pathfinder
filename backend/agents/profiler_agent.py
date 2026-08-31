import json
from services.llm_client import LLMClient
from services.graph_engine import SkillGraphEngine
from models.schemas import LearnerProfile

class ProfilerAgent:
    def __init__(self, llm_client: LLMClient = None, graph_engine: SkillGraphEngine = None):
        self.llm_client = llm_client or LLMClient()
        # FIX: Load the taxonomy so we can pass exact valid skill IDs to Gemini
        self.graph = graph_engine or SkillGraphEngine()
        
        self.system_instruction = (
            "You are an expert technical career counselor and curriculum architect. "
            "Your job is to analyze a learner's conversational input and extract a structured profile. "
            "You MUST map their described skills ONLY to the exact skill IDs from the taxonomy provided in the prompt. "
            "Do not invent new skill IDs. If a skill they mention does not closely match any taxonomy ID, omit it. "
            "If they don't specify hours, default to 10. If they don't specify pace, default to 'medium'."
        )

    def extract_profile(self, user_input: str) -> LearnerProfile:
        """
        Takes raw natural language input and returns a validated LearnerProfile object.
        FIX: Includes the full taxonomy skill IDs in the prompt so Gemini maps skills
        to exact valid keys (e.g., 'python_basics' not 'python').
        """
        valid_skill_ids = list(self.graph.graph.nodes.keys())
        if valid_skill_ids:
            taxonomy_str = ", ".join(f'"{k}"' for k in valid_skill_ids)
            taxonomy_prompt = f"RECOMMENDED SKILL IDs (map mentioned skills to snake_case IDs):\n[{taxonomy_str}]\n\n"
        else:
            taxonomy_prompt = "Map any skills the user mentions into lowercase snake_case keys (e.g. 'python_basics', 'javascript', 'docker').\n\n"

        prompt = (
            f"Analyze the following user input and extract their learning profile.\n\n"
            f"USER INPUT: \"{user_input}\"\n\n"
            f"{taxonomy_prompt}"
            f"Extract target_role, skills map with SkillLevel (beginner/intermediate/advanced), weekly_hours (default 10 if not stated), and learning_pace (slow/medium/fast)."
        )
        
        response_json_str = self.llm_client.generate_structured_output(
            prompt=prompt,
            response_schema=LearnerProfile,
            system_instruction=self.system_instruction
        )
        
        # Parse the JSON string into the Pydantic model
        profile = LearnerProfile.model_validate_json(response_json_str)
        return profile
