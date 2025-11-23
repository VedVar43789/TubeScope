# 📺 TubeScope  
### *Lifecycle Analytics of YouTube Trending Videos*  

**Most YouTube videos trend for just one day. TubeScope predicts which ones will go viral for longer.**
Using machine learning and the YouTube Data API, we analyze channel metrics, video metadata, and temporal patterns to identify videos with sustained trending potential, catching 2 out of 3 viral hits before they peak.

---
## Project Overview  

> **Goal:** Build predictive visualizations and metrics that estimate how long a trending video will remain relevant, helping creators prioritize which videos to focus promotions or sponsorships on based on category and channel factors.


## Key Features
- **Viral Video Detection** - Predicts which videos will trend >1 day
- **Daily Data Collection** - Automated YouTube API pipeline
- **ML Model** - Random Forest with ~70% recall, ~50% precision
- **Survival Analysis** - Kaplan-Meier curves showing dropoff patterns
- **Interactive Dashboard** - Streamlit web application
- **Production Ready** - Trained models with proper feature encoding


---

## Tech Stack  

| Component | Technology |
|------------|-------------|
| **API & Data** | YouTube Data API v3 (`videos.list`, `videoCategories.list`, `channels.list`) |
| **Storage** | Daily CSV snapshots |
| **Analysis** | pandas, numpy, matplotlib, seaborn, lifelines |
| **Web App** | Streamlit |
| **Version Control** | Git + GitHub |
| **Predictive Modeling** | scikit-learn (Random Forest Classifier)|

---

## Dataset  

TubeScope takes a hybrid approach: we train on a Kaggle dataset (for time limitations) and test daily pulls on Streamlit.

| Source | Description |
|--------|-------------|
| **YouTube Data API v3** | Fetches stats (views, likes, comments, etc.) for trending videos using `videos.list` |
| **Kaggle Dataset** |[Kaggle Dataset](https://www.kaggle.com/datasets/canerkonuk/youtube-trending-videos-global) Contains 10,000 historical data from the Youtube trending data (downloaded Nov 20th, static dataset)
| **Trending Videos Feed (U.S.)** | Pulled via API access `pull_trending.py` |
| **Category Lookup Table** | `videoCategories.list` endpoint used to tag videos (Music, Gaming, News, etc.) |

Each day’s trending data is stored as a **timestamped snapshot**, forming a **custom time-series dataset** of trending videos and their lifecycle.

---

## Workflow  

1. **Daily Pull:** Fetch trending videos and metadata via API  
2. **Store Snapshots:** Save as `/data/YYYY-MM-DD.csv` 
3. **Merge Data:** Combine daily files into lifecycle dataset (`main_new.csv`)
4. **EDA:** 
5. **Analyze:**  
   - Compute view trajectories and time-on-trending  
   - Run survival analysis to estimate category half-lives  
6. **Predict:** If a video is a one hit wonder (trends for only one day) or a viral video (trends for more than a day) 
7. **Visualize:** View results interactively via Streamlit dashboard

---

## Results


