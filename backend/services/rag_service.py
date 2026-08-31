import json
import os
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional

from models.schemas import LearningResource, ResourceType

class RAGService:
    def __init__(self, catalog_path: str = None, persist_directory: str = None):
        if catalog_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            catalog_path = os.path.join(current_dir, "..", "data", "curated_resources.json")
        
        self.catalog_path = catalog_path
        
        # Initialize ChromaDB
        if persist_directory:
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            self.client = chromadb.Client() # Ephemeral for prototype
            
        self.collection_name = "learning_resources"
        
        # Using default sentence-transformers model all-MiniLM-L6-v2
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.ef
        )
        
        self._load_catalog()

    def _load_catalog(self):
        """Loads JSON catalog and upserts into ChromaDB."""
        if not os.path.exists(self.catalog_path):
            raise FileNotFoundError(f"Catalog file not found at {self.catalog_path}")
            
        with open(self.catalog_path, "r", encoding="utf-8") as f:
            resources = json.load(f)
            
        if not resources:
            return

        documents = []
        metadatas = []
        ids = []
        
        for res in resources:
            # Create a rich text representation for semantic search
            doc_text = f"Title: {res['title']}. Provider: {res['provider']}. Skills: {', '.join(res['skills_covered'])}"
            documents.append(doc_text)
            
            # Filter metadata to strings/ints/floats for ChromaDB
            meta = {
                "id": res["id"],
                "title": res["title"],
                "provider": res["provider"],
                "url": res["url"],
                "type": res["type"],
                "estimated_hours": res["estimated_hours"],
                "cost": res["cost"],
                "rating": res["rating"],
                # Chroma metadata doesn't support lists, store as comma-separated
                "skills_covered": ",".join(res["skills_covered"])
            }
            metadatas.append(meta)
            ids.append(res["id"])
            
        # Upsert in batch
        self.collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def find_best_resources(
        self, 
        skill_name: str, 
        difficulty_cap: str = None, 
        resource_type: str = None,
        limit: int = 3
    ) -> List[LearningResource]:
        """
        Semantic search for resources matching a skill or topic, with metadata filtering.
        """
        query_text = f"Learn {skill_name}"
        
        # Build where filter
        where_clause = {}
        if resource_type:
             where_clause["type"] = resource_type
             
        # Add difficulty logic here if we add difficulty to metadata, 
        # for now we rely on semantic matching and basic filters.
        
        results = self.collection.query(
            query_texts=[query_text],
            n_results=limit,
            where=where_clause if where_clause else None
        )
        
        matched_resources = []
        if not results['metadatas'] or not results['metadatas'][0]:
            return matched_resources
            
        for meta in results['metadatas'][0]:
            # Reconstruct LearningResource
            res = LearningResource(
                id=meta["id"],
                title=meta["title"],
                provider=meta["provider"],
                url=meta["url"],
                type=meta["type"],
                estimated_hours=meta["estimated_hours"],
                cost=meta["cost"],
                rating=meta["rating"],
                skills_covered=meta["skills_covered"].split(",")
            )
            matched_resources.append(res)
            
        return matched_resources
