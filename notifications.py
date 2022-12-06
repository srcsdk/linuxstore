#!/usr/bin/env python3
"""desktop notifications for package updates"""

import subprocess


def send_notification(title, message, urgency="normal"):
    """send desktop notification via notify-send."""
    cmd = ["notify-send", f"--urgency={urgency}", title, message]
    try:
        subprocess.run(cmd, capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def notify_updates(update_count):
    """send notification about available updates."""
    if update_count == 0:
        return
    msg = f"{update_count} package update{'s' if update_count > 1 else ''} available"
    send_notification("linuxstore", msg, "normal")


def notify_install_complete(package, success=True):
    """send notification when install completes."""
    if success:
        send_notification("linuxstore", f"{package} installed successfully")
    else:
        send_notification("linuxstore", f"failed to install {package}", "critical")


def notify_security_updates(packages):
    """send urgent notification for security updates."""
    if not packages:
        return
    count = len(packages)
    names = ", ".join(p.get("name", "") for p in packages[:3])
    extra = f" and {count - 3} more" if count > 3 else ""
    msg = f"security updates: {names}{extra}"
    send_notification("linuxstore security", msg, "critical")


def is_notification_available():
    """check if desktop notifications are available."""
    try:
        result = subprocess.run(
            ["which", "notify-send"],
            capture_output=True, timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


if __name__ == "__main__":
    available = is_notification_available()
    print(f"notifications available: {available}")
    if available:
        send_notification("linuxstore", "notification test")
        print("test notification sent")
