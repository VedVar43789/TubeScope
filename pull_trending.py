import os
from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime

# print("="*60)
# print("TUBESCOPE: YouTube API Data Collection (WITH CHANNEL METRICS)")
# print("="*60)

from dotenv import load_dotenv
# Load local .env when developing
load_dotenv()

api_key = os.environ["YOUTUBE_API_KEY"]
youtube = build("youtube", "v3", developerKey=api_key)

# ============================================================================
# STEP 1: Get Top 50 Trending Videos
# ============================================================================

print("\n[1/4] Fetching trending videos...")

request = youtube.videos().list(
    part="snippet,contentDetails,statistics,status",
    chart="mostPopular",
    regionCode="US",
    maxResults=50
)

response = request.execute()
video_df = pd.json_normalize(response["items"])

video_df = video_df.rename(columns={
    'snippet.title': 'title',
    'snippet.channelTitle': 'channelTitle',
    'contentDetails.duration': 'duration',
    'snippet.description': 'description',
    'snippet.tags': 'tags',
    'snippet.categoryId': 'category'
})

print(f"Fetched {len(video_df)} trending videos")

# ============================================================================
# STEP 2: Get Channel Metrics 
# ============================================================================

print("\n[2/4] Fetching channel metrics...")

# Extract unique channel IDs
channel_ids = video_df['snippet.channelId'].unique().tolist()

# Batch request for channel stats (can request up to 50 at once)
channel_stats = []

# YouTube API allows max 50 IDs per request
batch_size = 50
for i in range(0, len(channel_ids), batch_size):
    batch = channel_ids[i:i+batch_size]
    
    channel_request = youtube.channels().list(
        part='statistics',
        id=','.join(batch)
    )
    
    channel_response = channel_request.execute()
    
    for item in channel_response['items']:
        channel_stats.append({
            'channel_id': item['id'],
            'channel_subscriber_count': int(item['statistics'].get('subscriberCount', 0)),
            'channel_video_count': int(item['statistics'].get('videoCount', 0)),
            'channel_view_count': int(item['statistics'].get('viewCount', 0))
        })

# Convert to DataFrame
channel_df = pd.DataFrame(channel_stats)

print(f"Fetched stats for {len(channel_df)} channels")

# ============================================================================
# STEP 3: Merge Channel Metrics into Video Data
# ============================================================================

print("\n[3/4] Merging channel metrics with video data...")

# Merge channel stats into video dataframe
video_df = video_df.merge(
    channel_df,
    left_on='snippet.channelId',
    right_on='channel_id',
    how='left'
)

print(f"   Channel metrics merged")
print(f"   Sample channel_subscriber_count: {video_df['channel_subscriber_count'].head(3).tolist()}")

# ============================================================================
# STEP 4: Get Category Names
# ============================================================================

print("\n[4/4] Mapping category names...")

# Step 4: Map category names
map_request = youtube.videoCategories().list(
    part="snippet",
    regionCode="US"
)
map_response = map_request.execute()

category_df = pd.json_normalize(map_response["items"])
category_df['id'] = category_df['id'].astype(int)

# Ensure we always have an int column
video_df['snippet.categoryId'] = video_df.get('snippet.categoryId', -1)
video_df['snippet.categoryId'] = video_df['snippet.categoryId'].fillna(-1).astype(int)

video_df = video_df.merge(
    category_df[['id', 'snippet.title']],
    left_on='snippet.categoryId',
    right_on='id',
    how='left'
).rename(columns={'snippet.title_y': 'category_name'})

print(f"   Categories mapped")

# ============================================================================
# STEP 5: Save Today's Data
# ============================================================================

timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"data/{timestamp}.csv"
video_df.to_csv(filename, index=False)

print(f"\n✅ Saved: {filename}")

# ============================================================================
# STEP 6: Combine All Historical Data (NEW DATA ONLY)
# ============================================================================

print("\n Combining all historical data with channel metrics...")

folder_path = 'data'
output_filename = 'data_processed/main_NEW.csv'  # Separate file for clean data

# Find all CSV files
all_files = os.listdir(folder_path)
csv_files = [os.path.join(folder_path, f) for f in all_files 
             if f.endswith('.csv') and f != output_filename and f != 'main_OLD.csv']

if csv_files:
    all_dfs = []
    for file in csv_files:
        df_temp = pd.read_csv(file)
        # Only include if it has channel metrics
        if 'channel_subscriber_count' in df_temp.columns:
            all_dfs.append(df_temp)
    
    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        combined_df.to_csv(output_filename, index=False)
        print(f"   ✓ Combined {len(all_dfs)} files into {output_filename}")
        print(f"   Total rows: {len(combined_df)}")
    else:
        print("No files with channel metrics found yet")
else:
    print("No CSV files found")