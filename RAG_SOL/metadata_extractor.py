from pathlib import Path

from config import DATA_DIR


def format_metadata_name(value: str) -> str:
    value = value.replace("_", " ").replace("-", " ").strip()
    return value.title()


def format_file_name(file_path: Path) -> str:
    clean_stem = format_metadata_name(file_path.stem)
    extension = file_path.suffix.lower()
    return f"{clean_stem}{extension}"


def extract_metadata(
    file_path: str | Path,
    chunk_index: int,
    total_chunks: int,
) -> dict:
    file_path = Path(file_path)

    try:
        relative_path = file_path.relative_to(DATA_DIR)
        parts = relative_path.parts
    except ValueError:
        relative_path = Path(file_path.name)
        parts = relative_path.parts

    # Case 1:
    # data/biology/biomolecule.txt
    # subject = biology
    # chapter = biomolecule
    if len(parts) == 2:
        subject_name = format_metadata_name(parts[0])
        chapter_name = format_metadata_name(file_path.stem)

    # Case 2:
    # data/biology/biomolecule/biomolecule.txt
    # subject = biology
    # chapter = biomolecule
    elif len(parts) >= 3:
        subject_name = format_metadata_name(parts[0])
        chapter_name = format_metadata_name(parts[1])

    else:
        subject_name = "General"
        chapter_name = format_metadata_name(file_path.stem)

    display_file_name = format_file_name(file_path)
    actual_file_name = file_path.name

    partition_key = f"{subject_name}/{chapter_name}/{display_file_name}"
    subject_group_key = subject_name
    chapter_group_key = f"{subject_name}/{chapter_name}"
    chunk_key = f"{partition_key}/chunk_{chunk_index}"

    return {
        "source_file": display_file_name,
        "actual_source_file": actual_file_name,
        "relative_path": str(relative_path),
        "file_type": file_path.suffix.lower(),

        "subject": subject_name,
        "subject_name": subject_name,
        "chapter_name": chapter_name,

        "partition_key": partition_key,
        "subject_group_key": subject_group_key,
        "chapter_group_key": chapter_group_key,
        "chunk_key": chunk_key,

        "chunk_index": chunk_index,
        "total_chunks": total_chunks,
    }