"""
cpu_scheduler/algorithms/__init__.py
-------------------------------------
Re-exports all six scheduling algorithm functions from a single namespace
so callers can simply write:

    from cpu_scheduler.algorithms import fcfs, sjf, srt, ...
"""

from cpu_scheduler.algorithms.fcfs        import fcfs
from cpu_scheduler.algorithms.sjf         import sjf
from cpu_scheduler.algorithms.srt         import srt
from cpu_scheduler.algorithms.round_robin import round_robin
from cpu_scheduler.algorithms.priority    import priority_preemptive
from cpu_scheduler.algorithms.priority_rr import priority_round_robin

__all__ = [
    "fcfs",
    "sjf",
    "srt",
    "round_robin",
    "priority_preemptive",
    "priority_round_robin",
]
