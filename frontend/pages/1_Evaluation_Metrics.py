
from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "processed"

METRICS_FILE = DATA_DIR / "retrieval_metrics.csv"
BENCHMARK_FILE = DATA_DIR / "retrieval_benchmark.csv"


st.set_page_config(
    page_title="GraphMind Evaluation",
    page_icon="📊",
    layout="wide"
)

st.title("GraphMind — Evaluation Metrics")
st.write(
    "Evaluation of biomedical research retrieval "
    "using manually reviewed questions."
)


st.header("1. Retrieval Quality")

if METRICS_FILE.exists():

    df = pd.read_csv(METRICS_FILE)

    required = [
        "precision_at_5",
        "recall_at_5",
        "reciprocal_rank_at_5"
    ]

    if all(col in df.columns for col in required):

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Mean Precision@5",
            f"{df['precision_at_5'].mean():.2f}"
        )

        col2.metric(
            "Mean Recall@5",
            f"{df['recall_at_5'].mean():.2f}"
        )

        col3.metric(
            "MRR@5",
            f"{df['reciprocal_rank_at_5'].mean():.2f}"
        )

        st.subheader("Results by Question")
        st.dataframe(df, use_container_width=True)

        st.download_button(
            "Download Evaluation Results",
            data=df.to_csv(index=False),
            file_name="retrieval_metrics.csv",
            mime="text/csv"
        )

    else:
        st.warning(
            "The evaluation CSV has missing metric columns."
        )

else:
    st.warning("Retrieval metrics file not found.")


st.divider()

st.header("2. Retrieval Diversity")

if BENCHMARK_FILE.exists():

    benchmark = pd.read_csv(BENCHMARK_FILE)

    columns = [
        "original_unique_papers",
        "improved_unique_papers"
    ]

    if all(col in benchmark.columns for col in columns):

        col1, col2 = st.columns(2)

        col1.metric(
            "Original Average Unique Papers",
            f"{benchmark['original_unique_papers'].mean():.1f}"
        )

        col2.metric(
            "Improved Average Unique Papers",
            f"{benchmark['improved_unique_papers'].mean():.1f}"
        )

        st.subheader("Original vs Improved Search")

        chart_data = benchmark[
            columns
        ].reset_index(drop=True)

        chart_data.index = [
            f"Question {i + 1}"
            for i in range(len(chart_data))
        ]

        st.bar_chart(chart_data)

        st.dataframe(
            benchmark,
            use_container_width=True
        )

    else:
        st.warning(
            "The benchmark CSV has missing columns."
        )

else:
    st.warning("Retrieval benchmark file not found.")


st.divider()

st.header("3. Understanding the Metrics")

st.markdown("""
**Precision@5:** How many of the top five
retrieved chunks are relevant?

**Recall@5:** How many of the known relevant
chunks were found in the top five?

**MRR@5:** How highly the first relevant
chunk appears in the results.

**Retrieval diversity:** How many different
research papers appear in the results.
""")

st.info(
    "These results describe a small evaluation "
    "dataset. Higher source diversity does not "
    "necessarily mean higher relevance."
)
