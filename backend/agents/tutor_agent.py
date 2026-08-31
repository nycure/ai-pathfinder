import json
from services.llm_client import LLMClient
from models.schemas import LearnerProfile, RoadmapResponse

class TutorAgent:
    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()

    def stream_chat(
        self,
        messages: list[dict],
        node_id: str,
        profile: LearnerProfile,
        roadmap: RoadmapResponse
    ):
        """
        Streams a chat response back to the user, acting as a contextual tutor.
        """
        # Find the active node
        active_node = next((n for n in roadmap.nodes if n.id == node_id), None)
        if not active_node:
            yield "Error: Active node context not found."
            return

        # Build System Instruction
        system_instruction = f"""
You are the AI Pathfinder In-Drawer Tutor, an empathetic, Socratic technical mentor.
The learner is currently studying this specific milestone:
- Milestone Title: {active_node.data.label}
- Phase: {active_node.data.phase_title}
- Description: {active_node.data.description}
- Why Recommended: {active_node.data.why_recommended}

Learner Profile Context:
- Target Role: {profile.target_role}
- Weekly Hours: {profile.weekly_hours}
- Learning Pace: {profile.learning_pace}
- Current Skills: {json.dumps(profile.skills)}

Guidelines for your responses:
1. Be encouraging and practical. Use analogies where appropriate.
2. Answer the user's specific question but tie it back to their target role of {profile.target_role}.
3. Keep your answers relatively concise as this is a chat interface inside a side-drawer.
4. If they ask a question completely unrelated to the milestone, politely guide them back to the topic.
5. Format your output in Markdown.
"""

        # Call the streaming LLM client
        for chunk in self.llm_client.generate_chat_stream(messages, system_instruction):
            yield chunk
