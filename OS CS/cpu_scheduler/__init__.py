"""
cpu_scheduler/__init__.py
--------------------------
Top-level package for the CPU Scheduling Algorithm Simulator.

Package layout:
    cpu_scheduler/
        core/
            process.py       -- Process data class
            utils.py         -- compute_metrics, merge_gantt, clone_processes
        algorithms/
            fcfs.py          -- First-Come, First-Served
            sjf.py           -- Shortest Job First (non-preemptive)
            srt.py           -- Shortest Remaining Time (preemptive)
            round_robin.py   -- Round Robin
            priority.py      -- Priority Scheduling (preemptive)
            priority_rr.py   -- Priority Scheduling with Round Robin
        ui/
            input_handler.py -- User input collection and validation
            display.py       -- Terminal output (Gantt chart, table, headers)
        menu.py              -- Main menu loop and algorithm dispatcher
    main.py                  -- Entry point: python main.py
"""

from cpu_scheduler.core import Process, compute_metrics, merge_gantt, clone_processes
from cpu_scheduler.algorithms import (
    fcfs, sjf, srt, round_robin, priority_preemptive, priority_round_robin,
)

__all__ = [
    "Process",
    "compute_metrics",
    "merge_gantt",
    "clone_processes",
    "fcfs",
    "sjf",
    "srt",
    "round_robin",
    "priority_preemptive",
    "priority_round_robin",
]
