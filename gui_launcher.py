#!/usr/bin/env python3
"""gui launcher for linuxstore application"""

import os
import sys


def check_display():
    """check if display server is available."""
    display = os.environ.get("DISPLAY")
    wayland = os.environ.get("WAYLAND_DISPLAY")
    return bool(display or wayland)


def check_tkinter():
    """check if tkinter is available."""
    try:
        import tkinter  # noqa: F401
        return True
    except ImportError:
        return False


def launch_gui(catalog=None, installer=None):
    """launch the gui application."""
    if not check_display():
        print("no display server detected, use cli mode")
        return False
    if not check_tkinter():
        print("tkinter not available, install python3-tk")
        return False
    try:
        import tkinter as tk
        from tkinter import ttk
    except ImportError:
        return False
    root = tk.Tk()
    root.title("linuxstore")
    root.geometry("900x600")
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=5, pady=5)
    essential_frame = ttk.Frame(notebook)
    popular_frame = ttk.Frame(notebook)
    all_frame = ttk.Frame(notebook)
    notebook.add(essential_frame, text="essential")
    notebook.add(popular_frame, text="popular")
    notebook.add(all_frame, text="all")
    _populate_tab(essential_frame, "essential", catalog)
    _populate_tab(popular_frame, "popular", catalog)
    _populate_tab(all_frame, "all", catalog)
    status = ttk.Label(root, text="ready")
    status.pack(side="bottom", fill="x", padx=5, pady=2)
    root.mainloop()
    return True


def _populate_tab(frame, tab_type, catalog):
    """populate a tab with package list."""
    from tkinter import ttk
    tree = ttk.Treeview(frame, columns=("package", "category", "status"),
                        show="headings", height=20)
    tree.heading("package", text="package")
    tree.heading("category", text="category")
    tree.heading("status", text="status")
    tree.column("package", width=250)
    tree.column("category", width=150)
    tree.column("status", width=100)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    if catalog:
        if tab_type == "essential":
            packages = catalog.get_essential()
        elif tab_type == "popular":
            packages = catalog.get_popular()
        else:
            packages = catalog.get_essential() + catalog.get_popular()
        for pkg in packages:
            tree.insert("", "end", values=(pkg, "", "available"))
    install_btn = ttk.Button(
        frame, text="install selected",
        command=lambda: _on_install(tree),
    )
    install_btn.pack(side="bottom", pady=5)


def _on_install(tree):
    """handle install button click."""
    selected = tree.selection()
    if not selected:
        return
    for item in selected:
        values = tree.item(item, "values")
        package = values[0]
        tree.set(item, "status", "installing...")
        print(f"installing: {package}")


if __name__ == "__main__":
    if "--cli" in sys.argv:
        print("linuxstore cli mode")
    else:
        if not launch_gui():
            print("falling back to cli mode")
