# 📺 TubeScope  
### *Lifecycle Analytics of YouTube Trending Videos*  

TubeScope explores what makes YouTube videos go viral — and how long that virality lasts.  
By tracking **daily trending videos** using the **YouTube Data API**, we analyze how long videos from different content categories (like Music, Gaming, or News) stay on the trending list, visualize their popularity curves, and even **predict** how long new videos might trend.

---

## 🧭 Project Overview  

> **Goal:** Build visualizations and metrics that show how long videos stay popular, how that varies by category, and predict the duration of virality.

### 🌟 Core Features  
- 📡 Automated daily data collection using YouTube Data API  
- 🕒 Time-series tracking of trending videos  
- 📊 Survival analysis (Kaplan-Meier) for category “half-life”  
- 🔮 Predictive modeling of video lifespan  
- 🌐 Interactive Streamlit dashboard for analytics & prediction  

**Difficulty Level:** Easy → Medium  

---

## 🧰 Tech Stack  

| Component | Technology |
|------------|-------------|
| **API & Data** | YouTube Data API v3 (`videos.list`, `videoCategories.list`) |
| **Storage** | Daily CSV snapshots |
| **Automation** | Launchd for cron job |
| **Analysis** | pandas, numpy, matplotlib, seaborn, lifelines |
| **Web App** | Streamlit |
| **Version Control** | Git + GitHub |

---

## 📚 Dataset  

Unlike static datasets, TubeScope builds its own dataset dynamically:  

| Source | Description |
|--------|-------------|
| **YouTube Data API v3** | Fetches stats (views, likes, etc.) for trending videos using `videos.list` |
| **Trending Videos Feed (U.S.)** | Pulled via API access `pull_request` |
| **Category Lookup Table** | `videoCategories.list` endpoint used to tag videos (Music, Gaming, News, etc.) |

Each day’s trending data is stored as a **timestamped snapshot**, forming a **custom time-series dataset** of trending videos and their lifecycle.

---

## 📈 Example Workflow  

1. **Daily Pull:** Fetch trending videos and metadata via API  
2. **Store Snapshots:** Save as `/data/YYYY-MM-DD.csv`  
3. **Merge Data:** Combine daily files into lifecycle dataset  
4. **Analyze:**  
   - Compute view trajectories and time-on-trending  
   - Run survival analysis to estimate category half-lives  
5. **Predict:** Estimate a new video’s expected trending duration  
6. **Visualize:** View results interactively via Streamlit dashboard  
