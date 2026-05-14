"""
algorithms/round_robin.py
-------------------------
Round Robin (RR) — Preemptive scheduling with a fixed time quantum.

Each process is allowed to run for at most `quantum` time units per turn.
If it has not finished it is placed at the back of the ready queue.
Newly arrived processes are admitted to the back of the queue after each
quantum completes, preserving the cyclic ordering. An IDLE segment is
inserted whenever the queue is empty but processes still remain.
"""

from __future__ import annotations
from typing import List, Set, Tuple
from cpu_scheduler.core import Process, compute_metrics, clone_processes, GanttSegment


def round_robin(
    processes: List[Process], quantum: int
) -> Tuple[List[Process], List[GanttSegment]]:
    """
    Simulate Round Robin scheduling with the given time quantum.

    Args:
        processes: Input list of Process objects (not mutated).
        quantum:   Maximum CPU time units granted per turn (must be > 0).

    Returns:
        (done, gantt) where:
            done  -- Processes in completion order with WT/TAT computed.
            gantt -- List of (pid, start, end) Gantt segments.
    """
    procs: List[Process] = clone_processes(processes)
    for p in procs:
        p.remaining = p.burst

    # Sort by arrival so the initial queue is in chronological order
    arrival_order = sorted(procs, key=lambda p: (p.arrival, p.pid))

    time:      int           = 0
    gantt:     List[GanttSegment] = []
    ready:     List[Process] = []   # circular ready queue
    done:      List[Process] = []
    pending:   List[Process] = list(arrival_order)   # not yet in the ready queue
    admitted:  Set[str]      = set()                 # tracks pids already enqueued

    # Seed the ready queue with any process that arrives at or before time 0
    _admit_arrivals(pending, ready, admitted, time)

    while ready or pending:
        if not ready:
            # No process is ready — advance clock to the next arrival
            next_arrival = min(p.arrival for p in pending)
            gantt.append(("IDLE", time, next_arrival))
            time = next_arrival
            _admit_arrivals(pending, ready, admitted, time)

        current    = ready.pop(0)
        exec_time  = min(quantum, current.remaining)

        # Record the first time this process touches the CPU
        if current.start == -1:
            current.start = time

        # Execute for exec_time units and append a Gantt segment
        gantt.append((current.pid, time, time + exec_time))
        time              += exec_time
        current.remaining -= exec_time

        # Admit any processes that arrived during this quantum
        _admit_arrivals(pending, ready, admitted, time)

        if current.remaining > 0:
            # Process is not finished — send it to the back of the queue
            ready.append(current)
        else:
            current.finish = time
            done.append(current)

    compute_metrics(done)
    return done, gantt


# ── Private helper ────────────────────────────────────────────────────────────

def _admit_arrivals(
    pending:  List[Process],
    ready:    List[Process],
    admitted: Set[str],
    time:     int,
) -> None:
    """
    Move processes from `pending` to the back of `ready` if their
    arrival time is at or before `time` and they have not been admitted yet.
    Processes are admitted in arrival order to maintain fairness.
    """
    to_admit = [p for p in pending if p.arrival <= time and p.pid not in admitted]
    # Sort by arrival then pid to ensure deterministic admission order
    to_admit.sort(key=lambda p: (p.arrival, p.pid))
    for p in to_admit:
        ready.append(p)
        admitted.add(p.pid)
        pending.remove(p)
