"""
Simple runner script for delivery optimization
Run this to start the optimization
"""
import os
import sys

def check_installation():
    """Check if required packages are installed"""
    try:
        import pandas
        import numpy
        print("✅ Required packages found")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("\nPlease install required packages:")
        print("pip install pandas numpy")
        return False

def main():
    """Main runner function"""
    print("\n" + "="*70)
    print("🚚 DELIVERY OPTIMIZATION SYSTEM")
    print("="*70)
    
    # Check installation
    if not check_installation():
        return
    
    # Check if main.py exists
    if not os.path.exists("main.py"):
        print("❌ main.py not found!")
        print("Make sure you're in the correct directory")
        return
    
    # Run the main program
    print("\n▶️  Starting optimization...")
    print("-"*40)
    
    # Import and run main
    try:
        import main
        main.main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure your dataset is in 'data/amazon_delivery_dataset.csv'")
        print("2. Check that all Python files are in the correct folders")
        print("3. Run: pip install pandas numpy")

if __name__ == "__main__":
    main()