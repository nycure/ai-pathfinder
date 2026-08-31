export type SkillLevel = "beginner" | "intermediate" | "advanced";

export type ResourceType = "course" | "project" | "documentation" | "video" | "certification";

export type NodeStatus = "locked" | "available" | "in_progress" | "completed";

export interface LearnerProfile {
  target_role: string;
  skills: Record<string, SkillLevel>;
  weekly_hours: number;
  learning_pace: "slow" | "medium" | "fast";
}

export interface LearningResource {
  id: string;
  title: string;
  provider: string;
  url: string;
  type: ResourceType;
  estimated_hours: number;
  cost: "free" | "paid" | "freemium";
  rating: number;
  skills_covered: string[];
}

export interface RoadmapNodeData extends Record<string, unknown> {
  label: string;
  phase: number;
  phase_title: string;
  description: string;
  status: NodeStatus;
  primary_resource: LearningResource | null;
  alternative_resources: LearningResource[];
  practical_project?: string;
  why_recommended: string;
  skills_acquired: string[];
  estimated_weeks: number;
  difficulty: SkillLevel;
}

import { Node, Edge } from '@xyflow/react';

export type RoadmapNode = Node<RoadmapNodeData, "customMilestoneNode">;

export type RoadmapEdge = Edge;

export interface RoadmapResponse {
  roadmap_id: string;
  title: string;
  target_role: string;
  total_estimated_weeks: number;
  total_hours: number;
  learner_summary: string;
  skill_gap_summary: string[];
  nodes: RoadmapNode[];
  edges: RoadmapEdge[];
}

export interface GenerateRoadmapResponse {
  profile: LearnerProfile;
  roadmap: RoadmapResponse;
}

export interface ExplainabilityResponse {
  justification: string;
  missing_prerequisites_for_this_node: string[];
}

export interface AdaptationResponse {
  updated_roadmap: RoadmapResponse;
  updated_profile: LearnerProfile;
  changes_made: string;
}
