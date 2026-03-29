"""
Main execution module for delivery optimization
"""
import sys
import os
import logging
from datetime import datetime

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_transformer import AmazonDeliveryTransformer
from src.dp_optimizer import DPOptimizer
from src.output_generator import OutputGenerator

def setup_logging():
    """Configure logging for the application"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def create_sample_data_if_needed():
    """Create sample data if real data not available"""
    import pandas as pd
    import numpy as np
    
    print("\n  Real dataset not found. Creating sample data for testing...")
    
    np.random.seed(42)
    n_samples = 50
    
    data = []
    for i in range(n_samples):
        distance = np.random.choice([
            np.random.uniform(1, 8),    # Close
            np.random.uniform(8, 18),   # Medium
            np.random.uniform(18, 32),  # Far
            np.random.uniform(32, 50)   # Very far
        ], p=[0.3, 0.4, 0.2, 0.1])
        
        priority = np.random.choice(
            ['High', 'Medium', 'Low'],
            p=[0.2, 0.3, 0.5]
        )
        
        data.append({
            'Location_ID': f'SAMPLE_{i+1:04d}',
            'Distance_km': round(distance, 2),
            'Priority': priority
        })
    
    df = pd.DataFrame(data)
    
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
    # Save sample data
    sample_file = "data/sample_delivery_data.csv"
    df.to_csv(sample_file, index=False)
    
    print(f"Sample data created: {sample_file}")
    print(f"   Total deliveries: {len(df)}")
    print(f"   Priority distribution:\n{df['Priority'].value_counts()}")
    
    return sample_file

def main():
    """Main execution function"""
    # Setup logging
    logger = setup_logging()
    
    try:
        # Configuration
        input_file = "data/amazon_delivery_dataset.csv"  # Your downloaded dataset
        output_file = "data/delivery_locations.csv"
        
        logger.info("="*80)
        logger.info("DELIVERY OPTIMIZATION SYSTEM")
        logger.info("="*80)
        
        # Check if input file exists
        if not os.path.exists(input_file):
            logger.warning(f"File not found: {input_file}")
            input_file = create_sample_data_if_needed()
            output_file = "data/delivery_locations.csv"
        
        # Step 1: Transform the dataset
        logger.info("\nSTEP 1: Transforming Delivery Dataset")
        logger.info("-"*40)
        
        transformer = AmazonDeliveryTransformer()
        
        
        transformed_df = transformer.run_transformation(
            input_file=input_file,
            output_file=output_file,
            priority_method='balanced'  # Try 'balanced', 'time_sensitive', 'traffic_based', 'category_based'
        )
        
        
        logger.info("\n STEP 2: Running DP Optimization")
        logger.info("-"*40)
        
        optimizer = DPOptimizer()
        optimizer.setup(transformed_df)
        agents = optimizer.solve_optimal()
        
        # Step 3: Generate outputs
        logger.info("\nSTEP 3: Generating Output Files")
        logger.info("-"*40)
        
        generator = OutputGenerator(optimizer.agents, optimizer.agent_distances)
        
        # Generate delivery plan
        delivery_plan = generator.generate_delivery_plan()
        
        # Generate agent summary
        agent_summary = generator.generate_agent_summary()
        
        # Print summary to console
        generator.print_summary()
        
        # Get balance score
        balance_score = optimizer.get_balance_score()
        
        # Get statistics
        stats = optimizer.get_statistics()
        
        # Step 4: Save detailed report
        logger.info("\nSTEP 4: Saving Detailed Report")
        logger.info("-"*40)
        
        # Create a detailed report file
        report_file = "outputs/detailed_report.txt"
        with open(report_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("DELIVERY OPTIMIZATION DETAILED REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            f.write("OPTIMIZATION STATISTICS\n")
            f.write("-"*40 + "\n")
            f.write(f"Total Deliveries: {stats['total_deliveries']}\n")
            f.write(f"Total Distance: {stats['total_distance']:.2f} km\n")
            f.write(f"Balance Score: {stats['balance_score']:.2%}\n\n")
            
            f.write("AGENT DISTANCES\n")
            f.write("-"*40 + "\n")
            for agent in [1, 2, 3]:
                f.write(f"Agent {agent}: {stats['agent_distances'][agent]:.2f} km ({stats['agent_counts'][agent]} deliveries)\n")
            
            f.write("\nPRIORITY DISTRIBUTION PER AGENT\n")
            f.write("-"*40 + "\n")
            for agent in [1, 2, 3]:
                priorities = stats[f'agent_{agent}_priorities']
                f.write(f"Agent {agent}: High={priorities['High']}, Medium={priorities['Medium']}, Low={priorities['Low']}\n")
            
            f.write("\n" + "="*80 + "\n")
        
        logger.info(f"Detailed report saved to: {report_file}")
        
        # Step 5: Print final status
        logger.info("\n" + "="*80)
        logger.info("OPTIMIZATION COMPLETED SUCCESSFULLY!")
        logger.info("="*80)
        
        logger.info("\nOUTPUT FILES GENERATED:")
        logger.info("   • outputs/delivery_plan.csv - Detailed delivery assignments")
        logger.info("   • outputs/agent_summary.csv - Summary per agent")
        logger.info("   • outputs/detailed_report.txt - Complete analysis report")
        logger.info(f"   • {output_file} - Transformed dataset")
        
        logger.info("\nPERFORMANCE METRICS:")
        logger.info(f"   • Balance Score: {balance_score:.2%}")
        logger.info(f"   • Total Distance: {stats['total_distance']:.2f} km")
        logger.info(f"   • Average per Agent: {(stats['total_distance']/3):.2f} km")
        
        # Performance assessment
        if balance_score >= 0.95:
            logger.info("\nEXCELLENT! Workload is perfectly balanced!")
        elif balance_score >= 0.90:
            logger.info("\nGOOD! Workload is well balanced.")
        elif balance_score >= 0.80:
            logger.info("\n FAIR: Workload balance could be improved.")
        else:
            logger.info("\nPOOR: Consider adjusting priority weights.")
        
        logger.info("\n" + "="*80)
        
        return optimizer.agents, optimizer.agent_distances
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        print("\nTIP: Make sure your dataset is in the 'data' folder")
        print("   Expected location: data/amazon_delivery_dataset.csv")
        print("   Or run: python create_sample_data.py to generate test data")
        raise
        
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        logger.exception("Detailed error trace:")
        raise

if __name__ == "__main__":
    # Run the main function
    agents, distances = main()
    
    print("\n" + "="*80)
    print("OPTIMIZATION COMPLETE")
    print("="*80)
    print("\nTo view results:")
    print("  1. Check the 'outputs' folder for CSV files")
    print("  2. Open 'outputs/delivery_plan.csv' to see assignments")
    print("  3. Review 'outputs/agent_summary.csv' for statistics")
    print("\nTo run again with different settings:")
    print("  - Change priority_method in main()")
    print("  - Modify warehouse coordinates")
    print("  - Use different dataset")
    print("="*80)
