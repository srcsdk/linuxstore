#!/usr/bin/env python3
"""package category icons and grid layout toggle"""

# category icon mapping using unicode symbols
CATEGORY_ICONS = {
    "gaming": "\U0001f3ae",
    "development": "\u2699",
    "security": "\U0001f512",
    "multimedia": "\u266b",
    "internet": "\U0001f310",
    "office": "\U0001f4c4",
    "system": "\U0001f5a5",
    "science": "\U0001f52c",
    "graphics": "\U0001f3a8",
    "education": "\U0001f4da",
}

# ascii fallback for terminals without unicode
CATEGORY_ASCII = {
    "gaming": "[G]",
    "development": "[D]",
    "security": "[S]",
    "multimedia": "[M]",
    "internet": "[I]",
    "office": "[O]",
    "system": "[*]",
    "science": "[R]",
    "graphics": "[A]",
    "education": "[E]",
}


def get_icon(category, use_unicode=True):
    """get icon for a category."""
    icons = CATEGORY_ICONS if use_unicode else CATEGORY_ASCII
    return icons.get(category.lower(), "[?]")


def grid_layout(packages, columns=3):
    """arrange packages in grid layout."""
    rows = []
    for i in range(0, len(packages), columns):
        rows.append(packages[i:i + columns])
    return rows


def list_layout(packages):
    """arrange packages in single column list."""
    return [[p] for p in packages]


def format_package_card(package, use_unicode=True):
    """format a package as a display card."""
    icon = get_icon(package.get("category", ""), use_unicode)
    name = package.get("name", "unknown")
    version = package.get("version", "")
    desc = package.get("description", "")
    if len(desc) > 40:
        desc = desc[:37] + "..."
    return f"{icon} {name} {version}\n   {desc}"


def render_grid(packages, columns=3, use_unicode=True):
    """render packages in grid format."""
    rows = grid_layout(packages, columns)
    lines = []
    for row in rows:
        cards = [format_package_card(p, use_unicode) for p in row]
        card_lines = [c.split("\n") for c in cards]
        max_lines = max(len(cl) for cl in card_lines)
        for i in range(max_lines):
            parts = []
            for cl in card_lines:
                if i < len(cl):
                    parts.append(f"{cl[i]:<30}")
                else:
                    parts.append(" " * 30)
            lines.append("  ".join(parts))
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    packages = [
        {"name": "firefox", "version": "93.0", "category": "internet",
         "description": "web browser"},
        {"name": "vim", "version": "8.2", "category": "development",
         "description": "text editor"},
        {"name": "vlc", "version": "3.0", "category": "multimedia",
         "description": "media player"},
    ]
    print(render_grid(packages, columns=2, use_unicode=False))
