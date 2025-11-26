import streamlit as st
st.set_page_config(layout="centered")

from pathlib import Path

STATIC_DIR = Path(__file__).resolve().parents[1] / "static"
EDA_DIR = STATIC_DIR / "TubeScope_EDA"

st.title("Models and Visualizations")

st.markdown(
    """
    TubeScope analyzes historical YouTube Trending snapshots to understand
    how videos rise and decay in visibility and which ones are likely to
    survive beyond the 24-hour cliff. This page walks through the core
    exploratory data analysis and model behavior.
    """
)

show_explanations = st.checkbox("Show detailed explanations", value=True)

tab_cats, tab_lifecycle, tab_timing, tab_model, tab_features, tab_content = st.tabs(
    [
        "Category Behavior",
        "View & Trending Lifecycles",
        "Posting Time",
        "Model Performance",
        "Feature Importance",
        "Content & Tags",
    ]
)

with tab_cats:
    st.subheader("Engagement and Category Presence")

    col1, col2 = st.columns(2)

    with col1:
        st.image(
            EDA_DIR / "Average Engagement Score by Category.png",
            use_container_width=True,
        )
        if show_explanations:
            st.markdown(
                """
                **Average Engagement Score by Category**

                Average engagement score (likes and comments normalized by views)
                for each category. It highlights which niches generate the most
                interaction per view rather than just raw volume.
                """
            )

    with col2:
        st.image(
            EDA_DIR / "Categories in Trending (Linear Scale).png",
            use_container_width=True,
        )
        if show_explanations:
            st.markdown(
                """
                **Categories in Trending (Linear Scale)**

                Raw counts of how often each category appears on Trending.
                Gaming, Music, and Entertainment dominate the feed in absolute
                terms.
                """
            )

    st.markdown("---")

    st.image(
        EDA_DIR / "Categories in Trending (Log Scale).png",
        use_container_width=True,
    )
    if show_explanations:
        st.markdown(
            """
            **Categories in Trending (Log Scale)**

            The same counts on a log scale. This view makes the long tail of
            smaller categories visible and comparable to the largest ones.
            """
        )

with tab_lifecycle:
    st.subheader("How Trending Videos Rise and Decay")

    st.image(
        EDA_DIR / "Average Video View Trajectory.png",
        use_container_width=True,
    )
    if show_explanations:
        st.markdown(
            """
            **Views per Day vs Days Since Published (Average Trajectory)**

            Average daily views for Trending videos over the first two weeks
            after publication. Most videos peak within the first few days and
            then decay quickly, motivating a classification target
            (survive > 24 hours) rather than a pure regression task.
            """
        )

    st.markdown("---")

    st.image(EDA_DIR / "category_survival.png", use_container_width=True)
    if show_explanations:
        st.markdown(
            """
            **Kaplan–Meier: Category Trending Survival**

            Survival curves track the probability that a video is still on
            Trending after a given number of days, both overall and by
            category. Music and Gaming tend to stay visible slightly longer,
            but most videos fall off within a few days.
            """
        )

with tab_timing:
    st.subheader("Effect of Posting Time")

    st.image(EDA_DIR / "trend_vs_publish_hour.png", use_container_width=True)
    if show_explanations:
        st.markdown(
            """
            **Average Trending Duration by Posting Hour**

            Average total days on Trending for videos published at each hour
            of the day (0–23). Morning uploads, especially around 8–10, tend
            to survive on Trending longer than late-evening uploads. This is
            why `publish_hour` and `is_weekend` are included as temporal
            features in the model.
            """
        )

with tab_model:
    st.subheader("Classification Performance")

    st.image(EDA_DIR / "confusion_matrix.png", use_container_width=True)
    if show_explanations:
        st.markdown(
            """
            **Confusion Matrix: Detecting Viral Videos**

            The confusion matrix summarizes how well the classifier
            distinguishes between Standard videos and Viral videos (those
            that survive past 24 hours on Trending). It shows true positives,
            false positives, true negatives, and false negatives, and makes
            the precision/recall tradeoff visible given that most videos drop
            off after one day.
            """
        )

    st.markdown("---")

    st.image(
        EDA_DIR / "Correlational Heatmap of Numeric Features.png",
        use_container_width=True,
    )
    if show_explanations:
        st.markdown(
            """
            **Correlation Heatmap of Numerical Features**

            Correlations between numeric features such as views, likes,
            comments, channel metrics, and total days trending. Strong
            correlations between channel view count and subscriber count
            reveal redundancy, while weak correlations with engagement score
            and duration show where new signal comes from.
            """
        )

with tab_features:
    st.subheader("What Drives the Prediction")

    st.image(EDA_DIR / "feature_importance.png", use_container_width=True)
    if show_explanations:
        st.markdown(
            """
            **Top 15 Features for Viral Video Prediction**

            Feature importance scores from the trained model. Duration and
            channel-level metrics are the strongest predictors, followed by
            text and category features such as description length, title
            length, tag count, and indicators for categories like Music and
            Gaming.
            """
        )

with tab_content:
    st.subheader("Content Structure and Tags")

    col1, col2 = st.columns(2)

    with col1:
        st.image(
            EDA_DIR / "Distribution of Video Durations.png",
            use_container_width=True,
        )
        if show_explanations:
            st.markdown(
                """
                **Distribution of Video Durations**

                Histogram of video durations for Trending videos. The heavy
                tail indicates that both short-form clips and long-form
                content can reach Trending, with longer videos providing more
                potential watch time.
                """
            )

    with col2:
        st.image(
            EDA_DIR / "Most Common Tags.png",
            use_container_width=True,
        )
        if show_explanations:
            st.markdown(
                """
                **Most Common Tags**

                The most frequently used tags across Trending videos. Many
                of the top tags are gaming-related, showing that gaming
                communities drive a large share of Trending content.
                """
            )

with st.expander("How TubeScope uses these insights", expanded=False):
    st.markdown(
        """
        Together, these visualizations show that Trending success is shaped by:
        category, creator scale, engagement efficiency, posting time, and
        content structure. TubeScope combines these signals in a classifier
        that predicts whether a video will survive beyond 24 hours on
        Trending, helping creators and sponsors prioritize which uploads
        deserve the most attention.
        """
    )