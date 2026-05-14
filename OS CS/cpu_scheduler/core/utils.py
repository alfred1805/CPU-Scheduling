"""
core/utils.py
-------------
Shared utility functions used by all scheduling algorithms:
  - compute_metrics  : calculates WT and TAT after simulation
  - merge_gantt      : collapses consecutive same-process Gantt segments
  - clone_processes  : deep-copies a process list with reset runtime state
"""

from __future__ import annotations
from typing import List, Tuple
from cpu_scheduler.core.process import Process

# Type alias: a Gantt segment is (pid, start_time, end_time)
GanttSegment = Tuple[str, int, int]


def compute_metrics(processes: List[Process]) -> None:
    """
    Calculate Waiting Time (WT) and Turnaround Time (TAT) for every process
    in-place after each process's finish time has been set by an algorithm.

        TAT = finish - arrival
        WT  = TAT   - burst
    """
    for p in processes:
        p.turnaround = p.finish - p.arrival
        p.waiting    = p.turnaround - p.burst


def merge_gantt(gantt: List[GanttSegment]) -> List[GanttSegment]:
    """
    Merge consecutive Gantt segments that belong to the same process.

    Preemptive algorithms operate at unit-time granularity and therefore
    produce many adjacent segments for the same pid (e.g. P1|P1|P1).
    This function collapses them into a single segment (e.g. P1) so the
    printed chart is readable.

    Example:
        [("P1",0,1), ("P1",1,2), ("P2",2,4)] -> [("P1",0,2), ("P2",2,4)]
    """
    if not gantt:
        return gantt

    merged = [list(gantt[0])]          # work with lists for mutability
    for pid, s, e in gantt[1:]:
        if pid == merged[-1][0]:
            merged[-1][2] = e          # extend the end of the current segment
        else:
            merged.append([pid, s, e])

    return [tuple(seg) for seg in merged]


def clone_processes(processes: List[Process]) -> List[Process]:
    """
    Return a list of fresh Process clones with all runtime state reset.
    Algorithms call this so they never mutate the original input list,
    allowing the same process set to be re-used across multiple algorithm
    runs (e.g. the "run all" option in the menu).
    """
    return [p.clone() for p in processes]
