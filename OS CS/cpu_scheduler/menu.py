"""
cpu_scheduler/menu.py
---------------------
Main application controller.

Owns the menu loop and routes user selections to the correct algorithm.
Keeps all business-logic decisions (which algorithm, whether priority or
quantum is needed) in one place so the algorithm and UI modules remain
independent of each other.
"""

from __future__ import annotations
from cpu_scheduler.algorithms import (
    fcfs, sjf, srt, round_robin,
    priority_preemptive, priority_round_robin,
)
from cpu_scheduler.ui import (
    get_processes, get_time_quantum, get_algorithm_choice, display_result,
)


# ── Algorithm registry ────────────────────────────────────────────────────────
# Each entry: (label, needs_priority, needs_quantum, runner_function)
# runner_function signature: (processes, quantum=None) -> (done, gantt)
#   - For algorithms that do not use quantum, the argument is ignored.

def _run_fcfs(processes, quantum):
    return fcfs(processes)

def _run_sjf(processes, quantum):
    return sjf(processes)

def _run_srt(processes, quantum):
    return srt(processes)

def _run_rr(processes, quantum):
    return round_robin(processes, quantum)

def _run_priority(processes, quantum):
    return priority_preemptive(processes)

def _run_priority_rr(processes, quantum):
    return priority_round_robin(processes, quantum)


ALGORITHMS = {
    "1": ("1. First-Come, First-Served (FCFS)",              False, False, _run_fcfs),
    "2": ("2. Shortest Job First (SJF) — Non-preemptive",    False, False, _run_sjf),
    "3": ("3. Shortest Remaining Time (SRT) — Preemptive",   False, False, _run_srt),
    "4": ("4. Round Robin (RR)",                             False, True,  _run_rr),
    "5": ("5. Priority Scheduling — Preemptive",             True,  False, _run_priority),
    "6": ("6. Priority Scheduling with Round Robin",         True,  True,  _run_priority_rr),
}


# ── Public entry point ─────────────────────────────────────────────────────────

def run() -> None:
    """
    Launch the interactive menu loop.

    Displays the menu, collects user choices, gathers process data,
    runs the selected algorithm(s), and prints results. Loops until
    the user chooses to exit.
    """
    _print_banner()

    while True:
        choice = get_algorithm_choice()

        if choice == "0":
            print("Goodbye.")
            break

        if choice not in ALGORITHMS and choice != "7":
            print("  Invalid choice. Enter a number from 0 to 7.")
            continue

        # ── Determine input requirements ──────────────────────────────────────
        if choice == "7":
            # "Run all" always needs priority and quantum
            needs_priority = True
            needs_quantum  = True
        else:
            label, needs_priority, needs_quantum, _ = ALGORITHMS[choice]

        # ── Collect process data ──────────────────────────────────────────────
        print("\n--- Enter Process Details ---\n")
        try:
            processes = get_processes(need_priority=needs_priority)
        except KeyboardInterrupt:
            print("\n  Cancelled.")
            continue

        # ── Collect time quantum if needed ────────────────────────────────────
        quantum = None
        if needs_quantum:
            quantum = get_time_quantum()

        # ── Dispatch ──────────────────────────────────────────────────────────
        if choice == "7":
            _run_all(processes, quantum)
        else:
            label, _, _, runner = ALGORITHMS[choice]
            result, gantt = runner(processes, quantum)
            # Append quantum to label for RR-based algorithms
            display_label = (
                f"{label} — Quantum={quantum}" if needs_quantum else label
            )
            display_result(display_label, result, gantt)

        print()
        again = input("Run another algorithm? (y/n): ").strip().lower()
        if again != "y":
            print("Goodbye.")
            break


# ── Private helpers ────────────────────────────────────────────────────────────

def _run_all(processes, quantum):
    """Run all six algorithms in sequence on the same process set."""
    for key in ("1", "2", "3", "4", "5", "6"):
        label, _, needs_quantum, runner = ALGORITHMS[key]
        result, gantt = runner(processes, quantum)
        display_label = (
            f"{label} — Quantum={quantum}" if needs_quantum else label
        )
        display_result(display_label, result, gantt)


def _print_banner() -> None:
    """Print the application title banner and menu options."""
    print("\n" + "=" * 60)
    print("       CPU SCHEDULING ALGORITHM SIMULATOR")
    print("=" * 60)
    print("""
  Algorithms:
    1. First-Come, First-Served (FCFS)
    2. Shortest Job First (SJF) — Non-preemptive
    3. Shortest Remaining Time (SRT) — Preemptive
    4. Round Robin (RR)
    5. Priority Scheduling — Preemptive
    6. Priority Scheduling with Round Robin
    7. Run all algorithms
    0. Exit
""")
