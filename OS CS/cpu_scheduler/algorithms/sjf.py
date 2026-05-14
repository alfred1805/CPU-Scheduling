"""
algorithms/sjf.py
-----------------
Shortest Job First (SJF) — Non-preemptive scheduling.

At each dispatch point the scheduler picks the available (already-arrived)
process with the shortest burst time. Once selected, it runs to completion
without interruption. Ties are broken by arrival time then pid.
"""

from __future__ import annotations
from typing import List, Tuple
from cpu_scheduler.core import Process, compute_metrics, clone_processes, GanttSegment


def sjf(processes: List[Process]) -> Tuple[List[Process], List[GanttSegment]]:
    """
    Simulate SJF (non-preemptive) scheduling on the given process list.

    Args:
        processes: Input list of Process objects (not mutated).

    Returns:
        (done, gantt) where:
            done  -- Processes in completion order with WT/TAT computed.
            gantt -- List of (pid, start, end) Gantt segments.
    """
    # Work on clones; keep a mutable pool of unscheduled processes
    pool: List[Process] = clone_processes(processes)
    time: int = 0
    gantt: List[GanttSegment] = []
    done: List[Process] = []

    while pool:
        # Identify processes that have already arrived
        available = [p for p in pool if p.arrival <= time]

        if not available:
            # No process ready — advance the clock to the next arrival
            next_arrival = min(p.arrival for p in pool)
            gantt.append(("IDLE", time, next_arrival))
            time = next_arrival
            available = [p for p in pool if p.arrival <= time]

        # Select the process with the shortest burst time
        # Tie-break: earlier arrival first, then alphabetical pid
        chosen = min(available, key=lambda p: (p.burst, p.arrival, p.pid))
        pool.remove(chosen)

        # Advance clock to chosen's arrival if needed (edge case: time < arrival)
        if time < chosen.arrival:
            gantt.append(("IDLE", time, chosen.arrival))
            time = chosen.arrival

        # Run the chosen process to completion (non-preemptive)
        chosen.start  = time
        chosen.finish = time + chosen.burst
        gantt.append((chosen.pid, time, chosen.finish))
        time = chosen.finish
        done.append(chosen)

    compute_metrics(done)
    return done, gantt
