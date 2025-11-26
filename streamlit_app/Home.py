# streamlit_app/Home.py
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="TubeScope",
    layout="wide",  
)

# ---------- Header: logo + title ----------
ROOT = Path(__file__).resolve().parent
LOGO_PATH = ROOT / "static" / "tubescope_logo.png"  # adjust if needed

col_logo, col_title = st.columns([1, 4])

with col_logo:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)

with col_title:
    st.title("TubeScope – Viral Lifecycle Analytics")
    st.write(
        "Predicting which trending YouTube videos will "
        "survive past **24 hours** on the Trending page."
    )

st.divider()

# ---------- Short welcome blurb ----------
st.subheader("Welcome")
st.write(
    "Use the navigation in the left sidebar to move between pages. "
    "Each section walks you through a different part of the TubeScope experience:"
)

# ---------- 2×2 grid of sections ----------
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

# 1. Overview
with row1_col1:
    st.markdown("### 1. Overview")
    st.write(
        "- What TubeScope is and why we built it\n"
        "- How we pivoted from regression to a **classification** framing\n"
        "- Why we care about “**survival past 1 day**” on Trending\n"
        "- High-level tour of the project and data"
    )

# 2. Models & Visualizations
with row1_col2:
    st.markdown("### 2. Models & Visualizations")
    st.write(
        "- Kaplan–Meier survival curves for trending videos\n"
        "- Viral vs non-viral breakdowns and class balance\n"
        "- Model performance metrics (accuracy, precision, recall, F1)\n"
        "- Top features driving viral predictions"
    )

# 3. Live Trending Analyzer
with row2_col1:
    st.markdown("### 3. Live Trending Analyzer")
    st.write(
        "- Pull the latest **Top 50** trending YouTube videos (US)\n"
        "- Score each video with the classifier\n"
        "- View a **viral leaderboard** sorted by predicted probability\n"
        "- Inspect individual videos with channel stats and thumbnail links to YouTube"
    )

# 4. Interactive Model Tester
with row2_col2:
    st.markdown("### 4. Interactive Model Tester")
    st.write(
        "- Manually adjust channel + video metrics (subscribers, views, duration, tags, etc.)\n"
        "- See how the model’s viral probability responds in real time\n"
        "- Copy metrics from a real trending video into the tester with one click\n"
        "- Great for “what-if” experiments and demoing the model"
    )

st.divider()

# ---------- Bottom helper message ----------
st.info(
    "Ready to explore? Use the sidebar on the left to switch between pages "
    "and interact with TubeScope’s models, visualizations, and live tools."
)