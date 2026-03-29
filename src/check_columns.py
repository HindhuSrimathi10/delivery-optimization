
import pandas as pd

df = pd.read_csv("D:\\delivery-optimization\\data\\amazon_delivery.csv")

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
