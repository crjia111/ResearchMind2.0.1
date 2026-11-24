"""Select a local or explicitly configured embedding service."""
import math
import os

from http_client import request
from local_inference import inference

FILENAME = "Qwen3-Embedding-0.6B-Q8_0.gguf"
LOCAL_MODEL = "Qwen3-Embedding-0.6B-Q8_0@370f27d"
QUERY_INSTRUCTION = "Given a research question, retrieve relevant scientific paper passages"


def configuration():
    if wants_local():
        return "local", LOCAL_MODEL, "", ""
    if google_key := os.getenv("GOOGLE_API_KEY"):
        return "google", os.getenv("GOOGLE_EMBEDDING_MODEL", "gemini-embedding-001"), google_key, ""
    model = os.getenv("OPENAI_EMBEDDING_MODEL")
    key = os.getenv("OPENAI_API_KEY")
    if not model or not key:
        raise RuntimeError("Configure a compatible embedding service for remote mode")
    return "openai", model, key, os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")


def wants_local():
    return os.getenv("RM_EMBED_BACKEND", "local") != "remote"


def read_vectors(data):
    return [row["embedding"] for row in sorted(data["data"], key=lambda row: row["index"])]


def embedded(config, texts, *, query=False):
    provider, model, key, base = config
    if provider == "local":
        if query:
            texts = [f"Instruct: {QUERY_INSTRUCTION}\nQuery: {text}" for text in texts]
        response = inference(FILENAME, "embedding").request(
            "/v1/embeddings", {"model": "bundled", "input": texts},
        )
        vectors = read_vectors(response)
    elif provider == "google":
        url = "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":batchEmbedContents"
        body = {"requests": [{"model": "models/" + model, "content": {"parts": [{"text": text}]}}
                              for text in texts]}
        data = request(url, body, {"x-goog-api-key": key}, timeout=120)
        vectors = [row["values"] for row in data["embeddings"]]
    else:
        data = request(base + "/embeddings", {"model": model, "input": texts},
                       {"Authorization": f"Bearer {key}"}, timeout=120)
        vectors = read_vectors(data)
    if len(vectors) != len(texts) or not all(vector and all(math.isfinite(x) for x in vector)
                                             for vector in vectors):
        raise ValueError("Embedding service returned invalid vectors")
    return vectors
