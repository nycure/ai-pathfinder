import uuid
from typing import Optional, List
from pydantic import BaseModel, Field
from services.llm_client import LLMClient
from services.resource_aggregator import ResourceAggregator
from models.schemas import (
    RoadmapResponse, RoadmapNode, RoadmapEdge, RoadmapNodeData, 
    NodeStatus, SkillLevel, LearningResource, ResourceType
)

class RefresherContent(BaseModel):
    title: str = Field(..., description="Short, motivating warmup title, e.g. 'Warmup: Neural Net Basics'")
    description: str = Field(..., description="Actionable 2-3 sentence overview of prerequisite concepts to quickly review before proceeding.")
    key_review_topics: List[str] = Field(default_factory=list, description="2-3 specific prerequisite concepts to review")
    rationale: str = Field(..., description="Why this review ensures higher retention based on spaced repetition")

class RecalibrationAgent:
    """
    AI-powered spaced repetition recalibration agent.
    Analyzes where the user currently is in the roadmap and generates a personalized
    warmup milestone with genuine review resources before they resume complex milestones.
    """
    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()
        self.aggregator = ResourceAggregator()

    def recalibrate_roadmap(self, roadmap: RoadmapResponse) -> RoadmapResponse:
        """
        Recalibrates the roadmap by inserting an AI-synthesized Refresher node
        directly upstream of the active/available milestone.
        """
        # Find the active or next available node
        target_node = None
        target_idx = -1
        for i, node in enumerate(roadmap.nodes):
            if node.data.status in (NodeStatus.IN_PROGRESS, NodeStatus.AVAILABLE):
                target_node = node
                target_idx = i
                break
                
        if not target_node:
            return roadmap  # Entire roadmap completed or empty

        # Prevent duplicate refreshers
        if "refresher" in target_node.id:
            return roadmap

        # Identify immediate prerequisites for the target node
        prereq_nodes = [
            n for n in roadmap.nodes 
            if any(e.source == n.id and e.target == target_node.id for e in roadmap.edges)
        ]
        prereq_labels = [p.data.label for p in prereq_nodes]

        # Call Gemini to synthesize a customized review brief
        system_instruction = (
            "You are an expert cognitive learning scientist and technical curriculum architect. "
            "The learner is returning to continue their learning journey. Generate a short, high-impact "
            "warmup review to combat the Ebbinghaus forgetting curve before they tackle their next milestone."
        )

        prompt = f"""
Upcoming Target Milestone: {target_node.data.label}
Milestone Description: {target_node.data.description}
Prerequisites Learned: {', '.join(prereq_labels) if prereq_labels else 'Foundational concepts'}
Target Career Role: {roadmap.target_role}

Synthesize a 15-minute quick warmup module to activate their prior knowledge before starting {target_node.data.label}.
"""

        try:
            response_json_str = self.llm_client.generate_structured_output(
                prompt=prompt,
                response_schema=RefresherContent,
                system_instruction=system_instruction
            )
            refresher_content = RefresherContent.model_validate_json(response_json_str)
        except Exception as e:
            print(f"[RecalibrationAgent] Gemini fallback: {e}")
            refresher_content = RefresherContent(
                title=f"Warmup: {target_node.data.label} Foundations",
                description=f"Quick 15-minute refresher on prerequisite concepts before diving into {target_node.data.label}.",
                key_review_topics=prereq_labels or [target_node.data.label],
                rationale="Combating the Ebbinghaus forgetting curve with spaced retrieval practice."
            )

        refresher_id = f"refresher_{uuid.uuid4().hex[:8]}"

        # Fetch genuine live review resources for the prerequisite skills
        primary_skill = prereq_labels[0] if prereq_labels else target_node.data.label
        live_resources = self.aggregator.fetch_resources(primary_skill, phase_level=1)
        
        primary_res = live_resources[0] if live_resources else LearningResource(
            id=f"res_{refresher_id}",
            title=f"Quick Review: {primary_skill}",
            provider="AI Pathfinder Review",
            url=f"https://www.google.com/search?q={primary_skill.replace(' ', '+')}+cheat+sheet",
            type=ResourceType.DOCUMENTATION,
            estimated_hours=1,
            cost="free",
            rating=4.9,
            skills_covered=refresher_content.key_review_topics
        )

        # Position node visually ahead of the target node
        pos_x = target_node.position.get('x', 0)
        pos_y = target_node.position.get('y', 0) - 160

        refresher_data = RoadmapNodeData(
            label=refresher_content.title,
            phase=target_node.data.phase,
            phase_title=f"{target_node.data.phase_title} (Review)",
            description=refresher_content.description,
            status=NodeStatus.AVAILABLE,
            primary_resource=primary_res,
            alternative_resources=live_resources[1:],
            why_recommended=refresher_content.rationale,
            skills_acquired=refresher_content.key_review_topics,
            estimated_weeks=0,
            difficulty=SkillLevel.BEGINNER
        )

        refresher_node = RoadmapNode(
            id=refresher_id,
            position={'x': pos_x, 'y': pos_y},
            data=refresher_data
        )

        # Rewire DAG edges to route through the refresher node
        edges_to_target = [e for e in roadmap.edges if e.target == target_node.id]
        
        new_edges = []
        for e in roadmap.edges:
            if e in edges_to_target:
                e.target = refresher_id
            new_edges.append(e)

        # Connect refresher -> target_node
        new_edge = RoadmapEdge(
            id=f"edge_{refresher_id}_{target_node.id}",
            source=refresher_id,
            target=target_node.id,
            animated=True
        )
        new_edges.append(new_edge)

        # Insert node in list
        roadmap.nodes.insert(target_idx, refresher_node)
        roadmap.edges = new_edges

        # Lock target node until refresher is completed
        if target_node.data.status == NodeStatus.AVAILABLE:
            target_node.data.status = NodeStatus.LOCKED

        return roadmap
