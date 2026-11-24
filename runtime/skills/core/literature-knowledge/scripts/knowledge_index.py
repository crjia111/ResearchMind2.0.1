"""Persist chunks in Chroma using an explicitly configured embedding service."""
import hashlib
import json

import chromadb
from chromadb.config import Settings

from embeddings import embedded

CHUNK_VERSION = "chars-v1"


def collection(index, name, config, chunk_size, *, create=False):
    provider, model, _, base = config
    digest = hashlib.sha256(json.dumps([name, provider, model, base, CHUNK_VERSION, chunk_size]).encode()).hexdigest()
    client = chromadb.PersistentClient(path=str(index.resolve()), settings=Settings(anonymized_telemetry=False))
    key = "papers-" + digest[:32]
    if create:
        return client.get_or_create_collection(
            key, embedding_function=None, metadata={"provider": provider, "model": model,
                                                    "chunk_version": CHUNK_VERSION, "chunk_size": chunk_size},
        )
    return client.get_collection(key, embedding_function=None)


def add_paper(store, config, row, text, evidence, source, chunk_size):
    documents, metadata, identifiers, vectors = [], [], [], []
    ident = str(row["paper_id"])
    version = hashlib.sha256(text.encode("utf-8")).hexdigest()[:20]
    for start in range(0, len(text), chunk_size):
        part = text[start:start + chunk_size].strip()
        if not part:
            continue
        part_offset = text.find(part, start, start + chunk_size)
        documents.append(part)
        metadata.append({"paper_id": ident, "start": part_offset, "end": part_offset + len(part),
                         "evidence": evidence, "source": source or "", "version": version})
        identifiers.append(f"{ident}:{version}:{start}")
    if not documents:
        raise ValueError(f"No indexable content for {ident}")
    for start in range(0, len(documents), 16):
        vectors.extend(embedded(config, documents[start:start + 16]))
    store.upsert(ids=identifiers, documents=documents, metadatas=metadata, embeddings=vectors)
    store.delete(where={"$and": [{"paper_id": ident}, {"version": {"$ne": version}}]})
    return len(documents)
