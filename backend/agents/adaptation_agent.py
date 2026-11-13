from pydantic import BaseModel
from services.llm_client import LLMClient
from agents.roadmap_agent import RoadmapAgent
from models.schemas import (
    LearnerProfile, RoadmapResponse, AdaptationRequest, AdaptationResponse, SkillLevel, NodeStatus
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
        
        # 1. Handle milestone completion (in-place progression)
        if request.completed_node_id:
            completed_node = next((n for n in current_roadmap.nodes if n.id == request.completed_node_id), None)
            if completed_node:
                # Mark target node as completed
                completed_node.data.status = NodeStatus.COMPLETED
                for skill in completed_node.data.skills_acquired:
                    updated_skills[skill] = SkillLevel.BEGINNER
                changes_summary.append(f"Marked '{completed_node.data.label}' as completed. Added skills to profile.")
                
                # Topological Unlock: Scan locked nodes and unlock them if all incoming prerequisites are completed
                node_map = {n.id: n for n in current_roadmap.nodes}
                for other_node in current_roadmap.nodes:
                    if other_node.data.status == NodeStatus.LOCKED:
                        incoming_prereqs = [e.source for e in current_roadmap.edges if e.target == other_node.id]
                        if incoming_prereqs and all(
                            node_map.get(pid) and node_map[pid].data.status == NodeStatus.COMPLETED 
                            for pid in incoming_prereqs
                        ):
                            other_node.data.status = NodeStatus.AVAILABLE
                            changes_summary.append(f"Unlocked downstream milestone '{other_node.data.label}'.")

                # Persist milestone progress and updated graph payload to Supabase
                if user_id and supabase:
                    try:
                        # 1. Upsert milestone progress record
                        supabase.table("milestone_progress").upsert({
                            "roadmap_id": current_roadmap.roadmap_id,
                            "node_id": completed_node.id,
                            "status": "completed",
                            "completed_at": datetime.now(timezone.utc).isoformat()
                        }, on_conflict="roadmap_id,node_id").execute()

                        # 2. Update existing active roadmap with updated node statuses in graph_payload
                        updated_payload = {
                            "nodes": [n.model_dump() for n in current_roadmap.nodes],
                            "edges": [e.model_dump() for e in current_roadmap.edges]
                        }
                        supabase.table("roadmaps").update({
                            "graph_payload": updated_payload
                        }).eq("id", current_roadmap.roadmap_id).execute()

                        # 3. Update learner profile skills
                        supabase.table("learner_profiles").upsert({
                            "user_id": user_id,
                            "skills": {k: v.value if hasattr(v, 'value') else str(v) for k, v in updated_skills.items()}
                        }, on_conflict="user_id").execute()
                    except Exception as e:
                        print(f"[Supabase Error] Failed to persist milestone completion: {e}")
                
        # 2. Handle qualitative feedback (Career Goal Pivot / Re-generation)
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

            updated_profile = current_profile.model_copy(update={
                "skills": updated_skills,
                "target_role": updated_target_role
            })

            new_roadmap = self.roadmap_agent.generate_roadmap(updated_profile, user_id)
            return AdaptationResponse(
                updated_roadmap=new_roadmap,
                updated_profile=updated_profile,
                changes_made=" ".join(changes_summary)
            )

        # If ONLY node completion occurred (no qualitative feedback), return current_roadmap updated in-place!
        updated_profile = current_profile.model_copy(update={
            "skills": updated_skills,
            "target_role": updated_target_role
        })

        if not changes_summary:
            changes_summary.append("No changes detected. Roadmap refreshed.")
            
        return AdaptationResponse(
            updated_roadmap=current_roadmap,
            updated_profile=updated_profile,
            changes_made=" ".join(changes_summary)
        )
