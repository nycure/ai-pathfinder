from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, Any
from database.client import SUPABASE_JWT_SECRET

from agents.profiler_agent import ProfilerAgent
from agents.roadmap_agent import RoadmapAgent
from agents.xai_agent import XAIAgent
from agents.adaptation_agent import AdaptationAgent
from agents.tutor_agent import TutorAgent
from agents.quiz_agent import QuizAgent
from agents.github_verifier_agent import GitHubVerifierAgent
from agents.recalibration_agent import RecalibrationAgent
from services.calendar_service import CalendarService
from services.cohort_service import CohortService
from fastapi.responses import Response

from models.schemas import (
    LearnerProfile, RoadmapResponse, ExplainabilityResponse, 
    AdaptationRequest, AdaptationResponse, QuizResponse, GitHubVerificationResponse,
    CohortResponse, CohortMember
)

router = APIRouter(prefix="/api")

# DTOs for incoming requests
class GenerateRoadmapRequest(BaseModel):
    user_input: str

class ExplainNodeRequest(BaseModel):
    node_id: str
    profile: LearnerProfile
    roadmap: RoadmapResponse

class GenerateRoadmapResponse(BaseModel):
    profile: LearnerProfile
    roadmap: RoadmapResponse

# Combined DTO matching what api.ts sends for adaptation
class AdaptRoadmapRequest(BaseModel):
    request: AdaptationRequest
    current_profile: LearnerProfile
    current_roadmap: RoadmapResponse

class TutorChatRequest(BaseModel):
    messages: list[dict]
    node_id: str
    profile: LearnerProfile
    roadmap: RoadmapResponse

class QuizGenerateRequest(BaseModel):
    node_id: str
    profile: LearnerProfile
    roadmap: RoadmapResponse

class GitHubVerifyRequest(BaseModel):
    repo_url: str
    node_id: str
    profile: LearnerProfile
    roadmap: RoadmapResponse

class CalendarSyncRequest(BaseModel):
    profile: LearnerProfile
    roadmap: RoadmapResponse

class RecalibrateRequest(BaseModel):
    roadmap: RoadmapResponse

# Dependency Injection for Agents (allows easier testing/mocking)
def get_profiler() -> ProfilerAgent: return ProfilerAgent()
def get_roadmap_agent() -> RoadmapAgent: return RoadmapAgent()
def get_xai_agent() -> XAIAgent: return XAIAgent()
def get_adaptation_agent() -> AdaptationAgent: return AdaptationAgent()
def get_tutor_agent() -> TutorAgent: return TutorAgent()
def get_quiz_agent() -> QuizAgent: return QuizAgent()
def get_github_verifier_agent() -> GitHubVerifierAgent: return GitHubVerifierAgent()
def get_recalibration_agent() -> RecalibrationAgent: return RecalibrationAgent()

# Security Dependency
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    token = credentials.credentials
    try:
        from database.client import supabase
        if not supabase:
            raise HTTPException(status_code=500, detail="Database not configured")
        
        # Verify the ES256 token securely via the Supabase Auth API
        response = supabase.auth.get_user(token)
        if not response or not response.user:
            raise HTTPException(status_code=401, detail="Invalid token: User not found")
            
        return response.user.id
    except Exception as e:
        print(f"[Auth Error] Authentication failed: {e}")
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

import traceback

@router.get("/active-roadmap", response_model=GenerateRoadmapResponse)
async def get_active_roadmap(user_id: str = Depends(get_current_user)):
    from database.client import supabase
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    try:
        # Fetch active roadmap
        roadmap_res = supabase.table("roadmaps").select("*").eq("user_id", user_id).eq("is_active", True).execute()
        if not roadmap_res.data:
            raise HTTPException(status_code=404, detail="No active roadmap found")
            
        roadmap_data = roadmap_res.data[0]
        
        # Fetch profile
        profile_res = supabase.table("learner_profiles").select("*").eq("user_id", user_id).execute()
        if not profile_res.data:
            raise HTTPException(status_code=404, detail="Profile not found")
            
        profile_data = profile_res.data[0]
        
        # Reconstruct Profile
        profile = LearnerProfile(
            target_role=profile_data["target_role"],
            weekly_hours=profile_data["weekly_hours"],
            learning_pace=profile_data["learning_pace"],
            skills=profile_data["skills"]
        )
        
        # Reconstruct Roadmap
        roadmap = RoadmapResponse(
            roadmap_id=roadmap_data["id"],
            title=roadmap_data["title"],
            target_role=roadmap_data["target_role"],
            total_estimated_weeks=roadmap_data["total_estimated_weeks"],
            total_hours=roadmap_data["total_hours"],
            learner_summary=roadmap_data["learner_summary"],
            skill_gap_summary=roadmap_data["skill_gap_summary"],
            nodes=roadmap_data["graph_payload"]["nodes"],
            edges=roadmap_data["graph_payload"]["edges"]
        )
        
        return GenerateRoadmapResponse(profile=profile, roadmap=roadmap)
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

import traceback

@router.post("/generate-roadmap", response_model=GenerateRoadmapResponse)
async def generate_roadmap(
    request: GenerateRoadmapRequest,
    profiler: ProfilerAgent = Depends(get_profiler),
    roadmap_agent: RoadmapAgent = Depends(get_roadmap_agent),
    user_id: str = Depends(get_current_user)
):
    try:
        # 1. Profile User
        profile = profiler.extract_profile(request.user_input)
        
        # 2. Generate Roadmap
        roadmap = roadmap_agent.generate_roadmap(profile, user_id)
        
        return GenerateRoadmapResponse(profile=profile, roadmap=roadmap)
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()  # Print full stack trace to backend terminal
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/explain-node", response_model=ExplainabilityResponse)
async def explain_node(
    request: ExplainNodeRequest,
    xai_agent: XAIAgent = Depends(get_xai_agent),
    user_id: str = Depends(get_current_user)
):
    try:
        return xai_agent.explain_node(request.node_id, request.profile, request.roadmap)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/adapt-roadmap", response_model=AdaptationResponse)
async def adapt_roadmap(
    body: AdaptRoadmapRequest,
    adaptation_agent: AdaptationAgent = Depends(get_adaptation_agent),
    user_id: str = Depends(get_current_user)
):
    try:
        return adaptation_agent.adapt_path(body.request, body.current_profile, body.current_roadmap, user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tutor/chat")
async def tutor_chat_stream(
    request: TutorChatRequest,
    tutor: TutorAgent = Depends(get_tutor_agent),
    user_id: str = Depends(get_current_user)
):
    try:
        generator = tutor.stream_chat(request.messages, request.node_id, request.profile, request.roadmap)
        return StreamingResponse(generator, media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify/quiz/generate", response_model=QuizResponse)
async def generate_quiz(
    request: QuizGenerateRequest,
    quiz_agent: QuizAgent = Depends(get_quiz_agent),
    user_id: str = Depends(get_current_user)
):
    try:
        return quiz_agent.generate_quiz(request.node_id, request.profile, request.roadmap)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify/github", response_model=GitHubVerificationResponse)
async def verify_github(
    request: GitHubVerifyRequest,
    github_verifier: GitHubVerifierAgent = Depends(get_github_verifier_agent),
    user_id: str = Depends(get_current_user)
):
    try:
        return await github_verifier.verify_project(request.repo_url, request.node_id, request.profile, request.roadmap)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calendar/sync")
async def sync_calendar(
    request: CalendarSyncRequest,
    user_id: str = Depends(get_current_user)
):
    try:
        ics_content = CalendarService.generate_ics(request.roadmap, request.profile)
        return Response(
            content=ics_content,
            media_type="text/calendar",
            headers={"Content-Disposition": f"attachment; filename=roadmap_{request.roadmap.roadmap_id}.ics"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/roadmap/recalibrate", response_model=RoadmapResponse)
async def recalibrate_roadmap(
    request: RecalibrateRequest,
    recalibration_agent: RecalibrationAgent = Depends(get_recalibration_agent),
    user_id: str = Depends(get_current_user)
):
    try:
        return recalibration_agent.recalibrate_roadmap(request.roadmap)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/public/roadmap/{username}", response_model=GenerateRoadmapResponse)
async def get_public_roadmap(username: str):
    from database.client import supabase
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    try:
        # Find user by username
        user_res = supabase.table("users").select("id").eq("username", username).execute()
        if not user_res.data:
            raise HTTPException(status_code=404, detail="User not found")
        target_user_id = user_res.data[0]["id"]

        # Fetch active public roadmap
        roadmap_res = supabase.table("roadmaps").select("*").eq("user_id", target_user_id).eq("is_active", True).eq("is_public", True).execute()
        if not roadmap_res.data:
            raise HTTPException(status_code=404, detail="No public active roadmap found")
            
        roadmap_data = roadmap_res.data[0]
        
        # Fetch profile
        profile_res = supabase.table("learner_profiles").select("*").eq("user_id", target_user_id).execute()
        if not profile_res.data:
            raise HTTPException(status_code=404, detail="Profile not found")
            
        profile_data = profile_res.data[0]
        
        # Reconstruct Profile
        profile = LearnerProfile(
            target_role=profile_data["target_role"],
            weekly_hours=profile_data["weekly_hours"],
            learning_pace=profile_data["learning_pace"],
            skills=profile_data["skills"]
        )
        
        # Reconstruct Roadmap
        roadmap = RoadmapResponse(
            roadmap_id=roadmap_data["id"],
            title=roadmap_data["title"],
            target_role=roadmap_data["target_role"],
            total_estimated_weeks=roadmap_data["total_estimated_weeks"],
            total_hours=roadmap_data["total_hours"],
            learner_summary=roadmap_data["learner_summary"],
            skill_gap_summary=roadmap_data["skill_gap_summary"],
            nodes=roadmap_data["graph_payload"]["nodes"],
            edges=roadmap_data["graph_payload"]["edges"]
        )
        
        return GenerateRoadmapResponse(profile=profile, roadmap=roadmap)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cohort/match")
async def match_cohort(user_id: str = Depends(get_current_user)):
    return CohortService.match_new_cohort(user_id)

@router.get("/cohort/me", response_model=CohortResponse)
async def get_my_cohort(user_id: str = Depends(get_current_user)):
    return CohortService.get_or_match_cohort(user_id)
