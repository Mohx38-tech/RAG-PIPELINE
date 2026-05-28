from chroma_store import get_chroma_collection


def main():
    collection = get_chroma_collection()

    print("Total chunks in Chroma:", collection.count())

    results = collection.get(
        limit=5,
        include=["documents", "metadatas"],
    )

    ids = results.get("ids", [])
    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])

    for index, chunk_id in enumerate(ids):
        print("\n" + "=" * 80)
        print("Chunk ID:", chunk_id)

        print("\nMetadata:")
        for key, value in metadatas[index].items():
            print(f"{key}: {value}")

        print("\nChunk Preview:")
        print(documents[index][:700])


if __name__ == "__main__":
    main()