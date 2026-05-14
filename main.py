"""
main.py
-------
Entry point for the CPU Scheduling Algorithm Simulator.

Run from the project root:
    python main.py

The program presents an interactive menu, collects process parameters
from the user, runs the selected scheduling algorithm, and displays a
Gantt chart with per-process and average metrics.
"""

from cpu_scheduler.menu import run

if __name__ == "__main__":
    run()
