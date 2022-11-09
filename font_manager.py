#!/usr/bin/env python3
"""font management and installation"""

import subprocess
import os


def list_installed_fonts():
    """list installed fonts using fc-list."""
    try:
        result = subprocess.run(
            ["fc-list", "--format=%{family}\n"],
            capture_output=True, text=True, timeout=15,
        )
        families = set()
        for line in result.stdout.strip().splitlines():
            for name in line.split(","):
                name = name.strip()
                if name:
                    families.add(name)
        return sorted(families)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def install_font_file(font_path):
    """install a font file to user fonts directory."""
    fonts_dir = os.path.expanduser("~/.local/share/fonts")
    os.makedirs(fonts_dir, exist_ok=True)
    name = os.path.basename(font_path)
    dest = os.path.join(fonts_dir, name)
    import shutil
    shutil.copy2(font_path, dest)
    subprocess.run(["fc-cache", "-f"], capture_output=True, timeout=30)
    return dest


def search_fonts(query):
    """search installed fonts by name."""
    fonts = list_installed_fonts()
    query = query.lower()
    return [f for f in fonts if query in f.lower()]


def font_info(family):
    """get font details."""
    try:
        result = subprocess.run(
            ["fc-list", f":family={family}"],
            capture_output=True, text=True, timeout=10,
        )
        files = []
        for line in result.stdout.strip().splitlines():
            if ":" in line:
                path = line.split(":")[0].strip()
                style = line.split(":")[-1].strip() if line.count(":") > 1 else ""
                files.append({"path": path, "style": style})
        return {"family": family, "files": files, "count": len(files)}
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {"family": family, "files": [], "count": 0}


if __name__ == "__main__":
    fonts = list_installed_fonts()
    print(f"installed font families: {len(fonts)}")
    for f in fonts[:10]:
        print(f"  {f}")
    mono = search_fonts("mono")
    print(f"\nmonospace fonts: {len(mono)}")
    for f in mono[:5]:
        print(f"  {f}")
