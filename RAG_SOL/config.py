from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "Data"
CHROMA_DIR = BASE_DIR / "chroma_db"

# New collection because metadata, grouping, embedding, and retrieval logic changed
COLLECTION_NAME = "rag_chroma_collection_v11"

# Embedding model for Chroma
EMBEDDING_MODEL_NAME = "all-mpnet-base-v2"

# Cross encoder reranker model
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Chunking settings
CHUNK_SIZE = 650
CHUNK_OVERLAP = 120

# Internal retrieval count from Chroma
RETRIEVAL_K = 12

# Final answer options shown to user
DISPLAY_OPTIONS = 3

SUPPORTED_EXTENSIONS = {".pdf", ".pptx", ".txt"}