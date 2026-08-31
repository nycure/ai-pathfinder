import uuid
from typing import Dict, Any, List, Optional
from database.client import supabase
from models.schemas import CohortResponse

class CohortService:
    @staticmethod
    def get_or_match_cohort(user_id: str, target_role: Optional[str] = None) -> CohortResponse:
        """
        Retrieves the user's current cohort or matches them into an open cohort
        based on their target role. Computes real-time progress for all cohort members.
        """
        if not supabase:
            # Fallback if database is not initialized (e.g., unit test environments)
            return CohortResponse(
                cohort_id="local-cohort",
                topic=target_role or "Full-Stack AI Engineering",
                members=[{"username": "you", "progress": 0, "is_me": True}]
            )

        try:
            # 1. Check if user is already in a cohort
            membership_res = supabase.table("cohort_members").select("cohort_id").eq("user_id", user_id).execute()
            cohort_id = None
            
            if membership_res.data:
                cohort_id = membership_res.data[0]["cohort_id"]
            else:
                # 2. If no target_role provided, lookup the user's active profile or roadmap
                if not target_role:
                    profile_res = supabase.table("learner_profiles").select("target_role").eq("user_id", user_id).execute()
                    if profile_res.data and profile_res.data[0].get("target_role"):
                        target_role = profile_res.data[0]["target_role"]
                    else:
                        target_role = "General Tech Mastery"

                # 3. Find open cohort with matching target role and available capacity (< 8 members)
                open_cohorts_res = supabase.table("cohorts").select("id, topic, max_members, cohort_members(count)").eq("target_role", target_role).execute()
                
                selected_cohort_id = None
                for c in (open_cohorts_res.data or []):
                    # Check member count
                    member_count_res = supabase.table("cohort_members").select("id", count="exact").eq("cohort_id", c["id"]).execute()
                    count = member_count_res.count if member_count_res.count is not None else 0
                    if count < c.get("max_members", 8):
                        selected_cohort_id = c["id"]
                        break

                # 4. If no open cohort exists, create a new one
                if not selected_cohort_id:
                    new_cohort_id = str(uuid.uuid4())
                    supabase.table("cohorts").insert({
                        "id": new_cohort_id,
                        "topic": target_role,
                        "target_role": target_role,
                        "max_members": 8
                    }).execute()
                    selected_cohort_id = new_cohort_id

                # 5. Join the cohort
                supabase.table("cohort_members").insert({
                    "cohort_id": selected_cohort_id,
                    "user_id": user_id
                }).execute()
                cohort_id = selected_cohort_id

            # 6. Fetch Cohort Details
            cohort_data_res = supabase.table("cohorts").select("*").eq("id", cohort_id).execute()
            if not cohort_data_res.data:
                raise ValueError("Cohort not found")
            cohort_info = cohort_data_res.data[0]

            # 7. Fetch all members in this cohort
            members_res = supabase.table("cohort_members").select("user_id").eq("cohort_id", cohort_id).execute()
            cohort_member_ids = [m["user_id"] for m in (members_res.data or [])]

            members_list: List[Dict[str, Any]] = []

            for m_id in cohort_member_ids:
                # Get username from users table
                u_res = supabase.table("users").select("username, email").eq("id", m_id).execute()
                username = "learner"
                if u_res.data:
                    username = u_res.data[0].get("username") or u_res.data[0].get("email", "").split("@")[0] or "learner"

                # Calculate progress from active roadmap and milestone_progress
                progress_percent = 0
                roadmap_res = supabase.table("roadmaps").select("id, graph_payload").eq("user_id", m_id).eq("is_active", True).execute()
                if roadmap_res.data:
                    active_roadmap = roadmap_res.data[0]
                    total_nodes = len(active_roadmap.get("graph_payload", {}).get("nodes", []))
                    
                    if total_nodes > 0:
                        completed_res = supabase.table("milestone_progress").select("id", count="exact").eq("roadmap_id", active_roadmap["id"]).eq("status", "completed").execute()
                        completed_count = completed_res.count if completed_res.count is not None else 0
                        progress_percent = int(round((completed_count / total_nodes) * 100))

                members_list.append({
                    "username": username,
                    "progress": progress_percent,
                    "is_me": (m_id == user_id)
                })

            return CohortResponse(
                cohort_id=cohort_id,
                topic=cohort_info.get("topic", "Study Cohort"),
                members=members_list
            )

        except Exception as e:
            print(f"[CohortService Error] {e}")
            # Graceful recovery
            return CohortResponse(
                cohort_id="error-fallback",
                topic=target_role or "Study Cohort",
                members=[{"username": "you", "progress": 0, "is_me": True}]
            )

    @staticmethod
    def match_new_cohort(user_id: str, target_role: Optional[str] = None) -> Dict[str, Any]:
        """Leaves the current cohort if any and matches the user into a fresh cohort."""
        if not supabase:
            return {"status": "success", "message": "Matched to cohort (standalone mode)"}

        try:
            # Leave existing cohort
            supabase.table("cohort_members").delete().eq("user_id", user_id).execute()
            # Match new
            cohort = CohortService.get_or_match_cohort(user_id, target_role)
            return {"status": "success", "message": "Successfully matched to cohort", "cohort": cohort.model_dump()}
        except Exception as e:
            print(f"[CohortService match_new_cohort Error] {e}")
            return {"status": "error", "message": str(e)}
