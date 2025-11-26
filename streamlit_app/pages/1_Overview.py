import streamlit as st
from pathlib import Path

STATIC_DIR = Path(__file__).resolve().parents[1] / "static"

st.set_page_config(layout="centered")


def main():
    st.title("Overview")

    st.markdown(
        """
## What is TubeScope

TubeScope is a data collection and machine learning platform that tracks YouTube Trending videos
and predicts whether a video will remain on the trending page for more than one day.

In the YouTube trending ecosystem, a strong majority of videos leave the trending page after a single day.
The project focuses on detecting videos that break this pattern, which we call viral videos.
"""
    )

    st.subheader("Problem framing")
    st.markdown(
        """
The original goal was to estimate the total number of days a video stays on the trending page using a regression model.
However, the distribution of the target variable is highly imbalanced: most videos appear exactly once.
This results in poor regression performance and models that predict a single day for nearly all samples.

After correcting data leakage, the regression approach consistently failed because the underlying question is categorical:
whether a video survives the twenty-four hour drop-off point. This observation led to a pivot.

The final formulation is binary:

- viral = 1 if a video remains on trending longer than one day  
- viral = 0 otherwise
"""
    )

    st.subheader("Motivation for the classification approach")
    st.markdown(
        """
The data exhibits a natural threshold at a single day of trending.
Treating the problem as classification removes noise created by long-tail survival durations
and makes model performance interpretable and operationally meaningful.

Creators, analysts, or sponsorship partners benefit more from determining whether a video is likely to persist on trending
than from predicting whether it will last three versus four days.
"""
    )

    st.subheader("Survival dynamics of trending videos")

    km_plot = STATIC_DIR / "survival_curve.png"
    if km_plot.exists():
        st.image(str(km_plot), use_container_width=True)
    else:
        st.info("Place `static/survival_curve.png` in the project to display the survival curve.")

    st.markdown(
        """
A Kaplan–Meier estimate shows a steep decline in survival probability at day one.
Beyond that point, the curve flattens and differentiates the minority of videos that stay on trending longer.
This single structural feature of the dataset is the foundation of the project.
"""
    )

    st.subheader("Model summary")
    st.markdown(
        """
TubeScope uses a RandomForestClassifier with balanced class weights.
Channel-level metrics, duration, textual complexity, and video category are converted into structured features.
Categorical variables are encoded using a fitted one-hot encoder trained on historical data.

Performance on the viral class:
- precision approximately 49 percent
- recall approximately 68 percent

This is significantly more effective than random guessing, which would correctly identify viral videos about 17 percent of the time.
"""
    )

    st.subheader("Navigation")
    st.markdown(
        """
The other pages provide deeper context and tooling:

- Models and Visualizations: exploratory analysis, survival distributions, model performance, and feature importance.
- Live Trending Analyzer: fetches current trending videos, scores them, and displays a ranked leaderboard with details.
- Interactive Model Tester: allows manual simulation of channel and video characteristics or copying real trending samples.
"""
    )


if __name__ == "__main__":
    main()