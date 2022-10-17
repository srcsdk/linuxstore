#!/usr/bin/env python3
"""one-click package installation with auto-detection"""

import subprocess
import platform


class OneClickInstaller:
    """install packages with automatic os and package manager detection."""

    def __init__(self):
        self.os_info = self._detect_os()
        self.pkg_manager = self._detect_pkg_manager()
        self.install_log = []

    def _detect_os(self):
        """detect operating system."""
        system = platform.system().lower()
        info = {"system": system, "machine": platform.machine()}
        if system == "linux":
            try:
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("ID="):
                            info["distro"] = line.split("=")[1].strip().strip('"')
                        elif line.startswith("ID_LIKE="):
                            info["family"] = line.split("=")[1].strip().strip('"')
            except FileNotFoundError:
                pass
        return info

    def _detect_pkg_manager(self):
        """detect available package manager."""
        managers = {
            "pacman": {"install": "pacman -S --noconfirm",
                       "update": "pacman -Syu --noconfirm"},
            "apt-get": {"install": "apt-get install -y",
                        "update": "apt-get update"},
            "dnf": {"install": "dnf install -y",
                    "update": "dnf update -y"},
            "yum": {"install": "yum install -y",
                    "update": "yum update -y"},
            "zypper": {"install": "zypper install -y",
                       "update": "zypper update -y"},
            "brew": {"install": "brew install",
                     "update": "brew update"},
            "apk": {"install": "apk add",
                    "update": "apk update"},
        }
        for cmd, info in managers.items():
            try:
                subprocess.run(
                    ["which", cmd], capture_output=True,
                    check=True, timeout=3,
                )
                return {"name": cmd, **info}
            except (subprocess.CalledProcessError, FileNotFoundError,
                    subprocess.TimeoutExpired):
                continue
        return None

    def install(self, package_name, sudo=True):
        """install a package using detected package manager."""
        if not self.pkg_manager:
            return {"success": False, "error": "no package manager found"}
        cmd = self.pkg_manager["install"]
        if sudo and self.os_info["system"] == "linux":
            cmd = f"sudo {cmd}"
        full_cmd = f"{cmd} {package_name}"
        try:
            result = subprocess.run(
                full_cmd.split(), capture_output=True,
                text=True, timeout=300,
            )
            success = result.returncode == 0
            self.install_log.append({
                "package": package_name,
                "success": success,
                "output": result.stdout[-200:] if result.stdout else "",
            })
            return {"success": success, "output": result.stdout}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "install timed out"}

    def install_batch(self, packages, sudo=True):
        """install multiple packages."""
        results = {}
        for pkg in packages:
            results[pkg] = self.install(pkg, sudo)
        return results

    def check_installed(self, package_name):
        """check if package is already installed."""
        if not self.pkg_manager:
            return False
        name = self.pkg_manager["name"]
        check_cmds = {
            "pacman": ["pacman", "-Q", package_name],
            "apt-get": ["dpkg", "-s", package_name],
            "dnf": ["rpm", "-q", package_name],
            "brew": ["brew", "list", package_name],
        }
        cmd = check_cmds.get(name)
        if not cmd:
            return False
        try:
            result = subprocess.run(
                cmd, capture_output=True, timeout=10,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def system_info(self):
        """return system detection info."""
        return {
            "os": self.os_info,
            "package_manager": self.pkg_manager["name"] if self.pkg_manager else None,
            "installed_count": len(self.install_log),
        }


if __name__ == "__main__":
    installer = OneClickInstaller()
    info = installer.system_info()
    print("system info:")
    for key, val in info.items():
        print(f"  {key}: {val}")
