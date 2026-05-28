from summarizer import build_gpt_style_options

dummy_chunks = [
    {
        "content": "Biomolecules are chemical compounds present in living organisms. Micromolecules include amino acids and sugars. Macromolecules include proteins, polysaccharides and nucleic acids.",
        "metadata": {
            "subject": "Biology",
            "chapter_name": "Biomolecule",
            "source_file": "Biomolecule.txt",
            "partition_key": "Biology/Biomolecule/Biomolecule.txt",
        },
        "match_score": 95,
        "rank": 1,
    }
]

options = build_gpt_style_options(
    question="What is biomolecule? Explain its types.",
    chunks=dummy_chunks,
    max_options=3,
)

for option in options:
    print("\n" + "=" * 80)
    print(option["option_type"])
    print(option["answer"][:300])