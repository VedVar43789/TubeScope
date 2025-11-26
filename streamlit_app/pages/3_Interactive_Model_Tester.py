import pandas as pd
import streamlit as st

from utils import (
    load_artifacts,
    prepare_features,
    get_latest_snapshot,
    score_latest_batch,
    CATEGORY_LABELS,
    REV_CATEGORY_LABELS,
    iso_to_minutes,
)


def compute_text_time_features(row):
    desc = str(row.get("description", "") or "")
    title = str(row.get("title", "") or "")

    tags_raw = row.get("tags", "") or ""
    if isinstance(tags_raw, list):
        tags_count = len(tags_raw)
    else:
        tags_count = len(str(tags_raw).split(",")) if tags_raw else 0

    published = row.get("snippet.publishedAt") or row.get("published_at") or ""
    try:
        ts = pd.to_datetime(published, utc=True).tz_convert(None)
        publish_hour = int(ts.hour)
        is_weekend = int(ts.dayofweek in (5, 6))
    except Exception:
        publish_hour = 0
        is_weekend = 0

    desc_words = len(desc.split())
    title_chars = len(title)
    duration_min = iso_to_minutes(row.get("duration", 0))

    return desc_words, title_chars, tags_count, publish_hour, is_weekend, duration_min


def build_manual_df(
    subs,
    views,
    vids,
    duration_min,
    desc_words,
    title_chars,
    tags_count,
    publish_hour,
    is_weekend,
    category,
) -> pd.DataFrame:
    row = {
        "channel_subscriber_count": subs,
        "channel_video_count": vids,
        "channel_view_count": views,
        "duration": duration_min,
        "description_word_count": desc_words,
        "title_char_count": title_chars,
        "tags_count": tags_count,
        "publish_hour": publish_hour,
        "is_weekend": 1 if is_weekend else 0,
        "category": category,
    }
    return pd.DataFrame([row])


@st.cache_resource
def get_artifacts():
    model, encoder, model_columns = load_artifacts()
    try:
        categories = list(encoder.categories_[0])
    except Exception:
        categories = [
            "Music",
            "Gaming",
            "Entertainment",
            "News & Politics",
            "Film & Animation",
            "Howto & Style",
            "People & Blogs",
            "Science & Technology",
            "Sports",
            "Travel & Events",
        ]
    return model, encoder, model_columns, categories


@st.cache_data(show_spinner=False)
def load_scored_top50():
    df_raw, date_label, filename = get_latest_snapshot()
    df_scored = score_latest_batch(df_raw)
    return df_scored, date_label


st.set_page_config(page_title="Interactive Viral Tester", page_icon="🧪")

# Apply pending prefill before widgets are created
if "pending_prefill" in st.session_state:
    row_dict = st.session_state.pop("pending_prefill")
    row = pd.Series(row_dict)

    def rget(key, default=0):
        return row_dict.get(key, default)

    st.session_state["subs"] = int(rget("channel_subscriber_count", 0))
    st.session_state["views"] = int(rget("channel_view_count", 0))
    st.session_state["vids"] = int(rget("channel_video_count", 0))

    desc_words, title_chars, tags_count, publish_hour, is_weekend, duration_min = (
        compute_text_time_features(row)
    )

    st.session_state["duration"] = float(duration_min)
    st.session_state["desc_words"] = int(desc_words)
    st.session_state["title_chars"] = int(title_chars)
    st.session_state["tags_count"] = int(tags_count)
    st.session_state["publish_hour"] = int(publish_hour)
    st.session_state["is_weekend"] = bool(is_weekend)

    cat_id = int(rget("category", -1))
    st.session_state["category_label"] = CATEGORY_LABELS.get(cat_id, "Music")

st.title("Interactive Viral Potential Tester")
st.write(
    "Play with channel + video metrics and see how our TubeScope classifier "
    "estimates the probability that a video will **survive > 1 day** on Trending."
)

model, encoder, model_columns, categories = get_artifacts()

st.sidebar.header("Input Parameters")

subs = st.sidebar.number_input(
    "Channel subscribers",
    min_value=0,
    value=st.session_state.get("subs", 1_000_000),
    step=10_000,
    key="subs",
)

views = st.sidebar.number_input(
    "Total channel views",
    min_value=0,
    value=st.session_state.get("views", 100_000_000),
    step=1_000_000,
    key="views",
)

vids = st.sidebar.number_input(
    "Total videos on channel",
    min_value=0,
    value=st.session_state.get("vids", 200),
    step=10,
    key="vids",
)

duration_min = st.sidebar.number_input(
    "Video duration (minutes)",
    min_value=0.0,
    value=st.session_state.get("duration", 5.0),
    step=0.5,
    key="duration",
)

desc_words = st.sidebar.number_input(
    "Description word count",
    min_value=0,
    value=st.session_state.get("desc_words", 100),
    step=5,
    key="desc_words",
)

title_chars = st.sidebar.number_input(
    "Title length (characters)",
    min_value=0,
    value=st.session_state.get("title_chars", 60),
    step=5,
    key="title_chars",
)

tags_count = st.sidebar.number_input(
    "Number of tags",
    min_value=0,
    value=st.session_state.get("tags_count", 10),
    step=1,
    key="tags_count",
)

publish_hour = st.sidebar.slider(
    "Publish hour (0–23, UTC)",
    min_value=0,
    max_value=23,
    value=st.session_state.get("publish_hour", 15),
    key="publish_hour",
)

is_weekend = st.sidebar.checkbox(
    "Published on weekend?",
    value=st.session_state.get("is_weekend", False),
    key="is_weekend",
)

category_label = st.sidebar.selectbox(
    "Category",
    list(CATEGORY_LABELS.values()),
    index=list(CATEGORY_LABELS.values()).index(
        st.session_state.get("category_label", "Music")
    ),
    key="category_label",
)

category_id = REV_CATEGORY_LABELS[category_label]

st.sidebar.markdown("---")
run_button = st.sidebar.button("Run Prediction")

st.subheader("Model Inputs Preview")

df_manual = build_manual_df(
    subs=subs,
    views=views,
    vids=vids,
    duration_min=duration_min,
    desc_words=desc_words,
    title_chars=title_chars,
    tags_count=tags_count,
    publish_hour=publish_hour,
    is_weekend=is_weekend,
    category=category_id,
)

st.dataframe(df_manual, hide_index=True, use_container_width=True)

st.markdown("---")

st.subheader("⬅ Input a custom video")
st.write("Enter custom parameters using the sidebar and click 'Run Prediction'")
st.subheader("OR")

# Load a real trending video
st.subheader("Load a real trending video")
st.write("Select a video from the Top 50 Trending, click 'Load to Tester', then 'Run Prediction'")

df_top, date_label = load_scored_top50()
df_top = df_top.reset_index(drop=True)
st.caption(f"Using latest snapshot: {date_label}")

title_series = df_top.get("title", df_top.get("snippet.title")).fillna("[untitled]")
channel_series = df_top.get("channelTitle", df_top.get("snippet.channelTitle")).fillna("[unknown]")
labels = title_series + " — " + channel_series

selected_idx = st.selectbox(
    "Copy metrics from a Top 50 video:",
    df_top.index,
    format_func=lambda i: labels.iloc[i],
)

row = df_top.loc[selected_idx]

video_id = row.get("id_x")
thumbnail_url = (
    row.get("snippet.thumbnails.medium.url")
    or row.get("snippet.thumbnails.high.url")
    or row.get("snippet.thumbnails.default.url")
)
video_url = f"https://www.youtube.com/watch?v={video_id}"

if thumbnail_url and video_id:
    st.markdown(
        f"""
        <a href="{video_url}" target="_blank">
            <img src="{thumbnail_url}" style="max-width: 380px; border-radius: 10px;">
        </a>
        """,
        unsafe_allow_html=True,
    )
else:
    st.caption("Thumbnail or video ID not available for this row.")

st.write("")

if st.button("Load to Tester"):
    st.session_state["pending_prefill"] = df_top.iloc[selected_idx].to_dict()
    st.rerun()

st.divider()
st.info("Set parameters in the sidebar and click **'Run Prediction'**.")
st.write("")

if run_button:
    st.divider()
    st.subheader("Prediction Result")

    try:
        X = prepare_features(df_manual, encoder, model_columns)
        probs = model.predict_proba(X)[:, 1]
        p_viral = float(probs[0])
        p_pct = p_viral * 100

        if p_viral >= 0.7:
            verdict = "Very likely viral"
            color = "🟢"
        elif p_viral >= 0.4:
            verdict = "Could go either way"
            color = "🟡"
        else:
            verdict = "Unlikely to be viral"
            color = "🔴"

        st.metric(
            label="Estimated Viral Probability ( >1 day on Trending )",
            value=f"{p_pct:.1f}%",
        )

        st.write(f"{color} **Verdict:** {verdict}")

        with st.expander("See model-ready feature vector"):
            st.write(X)

    except Exception as e:
        st.error("Something went wrong while scoring this input.")
        st.exception(e)