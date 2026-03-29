"""
Check the actual column names in your dataset
"""
import pandas as pd

# Load your dataset
df = pd.read_csv("D:\\delivery-optimization\\data\\amazon_delivery.csv")

# Print all column names
print("="*60)
print("COLUMN NAMES IN YOUR DATASET:")
print("="*60)
for i, col in enumerate(df.columns, 1):
    print(f"{i}. {col}")

print("\n" + "="*60)
print("FIRST FEW ROWS:")
print("="*60)
print(df.head(3))

print("\n" + "="*60)
print("DATA TYPES:")
print("="*60)
print(df.dtypes)