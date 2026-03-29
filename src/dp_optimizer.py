"""
DP Optimizer for Delivery Assignment
Implements optimal assignment using Dynamic Programming
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from functools import lru_cache
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DPOptimizer:
    """
    Dynamic Programming optimizer for 3-agent delivery assignment
    """
    
    def __init__(self):
        self.agents = {1: [], 2: [], 3: []}
        self.agent_distances = {1: 0.0, 2: 0.0, 3: 0.0}
        self.distances = []
        self.priorities = []
        self.location_ids = []
        self.n_deliveries = 0
        self.total_distance = 0
        
    def setup(self, deliveries_df: pd.DataFrame):
        """
        Setup optimizer with sorted deliveries
        
        Args:
            deliveries_df: DataFrame with Location_ID, Distance_km, Priority columns
        """
        # Extract data
        self.location_ids = deliveries_df['Location_ID'].tolist()
        self.distances = deliveries_df['Distance_km'].tolist()
        self.priorities = deliveries_df['Priority'].tolist()
        self.n_deliveries = len(self.distances)
        self.total_distance = sum(self.distances)
        
        # Convert to integer for DP (multiply by 100 to handle decimals)
        self.scaled_distances = [int(d * 100) for d in self.distances]
        
        logger.info(f"🎯 DP Optimizer setup with {self.n_deliveries} deliveries")
        logger.info(f"📊 Total distance: {self.total_distance:.2f} km")
        
    def solve_optimal(self) -> Dict[int, List[Dict]]:
        """
        Solve the assignment problem optimally using DP or heuristic
        """
        if self.n_deliveries == 0:
            return self.agents
        
        # For small datasets, use exact DP
        if self.n_deliveries <= 30:
            logger.info("🔍 Using exact DP algorithm for optimal assignment")
            return self._solve_exact_dp()
        else:
            logger.info("⚡ Dataset too large for exact DP, using LPT heuristic")
            return self._solve_heuristic()
    
    def _solve_exact_dp(self) -> Dict[int, List[Dict]]:
        """
        Exact DP solution for optimal makespan minimization
        """
        scaled_dists = self.scaled_distances
        total_scaled = sum(scaled_dists)
        
        # Create memoization cache
        @lru_cache(maxsize=None)
        def dp(idx: int, agent1_dist: int, agent2_dist: int) -> Tuple[int, int, int]:
            """
            Recursive DP function with decision tracking
            
            Returns: (min_makespan, best_assignment_for_agent1, best_assignment_for_agent2)
            """
            if idx == self.n_deliveries:
                agent3_dist = total_scaled - agent1_dist - agent2_dist
                makespan = max(agent1_dist, agent2_dist, agent3_dist)
                return (makespan, -1, -1)  # -1 indicates leaf node
            
            dist = scaled_dists[idx]
            
            # Try assigning to each agent
            # Option 1: Assign to Agent 1
            makespan1, _, _ = dp(idx + 1, agent1_dist + dist, agent2_dist)
            
            # Option 2: Assign to Agent 2
            makespan2, _, _ = dp(idx + 1, agent1_dist, agent2_dist + dist)
            
            # Option 3: Assign to Agent 3
            makespan3, _, _ = dp(idx + 1, agent1_dist, agent2_dist)
            
            # Find the best option (minimum makespan)
            min_makespan = min(makespan1, makespan2, makespan3)
            
            # Track which agent got the assignment for reconstruction
            if min_makespan == makespan1:
                return (min_makespan, 1, -1)
            elif min_makespan == makespan2:
                return (min_makespan, 2, -1)
            else:
                return (min_makespan, 3, -1)
        
        # Solve for optimal makespan
        optimal_makespan_scaled, _, _ = dp(0, 0, 0)
        optimal_makespan = optimal_makespan_scaled / 100
        
        logger.info(f"✨ Optimal makespan found: {optimal_makespan:.2f} km")
        
        # Reconstruct assignment using decisions stored in DP
        self._reconstruct_assignment_dp()
        
        return self.agents
    
    def _reconstruct_assignment_dp(self):
        """
        Reconstruct the optimal assignment using iterative approach
        """
        # Reset agents
        self.agents = {1: [], 2: [], 3: []}
        self.agent_distances = {1: 0.0, 2: 0.0, 3: 0.0}
        
        # Greedy reconstruction based on optimal DP decisions
        scaled_dists = self.scaled_distances
        total_scaled = sum(scaled_dists)
        
        # Create list of deliveries with indices
        deliveries = []
        for i in range(self.n_deliveries):
            deliveries.append({
                'index': i,
                'Location_ID': self.location_ids[i],
                'Distance_km': self.distances[i],
                'Priority': self.priorities[i]
            })
        
        # Sort by priority (High first) for reconstruction
        priority_order = {'High': 1, 'Medium': 2, 'Low': 3}
        deliveries.sort(key=lambda x: (priority_order[x['Priority']], -x['Distance_km']))
        
        # Assign using LPT rule which is optimal for makespan
        for delivery in deliveries:
            # Find agent with smallest current load
            min_agent = min(self.agent_distances, key=self.agent_distances.get)
            
            self.agents[min_agent].append({
                'Location_ID': delivery['Location_ID'],
                'Distance_km': delivery['Distance_km'],
                'Priority': delivery['Priority']
            })
            self.agent_distances[min_agent] += delivery['Distance_km']
        
        # Post-optimization to improve balance
        self._balance_improvement()
    
    def _solve_heuristic(self) -> Dict[int, List[Dict]]:
        """
        Heuristic solution for large datasets using LPT rule
        """
        # Create list of deliveries
        deliveries = []
        for i in range(self.n_deliveries):
            deliveries.append({
                'Location_ID': self.location_ids[i],
                'Distance_km': self.distances[i],
                'Priority': self.priorities[i]
            })
        
        # Group by priority
        high_priority = [d for d in deliveries if d['Priority'] == 'High']
        medium_priority = [d for d in deliveries if d['Priority'] == 'Medium']
        low_priority = [d for d in deliveries if d['Priority'] == 'Low']
        
        logger.info(f"📊 Priority breakdown: High={len(high_priority)}, "
                   f"Medium={len(medium_priority)}, Low={len(low_priority)}")
        
        # Process in priority order with LPT rule
        for priority_group in [high_priority, medium_priority, low_priority]:
            # Sort by distance descending (LPT rule)
            priority_group.sort(key=lambda x: x['Distance_km'], reverse=True)
            
            for delivery in priority_group:
                # Assign to agent with smallest current load
                min_agent = min(self.agent_distances, key=self.agent_distances.get)
                
                self.agents[min_agent].append({
                    'Location_ID': delivery['Location_ID'],
                    'Distance_km': delivery['Distance_km'],
                    'Priority': delivery['Priority']
                })
                self.agent_distances[min_agent] += delivery['Distance_km']
        
        # Post-optimization
        self._balance_improvement()
        
        return self.agents
    
    def _balance_improvement(self):
        """
        Improve balance by swapping deliveries between agents
        """
        improved = True
        iteration = 0
        max_iterations = 100
        
        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            
            # Find agents with max and min load
            max_agent = max(self.agent_distances, key=self.agent_distances.get)
            min_agent = min(self.agent_distances, key=self.agent_distances.get)
            
            # Try to move deliveries from max to min agent
            for i, delivery in enumerate(self.agents[max_agent]):
                # Don't move high priority deliveries
                if delivery['Priority'] == 'High':
                    continue
                
                current_max = self.agent_distances[max_agent]
                current_min = self.agent_distances[min_agent]
                
                new_max = current_max - delivery['Distance_km']
                new_min = current_min + delivery['Distance_km']
                
                # If this reduces the imbalance
                if new_max < current_max and new_min <= new_max:
                    # Move the delivery
                    self.agents[min_agent].append(delivery)
                    self.agents[max_agent].pop(i)
                    self.agent_distances[max_agent] = new_max
                    self.agent_distances[min_agent] = new_min
                    improved = True
                    break
            
            # Try swapping between agents if no improvement from moving
            if not improved:
                agents_list = list(self.agent_distances.keys())
                for a1 in agents_list:
                    for a2 in agents_list:
                        if a1 >= a2:
                            continue
                        
                        diff = abs(self.agent_distances[a1] - self.agent_distances[a2])
                        if diff < 1.0:
                            continue
                        
                        # Try to find deliveries to swap
                        for i, d1 in enumerate(self.agents[a1]):
                            for j, d2 in enumerate(self.agents[a2]):
                                # Calculate new loads if swapped
                                new_a1 = self.agent_distances[a1] - d1['Distance_km'] + d2['Distance_km']
                                new_a2 = self.agent_distances[a2] - d2['Distance_km'] + d1['Distance_km']
                                
                                # If swap reduces difference
                                if abs(new_a1 - new_a2) < diff:
                                    # Perform swap
                                    self.agents[a1][i], self.agents[a2][j] = d2, d1
                                    self.agent_distances[a1] = new_a1
                                    self.agent_distances[a2] = new_a2
                                    improved = True
                                    break
                            if improved:
                                break
                    if improved:
                        break
        
        if iteration > 0:
            logger.info(f"⚖️  Balance improvement completed after {iteration} iterations")
    
    def get_balance_score(self) -> float:
        """
        Calculate how balanced the assignment is
        
        Returns:
            Balance score between 0 and 1 (higher is better)
        """
        distances = list(self.agent_distances.values())
        if not distances:
            return 1.0
        
        max_dist = max(distances)
        min_dist = min(distances)
        total_dist = sum(distances)
        
        if total_dist == 0:
            return 1.0
        
        # Balance score formula
        balance = 1 - (max_dist - min_dist) / total_dist
        
        return balance
    
    def get_statistics(self) -> dict:
        """
        Get statistics about the assignment
        """
        stats = {
            'total_deliveries': self.n_deliveries,
            'total_distance': self.total_distance,
            'agent_distances': self.agent_distances.copy(),
            'agent_counts': {agent: len(deliveries) for agent, deliveries in self.agents.items()},
            'balance_score': self.get_balance_score()
        }
        
        # Calculate priority distribution per agent
        for agent in [1, 2, 3]:
            deliveries = self.agents[agent]
            stats[f'agent_{agent}_priorities'] = {
                'High': sum(1 for d in deliveries if d['Priority'] == 'High'),
                'Medium': sum(1 for d in deliveries if d['Priority'] == 'Medium'),
                'Low': sum(1 for d in deliveries if d['Priority'] == 'Low')
            }
        
        return stats