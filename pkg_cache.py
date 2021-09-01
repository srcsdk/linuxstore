#!/usr/bin/env python3
"""local package metadata cache for faster searches"""

import json
import os
import time

CACHE_DIR = os.path.expanduser("~/.cache/linuxstore")
CACHE_TTL = 3600


def ensure_cache_dir():
    """create cache directory if needed."""
    os.makedirs(CACHE_DIR, exist_ok=True)


def cache_key(query):
    """generate cache filename from query."""
    safe = query.lower().strip().replace(" ", "_")
    safe = "".join(c for c in safe if c.isalnum() or c == "_")
    return os.path.join(CACHE_DIR, f"{safe}.json")


def get_cached(query):
    """return cached results if fresh, else none."""
    path = cache_key(query)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as f:
            data = json.load(f)
        if time.time() - data.get("timestamp", 0) > CACHE_TTL:
            return None
        return data.get("results", [])
    except (json.JSONDecodeError, KeyError):
        return None


def set_cached(query, results):
    """store search results in cache."""
    ensure_cache_dir()
    path = cache_key(query)
    data = {
        "query": query,
        "timestamp": time.time(),
        "results": results,
    }
    with open(path, "w") as f:
        json.dump(data, f)


def clear_cache():
    """remove all cached files."""
    if not os.path.exists(CACHE_DIR):
        return 0
    count = 0
    for fname in os.listdir(CACHE_DIR):
        if fname.endswith(".json"):
            os.remove(os.path.join(CACHE_DIR, fname))
            count += 1
    return count


def cache_stats():
    """return cache statistics."""
    if not os.path.exists(CACHE_DIR):
        return {"entries": 0, "size_bytes": 0}
    entries = 0
    total_size = 0
    for fname in os.listdir(CACHE_DIR):
        if fname.endswith(".json"):
            entries += 1
            total_size += os.path.getsize(os.path.join(CACHE_DIR, fname))
    return {"entries": entries, "size_bytes": total_size}


if __name__ == "__main__":
    print(f"cache dir: {CACHE_DIR}")
    stats = cache_stats()
    print(f"entries: {stats['entries']}, size: {stats['size_bytes']} bytes")
