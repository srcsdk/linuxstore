#!/usr/bin/env python3
"""sorting and filtering options for package lists"""


def sort_packages(packages, sort_by="name", reverse=False):
    """sort a list of package dicts by a given key"""
    key_funcs = {
        "name": lambda p: p.get("name", "").lower(),
        "category": lambda p: p.get("category", "").lower(),
        "desc": lambda p: p.get("desc", "").lower(),
    }
    key_fn = key_funcs.get(sort_by, key_funcs["name"])
    return sorted(packages, key=key_fn, reverse=reverse)


def filter_packages(packages, installed_only=False, category=None,
                    search_fields=None, query=None, check_installed_fn=None):
    """filter packages by multiple criteria"""
    result = list(packages)

    if installed_only and check_installed_fn:
        result = [p for p in result if check_installed_fn(p["name"])]

    if category:
        result = [p for p in result if p.get("category", "").lower() == category.lower()]

    if query and search_fields:
        q = query.lower()
        result = [p for p in result
                  if any(q in str(p.get(f, "")).lower() for f in search_fields)]

    return result


def unique_categories(packages):
    """extract unique categories from package list"""
    cats = set()
    for pkg in packages:
        cat = pkg.get("category", "")
        if cat:
            cats.add(cat)
    return sorted(cats)


def group_by_category(packages):
    """group packages by their category"""
    groups = {}
    for pkg in packages:
        cat = pkg.get("category", "other")
        if cat not in groups:
            groups[cat] = []
        groups[cat].append(pkg)
    return groups
