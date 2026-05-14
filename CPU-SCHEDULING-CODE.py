"""
CPU Scheduling Algorithm Simulator
====================================
Simulates 6 scheduling algorithms:
  1. First-Come, First-Served (FCFS)
  2. Shortest Job First (SJF) - Non-preemptive
  3. Shortest Remaining Time (SRT) - Preemptive
  4. Round Robin (RR)
  5. Priority Scheduling - Preemptive (higher number = higher priority)
  6. Priority Scheduling with Round Robin

Each algorithm outputs:
  - Gantt Chart
  - Per-process Waiting Time (WT) and Turnaround Time (TAT)
  - Average WT and Average TAT
"""

# ─────────────────────────────────────────────
# Data Structures
# ─────────────────────────────────────────────

class Process:
    """Represents a single process with scheduling attributes."""
    def __init__(self, pid, arrival, burst, priority=0):
        self.pid      = pid        # Process identifier (e.g., P1)
        self.arrival  = arrival    # Arrival time
        self.burst    = burst      # Original burst time
        self.priority = priority   # Priority (higher number = higher priority)
        self.remaining = burst     # Remaining burst time (used in preemptive algorithms)
        self.start    = -1         # First time the process started execution
        self.finish   = 0          # Completion time
        self.waiting  = 0          # Waiting time
        self.turnaround = 0        # Turnaround time


# ─────────────────────────────────────────────
# Input Handling
# ─────────────────────────────────────────────

def get_processes(need_priority=True):
    """
    Prompt the user for the number of processes and their attributes.
    Returns a list of Process objects.
    """
    while True:
        try:
            n = int(input("Enter number of processes (min 3): "))
            if n >= 3:
                break
            print("  Please enter at least 3 processes.")
        except ValueError:
            print("  Invalid input. Enter an integer.")

    processes = []
    print()
    for i in range(n):
        pid = input(f"  Process {i+1} identifier (e.g., P{i+1}): ").strip() or f"P{i+1}"
        while True:
            try:
                arrival = int(input(f"  Arrival time for {pid}: "))
                if arrival >= 0:
                    break
                print("  Arrival time must be >= 0.")
            except ValueError:
                print("  Invalid input.")
        while True:
            try:
                burst = int(input(f"  Burst time for {pid}: "))
                if burst > 0:
                    break
                print("  Burst time must be > 0.")
            except ValueError:
                print("  Invalid input.")
        priority = 0
        if need_priority:
            while True:
                try:
                    priority = int(input(f"  Priority for {pid} (higher number = higher priority): "))
                    break
                except ValueError:
                    print("  Invalid input.")
        processes.append(Process(pid, arrival, burst, priority))
        print()
    return processes


def get_time_quantum():
    """Prompt the user for a time quantum used in Round Robin variants."""
    while True:
        try:
            tq = int(input("Enter Time Quantum (> 0): "))
            if tq > 0:
                return tq
            print("  Time quantum must be > 0.")
        except ValueError:
            print("  Invalid input.")


# ─────────────────────────────────────────────
# Output Helpers
# ─────────────────────────────────────────────

def print_gantt(gantt):
    """
    Renders a text-based Gantt chart from a list of (pid, start, end) tuples.
    Example:  | P1 | P2 | IDLE | P3 |
              0    3    6      9    12
    """
    if not gantt:
        print("  (no execution)")
        return

    # Top border
    bar = "|"
    for (pid, s, e) in gantt:
        width = max(len(pid), e - s, 3)
        bar += f" {pid.center(width)} |"
    print("  " + bar)

    # Time markers
    times = " " + str(gantt[0][1])
    for (pid, s, e) in gantt:
        width = max(len(pid), e - s, 3)
        label = str(e)
        times += " " * (width + 2 - len(str(s))) + label
    print("  " + times)


def print_table(processes):
    """
    Prints a summary table with WT and TAT per process,
    plus the average values at the bottom.
    """
    header = f"  {'PID':<8} {'Arrival':<10} {'Burst':<8} {'Priority':<10} {'WT':<8} {'TAT':<8}"
    print(header)
    print("  " + "-" * 56)
    total_wt = total_tat = 0
    for p in processes:
        print(f"  {p.pid:<8} {p.arrival:<10} {p.burst:<8} {p.priority:<10} {p.waiting:<8} {p.turnaround:<8}")
        total_wt  += p.waiting
        total_tat += p.turnaround
    n = len(processes)
    print("  " + "-" * 56)
    print(f"  Average Waiting Time    : {total_wt  / n:.2f}")
    print(f"  Average Turnaround Time : {total_tat / n:.2f}")


def compute_metrics(processes):
    """Calculate WT and TAT for each process after finish times are set."""
    for p in processes:
        p.turnaround = p.finish - p.arrival
        p.waiting    = p.turnaround - p.burst


def section(title):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


# ─────────────────────────────────────────────
# Algorithm 1: First-Come, First-Served (FCFS)
# ─────────────────────────────────────────────

def fcfs(processes):
    """
    FCFS — Non-preemptive.
    Processes are executed in the order they arrive.
    Ties in arrival time are broken by the order they were entered.
    """
    procs = sorted(processes, key=lambda p: (p.arrival, p.pid))
    time  = 0
    gantt = []

    for p in procs:
        # If CPU is idle, jump to the process arrival
        if time < p.arrival:
            gantt.append(("IDLE", time, p.arrival))
            time = p.arrival
        p.start  = time
        p.finish = time + p.burst
        gantt.append((p.pid, time, p.finish))
        time = p.finish

    compute_metrics(procs)
    return procs, gantt


# ─────────────────────────────────────────────
# Algorithm 2: Shortest Job First (SJF) — Non-preemptive
# ─────────────────────────────────────────────

def sjf(processes):
    """
    SJF — Non-preemptive.
    At each decision point, the process with the shortest burst time
    among all currently available (arrived) processes is selected.
    Once a process starts, it runs to completion.
    """
    procs     = [Process(p.pid, p.arrival, p.burst, p.priority) for p in processes]
    remaining = list(procs)
    time      = 0
    gantt     = []
    done      = []

    while remaining:
        # Processes that have arrived by current time
        available = [p for p in remaining if p.arrival <= time]
        if not available:
            # No process ready — advance time to the next arrival
            next_arrival = min(p.arrival for p in remaining)
            gantt.append(("IDLE", time, next_arrival))
            time = next_arrival
            available = [p for p in remaining if p.arrival <= time]

        # Select the process with the shortest burst (tie-break: arrival, then pid)
        chosen = min(available, key=lambda p: (p.burst, p.arrival, p.pid))
        remaining.remove(chosen)

        if time < chosen.arrival:
            gantt.append(("IDLE", time, chosen.arrival))
            time = chosen.arrival

        chosen.start  = time
        chosen.finish = time + chosen.burst
        gantt.append((chosen.pid, time, chosen.finish))
        time = chosen.finish
        done.append(chosen)

    compute_metrics(done)
    return done, gantt


# ─────────────────────────────────────────────
# Algorithm 3: Shortest Remaining Time (SRT) — Preemptive
# ─────────────────────────────────────────────

def srt(processes):
    """
    SRT — Preemptive version of SJF.
    At every time unit, the process with the shortest remaining burst
    is selected. A running process is preempted if a new arrival has
    a shorter remaining time.
    """
    procs = [Process(p.pid, p.arrival, p.burst, p.priority) for p in processes]
    for p in procs:
        p.remaining = p.burst

    time      = 0
    gantt     = []
    done      = []
    completed = 0
    n         = len(procs)
    prev_pid  = None
    prev_start = 0

    while completed < n:
        available = [p for p in procs if p.arrival <= time and p.remaining > 0]
        if not available:
            # CPU idle
            next_arrival = min(p.arrival for p in procs if p.remaining > 0)
            if prev_pid is not None:
                gantt.append((prev_pid, prev_start, time))
                prev_pid = None
            gantt.append(("IDLE", time, next_arrival))
            prev_start = next_arrival
            time = next_arrival
            continue

        # Choose process with shortest remaining time
        chosen = min(available, key=lambda p: (p.remaining, p.arrival, p.pid))

        # Record Gantt segment if process changes
        if chosen.pid != prev_pid:
            if prev_pid is not None:
                gantt.append((prev_pid, prev_start, time))
            prev_pid   = chosen.pid
            prev_start = time

        # Record first start time
        if chosen.start == -1:
            chosen.start = time

        # Execute for 1 time unit
        chosen.remaining -= 1
        time += 1

        if chosen.remaining == 0:
            chosen.finish = time
            done.append(chosen)
            completed += 1
            gantt.append((chosen.pid, prev_start, time))
            prev_pid = None

    compute_metrics(done)
    # Restore original burst for display
    for p in done:
        p.burst = p.burst  # already stored separately
    return done, gantt


def _merge_gantt(gantt):
    """Merge consecutive identical Gantt segments (e.g., P1|P1 → P1)."""
    if not gantt:
        return gantt
    merged = [gantt[0]]
    for pid, s, e in gantt[1:]:
        if pid == merged[-1][0]:
            merged[-1] = (pid, merged[-1][1], e)
        else:
            merged.append((pid, s, e))
    return merged


# ─────────────────────────────────────────────
# Algorithm 4: Round Robin (RR)
# ─────────────────────────────────────────────

def round_robin(processes, quantum):
    """
    Round Robin — Preemptive with a fixed time quantum.
    Processes are served in a circular order; each gets at most
    `quantum` time units per turn. New arrivals are added to the
    back of the ready queue.
    """
    procs = [Process(p.pid, p.arrival, p.burst, p.priority) for p in processes]
    for p in procs:
        p.remaining = p.burst

    # Sort by arrival for initial ordering
    arrival_order = sorted(procs, key=lambda p: (p.arrival, p.pid))
    time      = 0
    gantt     = []
    queue     = []
    done      = []
    remaining = list(arrival_order)
    visited   = set()

    # Seed queue with processes that arrive at time 0
    for p in arrival_order:
        if p.arrival <= time and p.pid not in visited:
            queue.append(p)
            visited.add(p.pid)
            remaining.remove(p)

    while queue or remaining:
        if not queue:
            # CPU idle — jump to next arrival
            next_arrival = min(p.arrival for p in remaining)
            gantt.append(("IDLE", time, next_arrival))
            time = next_arrival
            for p in list(remaining):
                if p.arrival <= time and p.pid not in visited:
                    queue.append(p)
                    visited.add(p.pid)
                    remaining.remove(p)

        current = queue.pop(0)
        exec_time = min(quantum, current.remaining)

        if current.start == -1:
            current.start = time

        gantt.append((current.pid, time, time + exec_time))
        time += exec_time
        current.remaining -= exec_time

        # Enqueue newly arrived processes (arrived during this slice)
        for p in list(remaining):
            if p.arrival <= time and p.pid not in visited:
                queue.append(p)
                visited.add(p.pid)
                remaining.remove(p)

        if current.remaining > 0:
            queue.append(current)   # Re-queue unfinished process
        else:
            current.finish = time
            done.append(current)

    compute_metrics(done)
    return done, gantt


# ─────────────────────────────────────────────
# Algorithm 5: Priority Scheduling — Preemptive
# ─────────────────────────────────────────────

def priority_preemptive(processes):
    """
    Priority Scheduling — Preemptive.
    Higher number = higher priority.
    At every time unit, the ready process with the highest priority runs.
    A running process is preempted if a higher-priority process arrives.
    Ties in priority are broken by arrival time, then process ID.
    """
    procs = [Process(p.pid, p.arrival, p.burst, p.priority) for p in processes]
    for p in procs:
        p.remaining = p.burst

    time       = 0
    gantt      = []
    done       = []
    completed  = 0
    n          = len(procs)
    prev_pid   = None
    prev_start = 0

    while completed < n:
        available = [p for p in procs if p.arrival <= time and p.remaining > 0]
        if not available:
            next_arrival = min(p.arrival for p in procs if p.remaining > 0)
            if prev_pid is not None:
                gantt.append((prev_pid, prev_start, time))
                prev_pid = None
            gantt.append(("IDLE", time, next_arrival))
            prev_start = next_arrival
            time = next_arrival
            continue

        # Choose process with highest priority (higher number = higher priority)
        chosen = max(available, key=lambda p: (p.priority, -p.arrival, p.pid))

        if chosen.pid != prev_pid:
            if prev_pid is not None:
                gantt.append((prev_pid, prev_start, time))
            prev_pid   = chosen.pid
            prev_start = time

        if chosen.start == -1:
            chosen.start = time

        chosen.remaining -= 1
        time += 1

        if chosen.remaining == 0:
            chosen.finish = time
            done.append(chosen)
            completed += 1
            gantt.append((chosen.pid, prev_start, time))
            prev_pid = None

    compute_metrics(done)
    return done, gantt


# ─────────────────────────────────────────────
# Algorithm 6: Priority Scheduling with Round Robin
# ─────────────────────────────────────────────

def priority_round_robin(processes, quantum):
    """
    Priority Scheduling with Round Robin.
    Processes are grouped by priority (higher number = higher priority).
    Within the same priority level, Round Robin with the given quantum is applied.
    A lower-priority group only runs when all higher-priority processes are done.
    """
    procs = [Process(p.pid, p.arrival, p.burst, p.priority) for p in processes]
    for p in procs:
        p.remaining = p.burst

    time     = 0
    gantt    = []
    done     = []
    pending  = sorted(procs, key=lambda p: (p.arrival, p.pid))

    while pending or any(p.remaining > 0 for p in procs):
        # Find highest priority among currently available processes
        available = [p for p in pending if p.arrival <= time]
        if not available:
            next_arr = min(p.arrival for p in pending)
            gantt.append(("IDLE", time, next_arr))
            time = next_arr
            available = [p for p in pending if p.arrival <= time]

        max_prio = max(p.priority for p in available)

        # Build RR queue for this priority level
        rr_group = [p for p in available if p.priority == max_prio]

        # Remove group from pending
        for p in rr_group:
            pending.remove(p)

        # Run one RR cycle for this group
        requeue = []
        for current in rr_group:
            # Check if a higher-priority process has arrived
            new_arrivals = [p for p in pending if p.arrival <= time and p.priority > max_prio]
            if new_arrivals:
                requeue.extend(rr_group[rr_group.index(current):])
                break

            exec_time = min(quantum, current.remaining)
            if current.start == -1:
                current.start = time

            gantt.append((current.pid, time, time + exec_time))
            time += exec_time
            current.remaining -= exec_time

            # Admit new arrivals
            newly_arrived = [p for p in pending if p.arrival <= time]
            # Higher priority arrivals break the current group cycle
            higher = [p for p in newly_arrived if p.priority > max_prio]
            if higher:
                if current.remaining > 0:
                    requeue.append(current)
                else:
                    current.finish = time
                    done.append(current)
                requeue.extend(rr_group[rr_group.index(current)+1:])
                break
            else:
                same_or_lower = [p for p in newly_arrived if p.priority == max_prio]
                for p in same_or_lower:
                    if p not in rr_group and p not in requeue:
                        requeue.append(p)
                        pending.remove(p)

            if current.remaining > 0:
                requeue.append(current)
            else:
                current.finish = time
                done.append(current)
        else:
            # Group finished one full cycle without interruption
            pending.extend(requeue)
            requeue = []
            continue

        pending.extend(requeue)

    compute_metrics(done)
    return done, gantt


# ─────────────────────────────────────────────
# Main Menu
# ─────────────────────────────────────────────

def display_result(algo_name, processes, gantt):
    """Helper to display a full result block for an algorithm."""
    section(algo_name)
    # Merge consecutive same-process segments for cleaner Gantt display
    merged = _merge_gantt(gantt)
    print("\n  Gantt Chart:")
    print_gantt(merged)
    print("\n  Process Summary:")
    print_table(processes)


def main():
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

    while True:
        choice = input("Select algorithm (0–7): ").strip()
        if choice == "0":
            print("Goodbye.")
            break

        # Determine if priority input is needed
        needs_priority = choice in {"5", "6", "7"}

        print("\n--- Enter Process Details ---\n")
        try:
            processes = get_processes(need_priority=needs_priority)
        except KeyboardInterrupt:
            print("\nCancelled.")
            continue

        quantum = None
        if choice in {"4", "6", "7"}:
            quantum = get_time_quantum()

        if choice == "1":
            result, gantt = fcfs(processes)
            display_result("1. First-Come, First-Served (FCFS)", result, gantt)

        elif choice == "2":
            result, gantt = sjf(processes)
            display_result("2. Shortest Job First (SJF) — Non-preemptive", result, gantt)

        elif choice == "3":
            result, gantt = srt(processes)
            display_result("3. Shortest Remaining Time (SRT) — Preemptive", result, gantt)

        elif choice == "4":
            result, gantt = round_robin(processes, quantum)
            display_result(f"4. Round Robin (RR) — Quantum={quantum}", result, gantt)

        elif choice == "5":
            result, gantt = priority_preemptive(processes)
            display_result("5. Priority Scheduling — Preemptive (higher = more priority)", result, gantt)

        elif choice == "6":
            result, gantt = priority_round_robin(processes, quantum)
            display_result(f"6. Priority Scheduling with Round Robin — Quantum={quantum}", result, gantt)

        elif choice == "7":
            # Run all — needs priority for algorithms 5 and 6
            if not needs_priority:
                print("\nNote: Algorithms 5 & 6 require priority values.")
                print("Re-enter processes with priority values.\n")
                try:
                    processes = get_processes(need_priority=True)
                    if quantum is None:
                        quantum = get_time_quantum()
                except KeyboardInterrupt:
                    print("\nCancelled.")
                    continue

            r1, g1 = fcfs(processes)
            display_result("1. First-Come, First-Served (FCFS)", r1, g1)

            r2, g2 = sjf(processes)
            display_result("2. Shortest Job First (SJF) — Non-preemptive", r2, g2)

            r3, g3 = srt(processes)
            display_result("3. Shortest Remaining Time (SRT) — Preemptive", r3, g3)

            r4, g4 = round_robin(processes, quantum)
            display_result(f"4. Round Robin (RR) — Quantum={quantum}", r4, g4)

            r5, g5 = priority_preemptive(processes)
            display_result("5. Priority Scheduling — Preemptive", r5, g5)

            r6, g6 = priority_round_robin(processes, quantum)
            display_result(f"6. Priority Scheduling with Round Robin — Quantum={quantum}", r6, g6)

        else:
            print("  Invalid choice. Enter a number from 0 to 7.")
            continue

        print("\n")
        again = input("Run another algorithm? (y/n): ").strip().lower()
        if again != "y":
            print("Goodbye.")
            break


if __name__ == "__main__":
    main()
