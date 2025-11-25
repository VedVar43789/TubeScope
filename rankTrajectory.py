import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data_processed/subset_newest_10k.csv")

df["snapshot_date"] = pd.to_datetime(df["video_trending__date"], format="%Y.%m.%d")
df["region"] = df["video_trending_country"]

df["rank"] = df.groupby(
    ["snapshot_date", "region"]
)["video_view_count"].rank(ascending=False, method="first")

key = ["video_id", "region"]
first_seen = df.groupby(key)["snapshot_date"].transform("min")
df["d_since_first"] = (df["snapshot_date"] - first_seen).dt.days

max_days = 14
df = df[(df["d_since_first"] >= 0) & (df["d_since_first"] <= max_days)]

curve = df.groupby("d_since_first")["rank"].mean()

plt.figure(figsize=(8, 5))
plt.plot(curve.index, curve.values, marker="o")
plt.gca().invert_yaxis()
plt.xlabel("Days since first Trending")
plt.ylabel("Average Rank")
plt.title("Average Rank Trajectory")
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig("TubeScope_Viz_V1/new_rank_trajectory.png", dpi=200, bbox_inches="tight")