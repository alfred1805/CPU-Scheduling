"""
algorithms/fcfs.py
------------------
First-Come, First-Served (FCFS) — Non-preemptive scheduling.

Processes are dispatched in the order they arrive in the ready queue.
Once a process starts, it runs to completion. If the CPU becomes free
before the next arrival, an IDLE segment is inserted in the Gantt chart.
"""

from __future__ import annotations
from typing import List, Tuple
from cpu_scheduler.core import Process, compute_metrics, clone_processes, GanttSegment


def fcfs(processes: List[Process]) -> Tuple[List[Process], List[GanttSegment]]:
    """
    Simulate FCFS scheduling on the given process list.

    Args:
        processes: Input list of Process objects (not mutated).

    Returns:
        (done, gantt) where:
            done  -- Processes in completion order with WT/TAT computed.
            gantt -- List of (pid, start, end) Gantt segments.
    """
    # Work on clones to leave the caller's list untouched
    procs = clone_processes(processes)

    # Sort by arrival time; tie-break by pid to ensure deterministic order
    procs.sort(key=lambda p: (p.arrival, p.pid))

    time: int = 0
    gantt: List[GanttSegment] = []

    for p in procs:
        # If the CPU is idle between the last finish and this arrival, insert IDLE
        if time < p.arrival:
            gantt.append(("IDLE", time, p.arrival))
            time = p.arrival

        # Dispatch: the process runs until it completes (non-preemptive)
        p.start  = time
        p.finish = time + p.burst
        gantt.append((p.pid, time, p.finish))
        time = p.finish

    compute_metrics(procs)
    return procs, gantt
