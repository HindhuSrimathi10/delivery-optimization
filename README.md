# Delivery Optimization System

**Author:** Hindhu Srimathi  
**Course:** Decision and Computing Sciences - Assessment 3

---

## Problem Statement

Design a system that:
1. Reads CSV with Location ID, Distance, Priority
2. Sorts by Priority (High > Medium > Low) and Distance
3. Assigns deliveries to 3 agents
4. Ensures nearly equal total distance per agent
5. Outputs delivery plan and agent summaries

---

## Algorithm Explanation

### Approach
I used a **greedy algorithm with LPT (Longest Processing Time) heuristic** combined with post-optimization balancing.

### Phase 1: Sorting
- Sort by Priority first (High → Medium → Low)
- Within each priority, sort by Distance in descending order

**Why:** Longer deliveries first (LPT rule) leads to better balance. Priority ensures time-sensitive deliveries are assigned early.

### Phase 2: Assignment
For each delivery in sorted order:
- Find the agent with the smallest current total distance
- Assign the delivery to that agent

**Why:** Always assigning to the least loaded agent prevents any single agent from becoming overloaded.

### Phase 3: Post-Optimization
After initial assignment:
- Identify agents with max and min load
- Move or swap deliveries to reduce imbalance
- Repeat until no improvement

Balance Score = 1 - (max_distance - min_distance) / total_distance
Higher score = better balance. Target: 95%+

---

## Results Achieved

| Agent | Total Distance | Deliveries | High | Medium | Low |
|-------|---------------|-----------|------|--------|-----|
| 1 | 281.30 km | 16 | 3 | 6 | 7 |
| 2 | 281.22 km | 17 | 1 | 8 | 8 |
| 3 | 281.88 km | 17 | 6 | 4 | 7 |

**Balance Score:** 99.92%  
**Max-Min Difference:** 0.66 km

---

## Complexity
- **Time:** O(n log n) - dominated by sorting
- **Space:** O(n) - stores deliveries

---



**Why:** Fixes any remaining imbalance from the greedy phase.

### Balance Calculation
