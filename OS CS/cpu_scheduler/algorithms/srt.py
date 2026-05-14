"""
algorithms/srt.py
-----------------
Shortest Remaining Time (SRT) — Preemptive scheduling.

The preemptive variant of SJF. At every unit of time the scheduler
re-evaluates all available processes and runs the one with the least
remaining burst. A running process is preempted the moment a shorter
arrival appears. Gantt segments are flushed on every context switch.
"""

from __future__ import annotations
from typing import List, Optional, Tuple
from cpu_scheduler.core import Process, compute_metrics, clone_processes, GanttSegment


def srt(processes: List[Process]) -> Tuple[List[Process], List[GanttSegment]]:
    """
    Simulate SRT (preemptive SJF) scheduling on the given process list.

    The simulation advances one time unit per iteration to detect every
    possible preemption point. Consecutive units of the same process are
    later merged by merge_gantt() before display.

    Args:
        processes: Input list of Process objects (not mutated).

    Returns:
        (done, gantt) where:
            done  -- Processes in completion order with WT/TAT computed.
            gantt -- List of (pid, start, end) Gantt segments (un-merged).
    """
    procs: List[Process] = clone_processes(processes)
    for p in procs:
        p.remaining = p.burst      # initialise remaining burst

    time:       int            = 0
    gantt:      List[GanttSegment] = []
    done:       List[Process]  = []
    completed:  int            = 0
    n:          int            = len(procs)
    prev_pid:   Optional[str]  = None   # pid of the process running last tick
    prev_start: int            = 0      # start of the current unbroken segment

    while completed < n:
        # Build the set of processes that have arrived and still need CPU time
        available = [p for p in procs if p.arrival <= time and p.remaining > 0]

        if not available:
            # CPU is idle — flush any open segment, then jump to next arrival
            if prev_pid is not None:
                gantt.append((prev_pid, prev_start, time))
                prev_pid = None
            next_arrival = min(p.arrival for p in procs if p.remaining > 0)
            gantt.append(("IDLE", time, next_arrival))
            prev_start = next_arrival
            time = next_arrival
            continue

        # Pick the process with the shortest remaining time
        # Tie-break: earlier arrival, then pid
        chosen = min(available, key=lambda p: (p.remaining, p.arrival, p.pid))

        # Detect context switch: flush the previous segment when the runner changes
        if chosen.pid != prev_pid:
            if prev_pid is not None:
                gantt.append((prev_pid, prev_start, time))
            prev_pid   = chosen.pid
            prev_start = time

        # Record first CPU access for this process
        if chosen.start == -1:
            chosen.start = time

        # Execute one time unit
        chosen.remaining -= 1
        time += 1

        if chosen.remaining == 0:
            # Process finished — flush segment and record completion
            chosen.finish = time
            done.append(chosen)
            completed += 1
            gantt.append((chosen.pid, prev_start, time))
            prev_pid = None

    compute_metrics(done)
    return done, gantt
