import { create } from 'zustand';
import { LearnerProfile, RoadmapResponse } from '@/lib/types';
import { api } from '@/lib/api';

interface RoadmapState {
  profile: LearnerProfile | null;
  roadmap: RoadmapResponse | null;
  isLoading: boolean;
  error: string | null;
  activeNodeId: string | null;
  
  // Actions
  initializeState: () => Promise<void>;
  submitGoal: (userInput: string) => Promise<void>;
  completeNode: (nodeId: string) => Promise<void>;
  submitFeedback: (feedback: string) => Promise<void>;
  recalibrateRoadmap: () => Promise<void>;
  syncCalendar: () => Promise<void>;
  setActiveNode: (nodeId: string | null) => void;
  reset: () => void;
}

export const useRoadmapStore = create<RoadmapState>((set, get) => ({
  profile: null,
  roadmap: null,
  isLoading: false,
  error: null,
  activeNodeId: null,

  initializeState: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await api.getActiveRoadmap();
      set({ profile: data.profile, roadmap: data.roadmap, isLoading: false });
    } catch (err: any) {
      if (err.message === "No active roadmap found" || err.message === "No active session") {
        set({ isLoading: false, error: null }); // Normal empty state on startup
      } else {
        set({ error: err.message || "Failed to load roadmap", isLoading: false });
      }
    }
  },

  submitGoal: async (userInput: string) => {
    set({ isLoading: true, error: null });
    try {
      const data = await api.generateRoadmap(userInput);
      set({ profile: data.profile, roadmap: data.roadmap, isLoading: false });
    } catch (err: any) {
      console.error("Submit Goal Error:", err);
      set({ error: err.message || "Failed to generate roadmap", isLoading: false });
    }
  },

  completeNode: async (nodeId: string) => {
    const { profile, roadmap } = get();
    if (!profile || !roadmap) return;

    set({ isLoading: true, error: null });
    try {
      const data = await api.adaptRoadmap(roadmap.roadmap_id, nodeId, null, profile, roadmap);
      // FIX: Update both roadmap AND profile so completed skills are excluded from next adaptation
      set({ roadmap: data.updated_roadmap, profile: data.updated_profile, isLoading: false });
    } catch (err: any) {
      set({ error: err.message || "Failed to complete node", isLoading: false });
    }
  },

  submitFeedback: async (feedback: string) => {
    const { profile, roadmap } = get();
    if (!profile || !roadmap) return;

    set({ isLoading: true, error: null });
    try {
      const data = await api.adaptRoadmap(roadmap.roadmap_id, null, feedback, profile, roadmap);
      // FIX: Update profile too so new target_role is reflected in subsequent calls
      set({ roadmap: data.updated_roadmap, profile: data.updated_profile, isLoading: false });
    } catch (err: any) {
      set({ error: err.message || "Failed to adapt roadmap", isLoading: false });
    }
  },

  recalibrateRoadmap: async () => {
    const { roadmap } = get();
    if (!roadmap) return;

    set({ isLoading: true, error: null });
    try {
      const data = await api.recalibrateRoadmap(roadmap);
      set({ roadmap: data, isLoading: false });
    } catch (err: any) {
      set({ error: err.message || "Failed to recalibrate roadmap", isLoading: false });
    }
  },

  syncCalendar: async () => {
    const { profile, roadmap } = get();
    if (!profile || !roadmap) return;

    set({ isLoading: true, error: null });
    try {
      await api.downloadCalendarSync(profile, roadmap);
      set({ isLoading: false });
    } catch (err: any) {
      set({ error: err.message || "Failed to sync calendar", isLoading: false });
    }
  },

  setActiveNode: (nodeId: string | null) => {
    set({ activeNodeId: nodeId });
  },

  reset: () => {
    set({ profile: null, roadmap: null, activeNodeId: null, error: null });
  }
}));
