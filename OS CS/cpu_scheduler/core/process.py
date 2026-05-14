"""
core/process.py
---------------
Defines the Process data class used by all scheduling algorithms.
Each Process instance holds both its static input attributes (pid,
arrival, burst, priority) and the runtime state that algorithms
update during simulation (remaining, start, finish, waiting,
turnaround).
"""


class Process:
    """
    Represents a single process with all scheduling attributes.

    Static attributes (set at creation):
        pid       -- Process identifier string, e.g. "P1"
        arrival   -- Time the process enters the ready queue
        burst     -- Original CPU burst duration
        priority  -- Numeric priority (higher number = higher priority)

    Runtime attributes (updated during simulation):
        remaining  -- Burst time still left; used by preemptive algorithms
        start      -- Clock time when the process first received the CPU
        finish     -- Clock time when the process completed execution
        waiting    -- Computed waiting time  (TAT - burst)
        turnaround -- Computed turnaround time (finish - arrival)
    """

    def __init__(self, pid: str, arrival: int, burst: int, priority: int = 0):
        # ── Static input fields ──────────────────────────────────────────────
        self.pid      = pid        # Process identifier
        self.arrival  = arrival    # Arrival time in the ready queue
        self.burst    = burst      # Original (full) burst time
        self.priority = priority   # Scheduling priority value

        # ── Runtime simulation state ─────────────────────────────────────────
        self.remaining  = burst    # Remaining burst (decremented by preemptive algos)
        self.start      = -1       # -1 means the process has not started yet
        self.finish     = 0        # Completion time (set when remaining reaches 0)
        self.waiting    = 0        # Waiting time (computed after finish is known)
        self.turnaround = 0        # Turnaround time (computed after finish is known)

    def clone(self) -> "Process":
        """
        Return a fresh copy of this process with runtime state reset.
        Used by algorithms that must not mutate the caller's process list.
        """
        return Process(self.pid, self.arrival, self.burst, self.priority)

    def __repr__(self) -> str:
        return (
            f"Process(pid={self.pid!r}, arrival={self.arrival}, "
            f"burst={self.burst}, priority={self.priority})"
        )
