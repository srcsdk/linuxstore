#!/usr/bin/env python3
"""keyboard shortcuts for linuxstore gui"""

import tkinter as tk


DEFAULT_BINDINGS = {
    "<Control-f>": "focus_search",
    "<Control-i>": "install_selected",
    "<Control-r>": "refresh",
    "<Control-q>": "quit",
    "<Control-1>": "tab_essential",
    "<Control-2>": "tab_popular",
    "<Control-3>": "tab_all",
    "<Control-4>": "tab_installed",
    "<Control-5>": "tab_updates",
    "<Escape>": "clear_search",
}


class ShortcutManager:
    """manage keyboard shortcuts for the application"""

    def __init__(self, root):
        self.root = root
        self.bindings = {}
        self.handlers = {}

    def register(self, action, handler):
        """register a handler for an action name"""
        self.handlers[action] = handler

    def bind_defaults(self):
        """bind all default keyboard shortcuts"""
        for key, action in DEFAULT_BINDINGS.items():
            self.bind(key, action)

    def bind(self, key_sequence, action):
        """bind a key sequence to an action"""
        self.bindings[key_sequence] = action
        self.root.bind(key_sequence, lambda e: self._dispatch(action))

    def _dispatch(self, action):
        """dispatch an action to its handler"""
        handler = self.handlers.get(action)
        if handler:
            handler()

    def unbind(self, key_sequence):
        """remove a key binding"""
        if key_sequence in self.bindings:
            self.root.unbind(key_sequence)
            del self.bindings[key_sequence]

    def get_bindings(self):
        """return current bindings as list of (key, action) tuples"""
        return list(self.bindings.items())


def setup_shortcuts(app):
    """set up keyboard shortcuts for a PackageStore instance"""
    mgr = ShortcutManager(app.root)

    def focus_search():
        app.search_var.set("")
        children = app.root.winfo_children()
        if children:
            inner = children[0].winfo_children()
            if inner:
                inner[-1].focus_set()

    mgr.register("focus_search", focus_search)
    mgr.register("install_selected", lambda: None)
    mgr.register("refresh", lambda: app.show_tab(app.current_view))
    mgr.register("quit", app.root.quit)
    mgr.register("clear_search", lambda: app.search_var.set(""))

    tab_names = ["essential", "popular", "all", "installed", "updates"]
    for i, tab in enumerate(tab_names):
        mgr.register(f"tab_{tab}", lambda t=tab: app.show_tab(t))

    mgr.bind_defaults()
    return mgr


def show_shortcuts_dialog(parent):
    """show a dialog listing keyboard shortcuts"""
    window = tk.Toplevel(parent)
    window.title("keyboard shortcuts")
    window.geometry("350x300")
    window.configure(bg="#1e1e1e")
    window.transient(parent)

    from tkinter import ttk
    ttk.Label(window, text="keyboard shortcuts",
              font=("monospace", 12, "bold")).pack(pady=10)

    shortcuts = [
        ("ctrl+f", "focus search"),
        ("ctrl+i", "install selected"),
        ("ctrl+r", "refresh view"),
        ("ctrl+q", "quit"),
        ("ctrl+1-5", "switch tabs"),
        ("escape", "clear search"),
    ]

    for key, desc in shortcuts:
        row = ttk.Frame(window)
        row.pack(fill=tk.X, padx=15, pady=2)
        ttk.Label(row, text=key, width=12,
                  foreground="#4ec9b0").pack(side=tk.LEFT)
        ttk.Label(row, text=desc,
                  foreground="#cccccc").pack(side=tk.LEFT)

    ttk.Button(window, text="close",
               command=window.destroy).pack(pady=10)
