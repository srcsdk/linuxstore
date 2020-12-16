#!/usr/bin/env python3
"""gui layout helpers for organizing frames and widgets"""

import tkinter as tk
from tkinter import ttk


def create_header_frame(parent, title_text):
    """create a standard header frame with title"""
    header = ttk.Frame(parent)
    header.pack(fill=tk.X, padx=10, pady=10)
    ttk.Label(header, text=title_text,
              font=("monospace", 14, "bold"),
              foreground="#ffffff").pack(side=tk.LEFT)
    return header


def create_search_bar(parent):
    """create a search entry with label, returns StringVar"""
    search_var = tk.StringVar()
    entry = ttk.Entry(parent, textvariable=search_var,
                      width=30, font=("monospace", 10))
    entry.pack(side=tk.RIGHT, padx=5)
    ttk.Label(parent, text="search:").pack(side=tk.RIGHT)
    return search_var


def create_scrollable_frame(parent):
    """create a scrollable frame inside a canvas.

    returns (canvas, scrollable_frame) tuple.
    """
    container = ttk.Frame(parent)
    container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    canvas = tk.Canvas(container, bg="#1e1e1e", highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL,
                              command=canvas.yview)
    scrollable = ttk.Frame(canvas)

    scrollable.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # mouse wheel support
    canvas.bind_all("<Button-4>",
                    lambda e: canvas.yview_scroll(-3, "units"))
    canvas.bind_all("<Button-5>",
                    lambda e: canvas.yview_scroll(3, "units"))

    return canvas, scrollable


def create_status_bar(parent):
    """create a status bar at the bottom, returns StringVar"""
    status_var = tk.StringVar(value="ready")
    label = ttk.Label(parent, textvariable=status_var)
    label.pack(fill=tk.X, padx=10, pady=5)
    return status_var


def create_tab_bar(parent, tabs, callback):
    """create a horizontal tab bar.

    tabs: list of tab names
    callback: function(tab_name) called on click
    returns dict of {tab_name: button_widget}
    """
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.X, padx=10)

    buttons = {}
    for tab in tabs:
        btn = ttk.Button(frame, text=tab, style="Tab.TButton",
                         command=lambda t=tab: callback(t))
        btn.pack(side=tk.LEFT, padx=2)
        buttons[tab] = btn

    return buttons
