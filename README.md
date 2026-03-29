# Delivery Optimization System

## Project Overview
A Python-based optimization system that assigns delivery tasks to three agents while ensuring balanced workload distribution and respecting delivery priorities. The system implements dynamic programming techniques to achieve near-perfect workload balance.

## Problem Statement
Optimize delivery assignments with the following constraints:
- Deliveries must be sorted by priority (High > Medium > Low)
- Within same priority, sort by distance from warehouse
- Assign to 3 agents with nearly equal total distance
- Generate detailed delivery plan and summary reports

## Features
- CSV data loading with automatic format detection
- Priority-based sorting algorithm
- Dynamic Programming optimization for workload balancing
- LPT (Longest Processing Time) heuristic for large datasets
- Post-optimization balancing through delivery swaps
- Comprehensive output generation with delivery plans and agent summaries

## Technical Requirements
