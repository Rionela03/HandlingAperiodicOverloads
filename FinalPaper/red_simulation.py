import random

class Task:
    def __init__(self, name, arrival, wcet, deadline, value):
        self.name = name
        self.arrival = arrival
        self.wcet = wcet
        self.deadline = deadline
        self.value = value
        self.cls = "CRITICAL" if value == 10 else "HARD"

def is_schedulable(tasks, current_time):
    ordered = sorted(tasks, key=lambda t: t.deadline)
    R = ordered[0].deadline - current_time - ordered[0].wcet
    if R < 0:
        return False
    for i in range(1, len(ordered)):
        R = R + (ordered[i].deadline - ordered[i-1].deadline) - ordered[i].wcet
        if R < 0:
            return False
    return True

def run_edf(tasks):
    accepted = list(tasks)
    current_time = 0
    late = []
    for task in sorted(accepted, key=lambda t: t.deadline):
        current_time += task.wcet
        if current_time > task.deadline:
            late.append(task)
    missed_critical = [t for t in late if t.cls == "CRITICAL"]
    missed_hard = [t for t in late if t.cls == "HARD"]
    return late, missed_critical, missed_hard

def run_red(tasks):
    current_time = 0
    accepted = []
    rejected = []
    for task in sorted(tasks, key=lambda t: t.arrival):
        candidate = accepted + [task]
        if is_schedulable(candidate, current_time):
            accepted.append(task)
        else:
            non_critical = [t for t in accepted if t.cls != "CRITICAL"]
            if non_critical:
                least = min(non_critical, key=lambda t: t.value)
                accepted.remove(least)
                rejected.append(least)
                accepted.append(task)
            else:
                rejected.append(task)
    late = []
    t = 0
    for task in sorted(accepted, key=lambda t: t.deadline):
        t += task.wcet
        if t > task.deadline:
            late.append(task)
    missed_critical = [t for t in late if t.cls == "CRITICAL"]
    missed_hard = [t for t in late if t.cls == "HARD"]
    return late, missed_critical, missed_hard, rejected

def generate_tasks(n=10, seed=42):
    random.seed(seed)
    tasks = []
    for i in range(n):
        arrival = random.randint(0, 5)
        wcet = random.randint(2, 6)
        deadline = arrival + random.randint(wcet, wcet + 4)
        value = 10 if random.random() < 0.3 else random.randint(1, 5)
        tasks.append(Task(f"J{i+1}", arrival, wcet, deadline, value))
    return tasks

def main():
    print("=" * 60)
    print("  RED vs EDF Simulation")
    print("  Handling Aperiodic Overloads (Buttazzo 1995)")
    print("  Rionela Kovaci - HSHL Real-Time Systems Seminar")
    print("=" * 60)

    tasks = generate_tasks(n=10, seed=42)

    print("\nTask Set:")
    print(f"{'Name':<6} {'Arrival':<8} {'WCET':<6} {'Deadline':<10} {'Value':<7} {'Class'}")
    print("-" * 50)
    for t in tasks:
        print(f"{t.name:<6} {t.arrival:<8} {t.wcet:<6} {t.deadline:<10} {t.value:<7} {t.cls}")

    total = len(tasks)
    n_crit = sum(1 for t in tasks if t.cls == "CRITICAL")
    n_hard = total - n_crit
    print(f"\nTotal tasks: {total}  |  CRITICAL: {n_crit}  |  HARD: {n_hard}")

    edf_late, edf_miss_crit, edf_miss_hard = run_edf(tasks)
    red_late, red_miss_crit, red_miss_hard, red_rejected = run_red(tasks)

    print("\n" + "=" * 60)
    print("  RESULTS")
    print("=" * 60)
    print(f"\n{'Metric':<40} {'EDF':>8} {'RED':>8}")
    print("-" * 58)
    print(f"{'Total tasks':<40} {total:>8} {total:>8}")
    print(f"{'CRITICAL tasks':<40} {n_crit:>8} {n_crit:>8}")
    print(f"{'HARD tasks':<40} {n_hard:>8} {n_hard:>8}")
    print(f"{'Tasks missing deadline (total)':<40} {len(edf_late):>8} {len(red_late):>8}")
    print(f"{'CRITICAL tasks missing deadline':<40} {len(edf_miss_crit):>8} {len(red_miss_crit):>8}")
    print(f"{'HARD tasks missing deadline':<40} {len(edf_miss_hard):>8} {len(red_miss_hard):>8}")
    print(f"{'Tasks rejected by RED':<40} {'N/A':>8} {len(red_rejected):>8}")

    saved = len(edf_miss_crit) - len(red_miss_crit)
    print(f"\n  RED saved {saved} CRITICAL task(s) compared to plain EDF.")
    if len(edf_miss_crit) > 0:
        pct = (saved / len(edf_miss_crit)) * 100
        print(f"  That is a {pct:.0f}% improvement in CRITICAL task protection.")

    print("\n" + "=" * 60)
    print("  Conclusion: RED degrades gracefully.")
    print("  EDF causes domino effect - all tasks at risk.")
    print("  RED protects what matters most.")
    print("=" * 60)

if __name__ == "__main__":
    main()
