
import os
import re
import html

import requests
import streamlit as st


# =========================================
# CONFIGURATION
# =========================================

st.set_page_config(
    page_title="GraphMind | Biomedical Research",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = os.getenv(
    "GRAPHMIND_API_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

EXAMPLE_QUESTIONS = [
    "How does Type 2 Diabetes affect immune cells?",
    "How does BMI affect Ramadan fasting outcomes in Type 2 Diabetes?",
    "How can GLP-1-based therapy reduce insulin requirements?",
    "What factors are associated with NK-cell dysfunction in Type 2 Diabetes?",
]


# =========================================
# HELPER FUNCTIONS
# =========================================

def clean_answer(text):
    """Remove common LLM formatting artifacts."""

    if not isinstance(text, str):
        return ""

    # Remove HTML line-break tags.
    text = re.sub(
        r"<br\s*/?>",
        " ",
        text,
        flags=re.IGNORECASE
    )

    # Convert common HTML formatting to Markdown.
    text = re.sub(
        r"(?i)</?p>",
        "\n",
        text
    )

    text = re.sub(
        r"(?i)</?(strong|b)>",
        "**",
        text
    )

    text = re.sub(
        r"(?i)</?(em|i)>",
        "*",
        text
    )

    text = html.unescape(text)

    return text.strip()


def ask_graphmind(question):
    """Send a biomedical question to FastAPI."""

    response = requests.post(
        f"{API_URL}/ask",
        json={"question": question},
        timeout=180
    )

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, dict):
        raise ValueError(
            "Unexpected API response format."
        )

    return data


def check_api():
    """Check whether the FastAPI server is reachable."""

    try:
        response = requests.get(
            f"{API_URL}/",
            timeout=3
        )

        return response.ok

    except requests.RequestException:
        return False


def use_example():
    """Update the question when an example is selected."""

    selected = st.session_state.example_choice

    if selected != "Choose an example...":
        st.session_state.question_input = selected


# =========================================
# CUSTOM CSS
# =========================================

st.markdown(
    """
    <style>

    /* MAIN APPLICATION */

    .stApp {
        background: #f7f9fc;
        color: #172033;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }


    /* SIDEBAR */

    [data-testid="stSidebar"] {
        background: #14213d;
    }

    [data-testid="stSidebar"] * {
        color: #f8fafc;
    }

    [data-testid="stSidebar"] h2 {
        font-size: 19px !important;
        font-weight: 700;
    }

    [data-testid="stSidebar"] h3 {
        font-size: 15px !important;
        font-weight: 650;
    }

    [data-testid="stSidebar"] p {
        font-size: 13px !important;
        line-height: 1.5;
    }

    [data-testid="stSidebar"] hr {
        margin-top: 12px;
        margin-bottom: 12px;
    }


    /* SIDEBAR API BUTTON */

    [data-testid="stSidebar"] .stButton > button {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 8px !important;
        min-height: 40px;
        font-weight: 600 !important;
        width: 100%;
        transition: background-color 0.2s ease;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #1d4ed8 !important;
        color: #ffffff !important;
        border-color: #60a5fa !important;
    }

    [data-testid="stSidebar"] .stButton > button:focus {
        background-color: #1d4ed8 !important;
        color: #ffffff !important;
        border-color: #93c5fd !important;
    }

    [data-testid="stSidebar"] .stButton > button p {
        color: #ffffff !important;
        font-size: 13px !important;
    }


    /* HERO HEADER */

    .hero {
        background: linear-gradient(
            115deg,
            #172554,
            #1d4ed8
        );
        border-radius: 16px;
        padding: 28px 32px;
        color: white;
        margin-bottom: 22px;
    }

    .hero h1 {
        color: white !important;
        font-size: 32px !important;
        margin: 0;
        font-weight: 750;
        line-height: 1.2;
    }

    .hero p {
        color: #dbeafe !important;
        font-size: 14px !important;
        margin-top: 8px;
        margin-bottom: 0;
    }


    /* SECTION TITLES */

    .section-title {
        color: #172554;
        font-size: 20px;
        font-weight: 700;
        margin-top: 16px;
        margin-bottom: 12px;
    }


    /* MAIN BODY TYPOGRAPHY */

    [data-testid="stMain"] p {
        font-size: 14px;
        line-height: 1.65;
    }

    [data-testid="stMain"] li {
        font-size: 14px;
        line-height: 1.6;
        margin-bottom: 4px;
    }

    [data-testid="stMain"] ul {
        margin-top: 6px;
        margin-bottom: 12px;
    }


    /* RESEARCH ANSWER TYPOGRAPHY */

    .research-answer-heading {
        font-size: 20px;
        font-weight: 700;
        color: #172554;
    }

    [data-testid="stMain"] h2 {
        font-size: 21px !important;
        font-weight: 650 !important;
        margin-top: 16px !important;
        margin-bottom: 10px !important;
        line-height: 1.3 !important;
    }

    [data-testid="stMain"] h3 {
        font-size: 17px !important;
        font-weight: 600 !important;
        margin-top: 14px !important;
        margin-bottom: 8px !important;
    }

    [data-testid="stMain"] h4 {
        font-size: 15px !important;
        font-weight: 600 !important;
    }


    /* RESEARCH ANSWER CONTAINER */

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px;
    }


    /* TEXT AREA */

    [data-testid="stTextArea"] textarea {
        border-radius: 10px;
        border: 1px solid #cbd5e1;
        background: white;
        color: #172033;
        font-size: 14px;
        line-height: 1.6;
    }

    [data-testid="stTextArea"] textarea:focus {
        border-color: #2563eb;
    }


    /* PRIMARY SEARCH BUTTON */

    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button[kind="primary"] {
        background: #2563eb !important;
        color: white !important;
        border-radius: 9px;
        font-weight: 650;
        padding: 10px 22px;
        border: none;
    }

    div.stButton > button[kind="primary"]:hover,
    div.stFormSubmitButton > button[kind="primary"]:hover {
        background: #1d4ed8 !important;
        color: white !important;
    }


    /* SOURCE CARDS */

    [data-testid="stMain"]
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #e2e8f0;
    }


    /* FOOTER */

    .footer {
        text-align: center;
        color: #64748b;
        font-size: 12px;
        margin-top: 35px;
        padding: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================
# SIDEBAR
# =========================================

with st.sidebar:

    st.markdown("## 🧠 GraphMind")

    st.caption(
        "Biomedical Research Intelligence"
    )

    st.divider()

    st.markdown("### Research Platform")

    st.write("PubMed Research")
    st.write("Neo4j Knowledge Graph")
    st.write("Qdrant Vector Search")
    st.write("LangGraph Agent")
    st.write("LLM Answer Generation")

    st.divider()

    st.markdown("### System Status")

    if st.button(
        "Check API Connection",
        key="api_connection_button"
    ):

        if check_api():
            st.success("FastAPI connected")
        else:
            st.error("FastAPI unavailable")

    st.divider()

    st.caption(
        "GraphMind | Biomedical GraphRAG Prototype"
    )


# =========================================
# MAIN HEADER
# =========================================

st.markdown(
    """
    <div class="hero">
        <h1>GraphMind</h1>
        <p>
            Biomedical Research Question Answering
            powered by GraphRAG
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    Explore biomedical research using semantic search,
    knowledge graph retrieval, and AI-generated answers
    grounded in PubMed evidence.
    """
)


# =========================================
# RESEARCH QUESTION FORM
# =========================================

st.markdown(
    '<div class="section-title">Ask a Research Question</div>',
    unsafe_allow_html=True
)

if "question_input" not in st.session_state:
    st.session_state.question_input = ""

st.selectbox(
    "Try an example question",
    ["Choose an example..."] + EXAMPLE_QUESTIONS,
    key="example_choice",
    on_change=use_example
)

with st.form("research_form"):

    question = st.text_area(
        "Your biomedical question",
        key="question_input",
        height=110,
        placeholder=(
            "Example: How does Type 2 Diabetes "
            "affect immune cells?"
        )
    )

    submitted = st.form_submit_button(
        "Search Biomedical Research",
        type="primary",
        use_container_width=True
    )


# =========================================
# API REQUEST
# =========================================

if submitted:

    # Clear old results before a new search.
    st.session_state.pop(
        "last_result",
        None
    )

    question = question.strip()

    if not question:

        st.warning(
            "Please enter a biomedical question."
        )

    else:

        with st.spinner(
            "Retrieving and analyzing biomedical evidence..."
        ):

            try:

                data = ask_graphmind(question)

                st.session_state.last_result = data

            except requests.exceptions.Timeout:

                st.error(
                    "The request took too long. "
                    "Please try again."
                )

            except requests.exceptions.HTTPError as error:

                st.error(
                    "The GraphMind backend returned an error."
                )

                st.caption(str(error))

            except requests.exceptions.RequestException:

                st.error(
                    "Unable to connect to FastAPI. "
                    "Make sure the backend is running."
                )

            except ValueError:

                st.error(
                    "The backend returned an invalid response."
                )


# =========================================
# DISPLAY RESULTS
# =========================================

if "last_result" in st.session_state:

    data = st.session_state.last_result

    st.divider()

    st.markdown(
        '<div class="section-title">Research Answer</div>',
        unsafe_allow_html=True
    )

    answer = clean_answer(
        data.get("answer", "")
    )

    if answer:

        with st.container(border=True):
            st.markdown(answer)

    else:

        st.info(
            "No answer was returned for this question."
        )

    st.markdown(
        '<div class="section-title">PubMed Sources</div>',
        unsafe_allow_html=True
    )

    sources = data.get("sources", [])

    if sources:

        st.caption(
            f"{len(sources)} research sources retrieved"
        )

        for index, source in enumerate(
            sources,
            start=1
        ):

            pmid = str(
                source.get("pmid", "")
            ).strip()

            title = (
                source.get("title")
                or "Untitled research paper"
            )

            with st.container(border=True):

                st.markdown(
                    f"**{index}. {title}**"
                )

                st.caption(
                    f"PubMed ID: {pmid}"
                )

                if pmid.isdigit():

                    st.link_button(
                        "View on PubMed",
                        (
                            "https://pubmed.ncbi.nlm.nih.gov/"
                            f"{pmid}/"
                        )
                    )

    else:

        st.info(
            "No supporting PubMed sources were returned."
        )


# =========================================
# FOOTER
# =========================================

st.markdown(
    """
    <div class="footer">
        GraphMind · Biomedical GraphRAG Research Prototype
        <br>
        For research exploration, not clinical diagnosis.
    </div>
    """,
    unsafe_allow_html=True
)
