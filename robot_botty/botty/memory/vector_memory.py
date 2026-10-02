"""
Vector memory — memoria a largo plazo basada en embeddings simples.
Almacena conversaciones y las recupera por similitud semantica.
"""

import json
import time
import math
import re
import os
from pathlib import Path
from collections import defaultdict

from botty.config import Config


STOPWORDS = set((
    "de la que en y a el lo un por con no me se su es al los sus "
    "las del le ya este ese esa esto eso esta estaba pero mas "
    "muy sin sobre entre hasta ahora como durante desde luego "
    "cuando donde mientras porque cual quien cada tod"
).split())


def _tokenize(text: str) -> list[str]:
    text = text.lower()
    tokens = re.findall(r"[a-záéíóúñ]+", text)
    return [t for t in tokens if t not in STOPWORDS and len(t) > 2]


def _tfidf_vector(text: str, vocab: dict[str, int], idf: dict[str, float]) -> list[float]:
    tokens = _tokenize(text)
    vec = [0.0] * len(vocab)
    if not tokens:
        return vec
    tf = defaultdict(int)
    for t in tokens:
        tf[t] += 1
    max_tf = max(tf.values())
    for word, count in tf.items():
        if word in vocab:
            idx = vocab[word]
            vec[idx] = (count / max_tf) * idf.get(word, 1.0)
    return vec


def _cosine_sim(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class MemoryEntry:
    def __init__(self, text: str, role: str = "user", timestamp: float = None,
                 tags: list[str] = None, metadata: dict = None):
        self.text = text
        self.role = role
        self.timestamp = timestamp or time.time()
        self.tags = tags or []
        self.metadata = metadata or {}
        self.vector = None

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "role": self.role,
            "timestamp": self.timestamp,
            "tags": self.tags,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            text=d["text"],
            role=d.get("role", "user"),
            timestamp=d.get("timestamp", 0),
            tags=d.get("tags", []),
            metadata=d.get("metadata", {}),
        )


class VectorMemory:
    def __init__(self, max_entries=1000, similarity_threshold=0.3):
        self.max_entries = max_entries
        self.similarity_threshold = similarity_threshold
        self.entries: list[MemoryEntry] = []
        self.vocab: dict[str, int] = {}
        self.idf: dict[str, float] = {}
        self._dirty = False
        self._path = Path(Config.MEMORY_DB_PATH).with_suffix(".vmem.json")
        self._loaded = False

    def load(self):
        if self._loaded:
            return
        self._loaded = True
        if not self._path.exists():
            return
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.entries = [MemoryEntry.from_dict(e) for e in data.get("entries", [])]
            self.vocab = data.get("vocab", {})
            self.idf = {k: float(v) for k, v in data.get("idf", {}).items()}
            print(f"  [VMem] Cargados {len(self.entries)} recuerdos")
        except Exception as e:
            print(f"  [VMem] Error cargando: {e}")

    def save(self):
        if not self._dirty:
            return
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump({
                    "entries": [e.to_dict() for e in self.entries[-self.max_entries:]],
                    "vocab": self.vocab,
                    "idf": self.idf,
                }, f, ensure_ascii=False, indent=2)
            self._dirty = False
            print(f"  [VMem] Guardados {len(self.entries)} recuerdos")
        except Exception as e:
            print(f"  [VMem] Error guardando: {e}")

    def _rebuild_index(self):
        self.vocab = {}
        self.idf = {}
        word_doc_count = defaultdict(int)
        all_tokens = []

        for entry in self.entries:
            tokens = _tokenize(" ".join((entry.text, *entry.tags)))
            all_tokens.append(tokens)
            for t in set(tokens):
                word_doc_count[t] += 1

        idx = 0
        for tokens in all_tokens:
            for t in tokens:
                if t not in self.vocab:
                    self.vocab[t] = idx
                    idx += 1

        n_docs = len(self.entries)
        for word, doc_count in word_doc_count.items():
            self.idf[word] = math.log((n_docs + 1) / (doc_count + 1)) + 1

        for entry, tokens in zip(self.entries, all_tokens):
            vec = [0.0] * len(self.vocab)
            if tokens:
                tf = defaultdict(int)
                for t in tokens:
                    if t in self.vocab:
                        tf[t] += 1
                max_tf = max(tf.values())
                for word, count in tf.items():
                    idx_w = self.vocab[word]
                    vec[idx_w] = (count / max_tf) * self.idf.get(word, 1.0)
            entry.vector = vec

    def add(self, text: str, role: str = "user", tags: list[str] = None,
            metadata: dict = None):
        entry = MemoryEntry(text, role=role, tags=tags, metadata=metadata)
        self.entries.append(entry)
        self._dirty = True
        if len(self.entries) > self.max_entries * 1.2:
            self.entries = self.entries[-self.max_entries:]

    def add_conversation(self, user_text: str, bot_reply: str, tags: list[str] = None):
        self.add(user_text, role="user", tags=tags)
        self.add(bot_reply, role="assistant", tags=tags)

    def search(self, query: str, top_k: int = 5) -> list[tuple[MemoryEntry, float]]:
        if not self.entries:
            return []
        self._rebuild_index()
        query_vec = _tfidf_vector(query, self.vocab, self.idf)
        if not any(query_vec):
            return []

        scored = []
        for entry in self.entries:
            if entry.vector:
                sim = _cosine_sim(query_vec, entry.vector)
                if sim > self.similarity_threshold:
                    scored.append((entry, sim))
        scored.sort(key=lambda x: -x[1])
        return scored[:top_k]

    def get_recent(self, n: int = 10) -> list[MemoryEntry]:
        return self.entries[-n:]

    def get_by_tag(self, tag: str) -> list[MemoryEntry]:
        return [e for e in self.entries if tag in e.tags]

    def get_context(self, query: str, max_chars: int = 1000) -> str:
        results = self.search(query, top_k=3)
        if not results:
            return ""
        lines = []
        total = 0
        for entry, sim in results:
            snippet = f"[{entry.role}]: {entry.text}"
            if total + len(snippet) > max_chars:
                break
            lines.append(snippet)
            total += len(snippet)
        return "\n".join(lines)

    def forget_old(self, max_age_days: int = 30):
        cutoff = time.time() - max_age_days * 86400
        before = len(self.entries)
        self.entries = [e for e in self.entries if e.timestamp > cutoff]
        self._dirty = True
        print(f"  [VMem] Olvidados {before - len(self.entries)} recuerdos viejos")

    def count(self) -> int:
        return len(self.entries)

    def clear(self):
        self.entries.clear()
        self.vocab.clear()
        self.idf.clear()
        self._dirty = True
        print("  [VMem] Memoria borrada")
