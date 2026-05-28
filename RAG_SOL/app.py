import streamlit as st
import summarizer

from config import DATA_DIR, DISPLAY_OPTIONS, RETRIEVAL_K
from reranker import rerank_chunks
from retriever import retrieve_top_chunks
from summarizer import build_gpt_style_options


def format_display_name(value: str) -> str:
    value = value.replace("_", " ").replace("-", " ").strip()
    return value.title()


def get_available_subjects() -> list[str]:
    if not DATA_DIR.exists():
        return ["All"]

    subjects = [
        format_display_name(path.name)
        for path in DATA_DIR.iterdir()
        if path.is_dir()
    ]

    return ["All"] + sorted(subjects)


def main() -> None:
    st.set_page_config(
        page_title="RAG Answer Options",
        page_icon="🤖",
        layout="wide",
    )

    st.title("RAG Answer Options")
    st.write("Ask a question and get the best 3 complete answer options from your documents.")

    with st.sidebar:
        st.header("Settings")

        subject = st.selectbox(
            "Subject filter",
            options=get_available_subjects(),
        )

        group_by_label = st.selectbox(
            "Group answer options by",
            options=["Partition Key", "Chapter", "Subject"],
            index=0,
        )

        group_by_map = {
            "Partition Key": "partition",
            "Chapter": "chapter",
            "Subject": "subject",
        }

        group_by = group_by_map[group_by_label]

        st.divider()
        st.write("**Internal retrieval:** 12 chunks")
        st.write("**Displayed output:** 3 options")
        st.write("**Vector DB:** Chroma")
        st.write("**Reranker:** Cross Encoder")

    st.info(
        "The system retrieves chunks from Chroma, reranks them, generates 3 complete "
        "answer options, and allows the user to select the best one."
    )

    question = st.text_input(
        "Ask your question",
        placeholder="Example: Explain biomolecules by covering micromolecules, macromolecules, and their major examples.",
    )

    search_clicked = st.button(
        "Generate Answer Options",
        use_container_width=True,
    )

    if search_clicked:
        if not question.strip():
            st.warning("Please enter a question.")
            return

        selected_subject = None if subject == "All" else subject

        with st.spinner("Retrieving candidate chunks from Chroma..."):
            candidate_chunks = retrieve_top_chunks(
                question=question,
                top_k=RETRIEVAL_K,
                subject=selected_subject,
            )

        if not candidate_chunks:
            st.error("No relevant chunks found.")
            return

        with st.spinner("Reranking and generating answer options..."):
            reranked_chunks = rerank_chunks(
                question=question,
                chunks=candidate_chunks,
                top_n=RETRIEVAL_K,
            )

            answer_options = build_gpt_style_options(
                question=question,
                chunks=reranked_chunks,
                group_by=group_by,
                max_options=DISPLAY_OPTIONS,
            )

        st.caption(
            f"Debug: retrieved {len(candidate_chunks)} chunks, "
            f"reranked {len(reranked_chunks)} chunks, "
            f"generated {len(answer_options)} options."
        )

        if not answer_options:
            st.error("No answer options could be generated.")
            return

        st.subheader("Best 3 Answer Options")

        option_labels = []

        for index, option in enumerate(answer_options, start=1):
            label = (
                f"Option {index} | "
                f"{option['subject']} | "
                f"{option['chapter']} | "
                f"Focus: {option.get('option_type', 'N/A')} | "
                f"Match: {option['match_score']}%"
            )
            option_labels.append(label)

        selected_option_label = st.radio(
            "Select the answer option that is most useful for you:",
            options=option_labels,
        )

        selected_index = option_labels.index(selected_option_label)
        selected_option = answer_options[selected_index]

        st.success(f"You selected: Option {selected_index + 1}")

        for index, option in enumerate(answer_options, start=1):
            with st.container(border=True):
                st.markdown(f"### Option {index}")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Match Strength", f"{option['match_score']}%")

                with col2:
                    st.write("**Subject**")
                    st.write(option["subject"])

                with col3:
                    st.write("**Chapter**")
                    st.write(option["chapter"])

                st.write("**Option Focus**")
                st.write(option.get("option_type", "N/A"))

                st.write("**Answer**")
                st.markdown(option["answer"])

                st.write("**Source file**")
                st.write(", ".join(option["source_files"]))

                st.write("**Partition key / Group key**")
                st.code(option["group_key"])

                st.write("**Chunks used**")
                st.write(option["chunk_count"])

                with st.expander(f"View all partition keys used in Option {index}"):
                    for key in option["partition_keys"]:
                        st.code(key)

        st.subheader("Final Selected Answer")
        st.markdown(selected_option["answer"])


if __name__ == "__main__":
    main()