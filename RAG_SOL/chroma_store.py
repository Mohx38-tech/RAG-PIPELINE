import chromadb

from config import CHROMA_DIR, COLLECTION_NAME, RETRIEVAL_K
from embedding_utilities import get_embedding_function


def get_chroma_collection():
    embedding_function = get_embedding_function()

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
        metadata={
            "description": "Local Chroma collection for grouped RAG POC",
            "hnsw:space": "cosine",
        },
    )

    return collection


def add_documents_to_chroma(
    ids: list[str],
    documents: list[str],
    metadatas: list[dict],
) -> None:
    collection = get_chroma_collection()

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )


def build_where_filter(
    subject: str | None = None,
    chapter: str | None = None,
    partition_key: str | None = None,
) -> dict | None:
    filters = []

    if subject and subject != "All":
        filters.append({"subject": subject})

    if chapter and chapter != "All":
        filters.append({"chapter_name": chapter})

    if partition_key and partition_key != "All":
        filters.append({"partition_key": partition_key})

    if not filters:
        return None

    if len(filters) == 1:
        return filters[0]

    return {"$and": filters}


def query_chroma(
    question: str,
    top_k: int = RETRIEVAL_K,
    subject: str | None = None,
    chapter: str | None = None,
    partition_key: str | None = None,
) -> dict:
    collection = get_chroma_collection()

    query_arguments = {
        "query_texts": [question],
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"],
    }

    where_filter = build_where_filter(
        subject=subject,
        chapter=chapter,
        partition_key=partition_key,
    )

    if where_filter:
        query_arguments["where"] = where_filter

    return collection.query(**query_arguments)