# Step 4: Curated Resource Knowledge Base & RAG Search Service

## Component Overview
The Retrieval-Augmented Generation (RAG) Service acts as the content engine for the learning paths. It uses ChromaDB to embed and search through a curated JSON catalog of learning resources (courses, GitHub repositories, documentation, and videos).

## Architectural Purpose
Standard LLM generations can hallucinate course names or provide dead links. By using a RAG architecture:
1. **Verifiability**: We guarantee every recommended resource actually exists, has a valid URL, and is from a trusted provider (e.g., Coursera, MIT OCW, Hugging Face).
2. **Metadata Filtering**: We can filter semantic search results based on the learner's level (e.g., beginner vs. advanced) and budget constraints (free vs. paid).
3. **Pydantic Alignment**: The search results map perfectly onto the `LearningResource` Pydantic schema, ensuring downstream stability.

## Detailed Implementation Specifications
1. **`backend/data/curated_resources.json`**: 
   - A JSON array of resources containing properties that match the `LearningResource` schema.
2. **`backend/services/rag_service.py`**:
   - Contains the `RAGService` class.
   - `__init__()`: Initializes the ChromaDB ephemeral client.
   - `load_catalog()`: Reads the JSON catalog, generates embeddings (using a lightweight model like `all-MiniLM-L6-v2` via ChromaDB's default embedding function), and upserts them into a ChromaDB collection.
   - `find_best_resources(query, difficulty, limit)`: Performs a semantic vector search against the collection. It allows metadata filtering (e.g., filtering out advanced resources if the learner is a beginner).
   
## Verification
- Unit tests (`backend/tests/test_rag_service.py`) verify the catalog loads successfully into ChromaDB.
- Tests assert that semantic queries return relevant, correctly mapped `LearningResource` Pydantic objects.
