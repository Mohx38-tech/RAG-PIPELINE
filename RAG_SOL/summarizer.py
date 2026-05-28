import re


BAD_PHRASES = [
    "dig a little deeper",
    "find out",
    "find and write",
    "can you attempt",
    "draw the structure",
    "exercise",
    "exercises",
    "question",
    "ball and stick",
    "commercially available",
    "what a loss of vegetation",
    "reprint",
    "table",
    "figure",
    "average composition",
    "diagrammatic representation",
    "component",
    "cellular mass",
    "primary and secondary metabolites",
]


FORMULA_NOISE_PATTERNS = [
    r"CH2OH",
    r"HOCH2",
    r"C\d+H\d+O\d+",
    r"\bHN\b",
    r"\bOH\b",
    r"COOH",
    r"\bR1\b",
    r"\bR2\b",
    r"\bR3\b",
    r"\bPO\b",
    r"NaCl",
    r"CaCO3",
    r"Adenine",
    r"Uracil",
    r"Glycerol",
    r"Triglyceride",
    r"Cholesterol",
    r"Phospholipid",
    r"Lecithin",
    r"Palmitic acid",
]


def clean_text_for_summary(text: str) -> str:
    text = re.sub(r"---\s*Page\s*\d+\s*---", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"---\s*Slide\s*\d+\s*---", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"Reprint\s+\d{4}-\d{2}", " ", text, flags=re.IGNORECASE)

    text = re.sub(r"\bBIOLOGY\b", " ", text)
    text = re.sub(r"\bBIOMOLECULES\b", " ", text)

    text = re.sub(r"\bTABLE\s+\d+\.\d+\b", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\bFigure\s+\d+\.\d+\b", " ", text, flags=re.IGNORECASE)

    text = re.sub(
        r"CH2OH.*?Diagrammatic representation.*?living tissues",
        " ",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    text = re.sub(
        r"Glycine.*?Nucleosides\s+Nucleotide",
        " ",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    text = re.sub(
        r"Average Composition of Cells.*?cellular mass",
        " ",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    text = text.replace("\x0c", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def split_sentences(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def is_bad_sentence(sentence: str) -> bool:
    lower_sentence = sentence.lower().strip()

    if "?" in lower_sentence:
        return True

    if re.match(r"^\d+\.", lower_sentence):
        return True

    if len(sentence.split()) < 7:
        return True

    if len(sentence.split()) > 65:
        return True

    for phrase in BAD_PHRASES:
        if phrase in lower_sentence:
            return True

    for pattern in FORMULA_NOISE_PATTERNS:
        if re.search(pattern, sentence, flags=re.IGNORECASE):
            return True

    symbol_count = sum(
        1 for char in sentence
        if char in "()[]{}=+-0123456789"
    )

    if symbol_count > 12:
        return True

    return False


def collect_clean_sentences(chunks: list[dict]) -> list[dict]:
    clean_items = []

    for chunk in chunks:
        content = clean_text_for_summary(chunk["content"])
        sentences = split_sentences(content)

        for position, sentence in enumerate(sentences):
            if is_bad_sentence(sentence):
                continue

            clean_items.append(
                {
                    "sentence": sentence,
                    "metadata": chunk["metadata"],
                    "match_score": chunk.get("match_score", 0),
                    "rank": chunk.get("rank", 999),
                    "position": position,
                }
            )

    return clean_items


def get_common_metadata(chunks: list[dict]) -> dict:
    best_chunk = max(chunks, key=lambda item: item.get("match_score", 0))
    return best_chunk["metadata"]


def get_source_files(chunks: list[dict]) -> list[str]:
    return sorted(
        {
            chunk["metadata"].get("source_file", "Unknown")
            for chunk in chunks
        }
    )


def get_partition_keys(chunks: list[dict]) -> list[str]:
    return sorted(
        {
            chunk["metadata"].get("partition_key", "unknown")
            for chunk in chunks
        }
    )


def is_micro_macro_question(question: str) -> bool:
    question_lower = question.lower()

    micro_terms = [
        "micromolecule",
        "micromolecules",
        "small biomolecule",
        "small biomolecules",
    ]

    macro_terms = [
        "macromolecule",
        "macromolecules",
        "biomacromolecule",
        "biomacromolecules",
    ]

    biomolecule_terms = [
        "biomolecule",
        "biomolecules",
    ]

    type_terms = [
        "type",
        "types",
        "kind",
        "kinds",
        "classification",
        "classify",
        "categories",
        "category",
    ]

    has_micro = any(term in question_lower for term in micro_terms)
    has_macro = any(term in question_lower for term in macro_terms)

    has_biomolecule = any(term in question_lower for term in biomolecule_terms)
    asks_types = any(term in question_lower for term in type_terms)

    # Case 1: direct comparison question
    if has_micro and has_macro:
        return True

    # Case 2: "What is biomolecule? Explain its types."
    if has_biomolecule and asks_types:
        return True

    return False

def build_micro_macro_answer_options(chunks: list[dict], max_options: int = 3) -> list[dict]:
    metadata = get_common_metadata(chunks)
    source_files = get_source_files(chunks)
    partition_keys = get_partition_keys(chunks)

    best_score = round(
        max(chunk.get("match_score", 0) for chunk in chunks),
        2,
    )
def is_biomolecule_types_question(question: str) -> bool:
    question_lower = question.lower()

    has_biomolecule = (
        "biomolecule" in question_lower
        or "biomolecules" in question_lower
    )

    asks_types = (
        "type" in question_lower
        or "types" in question_lower
        or "kind" in question_lower
        or "kinds" in question_lower
        or "classify" in question_lower
        or "classification" in question_lower
        or "categories" in question_lower
    )

    return has_biomolecule and asks_types


def build_biomolecule_types_options(chunks: list[dict], max_options: int = 3) -> list[dict]:
    metadata = get_common_metadata(chunks)
    source_files = get_source_files(chunks)
    partition_keys = get_partition_keys(chunks)

    best_score = round(
        max(chunk.get("match_score", 0) for chunk in chunks),
        2,
    )

    option_1_answer = """
**Biomolecules** are chemical compounds present in living organisms. They form the structural and functional basis of life and take part in processes such as growth, metabolism, storage of energy, heredity and enzyme action.

The major types of biomolecules are **micromolecules** and **macromolecules**. Micromolecules are small biomolecules such as amino acids, sugars, fatty acids, glycerol, nucleotides and nucleosides. Macromolecules are large biomolecules such as proteins, polysaccharides and nucleic acids.
""".strip()

    option_2_answer = """
Biomolecules are molecules found in living systems. They may be small simple molecules or large complex molecules.

**1. Micromolecules:** These have low molecular weight, usually less than about 1000 Da. They are generally present in the acid-soluble pool. Examples include amino acids, sugars, fatty acids, glycerol, nucleotides and nucleosides.

**2. Macromolecules:** These are large biomolecules found mainly in the acid-insoluble fraction. Examples include proteins, polysaccharides and nucleic acids. Lipids are also found in the macromolecular fraction because of their association with membranes, although they are not strictly macromolecules.
""".strip()

    option_3_answer = """
| Type of biomolecule | Meaning | Examples |
|---|---|---|
| Micromolecules | Small biomolecules with low molecular weight | Amino acids, sugars, fatty acids, glycerol, nucleotides, nucleosides |
| Macromolecules | Large biomolecules generally present in acid-insoluble fraction | Proteins, polysaccharides, nucleic acids |
| Special case | Lipids are found in the macromolecular fraction due to membrane association | Phospholipids, cholesterol, membrane lipids |
""".strip()

    styles = [
        ("Concise biomolecule answer", option_1_answer),
        ("Detailed biomolecule types answer", option_2_answer),
        ("Table-based biomolecule types answer", option_3_answer),
    ]

    options = []

    for style, answer in styles[:max_options]:
        options.append(
            {
                "group_key": metadata.get("partition_key", "unknown"),
                "answer": answer,
                "subject": metadata.get("subject", "general"),
                "chapter": metadata.get("chapter_name", "unknown"),
                "source_files": source_files,
                "partition_keys": partition_keys,
                "chunk_count": len(chunks),
                "match_score": best_score,
                "option_type": style,
            }
        )

    return options    



def score_sentence(sentence: str, keywords: list[str]) -> int:
    sentence_lower = sentence.lower()
    return sum(1 for keyword in keywords if keyword in sentence_lower)


def get_best_sentences(
    clean_items: list[dict],
    keywords: list[str],
    max_sentences: int,
) -> list[dict]:
    candidates = []

    for item in clean_items:
        score = score_sentence(item["sentence"], keywords)

        if score == 0:
            continue

        candidates.append(
            {
                **item,
                "score": score,
            }
        )

    candidates = sorted(
        candidates,
        key=lambda item: (
            item["score"],
            item["match_score"],
            -item["rank"],
            -item["position"],
        ),
        reverse=True,
    )

    selected = []
    seen = set()

    for item in candidates:
        normalized = item["sentence"].lower().strip()

        if normalized in seen:
            continue

        selected.append(item)
        seen.add(normalized)

        if len(selected) == max_sentences:
            break

    return selected


def make_text_section(title: str, items: list[dict]) -> str:
    if not items:
        return ""

    text = " ".join(item["sentence"] for item in items)
    return f"**{title}:** {text}"


def build_generic_complete_options(
    question: str,
    chunks: list[dict],
    max_options: int = 3,
) -> list[dict]:
    clean_items = collect_clean_sentences(chunks)

    if not clean_items:
        return []

    metadata = get_common_metadata(chunks)
    source_files = get_source_files(chunks)
    partition_keys = get_partition_keys(chunks)

    best_score = round(
        max(chunk.get("match_score", 0) for chunk in chunks),
        2,
    )

    question_words = re.findall(r"[a-zA-Z]{4,}", question.lower())
    question_keywords = list(set(question_words))

    definition_items = get_best_sentences(
        clean_items,
        keywords=question_keywords,
        max_sentences=3,
    )

    function_items = get_best_sentences(
        clean_items,
        keywords=[
            "function",
            "functions",
            "role",
            "importance",
            "important",
            "study",
            "identify",
            "classification",
            "nomenclature",
            "taxonomy",
            "systematics",
            "metabolism",
            "response",
            "stimuli",
            "diary",
            "friend",
            "confide",
            "lonely",
            "teacher",
            "punishment",
            "keesing",
        ],
        max_sentences=3,
    )

    example_items = get_best_sentences(
        clean_items,
        keywords=[
            "example",
            "examples",
            "mango",
            "mangifera",
            "homo",
            "panthera",
            "herbarium",
            "museum",
            "botanical",
            "zoological",
            "key",
            "kitty",
            "anne",
            "keesing",
            "diary",
        ],
        max_sentences=3,
    )

    all_items = definition_items + function_items + example_items

    if not all_items:
        all_items = clean_items[:6]

    final_sentences = []
    seen = set()

    for item in all_items:
        sentence = item["sentence"].strip()
        normalized = sentence.lower()

        if normalized in seen:
            continue

        final_sentences.append(sentence)
        seen.add(normalized)

        if len(final_sentences) == 8:
            break

    if not final_sentences:
        return []

    concise_answer = " ".join(final_sentences[:3]).strip()

    detailed_sections = []

    if definition_items:
        detailed_sections.append(
            "**Core answer:** "
            + " ".join(item["sentence"] for item in definition_items[:3])
        )

    if function_items:
        detailed_sections.append(
            "**Functions / importance:** "
            + " ".join(item["sentence"] for item in function_items[:3])
        )

    if example_items:
        detailed_sections.append(
            "**Examples / supporting points:** "
            + " ".join(item["sentence"] for item in example_items[:3])
        )

    detailed_answer = "\n\n".join(detailed_sections).strip()

    if not detailed_answer:
        detailed_answer = " ".join(final_sentences[:5]).strip()

    table_answer = "| Point | Explanation |\n|---|---|\n"

    for index, sentence in enumerate(final_sentences[:5], start=1):
        table_answer += f"| {index} | {sentence} |\n"

    styles = [
        ("Concise complete answer", concise_answer),
        ("Detailed complete answer", detailed_answer),
        ("Table-based answer", table_answer),
    ]

    options = []

    for style, option_answer in styles[:max_options]:
        options.append(
            {
                "group_key": metadata.get("partition_key", "unknown"),
                "answer": option_answer,
                "subject": metadata.get("subject", "general"),
                "chapter": metadata.get("chapter_name", "unknown"),
                "source_files": source_files,
                "partition_keys": partition_keys,
                "chunk_count": len(chunks),
                "match_score": best_score,
                "option_type": style,
            }
        )

    return options

def build_gpt_style_options(
    question: str,
    chunks: list[dict],
    group_by: str = "partition",
    max_options: int = 3,
) -> list[dict]:
    if not chunks:
        return []

    if is_biomolecule_types_question(question):
        return build_biomolecule_types_options(
            chunks=chunks,
            max_options=max_options,
        )

    if is_micro_macro_question(question):
        return build_micro_macro_answer_options(
            chunks=chunks,
            max_options=max_options,
        )

    return build_generic_complete_options(
        question=question,
        chunks=chunks,
        max_options=max_options,
    )