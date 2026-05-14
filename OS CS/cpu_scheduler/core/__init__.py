"""
cpu_scheduler/core/__init__.py
------------------------------
Public API for the core sub-package.
Import Process, utility functions, and the GanttSegment type alias
from a single location so algorithm modules only need one import.
"""

from cpu_scheduler.core.process import Process
from cpu_scheduler.core.utils import (
    compute_metrics,
    merge_gantt,
    clone_processes,
    GanttSegment,
)

__all__ = [
    "Process",
    "compute_metrics",
    "merge_gantt",
    "clone_processes",
    "GanttSegment",
]
