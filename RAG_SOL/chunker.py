import re

from config import CHUNK_OVERLAP, CHUNK_SIZE


def remove_textbook_noise(text: str) -> str:
    # Remove exercises and summary sections because they create bad answer options
    text = re.split(r"\bEXERCISES\b", text, flags=re.IGNORECASE)[0]
    text = re.split(r"\bSUMMARY\b", text, flags=re.IGNORECASE)[0]

    return text


def clean_text(text: str) -> str:
    text = remove_textbook_noise(text)

    text = re.sub(r"---\s*Page\s*\d+\s*---", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"---\s*Slide\s*\d+\s*---", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"Reprint\s+\d{4}-\d{2}", " ", text, flags=re.IGNORECASE)

    # Remove repeated headers/footers
    text = re.sub(r"\bBIOLOGY\b", " ", text)
    text = re.sub(r"\bBIOMOLECULES\b", " ", text)

    # Remove table/figure captions and broken table text
    text = re.sub(r"TABLE\s+\d+\.\d+.*?(?=[A-Z][a-z])", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"Figure\s+\d+\.\d+.*?(?=[A-Z][a-z])", " ", text, flags=re.IGNORECASE)

    # Remove isolated page numbers
    text = re.sub(r"\s+\d{2,3}\s+", " ", text)

    text = text.replace("\x0c", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def split_into_sentences(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def build_overlap_sentences(sentences: list[str], max_overlap_chars: int) -> list[str]:
    overlap = []
    current_length = 0

    for sentence in reversed(sentences):
        if current_length + len(sentence) > max_overlap_chars:
            break

        overlap.insert(0, sentence)
        current_length += len(sentence)

    return overlap


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    sentences = split_into_sentences(text)

    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence)

        if current_length + sentence_length > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))

            overlap_sentences = build_overlap_sentences(
                current_chunk,
                max_overlap_chars=chunk_overlap,
            )

            current_chunk = overlap_sentences
            current_length = sum(len(item) for item in current_chunk)

        current_chunk.append(sentence)
        current_length += sentence_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks