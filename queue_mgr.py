#!/usr/bin/env python3
"""download queue manager for multiple package installs"""

import threading
import time
from collections import deque


class InstallJob:
    """represents a single package install job"""

    def __init__(self, package_name, install_fn):
        self.package_name = package_name
        self.install_fn = install_fn
        self.status = "queued"
        self.message = ""
        self.started_at = None
        self.finished_at = None

    def run(self):
        self.status = "installing"
        self.started_at = time.time()
        try:
            success, msg = self.install_fn(self.package_name)
            self.status = "done" if success else "failed"
            self.message = msg
        except Exception as e:
            self.status = "failed"
            self.message = str(e)
        self.finished_at = time.time()

    @property
    def duration(self):
        if self.started_at and self.finished_at:
            return self.finished_at - self.started_at
        return 0


class InstallQueue:
    """manage a queue of package installations"""

    def __init__(self, install_fn, on_progress=None, on_complete=None):
        self.queue = deque()
        self.history = []
        self.install_fn = install_fn
        self.on_progress = on_progress
        self.on_complete = on_complete
        self.running = False
        self._thread = None

    def add(self, package_name):
        """add a package to the install queue"""
        job = InstallJob(package_name, self.install_fn)
        self.queue.append(job)
        return job

    def add_many(self, package_names):
        """add multiple packages to the queue"""
        jobs = []
        for name in package_names:
            jobs.append(self.add(name))
        return jobs

    def start(self):
        """start processing the queue in a background thread"""
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._process, daemon=True)
        self._thread.start()

    def stop(self):
        """stop processing after current job finishes"""
        self.running = False

    def _process(self):
        """process jobs from the queue"""
        total = len(self.queue)
        completed = 0

        while self.queue and self.running:
            job = self.queue.popleft()
            job.run()
            self.history.append(job)
            completed += 1

            if self.on_progress:
                self.on_progress(completed, total, job)

        self.running = False
        if self.on_complete:
            self.on_complete(self.history)

    @property
    def pending_count(self):
        return len(self.queue)

    @property
    def completed_count(self):
        return len(self.history)

    def summary(self):
        """get summary of completed jobs"""
        done = sum(1 for j in self.history if j.status == "done")
        failed = sum(1 for j in self.history if j.status == "failed")
        total_time = sum(j.duration for j in self.history)
        return {
            "total": len(self.history),
            "done": done,
            "failed": failed,
            "pending": self.pending_count,
            "total_time": round(total_time, 1),
        }

    def clear_history(self):
        """clear completed job history"""
        self.history.clear()
