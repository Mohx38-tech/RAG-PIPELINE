import hashlib
from pathlib import Path

from Loaders.pdf_loader import load_pdf
from Loaders.ppt_loader import load_pptx
from Loaders.txt_loader import load_txt
from chroma_store import add_documents_to_chroma
from chunker import chunk_text, clean_text
from config import DATA_DIR, SUPPORTED_EXTENSIONS
from metadata_extractor import extract_metadata


def load_file(file_path: Path) -> str:
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        return load_pdf(file_path)

    if suffix == ".pptx":
        return load_pptx(file_path)

    if suffix == ".txt":
        return load_txt(file_path)

    raise ValueError(f"Unsupported file type: {suffix}")


def get_supported_files() -> list[Path]:
    files = []

    for file_path in DATA_DIR.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(file_path)

    return sorted(files)

def create_chunk_id(file_path: Path, chunk_index: int, chunk_text_value: str) -> str:
    try:
        relative_path = file_path.relative_to(DATA_DIR)
    except ValueError:
        relative_path = file_path.name

    raw_id = f"{relative_path}_{chunk_index}_{chunk_text_value}"
    hash_id = hashlib.md5(raw_id.encode("utf-8")).hexdigest()

    clean_file_name = file_path.stem.replace(" ", "_")
    return f"{clean_file_name}_{chunk_index}_{hash_id[:10]}"


def ingest_documents() -> None:
    print("Starting document ingestion...")

    files = get_supported_files()

    if not files:
        print(f"No supported files found inside: {DATA_DIR}")
        return

    total_chunks = 0

    for file_path in files:
        print(f"\nProcessing: {file_path}")

        try:
            raw_text = load_file(file_path)
            cleaned_text = clean_text(raw_text)

            if not cleaned_text:
                print(f"Skipping empty file: {file_path.name}")
                continue

            chunks = chunk_text(cleaned_text)

            ids = []
            documents = []
            metadatas = []

            for index, chunk in enumerate(chunks):
                ids.append(create_chunk_id(file_path, index, chunk))
                documents.append(chunk)
                metadatas.append(
                    extract_metadata(
                        file_path=file_path,
                        chunk_index=index,
                        total_chunks=len(chunks),
                    )
                )

            add_documents_to_chroma(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )

            total_chunks += len(chunks)

            print(f"Stored {len(chunks)} chunks from {file_path.name}")

        except Exception as error:
            print(f"Error processing {file_path.name}: {error}")

    print("\nIngestion completed.")
    print(f"Total files processed: {len(files)}")
    print(f"Total chunks stored: {total_chunks}")


if __name__ == "__main__":
    ingest_documents()