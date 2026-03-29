"""
Output Generator Module
Creates delivery plans and summary reports
"""
import pandas as pd
import logging
import os
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OutputGenerator:
    """
    Generates output files and reports from optimization results
    """
    
    def __init__(self, agents: Dict[int, List[Dict]], agent_distances: Dict[int, float]):
        """
        Initialize with optimization results
        
        Args:
            agents: Dictionary mapping agent IDs to their deliveries
            agent_distances: Dictionary mapping agent IDs to total distances
        """
        self.agents = agents
        self.agent_distances = agent_distances
        self.output_dir = "outputs"
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate_delivery_plan(self, filename: str = 'delivery_plan.csv') -> pd.DataFrame:
        """
        Generate detailed delivery plan CSV
        
        Args:
            filename: Name of the output file
            
        Returns:
            DataFrame with delivery assignments
        """
        plan_data = []
        
        for agent_id in [1, 2, 3]:
            for delivery in self.agents.get(agent_id, []):
                plan_data.append({
                    'Agent_ID': agent_id,
                    'Location_ID': delivery['Location_ID'],
                    'Distance_km': delivery['Distance_km'],
                    'Priority': delivery['Priority']
                })
        
        df_plan = pd.DataFrame(plan_data)
        
        # Sort by Agent_ID and then by Priority
        priority_order = {'High': 1, 'Medium': 2, 'Low': 3}
        df_plan['priority_num'] = df_plan['Priority'].map(priority_order)
        df_plan = df_plan.sort_values(['Agent_ID', 'priority_num']).drop('priority_num', axis=1)
        
        # Save to CSV
        output_path = os.path.join(self.output_dir, filename)
        df_plan.to_csv(output_path, index=False)
        logger.info(f"📄 Delivery plan saved to {output_path}")
        
        return df_plan
    
    def generate_agent_summary(self, filename: str = 'agent_summary.csv') -> pd.DataFrame:
        """
        Generate agent summary statistics
        
        Args:
            filename: Name of the output file
            
        Returns:
            DataFrame with agent summaries
        """
        summary_data = []
        
        for agent_id in [1, 2, 3]:
            deliveries = self.agents.get(agent_id, [])
            total_distance = self.agent_distances.get(agent_id, 0)
            num_deliveries = len(deliveries)
            
            # Count priorities
            priority_counts = {
                'High': sum(1 for d in deliveries if d['Priority'] == 'High'),
                'Medium': sum(1 for d in deliveries if d['Priority'] == 'Medium'),
                'Low': sum(1 for d in deliveries if d['Priority'] == 'Low')
            }
            
            summary_data.append({
                'Agent': agent_id,
                'Total_Distance_km': round(total_distance, 2),
                'Number_of_Deliveries': num_deliveries,
                'High_Priority': priority_counts['High'],
                'Medium_Priority': priority_counts['Medium'],
                'Low_Priority': priority_counts['Low'],
                'Avg_Distance_km': round(total_distance / num_deliveries if num_deliveries > 0 else 0, 2)
            })
        
        df_summary = pd.DataFrame(summary_data)
        
        # Save to CSV
        output_path = os.path.join(self.output_dir, filename)
        df_summary.to_csv(output_path, index=False)
        logger.info(f"📊 Agent summary saved to {output_path}")
        
        return df_summary
    
    def print_summary(self):
        """
        Print formatted summary to console
        """
        print("\n" + "="*80)
        print("📦 DELIVERY OPTIMIZATION SUMMARY")
        print("="*80)
        
        # Print table header
        print(f"{'Agent':<8} {'Total Dist (km)':<18} {'Deliveries':<12} {'High':<8} {'Medium':<8} {'Low':<8} {'Avg Dist':<10}")
        print("-"*80)
        
        total_distance = 0
        total_deliveries = 0
        
        for agent_id in [1, 2, 3]:
            deliveries = self.agents.get(agent_id, [])
            total_dist = self.agent_distances.get(agent_id, 0)
            total_distance += total_dist
            total_deliveries += len(deliveries)
            
            priority_counts = {
                'High': sum(1 for d in deliveries if d['Priority'] == 'High'),
                'Medium': sum(1 for d in deliveries if d['Priority'] == 'Medium'),
                'Low': sum(1 for d in deliveries if d['Priority'] == 'Low')
            }
            
            avg_dist = total_dist / len(deliveries) if len(deliveries) > 0 else 0
            
            print(f"{agent_id:<8} {total_dist:<18.2f} {len(deliveries):<12} "
                  f"{priority_counts['High']:<8} {priority_counts['Medium']:<8} "
                  f"{priority_counts['Low']:<8} {avg_dist:<10.2f}")
        
        print("-"*80)
        print(f"{'TOTAL':<8} {total_distance:<18.2f} {total_deliveries:<12}")
        
        # Print balance metrics
        max_dist = max(self.agent_distances.values())
        min_dist = min(self.agent_distances.values())
        balance_score = 1 - (max_dist - min_dist) / total_distance if total_distance > 0 else 1
        
        print("\n" + "-"*80)
        print(f"{'📊 Balance Score:':<25} {balance_score:.2%}")
        print(f"{'📈 Max-Min Difference:':<25} {(max_dist - min_dist):.2f} km")
        print(f"{'🎯 Target Distance per Agent:':<25} {(total_distance/3):.2f} km")
        print("="*80)
        
        # Performance assessment
        if balance_score >= 0.95:
            print("✅ EXCELLENT: Workload is very well balanced!")
        elif balance_score >= 0.90:
            print("👍 GOOD: Workload is reasonably balanced.")
        elif balance_score >= 0.80:
            print("⚠️  FAIR: Workload balance could be improved.")
        else:
            print("❌ POOR: Workload is poorly balanced.")
        
        print("="*80 + "\n")