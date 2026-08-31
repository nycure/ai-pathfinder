from pydantic import BaseModel
from services.llm_client import LLMClient
from agents.roadmap_agent import RoadmapAgent
from models.schemas import (
    LearnerProfile, RoadmapResponse, AdaptationRequest, AdaptationResponse, SkillLevel
)
from database.client import supabase
from datetime import datetime, timezone

class ProfileUpdate(BaseModel):
    new_target_role: str

class AdaptationAgent:
    def __init__(self, llm_client: LLMClient = None, roadmap_agent: RoadmapAgent = None):
        self.llm_client = llm_client or LLMClient()
        self.roadmap_agent = roadmap_agent or RoadmapAgent()
        
        self.system_instruction = (
            "You are an AI learning path adapter. The user has provided feedback on their current learning path. "
            "Determine if their target career goal needs to change based on this feedback. "
            "Return the updated target role. If it shouldn't change, return the original target role."
        )

    def adapt_path(self, request: AdaptationRequest, current_profile: LearnerProfile, current_roadmap: RoadmapResponse, user_id: str = None) -> AdaptationResponse:
        """
        Adapts the roadmap based on user feedback or milestone completion.
        """
        changes_summary = []

        # Start with mutable copies of mutable fields
        updated_skills = dict(current_profile.skills)
        updated_target_role = current_profile.target_role
        
        # 1. Handle node completion
        if request.completed_node_id:
            node = next((n for n in current_roadmap.nodes if n.id == request.completed_node_id), None)
            if node:
                for skill in node.data.skills_acquired:
                    # FIX: Use SkillLevel enum instead of raw string
                    updated_skills[skill] = SkillLevel.BEGINNER
                changes_summary.append(f"Marked '{node.data.label}' as completed. Added skills to profile.")
                
                if user_id and supabase:
                    try:
                        supabase.table("milestone_progress").upsert({
                            "roadmap_id": current_roadmap.roadmap_id,
                            "node_id": node.id,
                            "status": "completed",
                            "completed_at": datetime.now(timezone.utc).isoformat()
                        }, on_conflict="roadmap_id,node_id").execute()
                    except Exception as e:
                        print(f"[Supabase Error] Failed to update milestone: {e}")
                
        # 2. Handle textual feedback
        if request.feedback:
            prompt = (
                f"Current Target Role: {current_profile.target_role}\n"
                f"User Feedback: \"{request.feedback}\"\n"
                f"What should their new target role be?"
            )
            
            response_json_str = self.llm_client.generate_structured_output(
                prompt=prompt,
                response_schema=ProfileUpdate,
                system_instruction=self.system_instruction
            )
            update_data = ProfileUpdate.model_validate_json(response_json_str)
            
            if update_data.new_target_role != current_profile.target_role:
                changes_summary.append(
                    f"Changed target role from '{current_profile.target_role}' "
                    f"to '{update_data.new_target_role}' based on feedback."
                )
                updated_target_role = update_data.new_target_role

        # FIX: Use model_copy to safely produce an updated profile without mutating the original
        updated_profile = current_profile.model_copy(update={
            "skills": updated_skills,
            "target_role": updated_target_role
        })
                
        # 3. Regenerate Roadmap with the updated profile
        if not changes_summary:
            changes_summary.append("No changes detected. Roadmap refreshed.")
            
        new_roadmap = self.roadmap_agent.generate_roadmap(updated_profile, user_id)
        
        return AdaptationResponse(
            updated_roadmap=new_roadmap,
            updated_profile=updated_profile,
            changes_made=" ".join(changes_summary)
        )
