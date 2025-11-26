from pathlib import Path
from datetime import datetime
import subprocess
import sys
import joblib
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
MODELS_DIR = ROOT / "models"

MODEL_FILE = MODELS_DIR / "viral_prediction_model.pkl"
ENCODER_FILE = MODELS_DIR / "category_encoder.pkl"
MODEL_COLS_FILE = MODELS_DIR / "model_columns.pkl"


CATEGORY_LABELS = {
    1: "Film & Animation",
    2: "Autos & Vehicles",
    10: "Music",
    15: "Pets & Animals",
    17: "Sports",
    19: "Travel & Events",
    20: "Gaming",
    22: "People & Blogs",
    23: "Comedy",
    24: "Entertainment",
    25: "News & Politics",
    26: "Howto & Style",
    27: "Education",
    28: "Science & Technology",
    29: "Nonprofits & Activism",
}

REV_CATEGORY_LABELS = {v: k for k, v in CATEGORY_LABELS.items()}

FEATURE_COLS = [
    "channel_subscriber_count",
    "channel_video_count",
    "channel_view_count",
    "duration",
    "description_word_count",
    "title_char_count",
    "tags_count",
    "publish_hour",
    "is_weekend",
    "category",
]

NUMERIC_COLS = [
    "channel_subscriber_count",
    "channel_video_count",
    "channel_view_count",
    "duration",
    "description_word_count",
    "title_char_count",
    "tags_count",
    "publish_hour",
    "is_weekend",
]

CAT_COLS = ["category"]


def load_artifacts():
    model = joblib.load(MODEL_FILE)
    encoder = joblib.load(ENCODER_FILE)
    model_columns = joblib.load(MODEL_COLS_FILE)
    return model, encoder, model_columns


def get_latest_snapshot():
    if not DATA_DIR.exists():
        raise FileNotFoundError("data/ directory not found at repo root.")

    csv_files = sorted(
        f
        for f in DATA_DIR.glob("*.csv")
        if f.name != "mainNEW.csv" and not f.name.startswith("main_OLD")
    )
    if not csv_files:
        raise FileNotFoundError("No daily snapshot CSVs found in data/.")

    latest_path = csv_files[-1]
    df = pd.read_csv(latest_path)

    stem = latest_path.stem
    try:
        dt = datetime.strptime(stem, "%Y-%m-%d_%H-%M-%S")
        label = dt.strftime("%b %d, %Y — %I:%M %p")
    except Exception:
        label = stem

    return df, label, latest_path.name


def iso_to_minutes(duration):
    if isinstance(duration, (int, float)):
        return float(duration)
    if not isinstance(duration, str):
        return 0.0

    duration = duration.replace("PT", "")
    h = m = s = 0

    if "H" in duration:
        h, duration = duration.split("H")[0], duration.split("H")[1] if "H" in duration else ""
        h = int(h)

    if "M" in duration:
        m, duration = duration.split("M")[0], duration.split("M")[1] if "M" in duration else ""
        m = int(m)

    if "S" in duration:
        s = int(duration.replace("S", ""))

    return h * 60 + m + s / 60.0


def prepare_features(df_raw, encoder, model_columns):
    df = df_raw.copy()

    if "title" not in df and "snippet.title" in df:
        df["title"] = df["snippet.title"]
    if "description" not in df and "snippet.description" in df:
        df["description"] = df["snippet.description"]
    if "tags" not in df and "snippet.tags" in df:
        df["tags"] = df["snippet.tags"]
    if "publishedAt" not in df and "snippet.publishedAt" in df:
        df["publishedAt"] = df["snippet.publishedAt"]
    if "category" not in df and "snippet.categoryId" in df:
        df["category"] = df["snippet.categoryId"]

    if "duration" in df:
        if df["duration"].astype(str).str.startswith("PT").any():
            df["duration"] = df["duration"].apply(iso_to_minutes)
        df["duration"] = pd.to_numeric(df["duration"], errors="coerce").fillna(0)
    else:
        df["duration"] = 0.0

    if "description_word_count" not in df:
        df["description_word_count"] = (
            df.get("description", "").fillna("").astype(str).str.split().str.len()
        )
    if "title_char_count" not in df:
        df["title_char_count"] = df.get("title", "").fillna("").astype(str).str.len()
    if "tags_count" not in df:
        tags = df.get("tags", "")

        def _count(x):
            if isinstance(x, list):
                return len(x)
            if not x:
                return 0
            return len(str(x).split(","))

        df["tags_count"] = tags.apply(_count)

    if "publish_hour" not in df or "is_weekend" not in df:
        pub = pd.to_datetime(df.get("publishedAt"), errors="coerce", utc=True)
        if pub.notna().any():
            pub = pub.dt.tz_localize(None)
            df["publish_hour"] = pub.dt.hour.fillna(-1).astype(int)
            df["is_weekend"] = pub.dt.dayofweek.isin([5, 6]).astype(int)
        else:
            df["publish_hour"] = pd.to_numeric(df.get("publish_hour", -1), errors="coerce").fillna(-1)
            df["is_weekend"] = pd.to_numeric(df.get("is_weekend", 0), errors="coerce").fillna(0)

    if "category" not in df:
        raise ValueError("Expected 'category' column in df_raw.")

    encoded = encoder.transform(df[["category"]].astype(str))
    cat_cols = encoder.get_feature_names_out(["category"])
    enc_df = pd.DataFrame(encoded, columns=cat_cols, index=df.index)
    df = pd.concat([df, enc_df], axis=1)

    defaults = {
        "channel_subscriber_count": 0,
        "channel_video_count": 0,
        "channel_view_count": 0,
        "duration": 0,
        "description_word_count": 0,
        "title_char_count": 0,
        "tags_count": 0,
        "publish_hour": -1,
        "is_weekend": 0,
    }
    for col, default in defaults.items():
        df[col] = pd.to_numeric(df.get(col, default), errors="coerce").fillna(default)

    missing_cols = [c for c in model_columns if c not in df]
    for m in missing_cols:
        df[m] = 0

    return df[model_columns].copy()


def score_latest_batch(df_raw):
    model, encoder, model_columns = load_artifacts()
    X = prepare_features(df_raw, encoder, model_columns)
    probs = model.predict_proba(X)[:, 1]
    out = df_raw.copy()
    out["viral_prob"] = probs
    return out


def run_pull_trending():
    """
    Run pull_trending.py at repo root as a subprocess.

    Assumes:
      - pull_trending.py is located at ROOT / "pull_trending.py"
      - It writes data/YYYY-MM-DD.csv and updates data_processed/main_NEW.csv
    """
    script = ROOT / "pull_trending.py"
    if not script.exists():
        return False, f"pull_trending.py not found at {script}"

    try:
        result = subprocess.run(
            [sys.executable, str(script)],  # 👈 use the SAME Python as Streamlit
            cwd=str(ROOT),                  # 👈 run from repo root so `data/` works
            capture_output=True,
            text=True,
            check=True,
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr or str(e)