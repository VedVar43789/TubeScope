# 📺 TubeScope  
### *Lifecycle Analytics of YouTube Trending Videos*  

**Most YouTube videos trend for just one day. TubeScope predicts which ones will go viral for longer.**
Using machine learning and the YouTube Data API, we analyze channel metrics, video metadata, and temporal patterns to identify videos with sustained trending potential, catching 2 out of 3 viral hits before they peak.

---
## Project Overview  

> **Goal:** Predict which YouTube trending videos will achieve sustained virality (>1 day trending) using machine learning, helping content creators and marketers identify high-potential content before it peaks.



## Key Features
- **Viral Video Detection** - Predicts which videos will trend >1 day
- **Daily Data Collection** - Automated YouTube API pipeline
- **ML Model** - Random Forest with 68.33% recall, 49.48% precision
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
## 📊 Model Performance

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **Accuracy** | 82.35% | Overall correct predictions |
| **Precision** | 48.83% | 2.9x better than 17% baseline |
| **Recall** | 68.33% | Catches 2 out of 3 viral videos |
| **F1-Score** | 57.4% | Balanced performance |

**Key Insight:** We optimized for recall to catch viral videos early, accepting slightly lower precision as a trade-off for early trend detection.

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

## 🔄 How TubeScope Works

### **For Users:**
1. **Refresh Data** - Click button to fetch today's 50 U.S. trending videos
2. **View Top 5** - See videos with highest viral probability
3. **Deep Dive** - Select any video from dropdown to see detailed analysis
4. **Get Insights** - Understand which features drive viral predictions
5. **Customize** - Customize your own inputs to see how well a video can survive the "24-Hour Cliff"

### **Behind the Scenes:**
1. **Data Collection** - Daily YouTube API pulls (50 trending videos + channel metrics)
2. **Feature Engineering** - Extract channel authority, video metadata, temporal patterns.
3. **ML Prediction** - Random Forest Classifier (trained on 10k historical videos)
4. **Live Dashboard** - Streamlit displays ranked predictions and video stats

**Model Details:**
- **Training:** Kaggle dataset (10k videos) with stratified 80/20 split
- **Features:** Channel metrics (subscribers, videos, views), video metadata (duration, tags, description word count), temporal patterns (upload time, day of week)
- **Optimization:** Class-weighted for imbalanced data (83/17 viral/standard ratio)



**Visualize:** View results interactively via Streamlit dashboard

---

## Results

**Streamlit dashboard:** [TubeScope Streamlit](https://tubescopeds3.streamlit.app/)

### **Key Findings**
- **Duration** is the #1 predictor
- **Categories** such as Gaming, Music, and Entertainment tend to perform better
- **Channel size/metrics** heavily dictates a video's virality
- **Upload timing** matters, posting at 12PM is stronger than at 2AM

### **Model Journey**
1. **Started with regression** → R² = 0.95 (data leakage!)
2. **Fixed leakage** → R² went negative (too noisy)
3. **Kaplan-Meier analysis** → 83% dropoff at 24 hours
4. **Pivoted to classification** → 68.33% recall, 48.83% precision ✅

