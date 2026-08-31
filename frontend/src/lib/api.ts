import { 
  LearnerProfile, 
  RoadmapResponse, 
  GenerateRoadmapResponse, 
  ExplainabilityResponse, 
  AdaptationResponse 
} from "./types";
import { createClient } from "./supabase/client";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

// Helper to get auth headers
async function getAuthHeaders() {
  const supabase = createClient();
  const { data: { session } } = await supabase.auth.getSession();
  
  if (!session) {
    throw new Error("No active session");
  }
  
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${session.access_token}`
  };
}

export const api = {
  async getActiveRoadmap(): Promise<GenerateRoadmapResponse> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${BASE_URL}/active-roadmap`, {
      method: "GET",
      headers,
    });
    
    if (!res.ok) {
      if (res.status === 404) {
        throw new Error("No active roadmap found");
      }
      throw new Error(`API error: ${res.statusText}`);
    }
    return res.json();
  },

  async generateRoadmap(userInput: string): Promise<GenerateRoadmapResponse> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${BASE_URL}/generate-roadmap`, {
      method: "POST",
      headers,
      body: JSON.stringify({ user_input: userInput }),
    });
    
    if (!res.ok) {
      throw new Error(`API error: ${res.statusText}`);
    }
    return res.json();
  },

  async explainNode(nodeId: string, profile: LearnerProfile, roadmap: RoadmapResponse): Promise<ExplainabilityResponse> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${BASE_URL}/explain-node`, {
      method: "POST",
      headers,
      body: JSON.stringify({ node_id: nodeId, profile, roadmap }),
    });
    
    if (!res.ok) {
      throw new Error(`API error: ${res.statusText}`);
    }
    return res.json();
  },

  async adaptRoadmap(
    roadmapId: string, 
    completedNodeId: string | null, 
    feedback: string | null, 
    currentProfile: LearnerProfile, 
    currentRoadmap: RoadmapResponse
  ): Promise<AdaptationResponse> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${BASE_URL}/adapt-roadmap`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        request: {
          roadmap_id: roadmapId,
          completed_node_id: completedNodeId,
          feedback: feedback
        },
        current_profile: currentProfile,
        current_roadmap: currentRoadmap
      }),
    });
    
    if (!res.ok) {
      throw new Error(`API error: ${res.statusText}`);
    }
    return res.json();
  },

  async recalibrateRoadmap(roadmap: RoadmapResponse): Promise<RoadmapResponse> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${BASE_URL}/roadmap/recalibrate`, {
      method: "POST",
      headers,
      body: JSON.stringify({ roadmap }),
    });
    
    if (!res.ok) {
      throw new Error(`API error: ${res.statusText}`);
    }
    return res.json();
  },

  async downloadCalendarSync(profile: LearnerProfile, roadmap: RoadmapResponse): Promise<void> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${BASE_URL}/calendar/sync`, {
      method: "POST",
      headers,
      body: JSON.stringify({ profile, roadmap }),
    });
    
    if (!res.ok) {
      throw new Error(`API error: ${res.statusText}`);
    }
    
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `roadmap_${roadmap.roadmap_id}.ics`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  },

  async getMyCohort(): Promise<any> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${BASE_URL}/cohort/me`, {
      method: "GET",
      headers,
    });
    
    if (!res.ok) {
      throw new Error(`API error: ${res.statusText}`);
    }
    return res.json();
  }
};
