"""
ui/input_handler.py
-------------------
All user-facing input routines.

Responsibilities:
  - Prompt for and validate the number of processes
  - Collect per-process attributes (pid, arrival, burst, priority)
  - Prompt for a time quantum
  - Prompt for the algorithm choice

Each function loops until it receives valid input, printing a clear
error message on each failed attempt.
"""

from __future__ import annotations
from typing import List
from cpu_scheduler.core import Process


def get_processes(need_priority: bool = True) -> List[Process]:
    """
    Interactively collect process details from the user.

    Args:
        need_priority: When True, prompts for a priority value per process.
                       When False, priority defaults to 0 (not needed by
                       FCFS, SJF, SRT, or plain Round Robin).

    Returns:
        A list of Process objects ready for use by any scheduling algorithm.
    """
    # ── Step 1: number of processes ─────────────────────────────────────────
    n = _read_int(
        prompt="Enter number of processes (min 3): ",
        error_msg="  Please enter at least 3 processes.",
        validate=lambda v: v >= 3,
    )

    processes: List[Process] = []
    print()

    # ── Step 2: per-process attributes ──────────────────────────────────────
    for i in range(n):
        default_pid = f"P{i + 1}"
        pid = input(f"  Process {i + 1} identifier (e.g., {default_pid}): ").strip()
        if not pid:
            pid = default_pid

        arrival = _read_int(
            prompt=f"  Arrival time for {pid}: ",
            error_msg="  Arrival time must be >= 0.",
            validate=lambda v: v >= 0,
        )
        burst = _read_int(
            prompt=f"  Burst time for {pid}: ",
            error_msg="  Burst time must be > 0.",
            validate=lambda v: v > 0,
        )
        priority = 0
        if need_priority:
            priority = _read_int(
                prompt=f"  Priority for {pid} (higher number = higher priority): ",
                error_msg="  Please enter a valid integer.",
                validate=lambda v: True,   # any integer is accepted
            )

        processes.append(Process(pid, arrival, burst, priority))
        print()

    return processes


def get_time_quantum() -> int:
    """
    Prompt the user for a positive integer time quantum.

    Returns:
        The validated time quantum value.
    """
    return _read_int(
        prompt="Enter Time Quantum (> 0): ",
        error_msg="  Time quantum must be > 0.",
        validate=lambda v: v > 0,
    )


def get_algorithm_choice() -> str:
    """
    Prompt the user for an algorithm selection from the main menu.

    Returns:
        The raw string entered by the user (validated by the caller).
    """
    return input("Select algorithm (0-7): ").strip()


# ── Private helper ─────────────────────────────────────────────────────────────

def _read_int(prompt: str, error_msg: str, validate) -> int:
    """
    Repeatedly prompt for an integer until `validate(value)` returns True.

    Args:
        prompt:     Text shown to the user.
        error_msg:  Text shown when validation fails or input is not an int.
        validate:   Callable(int) -> bool that returns True for acceptable values.

    Returns:
        A validated integer entered by the user.
    """
    while True:
        try:
            value = int(input(prompt))
            if validate(value):
                return value
            print(error_msg)
        except ValueError:
            print("  Invalid input. Please enter an integer.")
