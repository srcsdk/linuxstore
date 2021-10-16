#!/usr/bin/env python3
"""download progress bar with speed estimation"""

import sys
import time


class ProgressBar:
    """terminal progress bar for downloads."""

    def __init__(self, total, width=40, label=""):
        self.total = total
        self.width = width
        self.label = label
        self.current = 0
        self.start_time = time.time()

    def update(self, amount):
        """update progress by amount."""
        self.current = min(self.current + amount, self.total)
        self._render()

    def set(self, value):
        """set progress to specific value."""
        self.current = min(value, self.total)
        self._render()

    def _render(self):
        """render progress bar to terminal."""
        if self.total <= 0:
            return
        pct = self.current / self.total
        filled = int(self.width * pct)
        bar = "#" * filled + "-" * (self.width - filled)
        elapsed = time.time() - self.start_time
        speed = self.current / elapsed if elapsed > 0 else 0
        eta = (self.total - self.current) / speed if speed > 0 else 0
        speed_str = format_size(speed) + "/s"
        eta_str = format_time(eta)
        line = (f"\r{self.label} [{bar}] {pct:.0%} "
                f"{format_size(self.current)}/{format_size(self.total)} "
                f"{speed_str} eta {eta_str}")
        sys.stdout.write(line)
        sys.stdout.flush()
        if self.current >= self.total:
            sys.stdout.write("\n")

    def finish(self):
        """mark download as complete."""
        self.current = self.total
        self._render()


def format_size(bytes_val):
    """format byte count to human readable."""
    for unit in ["B", "KB", "MB", "GB"]:
        if abs(bytes_val) < 1024:
            return f"{bytes_val:.1f}{unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f}TB"


def format_time(seconds):
    """format seconds to mm:ss."""
    if seconds <= 0:
        return "00:00"
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


if __name__ == "__main__":
    total = 50 * 1024 * 1024
    bar = ProgressBar(total, label="downloading")
    chunk = total // 20
    for _ in range(20):
        bar.update(chunk)
        time.sleep(0.1)
    bar.finish()
