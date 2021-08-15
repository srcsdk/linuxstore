#!/usr/bin/env python3
"""track and suggest from package search history"""

import json
import os
from collections import Counter

HISTORY_FILE = os.path.expanduser("~/.linuxstore_history.json")


def load_history():
    """load search history from file."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {"searches": [], "installs": []}


def save_history(history):
    """save search history to file."""
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def add_search(query):
    """record a search query."""
    history = load_history()
    history["searches"].append(query.lower().strip())
    if len(history["searches"]) > 500:
        history["searches"] = history["searches"][-500:]
    save_history(history)


def add_install(package_name):
    """record an installed package."""
    history = load_history()
    history["installs"].append(package_name)
    save_history(history)


def suggest_searches(prefix, limit=5):
    """suggest completions based on search history."""
    history = load_history()
    counts = Counter(history["searches"])
    matches = [
        (term, count) for term, count in counts.items()
        if term.startswith(prefix.lower())
    ]
    matches.sort(key=lambda x: x[1], reverse=True)
    return [m[0] for m in matches[:limit]]


def frequent_searches(limit=10):
    """return most frequent searches."""
    history = load_history()
    counts = Counter(history["searches"])
    return counts.most_common(limit)


if __name__ == "__main__":
    print("search history tracker")
    print(f"history file: {HISTORY_FILE}")
