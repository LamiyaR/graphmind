
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="GraphMind | Evaluation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "processed"


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f8fafc;
        color: #172033;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1 {
        color: #172554;
        font-size: 2rem !important;
        font-weight: 750;
    }

    h2 {
        color: #172554;
        font-size: 1.45rem !important;
    }

    h3 {
        color: #1e293b;
        font-size: 1.2rem !important;
    }

    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.6rem;
        color: #172554;
    }

    [data-testid="stMetricLabel"] {
        color: #475569;
    }

    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }

    [data-testid="stSidebar"] {
        background: #14213d;
    }

    [data-testid="stSidebar"] * {
        color: #f8fafc;
    }

    [data-testid="stSidebarNav"] a:hover {
        background: rgba(255, 255, 255, 0.12);
    }

    .dashboard-footer {
        margin-top: 35px;
        padding-top: 18px;
        border-top: 1px solid #e2e8f0;
        color: #64748b;
        font-size: 12px;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATA HELPERS
# ============================================================

def load_csv(filename):
    """Load an evaluation CSV without crashing if missing."""

    path = DATA_DIR / filename

    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except (OSError, pd.errors.EmptyDataError, pd.errors.ParserError):
        return pd.DataFrame()


def mean_metric(df, column):
    """Return the mean of a numeric metric column."""

    if df.empty or column not in df.columns:
        return None

    values = pd.to_numeric(df[column], errors="coerce")

    if values.dropna().empty:
        return None

    return float(values.mean())


def display_score(value, percent=False):
    """Format a metric safely."""

    if value is None or pd.isna(value):
        return "N/A"

    if percent:
        return f"{float(value) * 100:.1f}%"

    return f"{float(value):.3f}"


def numeric_column(df, column):
    """Convert a DataFrame column to numeric values."""

    return pd.to_numeric(df[column], errors="coerce")


def show_download(df, filename, label="Download Results"):
    """Download a DataFrame as CSV."""

    st.download_button(
        label=label,
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
    )


# ============================================================
# LOAD EVALUATION RESULTS
# ============================================================

retrieval = load_csv("retrieval_metrics.csv")

methods = load_csv("retrieval_methods_benchmark.csv")

diversity = load_csv("retrieval_benchmark.csv")

citations = load_csv("citation_metrics.csv")

ner = load_csv("ner_metrics.csv")

linking = load_csv("entity_linking_metrics.csv")


# ============================================================
# DASHBOARD HEADER
# ============================================================

st.title("Evaluation & Benchmarking")

st.caption(
    "Experimental evaluation of the GraphMind "
    "biomedical GraphRAG system."
)

st.info(
    "All metrics are loaded from saved evaluation files. "
    "Results are preliminary and depend on the current "
    "evaluation datasets."
)


# ============================================================
# NAVIGATION TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Retrieval Quality",
    "Retrieval Comparison",
    "Citation & Answer Support",
    "NER & Entity Linking",
    "Retrieval Diversity",
])


# ============================================================
# TAB 1 — SEMANTIC RETRIEVAL QUALITY
# ============================================================

with tab1:

    st.subheader("Semantic Retrieval Performance")

    st.write(
        "Evaluation of Qdrant semantic search using "
        "manually labeled relevant research chunks."
    )

    required = [
        "precision_at_5",
        "recall_at_5",
        "reciprocal_rank_at_5",
    ]

    if retrieval.empty:

        st.warning(
            "Retrieval results were not found. "
            "Expected: data/processed/retrieval_metrics.csv"
        )

    elif not all(col in retrieval.columns for col in required):

        st.warning(
            "The retrieval CSV is missing required metric columns."
        )

    else:

        precision = mean_metric(retrieval, "precision_at_5")
        recall = mean_metric(retrieval, "recall_at_5")
        mrr = mean_metric(retrieval, "reciprocal_rank_at_5")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Mean Precision@5",
            display_score(precision, True),
        )

        col2.metric(
            "Mean Recall@5",
            display_score(recall, True),
        )

        col3.metric(
            "MRR@5",
            display_score(mrr, True),
        )

        st.markdown("#### Results by Research Question")

        display_columns = [
            "question",
            "precision_at_5",
            "recall_at_5",
            "reciprocal_rank_at_5",
        ]

        available_columns = [
            col for col in display_columns
            if col in retrieval.columns
        ]

        st.dataframe(
            retrieval[available_columns],
            column_config={
                "question": "Research Question",
                "precision_at_5": st.column_config.NumberColumn(
                    "Precision@5",
                    format="%.2f",
                ),
                "recall_at_5": st.column_config.NumberColumn(
                    "Recall@5",
                    format="%.2f",
                ),
                "reciprocal_rank_at_5": st.column_config.NumberColumn(
                    "RR@5",
                    format="%.2f",
                ),
            },
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            f"Evaluation based on {len(retrieval)} biomedical "
            "questions. Metrics are calculated at the chunk level. "
            "The current relevance labels may not include every "
            "relevant chunk in the corpus."
        )

        show_download(
            retrieval,
            "retrieval_metrics.csv",
            "Download Retrieval Results",
        )


# ============================================================
# TAB 2 — VECTOR VS GRAPH VS HYBRID
# ============================================================

with tab2:

    st.subheader("Comparative Retrieval Evaluation")

    st.write(
        "Comparison of vector-only retrieval using Qdrant, "
        "graph-only retrieval using Neo4j, and hybrid retrieval "
        "combining both evidence sources."
    )

    metric_columns = [
        "precision_at_5",
        "recall_at_5",
        "rr_at_5",
    ]

    if methods.empty:

        st.warning(
            "Retrieval comparison results were not found. "
            "Expected: "
            "data/processed/retrieval_methods_benchmark.csv"
        )

    elif not all(
        col in methods.columns
        for col in ["method"] + metric_columns
    ):

        st.warning(
            "The retrieval comparison CSV is missing "
            "required columns."
        )

    else:

        comparison = methods.copy()

        for column in metric_columns:
            comparison[column] = numeric_column(
                comparison,
                column,
            )

        summary = (
            comparison.groupby("method")[metric_columns]
            .mean()
            .reset_index()
        )

        summary["method"] = summary["method"].replace({
            "vector": "Vector-only",
            "graph": "Graph-only",
            "hybrid": "Hybrid GraphRAG",
        })

        st.markdown("#### Average Retrieval Performance")

        st.dataframe(
            summary,
            column_config={
                "method": "Retrieval Method",
                "precision_at_5": st.column_config.NumberColumn(
                    "Precision@5",
                    format="%.2f",
                ),
                "recall_at_5": st.column_config.NumberColumn(
                    "Recall@5",
                    format="%.2f",
                ),
                "rr_at_5": st.column_config.NumberColumn(
                    "MRR@5",
                    format="%.2f",
                ),
            },
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("#### Performance by Retrieval Strategy")

        chart_data = summary.set_index("method")

        chart_data = chart_data.rename(columns={
            "precision_at_5": "Precision@5",
            "recall_at_5": "Recall@5",
            "rr_at_5": "MRR@5",
        })

        st.bar_chart(
            chart_data,
            stack=False,
            horizontal=False,
            height=350,
        )

        st.caption(
            "Paper-level evaluation using the same questions "
            "for all three methods. The comparison uses a "
            "broader candidate pool than production hybrid "
            "retrieval and a separate graph-ranking heuristic."
        )

        st.markdown("#### Detailed Benchmark Results")

        detail_columns = [
            "question",
            "method",
            "precision_at_5",
            "recall_at_5",
            "rr_at_5",
            "returned_papers",
            "retrieved_pmids",
        ]

        available = [
            col for col in detail_columns
            if col in comparison.columns
        ]

        st.dataframe(
            comparison[available],
            column_config={
                "question": "Research Question",
                "method": "Retrieval Method",
                "precision_at_5": "Precision@5",
                "recall_at_5": "Recall@5",
                "rr_at_5": "RR@5",
                "returned_papers": "Papers Returned",
                "retrieved_pmids": "Retrieved PMIDs",
            },
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "The hybrid method should not be described as "
            "more accurate unless its measured results "
            "outperform the vector-only baseline."
        )

        show_download(
            methods,
            "retrieval_methods_benchmark.csv",
            "Download Comparison Results",
        )


# ============================================================
# TAB 3 — CITATION VALIDITY AND SUPPORT
# ============================================================

with tab3:

    st.subheader("Citation Validity & Evidence Support")

    st.write(
        "Evaluation of whether GraphMind references known "
        "PubMed papers and whether the associated biomedical "
        "claims are supported by those papers."
    )

    required = [
        "citation_validity",
        "citation_accuracy",
        "reviewed_pairs",
        "total_citation_pairs",
    ]

    if citations.empty:

        st.warning(
            "Citation evaluation results were not found. "
            "Expected: data/processed/citation_metrics.csv"
        )

    elif not all(col in citations.columns for col in required):

        st.warning(
            "The citation metrics CSV is missing "
            "required columns."
        )

    else:

        row = citations.iloc[0]

        validity = row.get("citation_validity")
        accuracy = row.get("citation_accuracy")
        reviewed = row.get("reviewed_pairs", 0)
        total = row.get("total_citation_pairs", 0)

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "PMID Validity",
            display_score(validity, True),
        )

        col2.metric(
            "Citation Support",
            display_score(accuracy, True),
        )

        col3.metric(
            "Reviewed Claim–Citation Pairs",
            f"{int(reviewed)}/{int(total)}",
        )

        st.markdown("#### Citation Evaluation Summary")

        st.dataframe(
            citations,
            column_config={
                "total_citation_pairs": "Candidate Pairs",
                "valid_pmids": "Valid PMIDs",
                "citation_validity": "PMID Validity",
                "reviewed_pairs": "Reviewed Pairs",
                "supported_pairs": "Supported Pairs",
                "citation_accuracy": "Citation Support",
            },
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "Citation-support judgments are based on "
            "AI-assisted abstract-level review and have "
            "not been independently validated. "
            "Candidate associations are not necessarily "
            "explicit inline citations."
        )

        show_download(
            citations,
            "citation_metrics.csv",
            "Download Citation Results",
        )


# ============================================================
# TAB 4 — NER AND ENTITY LINKING
# ============================================================

with tab4:

    st.subheader("Biomedical Named Entity Recognition")

    st.write(
        "Evaluation of biomedical entity extraction using "
        "the NER fallback model."
    )

    ner_columns = [
        "true_positives",
        "false_positives",
        "false_negatives",
    ]

    if ner.empty:

        st.warning(
            "NER evaluation results were not found. "
            "Expected: data/processed/ner_metrics.csv"
        )

    elif not all(col in ner.columns for col in ner_columns):

        st.warning(
            "The NER metrics CSV is missing required columns."
        )

    else:

        tp = int(numeric_column(
            ner, "true_positives"
        ).sum())

        fp = int(numeric_column(
            ner, "false_positives"
        ).sum())

        fn = int(numeric_column(
            ner, "false_negatives"
        ).sum())

        precision = (
            tp / (tp + fp)
            if tp + fp else 0.0
        )

        recall = (
            tp / (tp + fn)
            if tp + fn else 0.0
        )

        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall else 0.0
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "NER Precision",
            display_score(precision, True),
        )

        col2.metric(
            "NER Recall",
            display_score(recall, True),
        )

        col3.metric(
            "NER F1-Score",
            display_score(f1, True),
        )

        st.caption(
            "Current NER evaluation uses a single synthetic "
            "test sentence. These results are a preliminary "
            "sanity check, not a corpus-wide benchmark."
        )

        with st.expander("View NER Evaluation Details"):

            st.dataframe(
                ner,
                use_container_width=True,
                hide_index=True,
            )

            show_download(
                ner,
                "ner_metrics.csv",
                "Download NER Results",
            )

    st.divider()

    st.subheader("Biomedical Entity Linking")

    st.write(
        "Evaluation of entity normalization and linking "
        "to standardized biomedical identifiers."
    )

    linking_columns = [
        "total_mentions",
        "linked_mentions",
        "coverage",
        "reviewed_links",
        "linking_precision",
    ]

    if linking.empty:

        st.warning(
            "Entity-linking results were not found. "
            "Expected: "
            "data/processed/entity_linking_metrics.csv"
        )

    elif not all(
        col in linking.columns
        for col in linking_columns
    ):

        st.warning(
            "The entity-linking CSV is missing "
            "required columns."
        )

    else:

        row = linking.iloc[0]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Linking Coverage",
            display_score(
                row.get("coverage"),
                True,
            ),
        )

        col2.metric(
            "Linking Precision",
            display_score(
                row.get("linking_precision"),
                True,
            ),
        )

        col3.metric(
            "Linked Mentions",
            str(int(row.get("linked_mentions", 0))),
        )

        st.markdown("#### Entity Linking Summary")

        st.dataframe(
            linking,
            column_config={
                "total_mentions": "Total Mentions",
                "linked_mentions": "Linked Mentions",
                "coverage": "Linking Coverage",
                "reviewed_links": "Reviewed Links",
                "correct_links": "Correct Links",
                "linking_precision": "Linking Precision",
            },
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "The current linking dictionary contains three "
            "biomedical concepts. All 12 successfully linked "
            "mentions refer to Type 2 Diabetes. Linking "
            "precision reflects preliminary terminology-based "
            "review, not independent contextual validation."
        )

        show_download(
            linking,
            "entity_linking_metrics.csv",
            "Download Entity Linking Results",
        )


# ============================================================
# TAB 5 — RETRIEVAL DIVERSITY
# ============================================================

with tab5:

    st.subheader("Retrieval Diversity Analysis")

    st.write(
        "Comparison of the original semantic search and "
        "the improved diversity-aware retrieval strategy."
    )

    diversity_columns = [
        "original_unique_papers",
        "improved_unique_papers",
    ]

    if diversity.empty:

        st.warning(
            "Retrieval diversity results were not found. "
            "Expected: data/processed/retrieval_benchmark.csv"
        )

    elif not all(
        col in diversity.columns
        for col in diversity_columns
    ):

        st.warning(
            "The diversity benchmark CSV is missing "
            "required columns."
        )

    else:

        original = mean_metric(
            diversity,
            "original_unique_papers",
        )

        improved = mean_metric(
            diversity,
            "improved_unique_papers",
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Original Average",
            f"{original:.1f} papers"
            if original is not None else "N/A",
        )

        col2.metric(
            "Improved Average",
            f"{improved:.1f} papers"
            if improved is not None else "N/A",
        )

        increase = (
            improved - original
            if original is not None and improved is not None
            else None
        )

        col3.metric(
            "Average Increase",
            f"+{increase:.1f} papers"
            if increase is not None else "N/A",
        )

        st.markdown("#### Unique Papers Retrieved per Question")

        chart_data = diversity[diversity_columns].copy()

        chart_data = chart_data.apply(
            pd.to_numeric,
            errors="coerce",
        )

        chart_data.index = [
            f"Question {i + 1}"
            for i in range(len(chart_data))
        ]

        chart_data.columns = [
            "Original Search",
            "Improved Search",
        ]

        st.bar_chart(
            chart_data,
            stack=False,
            height=350,
        )

        st.markdown("#### Detailed Diversity Results")

        st.dataframe(
            diversity,
            column_config={
                "question": "Research Question",
                "original_unique_papers": "Original Unique Papers",
                "improved_unique_papers": "Improved Unique Papers",
            },
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "Unique Papers@5 counts the distinct PubMed papers "
            "represented among the top five results. "
            "Greater source diversity does not necessarily "
            "mean greater retrieval relevance."
        )

        show_download(
            diversity,
            "retrieval_benchmark.csv",
            "Download Diversity Results",
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="dashboard-footer">
        GraphMind · Biomedical GraphRAG Research Prototype
        <p>
            Experimental evaluation for research purposes.
            Results are preliminary and not clinical validation.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
