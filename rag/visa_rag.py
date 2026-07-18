#rag/visa_rag.py
"""
Visa requirements RAG module.

Pinecone and the embedding model are loaded LAZILY (only on first Online-mode
call) so importing this module never requires network access, an API key, or
a model download when running in Demo mode.
"""
import os
from datetime import datetime

PINECONE_ENV = "us-east-1"
PINECONE_INDEX = "visa-requirements"
PINECONE_HOST = os.getenv("PINECONE_HOST", "https://default-pinecone-host.svc.aped-4627-b74a.pinecone.io")

_index = None
_embedder = None


def _get_index():
    global _index
    if _index is None:
        import pinecone
        pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=PINECONE_ENV)
        _index = pinecone.Index(PINECONE_INDEX, host=PINECONE_HOST)
    return _index


def _get_embedder():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        model_name = os.getenv("VISA_RAG_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        _embedder = SentenceTransformer(model_name)
    return _embedder


# -------------------------------
# Filters
# -------------------------------
def _is_valid_entry(entry):
    """Apply freshness filter (≤ 12 months)."""
    updated = entry.get("last_updated")
    if not updated:
        return False
    if (datetime.now() - updated).days > 365:
        return False
    return True


# -------------------------------
# Add Visa Requirements
# -------------------------------
def add_requirements(entries, mode="Online"):
    """
    entries: list of dicts with keys:
        country, visa_type, requirements, duration, documents, fees, processing, source, last_updated
    mode: "Online" or "Demo"
    """
    if mode == "Demo":
        print("🎬 Demo Mode: Skipping Pinecone upsert, returning stub.")
        return [{"demo": f"Stubbed visa entry for {e['country']}"} for e in entries]

    valid_entries = [e for e in entries if _is_valid_entry(e)]
    if not valid_entries:
        print("⚠️ No valid entries after filtering.")
        return []

    embedder = _get_embedder()
    index = _get_index()

    texts = [f"{e['country']} {e['visa_type']} {e['requirements']}" for e in valid_entries]
    vectors = embedder.encode(texts, batch_size=8).tolist()

    upserts = []
    for e, vec in zip(valid_entries, vectors):
        upserts.append((
            f"{e['country']}_{e['visa_type']}",
            vec,
            {
                "country": e["country"],
                "visa_type": e["visa_type"],
                "requirements": e["requirements"],
                "duration": e["duration"],
                "documents": e.get("documents", []),
                "fees": e["fees"],
                "processing": e["processing"],
                "source": e["source"],
                "last_updated": str(e["last_updated"])
            }
        ))
    index.upsert(upserts)
    print(f"✅ Upserted {len(upserts)} visa entries into Pinecone.")
    return upserts


# -------------------------------
# Query Visa Requirements
# -------------------------------
def query_requirements(country, visa_type="tourist", top_k=3, mode="Online"):
    if mode == "Demo":
        return {
            "insights": [
                f"🎬 Demo visa info: {country} {visa_type} visa valid 30 days.",
                f"🎬 Demo visa info: Requires passport + proof of funds."
            ]
        }

    try:
        embedder = _get_embedder()
        index = _get_index()

        query_text = f"{country} {visa_type} visa requirements"
        query_vector = embedder.encode([query_text])[0].tolist()

        results = index.query(vector=query_vector, top_k=top_k, include_metadata=True)
        return results
    except Exception as e:
        print(f"⚠️ Visa RAG query failed, falling back to empty results: {e!r}")
        return {"matches": []}


# -------------------------------
# Summarization Agent
# -------------------------------
def summarize_results(results, mode="Online"):
    if mode == "Demo":
        return [
            "🎬 Demo summary: Tourist visa valid 30 days, fee $50.",
            "🎬 Demo summary: Documents required — passport, photos, proof of funds."
        ]

    insights = []
    for match in results.get("matches", []):
        meta = match.get("metadata", {})
        insights.append(
            f"🛂 {meta.get('country')} {meta.get('visa_type')} visa — "
            f"Duration: {meta.get('duration')}, Fee: {meta.get('fees')}, "
            f"Processing: {meta.get('processing')}, Docs: {meta.get('documents')}"
        )
    return insights
