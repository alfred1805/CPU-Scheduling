"""
algorithms/priority_rr.py
-------------------------
Priority Scheduling with Round Robin — Preemptive hybrid algorithm.

Processes are grouped by priority (higher number = higher priority).
The highest-priority group runs first; within that group, Round Robin
with the given quantum is applied. If a higher-priority process arrives
mid-quantum the current process is preempted and the new group takes over.
Lower-priority groups run only when no higher-priority work is pending.
"""

from __future__ import annotations
from typing import List, Tuple
from cpu_scheduler.core import Process, compute_metrics, clone_processes, GanttSegment


def priority_round_robin(
    processes: List[Process], quantum: int
) -> Tuple[List[Process], List[GanttSegment]]:
    """
    Simulate Priority + Round Robin scheduling on the given process list.

    Args:
        processes: Input list of Process objects (not mutated).
        quantum:   Maximum CPU time units per turn within a priority group.

    Returns:
        (done, gantt) where:
            done  -- Processes in completion order with WT/TAT computed.
            gantt -- List of (pid, start, end) Gantt segments.
    """
    procs: List[Process] = clone_processes(processes)
    for p in procs:
        p.remaining = p.burst

    # pending: processes not yet assigned to a RR group; sorted by arrival
    pending: List[Process] = sorted(procs, key=lambda p: (p.arrival, p.pid))
    time:    int           = 0
    gantt:   List[GanttSegment] = []
    done:    List[Process] = []

    while pending or any(p.remaining > 0 for p in procs):
        # ── Identify available processes ──────────────────────────────────────
        available = [p for p in pending if p.arrival <= time]

        if not available:
            # CPU idle — advance to the next arrival
            next_arr = min(p.arrival for p in pending)
            gantt.append(("IDLE", time, next_arr))
            time = next_arr
            available = [p for p in pending if p.arrival <= time]

        # ── Build the RR group for the current highest priority tier ──────────
        max_prio = max(p.priority for p in available)
        rr_group = [p for p in available if p.priority == max_prio]

        # Remove the selected group from the pending pool
        for p in rr_group:
            pending.remove(p)

        # ── Run one RR cycle over the group ───────────────────────────────────
        interrupted, requeue = _run_rr_cycle(
            rr_group, pending, done, gantt, time, quantum, max_prio
        )
        time = interrupted   # _run_rr_cycle returns the updated clock

        # Leftover processes (unfinished or preempted) go back to pending
        pending.extend(requeue)

    compute_metrics(done)
    return done, gantt


# ── Private helper ─────────────────────────────────────────────────────────────

def _run_rr_cycle(
    rr_group: List[Process],
    pending:  List[Process],
    done:     List[Process],
    gantt:    List[GanttSegment],
    time:     int,
    quantum:  int,
    max_prio: int,
) -> Tuple[int, List[Process]]:
    """
    Execute one full Round Robin cycle over `rr_group`.

    Returns:
        (time, requeue) where `time` is the updated clock and `requeue`
        is the list of processes that must re-enter the pending pool
        (either because they were preempted or still have remaining burst).
    """
    requeue: List[Process] = []

    for idx, current in enumerate(rr_group):
        # Check for a higher-priority arrival before we execute this process
        higher_arrivals = [
            p for p in pending
            if p.arrival <= time and p.priority > max_prio
        ]
        if higher_arrivals:
            # Preempt: return the rest of the group (including `current`) to pending
            requeue.extend(rr_group[idx:])
            return time, requeue

        exec_time = min(quantum, current.remaining)

        # Record first CPU access for this process
        if current.start == -1:
            current.start = time

        # Execute for exec_time units and log the Gantt segment
        gantt.append((current.pid, time, time + exec_time))
        time              += exec_time
        current.remaining -= exec_time

        # Admit newly arrived same-priority processes into the cycle's requeue
        newly_arrived = [p for p in pending if p.arrival <= time]
        higher = [p for p in newly_arrived if p.priority > max_prio]

        if higher:
            # A higher-priority process arrived mid-quantum — flush and break
            if current.remaining > 0:
                requeue.append(current)
            else:
                current.finish = time
                done.append(current)
            requeue.extend(rr_group[idx + 1:])
            return time, requeue

        # Admit same-priority arrivals to the back of the current cycle
        same_prio = [
            p for p in newly_arrived
            if p.priority == max_prio and p not in rr_group and p not in requeue
        ]
        for p in same_prio:
            requeue.append(p)
            pending.remove(p)

        # Decide fate of the current process
        if current.remaining > 0:
            requeue.append(current)   # not finished — re-queue for another turn
        else:
            current.finish = time
            done.append(current)

    # Entire group completed one full cycle without high-priority interruption
    return time, requeue
