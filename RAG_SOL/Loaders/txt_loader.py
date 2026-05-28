from pathlib import Path


def load_txt(file_path: str | Path) -> str:
    file_path = Path(file_path)

    return file_path.read_text(
        encoding="utf-8",
        errors="ignore",
    )