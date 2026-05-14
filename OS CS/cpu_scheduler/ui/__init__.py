"""
cpu_scheduler/ui/__init__.py
-----------------------------
Re-exports the public UI functions from a single namespace.
"""

from cpu_scheduler.ui.input_handler import (
    get_processes,
    get_time_quantum,
    get_algorithm_choice,
)
from cpu_scheduler.ui.display import (
    display_result,
    print_gantt,
    print_table,
    print_section_header,
)

__all__ = [
    "get_processes",
    "get_time_quantum",
    "get_algorithm_choice",
    "display_result",
    "print_gantt",
    "print_table",
    "print_section_header",
]
