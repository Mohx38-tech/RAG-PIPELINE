from chroma_store import query_chroma
from config import RETRIEVAL_K


def convert_cosine_distance_to_score(distance: float) -> float:
    """
    For cosine distance:
    lower distance = better match.
    score = 1 - distance.
    This is approximate semantic match score, not final accuracy.
    """
    score = (1 - distance) * 100
    score = max(0, min(100, score))
    return round(score, 2)


def retrieve_top_chunks(
    question: str,
    top_k: int = RETRIEVAL_K,
    subject: str | None = None,
    chapter: str | None = None,
    partition_key: str | None = None,
) -> list[dict]:
    results = query_chroma(
        question=question,
        top_k=top_k,
        subject=subject,
        chapter=chapter,
        partition_key=partition_key,
    )

    if not results.get("documents") or not results["documents"][0]:
        return []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    retrieved_chunks = []

    for rank, (document, metadata, distance) in enumerate(
        zip(documents, metadatas, distances),
        start=1,
    ):
        retrieved_chunks.append(
            {
                "rank": rank,
                "content": document,
                "metadata": metadata,
                "distance": distance,
                "score": convert_cosine_distance_to_score(distance),
            }
        )

    return retrieved_chunks


def main() -> None:
    question = input("Ask your question: ")

    results = retrieve_top_chunks(question)

    print("\nTop retrieved chunks:\n")

    for result in results:
        metadata = result["metadata"]

        print("=" * 80)
        print(f"Rank: {result['rank']}")
        print(f"Score: {result['score']}%")
        print(f"Subject: {metadata.get('subject')}")
        print(f"Chapter: {metadata.get('chapter_name')}")
        print(f"Partition Key: {metadata.get('partition_key')}")
        print(f"Source File: {metadata.get('source_file')}")
        print("-" * 80)
        print(result["content"][:1000])
        print()


if __name__ == "__main__":
    main()