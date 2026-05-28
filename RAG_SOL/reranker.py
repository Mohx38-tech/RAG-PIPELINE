from sentence_transformers import CrossEncoder

from config import DISPLAY_OPTIONS, RERANKER_MODEL_NAME


_reranker_model = None


def get_reranker_model() -> CrossEncoder:
    global _reranker_model

    if _reranker_model is None:
        _reranker_model = CrossEncoder(RERANKER_MODEL_NAME)

    return _reranker_model


def normalize_scores(raw_scores: list[float]) -> list[float]:
    if not raw_scores:
        return []

    min_score = min(raw_scores)
    max_score = max(raw_scores)

    if max_score == min_score:
        return [85.0 for _ in raw_scores]

    normalized = []

    for score in raw_scores:
        value = 70 + ((score - min_score) / (max_score - min_score)) * 25
        normalized.append(round(value, 2))

    return normalized


def rerank_chunks(
    question: str,
    chunks: list[dict],
    top_n: int = DISPLAY_OPTIONS,
) -> list[dict]:
    if not chunks:
        return []

    model = get_reranker_model()

    pairs = [
        [question, chunk["content"]]
        for chunk in chunks
    ]

    raw_scores = model.predict(pairs)
    raw_scores = [float(score) for score in raw_scores]

    display_scores = normalize_scores(raw_scores)

    reranked = []

    for chunk, raw_score, display_score in zip(chunks, raw_scores, display_scores):
        updated_chunk = dict(chunk)
        updated_chunk["rerank_score"] = raw_score
        updated_chunk["match_score"] = display_score
        reranked.append(updated_chunk)

    reranked = sorted(
        reranked,
        key=lambda item: item["rerank_score"],
        reverse=True,
    )

    final_results = reranked[:top_n]

    for index, chunk in enumerate(final_results, start=1):
        chunk["rank"] = index

    return final_results