#!/usr/bin/env python3
"""package review and rating display"""

import json
import os


REVIEWS_FILE = os.path.join(os.path.dirname(__file__), "reviews.json")


def load_reviews():
    """load cached reviews."""
    if os.path.exists(REVIEWS_FILE):
        with open(REVIEWS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_reviews(reviews):
    """save reviews to cache."""
    with open(REVIEWS_FILE, "w") as f:
        json.dump(reviews, f, indent=2)


def add_review(package, rating, comment, author="anonymous"):
    """add a review for a package (1-5 stars)."""
    reviews = load_reviews()
    reviews.setdefault(package, [])
    reviews[package].append({
        "rating": max(1, min(5, rating)),
        "comment": comment,
        "author": author,
    })
    save_reviews(reviews)


def avg_rating(package):
    """get average rating for a package."""
    reviews = load_reviews()
    pkg_reviews = reviews.get(package, [])
    if not pkg_reviews:
        return 0.0
    total = sum(r["rating"] for r in pkg_reviews)
    return round(total / len(pkg_reviews), 1)


def format_stars(rating, max_stars=5):
    """format rating as ascii stars."""
    full = int(rating)
    half = 1 if rating - full >= 0.5 else 0
    empty = max_stars - full - half
    return "*" * full + ("+" if half else "") + "." * empty


def top_rated(n=10):
    """get top n rated packages."""
    reviews = load_reviews()
    ratings = []
    for pkg, pkg_reviews in reviews.items():
        if pkg_reviews:
            avg = sum(r["rating"] for r in pkg_reviews) / len(pkg_reviews)
            ratings.append({
                "package": pkg,
                "avg_rating": round(avg, 1),
                "review_count": len(pkg_reviews),
            })
    ratings.sort(key=lambda r: r["avg_rating"], reverse=True)
    return ratings[:n]


def format_review(review):
    """format a single review for display."""
    stars = format_stars(review["rating"])
    return f"  {stars} ({review['author']}): {review['comment']}"


if __name__ == "__main__":
    reviews = load_reviews()
    total_pkgs = len(reviews)
    total_reviews = sum(len(r) for r in reviews.values())
    print(f"reviews: {total_reviews} across {total_pkgs} packages")
    top = top_rated(5)
    for pkg in top:
        stars = format_stars(pkg["avg_rating"])
        print(f"  {stars} {pkg['package']} "
              f"({pkg['review_count']} reviews)")
