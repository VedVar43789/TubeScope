# pull_trending.py

import os
from pathlib import Path
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def get_youtube_client():
    """
    Return an authenticated YouTube Data API client.

    Locally:
      - Put YOUTUBE_API_KEY=... in a .env file at the repo root.
    On Streamlit Cloud:
      - Add YOUTUBE_API_KEY as an environment variable in the dashboard.
    """
    # Load .env for local development (no-op on Cloud if no .env)
    load_dotenv()

    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "YOUTUBE_API_KEY is not set. "
            "Set it in a local .env file or as an environment variable on Streamlit Cloud."
        )

    # Import here so the module can be imported even if googleapiclient is missing
    from googleapiclient.discovery import build

    return build("youtube", "v3", developerKey=api_key)


def get_paths():
    """
    Compute project-relative paths in a robust way.
    Assumes this file lives at repo_root/pull_trending.py
    and data folders live under repo_root/data and repo_root/data_processed.
    """
    root = Path(__file__).resolve().parent  # repo root if pull_trending.py is there
    data_dir = root / "data"
    processed_dir = root / "data_processed"

    data_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    return root, data_dir, processed_dir


# ---------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------
def main():
    youtube = get_youtube_client()
    root, data_dir, processed_dir = get_paths()

    # ==============================================================
    # STEP 1: Get Top 50 Trending Videos
    # ==============================================================
    print("\n[1/4] Fetching trending videos...")

    request = youtube.videos().list(
        part="snippet,contentDetails,statistics,status",
        chart="mostPopular",
        regionCode="US",
        maxResults=50,
    )
    response = request.execute()

    video_df = pd.json_normalize(response["items"])

    video_df = video_df.rename(
        columns={
            "snippet.title": "title",
            "snippet.channelTitle": "channelTitle",
            "contentDetails.duration": "duration",
            "snippet.description": "description",
            "snippet.tags": "tags",
            "snippet.categoryId": "category",
        }
    )

    print(f"Fetched {len(video_df)} trending videos")

    # ==============================================================
    # STEP 2: Get Channel Metrics
    # ==============================================================
    print("\n[2/4] Fetching channel metrics...")

    channel_ids = video_df["snippet.channelId"].unique().tolist()
    channel_stats = []

    batch_size = 50
    for i in range(0, len(channel_ids), batch_size):
        batch = channel_ids[i : i + batch_size]

        channel_request = youtube.channels().list(
            part="statistics",
            id=",".join(batch),
        )
        channel_response = channel_request.execute()

        for item in channel_response["items"]:
            channel_stats.append(
                {
                    "channel_id": item["id"],
                    "channel_subscriber_count": int(
                        item["statistics"].get("subscriberCount", 0)
                    ),
                    "channel_video_count": int(
                        item["statistics"].get("videoCount", 0)
                    ),
                    "channel_view_count": int(
                        item["statistics"].get("viewCount", 0)
                    ),
                }
            )

    channel_df = pd.DataFrame(channel_stats)
    print(f"Fetched stats for {len(channel_df)} channels")

    # ==============================================================
    # STEP 3: Merge Channel Metrics into Video Data
    # ==============================================================
    print("\n[3/4] Merging channel metrics with video data...")

    video_df = video_df.merge(
        channel_df,
        left_on="snippet.channelId",
        right_on="channel_id",
        how="left",
    )

    print("   Channel metrics merged")
    print(
        f"   Sample channel_subscriber_count: "
        f"{video_df['channel_subscriber_count'].head(3).tolist()}"
    )

    # ==============================================================
    # STEP 4: Get Category Names
    # ==============================================================
    print("\n[4/4] Mapping category names...")

    map_request = youtube.videoCategories().list(
        part="snippet",
        regionCode="US",
    )
    map_response = map_request.execute()

    category_df = pd.json_normalize(map_response["items"])
    category_df["id"] = category_df["id"].astype(int)

    # Ensure we always have an int category id column
    video_df["snippet.categoryId"] = video_df.get("snippet.categoryId", -1)
    video_df["snippet.categoryId"] = (
        video_df["snippet.categoryId"].fillna(-1).astype(int)
    )

    video_df = video_df.merge(
        category_df[["id", "snippet.title"]],
        left_on="snippet.categoryId",
        right_on="id",
        how="left",
    ).rename(columns={"snippet.title_y": "category_name"})

    print("   Categories mapped")

    # ==============================================================
    # STEP 5: Save Today's Data
    # ==============================================================
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    snapshot_path = data_dir / f"{timestamp}.csv"
    video_df.to_csv(snapshot_path, index=False)

    print(f"\nSaved snapshot: {snapshot_path}")

    # ==============================================================
    # STEP 6: Combine All Historical Data (with channel metrics)
    # ==============================================================
    print("\nCombining all historical data with channel metrics...")

    output_filename = processed_dir / "main_NEW.csv"

    csv_files = [
        p
        for p in data_dir.glob("*.csv")
        if p.name not in {"main_OLD.csv"} and p != output_filename
    ]

    if csv_files:
        all_dfs = []
        for file in csv_files:
            df_temp = pd.read_csv(file)
            if "channel_subscriber_count" in df_temp.columns:
                all_dfs.append(df_temp)

        if all_dfs:
            combined_df = pd.concat(all_dfs, ignore_index=True)
            combined_df.to_csv(output_filename, index=False)
            print(f"   Combined {len(all_dfs)} files into {output_filename}")
            print(f"   Total rows: {len(combined_df)}")
        else:
            print("No files with channel metrics found yet.")
    else:
        print("No CSV files found in data/.")


if __name__ == "__main__":
    main()
