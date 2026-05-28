from chromadb.utils import embedding_functions

from config import EMBEDDING_MODEL_NAME


def get_embedding_function():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL_NAME
    )