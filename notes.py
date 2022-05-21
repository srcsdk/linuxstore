#!/usr/bin/env python3
"""package notes and ratings system"""

import json
import os
import time


class PackageNotes:
    """store user notes and ratings for packages."""

    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = os.path.expanduser("~/.linuxstore")
        self.data_dir = data_dir
        self.notes_file = os.path.join(data_dir, "notes.json")
        os.makedirs(data_dir, exist_ok=True)
        self.notes = self._load()

    def _load(self):
        if os.path.isfile(self.notes_file):
            with open(self.notes_file) as f:
                return json.load(f)
        return {}

    def _save(self):
        with open(self.notes_file, "w") as f:
            json.dump(self.notes, f, indent=2)

    def add_note(self, package, text, rating=None):
        """add a note for a package."""
        if package not in self.notes:
            self.notes[package] = {"notes": [], "rating": None}
        self.notes[package]["notes"].append({
            "text": text,
            "timestamp": time.strftime("%Y-%m-%d %H:%M"),
        })
        if rating is not None:
            self.notes[package]["rating"] = max(1, min(5, rating))
        self._save()

    def get_notes(self, package):
        """get notes for a package."""
        return self.notes.get(package, {"notes": [], "rating": None})

    def set_rating(self, package, rating):
        """set rating (1-5) for a package."""
        if package not in self.notes:
            self.notes[package] = {"notes": [], "rating": None}
        self.notes[package]["rating"] = max(1, min(5, rating))
        self._save()

    def search_notes(self, query):
        """search across all package notes."""
        query = query.lower()
        results = []
        for pkg, data in self.notes.items():
            for note in data.get("notes", []):
                if query in note["text"].lower() or query in pkg.lower():
                    results.append({"package": pkg, "note": note})
        return results

    def rated_packages(self, min_rating=1):
        """get packages with ratings >= min_rating."""
        rated = []
        for pkg, data in self.notes.items():
            rating = data.get("rating")
            if rating and rating >= min_rating:
                rated.append({"package": pkg, "rating": rating})
        rated.sort(key=lambda r: r["rating"], reverse=True)
        return rated

    def remove_notes(self, package):
        """remove all notes for a package."""
        if package in self.notes:
            del self.notes[package]
            self._save()


if __name__ == "__main__":
    pn = PackageNotes("/tmp/linuxstore_test")
    pn.add_note("vim", "essential editor", rating=5)
    pn.add_note("vim", "check vim-plug for plugins")
    pn.add_note("htop", "better than top", rating=4)
    notes = pn.get_notes("vim")
    print(f"vim notes: {len(notes['notes'])}, rating: {notes['rating']}")
    rated = pn.rated_packages(4)
    print(f"highly rated: {len(rated)}")
    for r in rated:
        print(f"  {r['package']}: {r['rating']}/5")
