#rag/youtube_rag.py
"""
YouTube travel vlog RAG module.

IMPORTANT: Pinecone and the sentence-transformer embedding model are loaded
LAZILY (only on first Online-mode call) so that importing this module - and
any agent that imports it - never requires network access, an API key, or a
model download when running in Demo mode.
"""
import os
from datetime import datetime

PINECONE_ENV = "us-east-1"
PINECONE_INDEX = "youtube-travel-blogs"
PINECONE_HOST = os.getenv("PINECONE_HOST", "https://default-pinecone-host.svc.aped-4627-b74a.pinecone.io")

# Module-level singletons, created on first use only
_index = None
_embedder = None


def _get_index():
    """Lazily initialize and cache the Pinecone index client."""
    global _index
    if _index is None:
        import pinecone
        pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=PINECONE_ENV)
        _index = pinecone.Index(PINECONE_INDEX, host=PINECONE_HOST)
    return _index


def _get_embedder():
    """Lazily initialize and cache the sentence-transformer embedding model."""
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        model_name = os.getenv("YOUTUBE_RAG_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        _embedder = SentenceTransformer(model_name)
    return _embedder


# -------------------------------
# Filters
# -------------------------------
def _is_valid_video(video):
    """Apply freshness + popularity filters."""
    if video.get("views", 0) < 50000:
        return False
    upload_date = video.get("upload_date")
    if not upload_date:
        return False
    if (datetime.now() - upload_date).days > 180:
        return False
    return True


# -------------------------------
# Add Videos (Batch)
# -------------------------------
def add_videos_to_index(videos, mode="Online"):
    """
    videos: list of dicts with keys:
        video_id, title, description, transcript, views, upload_date, destination, tags, creator
    mode: "Online" or "Demo"
    """
    if mode == "Demo":
        print("🎬 Demo Mode: Skipping Pinecone upsert, returning stub.")
        return [{"demo": f"Stubbed video for {v['destination']}"} for v in videos]

    valid_videos = [v for v in videos if _is_valid_video(v)]
    if not valid_videos:
        print("⚠️ No valid videos after filtering.")
        return []

    embedder = _get_embedder()
    index = _get_index()

    texts = [
        f"{v['title']} {v['description']} {v.get('transcript','')}"
        for v in valid_videos
    ]
    vectors = embedder.encode(texts, batch_size=8).tolist()

    upserts = []
    for v, vec in zip(valid_videos, vectors):
        upserts.append((
            v["video_id"],
            vec,
            {
                "title": v["title"],
                "description": v["description"],
                "destination": v["destination"],
                "tags": v.get("tags", []),
                "creator": v["creator"],
                "views": v["views"],
                "upload_date": str(v["upload_date"])
            }
        ))
    index.upsert(upserts)
    print(f"✅ Upserted {len(upserts)} videos into Pinecone.")
    return upserts


# -------------------------------
# Query RAG
# -------------------------------
def query_videos(destination, interests, top_k=5, mode="Online"):
    """
    Query Pinecone for relevant travel vlogs.
    destination: str (e.g., "Rome")
    interests: list of str (e.g., ["food", "culture"])
    mode: "Online" or "Demo"
    """
    if mode == "Demo":
        return {
            "insights": [
                f"🎥 Demo vlog: {destination} street food highlights",
                f"🎥 Demo vlog: {destination} cultural walking tour"
            ]
        }

    try:
        embedder = _get_embedder()
        index = _get_index()

        query_text = f"{destination} travel {', '.join(interests)}"
        query_vector = embedder.encode([query_text])[0].tolist()

        results = index.query(vector=query_vector, top_k=top_k, include_metadata=True)
        return results
    except Exception as e:
        print(f"⚠️ YouTube RAG query failed, falling back to empty results: {e!r}")
        return {"matches": []}


# -------------------------------
# Summarization Agent
# -------------------------------
def summarize_results(results, mode="Online"):
    """
    Summarize retrieved vlog metadata into user-friendly insights.
    """
    if mode == "Demo":
        return [
            "🎥 Demo vlog: Rome pasta tour — highlights authentic trattorias",
            "🎥 Demo vlog: Paris night walk — Eiffel Tower lighting show"
        ]

    insights = []
    for match in results.get("matches", []):
        meta = match.get("metadata", {})
        insights.append(
            f"🎥 {meta.get('title')} ({meta.get('creator')}) — "
            f"Highlights {meta.get('destination')} with tags {meta.get('tags')}"
        )
    return insights
