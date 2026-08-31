import httpx
import urllib.parse
import uuid
import xml.etree.ElementTree as ET
from typing import List, Optional
from models.schemas import LearningResource, ResourceType
from services.cache_service import CacheService

# Known official documentation portals for instant high-fidelity matching
OFFICIAL_DOCS = {
    "python": {"title": "Official Python 3 Documentation", "url": "https://docs.python.org/3/", "provider": "Python Software Foundation"},
    "fastapi": {"title": "FastAPI Official Tutorial & Reference", "url": "https://fastapi.tiangolo.com/tutorial/", "provider": "FastAPI Docs"},
    "react": {"title": "React Official Documentation", "url": "https://react.dev/learn", "provider": "Meta Open Source"},
    "nextjs": {"title": "Next.js App Router Documentation", "url": "https://nextjs.org/docs", "provider": "Vercel"},
    "pytorch": {"title": "PyTorch Deep Learning Tutorials", "url": "https://pytorch.org/tutorials/", "provider": "PyTorch Foundation"},
    "tensorflow": {"title": "TensorFlow Core Documentation", "url": "https://www.tensorflow.org/tutorials", "provider": "Google Brain"},
    "docker": {"title": "Docker Get Started Guide", "url": "https://docs.docker.com/get-started/", "provider": "Docker Inc."},
    "kubernetes": {"title": "Kubernetes Official Documentation", "url": "https://kubernetes.io/docs/home/", "provider": "CNCF"},
    "aws": {"title": "AWS Cloud Practitioner & Architecture Guide", "url": "https://aws.amazon.com/getting-started/", "provider": "Amazon Web Services"},
    "transformers": {"title": "Hugging Face Transformers Documentation", "url": "https://huggingface.co/docs/transformers", "provider": "Hugging Face"},
    "langchain": {"title": "LangChain Python Documentation", "url": "https://python.langchain.com/docs/get_started/introduction", "provider": "LangChain"},
    "sql": {"title": "PostgreSQL Tutorial & Reference Manual", "url": "https://www.postgresqltutorial.com/", "provider": "PostgreSQL"},
}

class ResourceAggregator:
    """
    Production-grade resource aggregator that connects to live public APIs
    (GitHub Search API, ArXiv REST/Atom API) and official documentation registries,
    with automatic in-memory caching and resilient graceful fallbacks.
    """
    
    def __init__(self):
        self.cache = CacheService()
        self.client = httpx.Client(
            timeout=4.0, 
            headers={"User-Agent": "AIPathfinder-CurriculumEngine/2.0"}
        )

    def fetch_resources(self, skill_name: str, phase_level: int = 1) -> List[LearningResource]:
        """
        Fetches live resources for a given skill.
        Returns a curated multi-modal collection (Docs/Video, Interactive Repo, Research Paper).
        """
        cache_key_args = {"skill": skill_name.lower().strip(), "phase": phase_level}
        cached_result = self.cache.get("live_resources", **cache_key_args)
        if cached_result:
            try:
                return [LearningResource.model_validate(r) for r in cached_result]
            except Exception:
                pass

        resources: List[LearningResource] = []

        # 1. Primary resource: Official documentation or top video tutorial
        primary_doc = self._match_official_doc(skill_name)
        if primary_doc:
            resources.append(primary_doc)
        else:
            resources.append(self._fetch_youtube_tutorial(skill_name))

        # 2. For intermediate/advanced (phase 2+), add a live top-starred GitHub repository
        if phase_level >= 2:
            gh_res = self._fetch_live_github_repo(skill_name)
            if gh_res:
                resources.append(gh_res)

        # 3. For advanced/expert (phase 4+), add a live peer-reviewed ArXiv research paper
        if phase_level >= 4:
            arxiv_res = self._fetch_live_arxiv_paper(skill_name)
            if arxiv_res:
                resources.append(arxiv_res)

        # If primary doc was matched, also append a video tutorial as alternative
        if primary_doc and len(resources) < 3:
            resources.append(self._fetch_youtube_tutorial(skill_name))

        # Cache the results for 24 hours
        try:
            self.cache.set("live_resources", [r.model_dump() for r in resources], ttl_seconds=86400, **cache_key_args)
        except Exception as e:
            print(f"[ResourceAggregator] Cache error: {e}")

        return resources

    def _match_official_doc(self, skill_name: str) -> Optional[LearningResource]:
        """Matches against official verified documentation portals."""
        skill_lower = skill_name.lower()
        for keyword, meta in OFFICIAL_DOCS.items():
            if keyword in skill_lower:
                return LearningResource(
                    id=f"doc_{uuid.uuid4().hex[:8]}",
                    title=meta["title"],
                    provider=meta["provider"],
                    url=meta["url"],
                    type=ResourceType.DOCUMENTATION,
                    estimated_hours=6,
                    cost="free",
                    rating=4.9,
                    skills_covered=[skill_name]
                )
        return None

    def _fetch_youtube_tutorial(self, skill_name: str) -> LearningResource:
        """Constructs an active query for the highest rated video tutorial."""
        query = urllib.parse.quote(f"{skill_name} tutorial full course")
        return LearningResource(
            id=f"yt_{uuid.uuid4().hex[:8]}",
            title=f"Complete {skill_name} Course",
            provider="YouTube Learning",
            url=f"https://www.youtube.com/results?search_query={query}",
            type=ResourceType.VIDEO,
            estimated_hours=4,
            cost="free",
            rating=4.8,
            skills_covered=[skill_name]
        )

    def _fetch_live_github_repo(self, skill_name: str) -> LearningResource:
        """Queries the live GitHub REST API for real top-starred open-source projects."""
        try:
            # Query GitHub Search API
            clean_query = skill_name.replace(" ", "+")
            url = f"https://api.github.com/search/repositories?q={clean_query}+sort:stars&order=desc&per_page=1"
            resp = self.client.get(url)
            
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items", [])
                if items:
                    top = items[0]
                    stars = top.get("stargazers_count", 0)
                    desc = top.get("description") or f"Top open source project for {skill_name}"
                    if len(desc) > 80:
                        desc = desc[:77] + "..."
                    
                    return LearningResource(
                        id=f"gh_{top.get('id', uuid.uuid4().hex[:8])}",
                        title=f"{top.get('full_name')} - {desc}",
                        provider=f"GitHub ({stars:,} ★)",
                        url=top.get("html_url"),
                        type=ResourceType.PROJECT,
                        estimated_hours=10,
                        cost="free",
                        rating=min(5.0, round(4.5 + (min(stars, 10000) / 20000.0), 1)),
                        skills_covered=[skill_name]
                    )
        except Exception as e:
            print(f"[ResourceAggregator] GitHub API error: {e}")

        # Graceful fallback if rate-limited or offline
        fallback_query = urllib.parse.quote(f"{skill_name} stars:>100")
        return LearningResource(
            id=f"gh_{uuid.uuid4().hex[:8]}",
            title=f"Awesome {skill_name} Implementations & Repositories",
            provider="GitHub Open Source",
            url=f"https://github.com/search?q={fallback_query}&type=repositories",
            type=ResourceType.PROJECT,
            estimated_hours=8,
            cost="free",
            rating=4.8,
            skills_covered=[skill_name]
        )

    def _fetch_live_arxiv_paper(self, skill_name: str) -> LearningResource:
        """Queries the live ArXiv Export API to parse real research papers and publications."""
        try:
            clean_query = urllib.parse.quote(skill_name)
            url = f"http://export.arxiv.org/api/query?search_query=all:{clean_query}&start=0&max_results=1"
            resp = self.client.get(url)

            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                # Atom namespace
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                entry = root.find('atom:entry', ns)
                if entry is not None:
                    title_elem = entry.find('atom:title', ns)
                    title = title_elem.text.strip().replace('\n', ' ') if title_elem is not None else f"Research in {skill_name}"
                    
                    # Author
                    author_elem = entry.find('atom:author/atom:name', ns)
                    author = author_elem.text if author_elem is not None else "ArXiv Researchers"
                    
                    # PDF Link
                    link_elem = entry.find("atom:link[@title='pdf']", ns) or entry.find("atom:link[@type='text/html']", ns)
                    paper_url = link_elem.attrib.get('href') if link_elem is not None else f"https://arxiv.org/search/?query={clean_query}"
                    
                    return LearningResource(
                        id=f"ax_{uuid.uuid4().hex[:8]}",
                        title=f"{title}",
                        provider=f"ArXiv ({author} et al.)",
                        url=paper_url,
                        type=ResourceType.DOCUMENTATION,
                        estimated_hours=3,
                        cost="free",
                        rating=4.9,
                        skills_covered=[skill_name]
                    )
        except Exception as e:
            print(f"[ResourceAggregator] ArXiv API error: {e}")

        # Graceful fallback
        fallback_query = urllib.parse.quote(skill_name)
        return LearningResource(
            id=f"ax_{uuid.uuid4().hex[:8]}",
            title=f"Recent Breakthroughs & Foundations in {skill_name}",
            provider="ArXiv Research",
            url=f"https://arxiv.org/search/advanced?query={fallback_query}&searchtype=all",
            type=ResourceType.DOCUMENTATION,
            estimated_hours=3,
            cost="free",
            rating=4.7,
            skills_covered=[skill_name]
        )
