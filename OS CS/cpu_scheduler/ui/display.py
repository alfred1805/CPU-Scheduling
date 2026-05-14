"""
ui/display.py
-------------
All terminal output routines.

Responsibilities:
  - Print a formatted Gantt chart from a list of (pid, start, end) segments
  - Print a process summary table with WT, TAT, and averages
  - Print section headers and a full algorithm result block
"""

from __future__ import annotations
from typing import List
from cpu_scheduler.core import Process, merge_gantt, GanttSegment


# ── Public display functions ──────────────────────────────────────────────────

def print_gantt(gantt: List[GanttSegment]) -> None:
    """
    Render a text-based Gantt chart.

    Each segment is a cell whose width scales with the label length or
    duration (whichever is larger). Time markers are printed on the line
    below the chart.

    Example output:
        | P1  | P2 | IDLE | P3 |
        0     3    6      9    12
    """
    if not gantt:
        print("  (no execution recorded)")
        return

    # ── Bar row ──────────────────────────────────────────────────────────────
    bar = "|"
    for pid, s, e in gantt:
        cell_width = max(len(pid), e - s, 3)
        bar += f" {pid.center(cell_width)} |"
    print("  " + bar)

    # ── Time-marker row ───────────────────────────────────────────────────────
    # The first marker is the start of the first segment; every subsequent
    # marker is the end of its segment, right-aligned within the cell.
    markers = " " + str(gantt[0][1])
    for pid, s, e in gantt:
        cell_width = max(len(pid), e - s, 3)
        end_label  = str(e)
        # Padding: cell_width + 2 spaces for " " on each side, minus prev label width
        markers += " " * (cell_width + 2 - len(str(s))) + end_label
    print("  " + markers)


def print_table(processes: List[Process]) -> None:
    """
    Print a summary table of per-process metrics plus averages.

    Columns: PID | Arrival | Burst | Priority | WT | TAT
    Footer:  Average WT and Average TAT across all processes.
    """
    header = (
        f"  {'PID':<8} {'Arrival':<10} {'Burst':<8} "
        f"{'Priority':<10} {'WT':<8} {'TAT':<8}"
    )
    separator = "  " + "-" * 56

    print(header)
    print(separator)

    total_wt = total_tat = 0
    for p in processes:
        print(
            f"  {p.pid:<8} {p.arrival:<10} {p.burst:<8} "
            f"{p.priority:<10} {p.waiting:<8} {p.turnaround:<8}"
        )
        total_wt  += p.waiting
        total_tat += p.turnaround

    n = len(processes)
    print(separator)
    print(f"  Average Waiting Time    : {total_wt  / n:.2f}")
    print(f"  Average Turnaround Time : {total_tat / n:.2f}")


def print_section_header(title: str) -> None:
    """Print a visually distinct section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def display_result(
    algo_name: str,
    processes: List[Process],
    gantt: List[GanttSegment],
) -> None:
    """
    Display a complete algorithm result: header, Gantt chart, and table.

    Merges consecutive same-process Gantt segments before printing so that
    the preemptive algorithms (SRT, Priority, Priority+RR) produce a clean,
    readable chart rather than unit-wide cells.

    Args:
        algo_name: Human-readable label for the algorithm.
        processes: Completed process list with WT/TAT already computed.
        gantt:     Raw Gantt segment list (may have consecutive duplicates).
    """
    print_section_header(algo_name)
    merged = merge_gantt(gantt)
    print("\n  Gantt Chart:")
    print_gantt(merged)
    print("\n  Process Summary:")
    print_table(processes)
