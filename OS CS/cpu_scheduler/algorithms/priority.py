"""
algorithms/priority.py
----------------------
Priority Scheduling — Preemptive (higher number = higher priority).

At every unit of time the available process with the highest numeric
priority is selected. A running process is preempted immediately if a
newly arrived process has a strictly higher priority. Ties in priority
are broken by arrival time (earlier first), then by pid.
"""

from __future__ import annotations
from typing import List, Optional, Tuple
from cpu_scheduler.core import Process, compute_metrics, clone_processes, GanttSegment


def priority_preemptive(
    processes: List[Process],
) -> Tuple[List[Process], List[GanttSegment]]:
    """
    Simulate preemptive Priority scheduling on the given process list.

    The simulation advances one time unit per iteration so every
    preemption point is captured. Gantt segments are flushed whenever
    the running process changes. Consecutive same-process segments are
    collapsed by merge_gantt() before display.

    Args:
        processes: Input list of Process objects (not mutated).

    Returns:
        (done, gantt) where:
            done  -- Processes in completion order with WT/TAT computed.
            gantt -- List of (pid, start, end) Gantt segments (un-merged).
    """
    procs: List[Process] = clone_processes(processes)
    for p in procs:
        p.remaining = p.burst

    time:       int            = 0
    gantt:      List[GanttSegment] = []
    done:       List[Process]  = []
    completed:  int            = 0
    n:          int            = len(procs)
    prev_pid:   Optional[str]  = None   # pid currently "owning" an open segment
    prev_start: int            = 0      # start of that open segment

    while completed < n:
        # Find all processes that have arrived and still need CPU time
        available = [p for p in procs if p.arrival <= time and p.remaining > 0]

        if not available:
            # CPU idle — flush any open segment, jump forward
            if prev_pid is not None:
                gantt.append((prev_pid, prev_start, time))
                prev_pid = None
            next_arrival = min(p.arrival for p in procs if p.remaining > 0)
            gantt.append(("IDLE", time, next_arrival))
            prev_start = next_arrival
            time = next_arrival
            continue

        # Select highest-priority process
        # Tie-break: prefer earlier arrival, then lexicographically smaller pid
        chosen = max(available, key=lambda p: (p.priority, -p.arrival, p.pid))

        # Flush the previous segment on a context switch
        if chosen.pid != prev_pid:
            if prev_pid is not None:
                gantt.append((prev_pid, prev_start, time))
            prev_pid   = chosen.pid
            prev_start = time

        # Record first CPU access
        if chosen.start == -1:
            chosen.start = time

        # Execute one time unit
        chosen.remaining -= 1
        time += 1

        if chosen.remaining == 0:
            chosen.finish = time
            done.append(chosen)
            completed += 1
            gantt.append((chosen.pid, prev_start, time))
            prev_pid = None

    compute_metrics(done)
    return done, gantt
