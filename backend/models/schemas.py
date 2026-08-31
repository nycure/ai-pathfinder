from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict
from enum import Enum

class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ResourceType(str, Enum):
    COURSE = "course"
    PROJECT = "project"
    DOCUMENTATION = "documentation"
    VIDEO = "video"
    CERTIFICATION = "certification"

class NodeStatus(str, Enum):
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class LearnerProfile(BaseModel):
    target_role: str = Field(..., description="The ultimate career goal or target role of the learner.")
    skills: Dict[str, SkillLevel] = Field(..., description="Map of existing skills to their proficiency level.")
    weekly_hours: int = Field(..., description="Hours per week the learner can dedicate to studying.")
    learning_pace: Literal["slow", "medium", "fast"] = Field("medium", description="The preferred pace of learning.")

class LearningResource(BaseModel):
    id: str = Field(..., description="Unique identifier for the resource.")
    title: str = Field(..., description="Title of the learning resource.")
    provider: str = Field(..., description="Provider of the resource (e.g., Coursera, YouTube, GitHub).")
    url: str = Field(..., description="URL to access the resource.")
    type: ResourceType = Field(..., description="Type of the resource.")
    estimated_hours: int = Field(..., description="Estimated hours to complete the resource.")
    cost: Literal["free", "paid", "freemium"] = Field(..., description="Cost structure of the resource.")
    rating: float = Field(4.8, description="Rating of the resource out of 5.")
    skills_covered: List[str] = Field(..., description="List of skills covered by this resource.")

class RoadmapNodeData(BaseModel):
    label: str = Field(..., description="Display title of the milestone.")
    phase: int = Field(..., description="Phase index this milestone belongs to.")
    phase_title: str = Field(..., description="Title of the phase.")
    description: str = Field(..., description="Detailed description of what will be learned.")
    status: NodeStatus = Field(default=NodeStatus.LOCKED, description="Current completion status.")
    primary_resource: LearningResource = Field(..., description="The main recommended resource.")
    alternative_resources: List[LearningResource] = Field(default_factory=list, description="Alternative resources.")
    practical_project: Optional[str] = Field(None, description="Description of a hands-on project to validate learning.")
    why_recommended: str = Field(..., description="XAI explanation of why this is recommended.")
    skills_acquired: List[str] = Field(..., description="Skills acquired upon completion.")
    estimated_weeks: int = Field(..., description="Estimated weeks to complete this milestone.")
    difficulty: SkillLevel = Field(..., description="Overall difficulty level of the milestone.")

class RoadmapNode(BaseModel):
    id: str = Field(..., description="Unique node ID.")
    type: str = Field("customMilestoneNode", description="Node type for React Flow.")
    position: dict = Field(..., description="x and y coordinates for React Flow, e.g. {'x': 0, 'y': 0}.")
    data: RoadmapNodeData = Field(..., description="The content of the node.")

class RoadmapEdge(BaseModel):
    id: str = Field(..., description="Unique edge ID.")
    source: str = Field(..., description="Source node ID.")
    target: str = Field(..., description="Target node ID.")
    animated: bool = Field(False, description="Whether the edge is animated (active learning path).")
    style: Optional[dict] = Field(None, description="CSS styles for the edge.")
    label: Optional[str] = Field(None, description="Optional label for the edge.")

class RoadmapResponse(BaseModel):
    roadmap_id: str = Field(..., description="Unique ID for the generated roadmap.")
    title: str = Field(..., description="Title of the roadmap.")
    target_role: str = Field(..., description="The target role.")
    total_estimated_weeks: int = Field(..., description="Total estimated weeks to complete.")
    total_hours: int = Field(..., description="Total estimated hours.")
    learner_summary: str = Field(..., description="Summary of the learner's profile and goal.")
    skill_gap_summary: List[str] = Field(..., description="List of major skill gaps identified.")
    nodes: List[RoadmapNode] = Field(..., description="List of React Flow nodes.")
    edges: List[RoadmapEdge] = Field(..., description="List of React Flow edges.")

class AdaptationRequest(BaseModel):
    roadmap_id: str = Field(..., description="ID of the roadmap to adapt.")
    completed_node_id: Optional[str] = Field(None, description="ID of the node that was just completed or skipped.")
    feedback: Optional[str] = Field(None, description="Optional feedback from the user (e.g. 'too hard').")

class AdaptationResponse(BaseModel):
    updated_roadmap: RoadmapResponse = Field(..., description="The newly updated roadmap.")
    updated_profile: LearnerProfile = Field(..., description="The updated learner profile reflecting newly acquired skills and role changes.")
    changes_made: str = Field(..., description="Summary of changes made to the roadmap.")

class ExplainabilityResponse(BaseModel):
    justification: str = Field(..., description="A 2-3 sentence explanation of why this node is required for the user's goal.")
    missing_prerequisites_for_this_node: List[str] = Field(default_factory=list, description="List of prerequisite skills the user is missing before tackling this node.")

# --- Phase 2: Dynamic Taxonomy Generation ---

class DynamicNode(BaseModel):
    id: str = Field(..., description="Unique ID for this skill node (e.g. 'aws_iam'). Must be snake_case.")
    name: str = Field(..., description="Display name of the skill (e.g. 'AWS IAM & Security').")
    description: str = Field(..., description="Brief description of what this skill entails.")

class DynamicEdge(BaseModel):
    source: str = Field(..., description="The ID of the prerequisite skill node.")
    target: str = Field(..., description="The ID of the dependent skill node.")

class DynamicTaxonomyResponse(BaseModel):
    nodes: List[DynamicNode] = Field(..., description="List of generated skill nodes required for the goal.")
    edges: List[DynamicEdge] = Field(..., description="List of prerequisite relationships between the nodes.")

# --- Phase 4 Validation Schemas ---

class QuizQuestion(BaseModel):
    text: str = Field(description="The question text")
    options: list[str] = Field(description="Exactly 4 multiple choice options")
    correct_option_index: int = Field(description="0-indexed index of the correct option")
    explanation: str = Field(description="Explanation of why the answer is correct and others are wrong")

class QuizResponse(BaseModel):
    questions: list[QuizQuestion] = Field(description="List of exactly 3 questions")

class GitHubVerificationResponse(BaseModel):
    approved: bool = Field(description="True if the project meets the milestone requirements, False otherwise")
    strengths: list[str] = Field(description="List of 2-3 positive aspects of the codebase")
    weaknesses: list[str] = Field(description="List of 2-3 areas for improvement or missing requirements")
    feedback_summary: str = Field(description="A short, encouraging summary of the evaluation")

# --- Phase 6 Cohort Schemas ---

class CohortMember(BaseModel):
    username: str = Field(..., description="Username of the cohort peer")
    progress: int = Field(0, description="Percentage of milestones completed (0-100)")
    is_me: bool = Field(False, description="Whether this peer is the current user")

class CohortResponse(BaseModel):
    cohort_id: str = Field(..., description="Unique cohort ID")
    topic: str = Field(..., description="Topic or target role of the study cohort")
    members: List[CohortMember] = Field(default_factory=list, description="List of cohort peers and their progress")

class GenerateRoadmapResponse(BaseModel):
    profile: LearnerProfile = Field(..., description="The learner's profile.")
    roadmap: RoadmapResponse = Field(..., description="The synthesized curriculum roadmap.")


