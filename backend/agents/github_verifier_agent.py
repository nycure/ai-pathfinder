import httpx
import base64
from urllib.parse import urlparse
from services.llm_client import LLMClient
from models.schemas import LearnerProfile, RoadmapResponse, GitHubVerificationResponse

class GitHubVerifierAgent:
    def __init__(self, llm_client: LLMClient = None, http_client: httpx.AsyncClient = None):
        self.llm_client = llm_client or LLMClient()
        self.http_client = http_client or httpx.AsyncClient(
            headers={"User-Agent": "AI-Pathfinder-Verifier/1.0"},
            timeout=15.0
        )

    async def verify_project(self, repo_url: str, node_id: str, profile: LearnerProfile, roadmap: RoadmapResponse) -> GitHubVerificationResponse:
        active_node = next((n for n in roadmap.nodes if n.id == node_id), None)
        if not active_node:
            raise ValueError("Node not found in roadmap.")

        # Parse owner and repo from URL
        try:
            path_parts = urlparse(repo_url).path.strip('/').split('/')
            if len(path_parts) < 2:
                raise ValueError("Invalid GitHub URL.")
            owner, repo = path_parts[0], path_parts[1]
        except Exception:
            raise ValueError("Invalid GitHub URL. Must be in format https://github.com/owner/repo")

        tree_str = "Could not fetch repository structure."
        readme_str = "Could not fetch README."

        try:
            # Fetch repository tree (shallow)
            tree_response = await self.http_client.get(f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1")
            if tree_response.status_code == 200:
                tree_data = tree_response.json()
                paths = [item["path"] for item in tree_data.get("tree", []) if item["type"] == "blob"]
                # Keep it concise for the LLM
                tree_str = "\n".join(paths[:100])
                if len(paths) > 100:
                    tree_str += "\n... (truncated)"

            # Fetch README
            readme_response = await self.http_client.get(f"https://api.github.com/repos/{owner}/{repo}/readme")
            if readme_response.status_code == 200:
                readme_data = readme_response.json()
                if readme_data.get("content"):
                    readme_str = base64.b64decode(readme_data["content"]).decode('utf-8')
                    # Truncate to save tokens
                    readme_str = readme_str[:5000]
        except Exception as e:
            print(f"Error fetching GitHub data: {e}")

        system_instruction = (
            "You are an expert Senior Software Engineer evaluating a junior developer's capstone project."
            "Assess the repository structure and README against the milestone requirements."
        )

        prompt = f"""
Milestone Requirements:
Title: {active_node.data.label}
Description: {active_node.data.description}
Expected Practical Project: {active_node.data.practical_project}

GitHub Repository Data:
Repository: {owner}/{repo}
--- File Structure ---
{tree_str}
--- README.md ---
{readme_str}

Evaluate if the project meets the milestone's requirements.
Generate a structured response with strengths, weaknesses, and a final approval decision.
"""

        response_str = self.llm_client.generate_structured_output(
            prompt=prompt,
            response_schema=GitHubVerificationResponse,
            system_instruction=system_instruction
        )
        
        return GitHubVerificationResponse.model_validate_json(response_str)
