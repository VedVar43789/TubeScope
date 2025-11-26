import streamlit as st
import pandas as pd
import isodate
from utils import (
    get_latest_snapshot,
    score_latest_batch,
    run_pull_trending,
    FEATURE_COLS,
    CATEGORY_LABELS,
)


def comma_number(n):
    try:
        return f"{int(n):,}"
    except Exception:
        return n


def iso_to_mmss(iso_str: str):
    if not isinstance(iso_str, str):
        return ""
    try:
        total = int(isodate.parse_duration(iso_str).total_seconds())
    except Exception:
        return iso_str
    m, s = divmod(total, 60)
    return f"{m}:{s:02d}"


st.title("Live Trending Analyzer")

st.markdown(
    """
    This page:

    1. Allows you to **pull a fresh Trending snapshot** by running `pull_trending.py`
    2. Automatically **loads the most recent snapshot** from `data/`
    3. Uses the **trained classification model** to predict whether each video will trend beyond 24 hours
    4. Provides:
       - A **Viral Leaderboard** ranking the current Top 50 by predicted survival probability
       - A **Video Inspector** for detailed metadata, engagement signals, and model output for any video
    """
)


# Step 1: Data refresh
st.markdown("### Step 1: Refresh data")

if st.button("↻ Run pull_trending.py and refresh snapshot"):
    with st.spinner("Calling YouTube API and updating data/ ..."):
        success, msg = run_pull_trending()
    if success:
        st.success("pull_trending.py completed successfully.")
        if msg:
            st.caption(msg)
    else:
        st.error("pull_trending.py failed.")
        st.code(msg)


# Step 2: Load most recent snapshot
st.markdown("### Step 2: Load latest snapshot")

try:
    df_raw, date_label, filename = get_latest_snapshot()
except Exception as e:
    st.error("Unable to load latest snapshot.")
    st.exception(e)
    st.stop()

# Normalize raw columns
rename_map = {}
cols = df_raw.columns

for old, new in [
    ("snippet.title", "title"),
    ("snippet.channelTitle", "channelTitle"),
    ("contentDetails.duration", "duration"),
    ("snippet.description", "description"),
    ("snippet.tags", "tags"),
    ("snippet.categoryId", "category"),
]:
    if old in cols and new not in cols:
        rename_map[old] = new

if rename_map:
    df_raw = df_raw.rename(columns=rename_map)

st.caption(f"Using snapshot **{filename}** from data/ ({len(df_raw)} rows).")


# Scoring and feature sanity
try:
    df = score_latest_batch(df_raw)
except Exception as e:
    st.error("Error while scoring.")
    st.exception(e)
    st.stop()

cols = df.columns

if "tags_count" not in cols:
    def _count_tags(v):
        if isinstance(v, list): return len(v)
        if isinstance(v, str): return len([t for t in v.split(",") if t.strip()])
        return 0
    tag_src = "tags" if "tags" in cols else "snippet.tags" if "snippet.tags" in cols else None
    df["tags_count"] = df[tag_src].apply(_count_tags) if tag_src else 0

if "title" not in cols:
    if "snippet.title" in cols:
        df["title"] = df["snippet.title"]
    elif "video_title" in cols:
        df["title"] = df["video_title"]
    else:
        df["title"] = "[unknown title]"

if "channelTitle" not in cols:
    if "snippet.channelTitle" in cols:
        df["channelTitle"] = df["snippet.channelTitle"]
    elif "channel_title" in cols:
        df["channelTitle"] = df["channel_title"]
    else:
        df["channelTitle"] = "[unknown channel]"

if "description_word_count" not in cols:
    src = "description" if "description" in cols else "snippet.description" if "snippet.description" in cols else None
    df["description_word_count"] = (
        df[src].fillna("").apply(lambda s: len(str(s).split()))
        if src else 0
    )

if "publish_hour" not in cols or "is_weekend" not in cols:
    src = "snippet.publishedAt" if "snippet.publishedAt" in cols else "published_at" if "published_at" in cols else None
    if src:
        dt = pd.to_datetime(df[src], errors="coerce", utc=True)
        df["publish_hour"] = dt.dt.hour.fillna(0).astype(int)
        df["is_weekend"] = dt.dt.weekday.isin([5, 6]).astype(int)
    else:
        df["publish_hour"] = 0
        df["is_weekend"] = 0


# Viral Leaderboard
st.divider()
st.header("Viral Leaderboard – Top 5 by viral probability")

top = df.sort_values("viral_prob", ascending=False).head(5).copy()
top["Viral Prob (%)"] = (top["viral_prob"] * 100).round(1)
top["Subscribers"] = top["channel_subscriber_count"].apply(comma_number)
top["Channel Views"] = top["channel_view_count"].apply(comma_number)
top["Duration"] = top["duration"].apply(iso_to_mmss)

tbl = top[
    ["title", "channelTitle", "Viral Prob (%)", "Subscribers", "Channel Views", "Duration"]
].rename(columns={"title": "Title", "channelTitle": "Channel"})

st.dataframe(tbl, hide_index=True, use_container_width=True)
st.caption("Viral probability = model's confidence that the video will survive more than 1 day on Trending.")


# Video inspector
st.divider()
st.header("Inspect a specific video")

labels = df["title"] + " — " + df["channelTitle"]
choice = st.selectbox("Pick any of the current Top 50 videos:", list(labels))
row = df.iloc[labels[labels == choice].index[0]]

video_id = row.get("id_x")
thumb = row.get("snippet.thumbnails.medium.url")
yt_url = f"https://www.youtube.com/watch?v={video_id}"

col1, col2 = st.columns(2)


with col1:
    st.markdown(
        f"""
        <a href="{yt_url}" target="_blank">
            <img src="{thumb}" style="max-width: 360px; border-radius: 8px;">
        </a>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f"### {row['title']}")
    st.write(f"**Channel:** {row['channelTitle']}")

    cat_raw = row.get("category")
    cat = None
    if cat_raw is not None:
        try:
            cat = CATEGORY_LABELS.get(int(cat_raw))
        except Exception:
            pass
    cat = cat or row.get("category_name", cat_raw or "Unknown")

    st.write(f"**Category:** {cat}")
    st.write(f"**Duration:** {iso_to_mmss(row['duration'])}")
    st.write(f"**Channel subscribers:** {int(row['channel_subscriber_count']):,}")
    st.write(f"**Channel total views:** {int(row['channel_view_count']):,}")
    st.write(f"**Channel video count:** {int(row['channel_video_count']):,}")
    st.write(f"**Tags count:** {int(row['tags_count'])}")
    st.write(f"**Description words:** {int(row['description_word_count'])}")
    st.write(f"**Published hour:** {row['publish_hour']}:00")
    st.write("**Weekend publish?** " + ("Yes" if row["is_weekend"] else "No"))


with col2:
    st.markdown("### Viral potential")
    st.metric("Viral probability", f"{row['viral_prob'] * 100:.1f}%")

    p = row["viral_prob"]
    if p >= 0.7:
        st.success("High viral potential – strong chance of surviving the 24-hour cliff.")
    elif p >= 0.4:
        st.warning("Moderate viral potential – could go either way, worth watching.")
    else:
        st.info("Low viral potential – likely a one-day trend.")

    with st.expander("Show model input features for this video"):
        st.json({c: row[c] for c in FEATURE_COLS if c in row})