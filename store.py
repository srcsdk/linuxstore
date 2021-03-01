#!/usr/bin/env python3
"""linux package browser - gui for discovering and installing packages"""

import json
import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox

PACKAGES_FILE = os.path.join(os.path.dirname(__file__), "packages.json")


def load_packages():
    """load package database"""
    with open(PACKAGES_FILE, "r") as f:
        return json.load(f)


def _get_pkg_mgr():
    """get detected package manager info"""
    try:
        from detect_os import get_package_manager
        return get_package_manager()
    except ImportError:
        return {"command": None, "family": "unknown"}


def check_installed(package_name):
    """check if a package is installed"""
    mgr = _get_pkg_mgr()
    cmd = mgr.get("command")
    if not cmd:
        return False

    check_cmds = {
        "pacman": ["pacman", "-Qi", package_name],
        "apt": ["dpkg", "-s", package_name],
        "dnf": ["rpm", "-q", package_name],
        "zypper": ["rpm", "-q", package_name],
        "brew": ["brew", "list", package_name],
        "winget": ["winget", "list", "--name", package_name],
        "choco": ["choco", "list", "--local-only", package_name],
    }
    args = check_cmds.get(cmd, [cmd, "list", package_name])
    try:
        result = subprocess.run(args, capture_output=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def install_package(package_name):
    """install a package using the detected package manager"""
    mgr = _get_pkg_mgr()
    cmd = mgr.get("command")
    if not cmd:
        return False, "no package manager detected"

    install_cmds = {
        "pacman": ["sudo", "pacman", "-S", "--noconfirm", package_name],
        "apt": ["sudo", "apt", "install", "-y", package_name],
        "dnf": ["sudo", "dnf", "install", "-y", package_name],
        "zypper": ["sudo", "zypper", "install", "-y", package_name],
        "brew": ["brew", "install", package_name],
        "winget": ["winget", "install", "--accept-package-agreements", package_name],
        "choco": ["choco", "install", "-y", package_name],
    }
    args = install_cmds.get(cmd, [cmd, "install", package_name])
    try:
        result = subprocess.run(
            args, capture_output=True, text=True, timeout=300
        )
        if result.returncode == 0:
            return True, f"installed with {cmd}"
        return False, result.stderr[:200]
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except FileNotFoundError:
        return False, f"{cmd} not found"


class PackageStore:
    """main application window"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("linux package browser")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")

        self.packages = load_packages()
        self.current_view = "essential"

        self.setup_styles()
        self.build_ui()
        self.show_tab("essential")

    def setup_styles(self):
        """configure ttk styles"""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background="#1e1e1e")
        style.configure("TLabel", background="#1e1e1e",
                        foreground="#cccccc", font=("monospace", 10))
        style.configure("Title.TLabel", font=("monospace", 14, "bold"),
                        foreground="#ffffff")
        style.configure("TButton", font=("monospace", 10))
        style.configure("Tab.TButton", font=("monospace", 11),
                        padding=8)
        style.configure("Install.TButton", font=("monospace", 9))

    def build_ui(self):
        """build the main interface"""
        # header
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(header, text="packages",
                  style="Title.TLabel").pack(side=tk.LEFT)

        # search
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search)
        search_entry = ttk.Entry(header, textvariable=self.search_var,
                                 width=30, font=("monospace", 10))
        search_entry.pack(side=tk.RIGHT, padx=5)
        ttk.Label(header, text="search:").pack(side=tk.RIGHT)

        # tabs
        tab_frame = ttk.Frame(self.root)
        tab_frame.pack(fill=tk.X, padx=10)

        tabs = ["essential", "popular", "all"]
        self.tab_buttons = {}
        for tab in tabs:
            btn = ttk.Button(tab_frame, text=tab, style="Tab.TButton",
                             command=lambda t=tab: self.show_tab(t))
            btn.pack(side=tk.LEFT, padx=2)
            self.tab_buttons[tab] = btn

        # category sidebar (for 'all' view)
        self.sidebar = ttk.Frame(self.root)

        # package list
        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # scrollable canvas
        self.canvas = tk.Canvas(list_frame, bg="#1e1e1e",
                                highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                                  command=self.canvas.yview)
        self.scrollable = ttk.Frame(self.canvas)

        self.scrollable.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable,
                                  anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>",
                             lambda e: self.canvas.yview_scroll(
                                 int(-1*(e.delta/120)), "units"))
        self.canvas.bind_all("<Button-4>",
                             lambda e: self.canvas.yview_scroll(-3, "units"))
        self.canvas.bind_all("<Button-5>",
                             lambda e: self.canvas.yview_scroll(3, "units"))

        # status bar
        self.status_var = tk.StringVar(value="ready")
        status = ttk.Label(self.root, textvariable=self.status_var)
        status.pack(fill=tk.X, padx=10, pady=5)

    def show_tab(self, tab):
        """switch to a tab"""
        self.current_view = tab

        # clear sidebar
        self.sidebar.pack_forget()

        if tab == "essential":
            self.display_packages(self.packages["essential"])
        elif tab == "popular":
            self.display_packages(self.packages["popular"])
        elif tab == "all":
            self.show_all_view()

    def show_all_view(self):
        """show all packages organized by category"""
        # show sidebar
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5,
                          before=self.canvas.master)

        # clear sidebar
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        ttk.Label(self.sidebar, text="categories",
                  font=("monospace", 10, "bold")).pack(pady=5)

        # show all button
        total = sum(len(v) for v in self.packages["all"].values())
        all_btn = ttk.Button(
            self.sidebar,
            text=f"all ({total})",
            command=self.show_all_categories
        )
        all_btn.pack(fill=tk.X, padx=2, pady=1)

        ttk.Separator(self.sidebar, orient=tk.HORIZONTAL).pack(
            fill=tk.X, padx=2, pady=3)

        categories = list(self.packages["all"].keys())
        for cat in categories:
            count = len(self.packages["all"][cat])
            btn = ttk.Button(
                self.sidebar,
                text=f"{cat} ({count})",
                command=lambda c=cat: self.show_category(c)
            )
            btn.pack(fill=tk.X, padx=2, pady=1)

        # show first category
        if categories:
            self.show_category(categories[0])

    def show_all_categories(self):
        """show every package across all categories"""
        all_pkgs = []
        for cat_pkgs in self.packages["all"].values():
            all_pkgs.extend(cat_pkgs)
        self.display_packages(all_pkgs, "all categories")

    def show_category(self, category):
        """show packages in a category"""
        pkgs = self.packages["all"].get(category, [])
        self.display_packages(pkgs, category)

    def display_packages(self, packages, header=None):
        """display a list of packages"""
        for widget in self.scrollable.winfo_children():
            widget.destroy()

        if header:
            ttk.Label(self.scrollable, text=header,
                      font=("monospace", 12, "bold")).pack(
                anchor="w", pady=(0, 5))

        for pkg in packages:
            self.create_package_row(pkg)

        self.status_var.set(f"{len(packages)} packages")

    def create_package_row(self, pkg):
        """create a row for a package"""
        row = ttk.Frame(self.scrollable)
        row.pack(fill=tk.X, pady=2)

        name = pkg["name"]
        desc = pkg["desc"]

        ttk.Label(row, text=name, font=("monospace", 10, "bold"),
                  foreground="#4ec9b0", width=30,
                  anchor="w").pack(side=tk.LEFT)

        ttk.Label(row, text=desc, foreground="#888888",
                  anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)

        install_btn = ttk.Button(
            row, text="install", style="Install.TButton",
            command=lambda n=name: self.install(n)
        )
        install_btn.pack(side=tk.RIGHT, padx=5)

    def install(self, package_name):
        """install a package"""
        self.status_var.set(f"installing {package_name}...")
        self.root.update()

        success, msg = install_package(package_name)
        if success:
            self.status_var.set(f"{package_name}: {msg}")
        else:
            self.status_var.set(f"failed: {msg}")
            messagebox.showerror("install failed",
                                 f"could not install {package_name}:\n{msg}")

    def search_packages(self, query):
        """search all package lists for matches"""
        results = []
        seen = set()
        sources = [
            self.packages["essential"],
            self.packages["popular"],
        ]
        for cat_pkgs in self.packages["all"].values():
            sources.append(cat_pkgs)

        for pkg_list in sources:
            for pkg in pkg_list:
                name = pkg["name"]
                if name in seen:
                    continue
                if query in name.lower() or query in pkg["desc"].lower():
                    results.append(pkg)
                    seen.add(name)

        # sort by name match first, then description match
        results.sort(key=lambda p: (0 if query in p["name"].lower() else 1,
                                    p["name"]))
        return results

    def on_search(self, *args):
        """filter packages by search term"""
        query = self.search_var.get().lower()
        if not query:
            self.show_tab(self.current_view)
            return

        results = self.search_packages(query)
        self.display_packages(results, f"search: {query} ({len(results)} found)")

    def run(self):
        """start the application"""
        self.root.mainloop()


def main():
    if not os.path.exists(PACKAGES_FILE):
        print(f"missing {PACKAGES_FILE}", file=sys.stderr)
        sys.exit(1)

    app = PackageStore()
    app.run()


if __name__ == "__main__":
    main()


class InstallProgress:
    """show a progress window during package installation"""

    def __init__(self, parent, package_name):
        self.window = tk.Toplevel(parent)
        self.window.title(f"installing {package_name}")
        self.window.geometry("400x120")
        self.window.configure(bg="#1e1e1e")
        self.window.transient(parent)

        ttk.Label(self.window, text=f"installing {package_name}...",
                  font=("monospace", 10)).pack(pady=10)

        self.progress = ttk.Progressbar(
            self.window, mode="indeterminate", length=350
        )
        self.progress.pack(pady=5, padx=20)
        self.progress.start(20)

        self.status_label = ttk.Label(
            self.window, text="running pacman...",
            font=("monospace", 9), foreground="#888888"
        )
        self.status_label.pack(pady=5)

    def update_status(self, text):
        """update the status text"""
        self.status_label.configure(text=text)
        self.window.update()

    def finish(self, success, message):
        """stop progress and show result"""
        self.progress.stop()
        color = "#4ec9b0" if success else "#f44747"
        self.status_label.configure(text=message, foreground=color)
        self.window.after(2000, self.window.destroy)

    def close(self):
        """close the progress window"""
        self.window.destroy()


class PackageDetail:
    """popup window showing package details"""

    def __init__(self, parent, pkg):
        self.window = tk.Toplevel(parent)
        self.window.title(pkg["name"])
        self.window.geometry("500x300")
        self.window.configure(bg="#1e1e1e")
        self.window.transient(parent)

        name_label = ttk.Label(
            self.window, text=pkg["name"],
            font=("monospace", 14, "bold"), foreground="#4ec9b0"
        )
        name_label.pack(anchor="w", padx=15, pady=(15, 5))

        desc_label = ttk.Label(
            self.window, text=pkg["desc"],
            font=("monospace", 10), foreground="#cccccc",
            wraplength=460
        )
        desc_label.pack(anchor="w", padx=15, pady=5)

        # check if installed
        installed = check_installed(pkg["name"])
        status_text = "installed" if installed else "not installed"
        status_color = "#4ec9b0" if installed else "#888888"

        ttk.Label(
            self.window, text=f"status: {status_text}",
            font=("monospace", 10), foreground=status_color
        ).pack(anchor="w", padx=15, pady=5)

        # buttons
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(anchor="w", padx=15, pady=15)

        if not installed:
            ttk.Button(
                btn_frame, text="install",
                command=lambda: self.window.destroy()
            ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame, text="close",
            command=self.window.destroy
        ).pack(side=tk.LEFT, padx=5)


def list_installed_packages():
    """get list of explicitly installed packages"""
    mgr = _get_pkg_mgr()
    cmd = mgr.get("command")

    list_cmds = {
        "pacman": ["pacman", "-Qe"],
        "apt": ["dpkg", "--get-selections"],
        "dnf": ["dnf", "list", "installed"],
        "brew": ["brew", "list", "--versions"],
        "winget": ["winget", "list"],
        "choco": ["choco", "list", "--local-only"],
    }
    args = list_cmds.get(cmd)
    if not args:
        return []

    try:
        result = subprocess.run(
            args, capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return []

        packages = []
        for line in result.stdout.strip().split("\n"):
            parts = line.strip().split(None, 1)
            if parts and not parts[0].startswith(("-", "=", "Listing")):
                name = parts[0]
                version = parts[1] if len(parts) > 1 else ""
                packages.append({"name": name, "version": version})
        return packages
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def get_package_info(package_name):
    """get detailed info for an installed package"""
    mgr = _get_pkg_mgr()
    cmd = mgr.get("command")

    info_cmds = {
        "pacman": ["pacman", "-Qi", package_name],
        "apt": ["apt", "show", package_name],
        "dnf": ["dnf", "info", package_name],
        "brew": ["brew", "info", package_name],
        "winget": ["winget", "show", package_name],
    }
    args = info_cmds.get(cmd)
    if not args:
        return None

    try:
        result = subprocess.run(
            args, capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return None

        info = {}
        for line in result.stdout.split("\n"):
            if ":" in line:
                key, _, value = line.partition(":")
                info[key.strip().lower()] = value.strip()
        return info
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def check_updates():
    """check for available package updates"""
    mgr = _get_pkg_mgr()
    cmd = mgr.get("command")

    update_cmds = {
        "pacman": ["pacman", "-Qu"],
        "apt": ["apt", "list", "--upgradable"],
        "dnf": ["dnf", "check-update"],
        "brew": ["brew", "outdated"],
        "winget": ["winget", "upgrade"],
        "choco": ["choco", "outdated"],
    }
    args = update_cmds.get(cmd)
    if not args:
        return []

    try:
        result = subprocess.run(
            args, capture_output=True, text=True, timeout=30
        )
        if not result.stdout.strip():
            return []

        updates = []
        for line in result.stdout.strip().split("\n"):
            parts = line.strip().split()
            if len(parts) >= 2 and not parts[0].startswith(("Listing", "-", "=")):
                updates.append({
                    "name": parts[0],
                    "current": parts[1] if len(parts) > 1 else "",
                    "new": parts[3] if len(parts) > 3 else parts[-1],
                })
        return updates
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def format_update_summary(updates):
    """format update list for display"""
    if not updates:
        return "system is up to date"
    lines = [f"{len(updates)} updates available:"]
    for u in updates[:20]:
        lines.append(f"  {u['name']} {u['current']} -> {u['new']}")
    if len(updates) > 20:
        lines.append(f"  ... and {len(updates) - 20} more")
    return "\n".join(lines)


def uninstall_package(package_name):
    """remove a package using the detected package manager"""
    if not check_installed(package_name):
        return False, f"{package_name} is not installed"

    mgr = _get_pkg_mgr()
    cmd = mgr.get("command")
    if not cmd:
        return False, "no package manager detected"

    remove_cmds = {
        "pacman": ["sudo", "pacman", "-Rs", "--noconfirm", package_name],
        "apt": ["sudo", "apt", "remove", "-y", package_name],
        "dnf": ["sudo", "dnf", "remove", "-y", package_name],
        "brew": ["brew", "uninstall", package_name],
        "winget": ["winget", "uninstall", package_name],
        "choco": ["choco", "uninstall", "-y", package_name],
    }
    args = remove_cmds.get(cmd, [cmd, "remove", package_name])
    try:
        result = subprocess.run(
            args, capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            return True, f"removed {package_name}"
        return False, result.stderr[:200]
    except subprocess.TimeoutExpired:
        return False, "timeout during removal"
    except FileNotFoundError:
        return False, f"{cmd} not found"


class SystemInfoPanel:
    """display system information in a popup window"""

    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("system info")
        self.window.geometry("450x350")
        self.window.configure(bg="#1e1e1e")
        self.window.transient(parent)

        ttk.Label(
            self.window, text="system information",
            font=("monospace", 12, "bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))

        info_frame = ttk.Frame(self.window)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=15)

        try:
            from detect_os import system_report
            report = system_report()

            fields = [
                ("distro", f"{report['distro']['name']} {report['distro']['version']}"),
                ("kernel", report["kernel"]),
                ("arch", report["hardware"]["arch"]),
                ("cpu", report["hardware"]["cpu"][:40]),
                ("cores", str(report["hardware"]["cores"])),
                ("ram", f"{report['hardware']['ram_gb']} gb"),
                ("pkg manager", report["package_manager"]["command"] or "unknown"),
                ("python", report["python"]),
            ]

            for label, value in fields:
                row = ttk.Frame(info_frame)
                row.pack(fill=tk.X, pady=2)
                ttk.Label(row, text=f"{label}:", width=14,
                          foreground="#888888").pack(side=tk.LEFT)
                ttk.Label(row, text=value,
                          foreground="#4ec9b0").pack(side=tk.LEFT)

            for gpu in report["hardware"].get("gpu", []):
                row = ttk.Frame(info_frame)
                row.pack(fill=tk.X, pady=2)
                ttk.Label(row, text="gpu:", width=14,
                          foreground="#888888").pack(side=tk.LEFT)
                ttk.Label(row, text=f"{gpu['name'][:35]} ({gpu['vendor']})",
                          foreground="#4ec9b0").pack(side=tk.LEFT)

        except ImportError:
            ttk.Label(info_frame, text="detect_os module not found",
                      foreground="#f44747").pack(pady=20)

        ttk.Button(
            self.window, text="close",
            command=self.window.destroy
        ).pack(pady=10)
