import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import os

class AmazonDeliveryTransformer:
    
    def __init__(self, warehouse_coords=None):
        self.warehouse_coords = warehouse_coords
        self.df = None
        self.data_type = None
        
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 6371
        
        if pd.isna(lat1) or pd.isna(lon1) or pd.isna(lat2) or pd.isna(lon2):
            return 0.0
            
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def detect_data_format(self):
        columns = set(self.df.columns)
        
        if {'Location_ID', 'Distance_km', 'Priority'}.issubset(columns):
            self.data_type = 'transformed'
            print("Detected: Already transformed format")
            return 'transformed'
        
        if {'Store_Latitude', 'Store_Longitude', 'Drop_Latitude', 'Drop_Longitude'}.issubset(columns):
            self.data_type = 'real'
            print("Detected: Real Amazon dataset with coordinates")
            return 'real'
        
        if {'store_lat', 'store_lon', 'drop_lat', 'drop_lon'}.issubset(columns):
            self.data_type = 'sample_coords'
            print("Detected: Sample dataset with coordinates")
            return 'sample_coords'
        
        self.data_type = 'transformed'
        print("Detected: Generic format - assuming already transformed")
        return 'transformed'
    
    def load_data(self, file_path):
        try:
            self.df = pd.read_csv(file_path)
            print(f"Loaded {len(self.df)} deliveries from {file_path}")
            print(f"Columns: {list(self.df.columns)}")
            
            self.detect_data_format()
            
            return self.df
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def calculate_distances(self):
        if self.data_type == 'transformed':
            if 'Distance_km' in self.df.columns:
                print(f"Using existing distances from data")
                print(f"Range: {self.df['Distance_km'].min():.2f} - {self.df['Distance_km'].max():.2f} km")
                return self.df
            else:
                print("No distance column found, generating sample distances")
                self.df['Distance_km'] = np.random.uniform(5, 30, len(self.df))
                return self.df
        
        if self.warehouse_coords is None:
            if self.data_type == 'real':
                first_row = self.df.iloc[0]
                self.warehouse_coords = (first_row['Store_Latitude'], first_row['Store_Longitude'])
            elif self.data_type == 'sample_coords':
                first_row = self.df.iloc[0]
                self.warehouse_coords = (first_row['store_lat'], first_row['store_lon'])
            else:
                self.warehouse_coords = (12.9716, 77.5946)
            
            print(f"Using warehouse coordinates: ({self.warehouse_coords[0]:.4f}, {self.warehouse_coords[1]:.4f})")
        
        warehouse_lat, warehouse_lon = self.warehouse_coords
        
        if self.data_type == 'real':
            self.df['Distance_km'] = self.df.apply(
                lambda row: self.haversine_distance(
                    warehouse_lat, warehouse_lon,
                    row['Drop_Latitude'], row['Drop_Longitude']
                ), axis=1
            )
        elif self.data_type == 'sample_coords':
            self.df['Distance_km'] = self.df.apply(
                lambda row: self.haversine_distance(
                    warehouse_lat, warehouse_lon,
                    row['drop_lat'], row['drop_lon']
                ), axis=1
            )
        
        print(f"Distances calculated:")
        print(f"Min: {self.df['Distance_km'].min():.2f} km")
        print(f"Max: {self.df['Distance_km'].max():.2f} km")
        print(f"Avg: {self.df['Distance_km'].mean():.2f} km")
        
        return self.df
    
    def assign_priorities(self, method='balanced'):
        if 'Priority' in self.df.columns and self.data_type == 'transformed':
            print("Using existing priorities from data")
            print(f"\nPriority Distribution:")
            priority_counts = self.df['Priority'].value_counts()
            for priority in ['High', 'Medium', 'Low']:
                count = priority_counts.get(priority, 0)
                percentage = (count / len(self.df)) * 100 if len(self.df) > 0 else 0
                print(f"{priority}: {count} deliveries ({percentage:.1f}%)")
            return self.df
        
        print(f"Using {method} priority assignment...")
        
        if method == 'balanced':
            self.df['priority_score'] = 0
            weights_used = []
            
            if 'Traffic' in self.df.columns:
                traffic_map = {
                    'Low': 1, 
                    'Medium': 2, 
                    'High': 3, 
                    'Jam': 4
                }
                self.df['traffic_score'] = self.df['Traffic'].map(traffic_map).fillna(2)
                self.df['priority_score'] += self.df['traffic_score'] * 0.4
                weights_used.append("Traffic (40%)")
                print("Added Traffic factor (40%)")
            
            if 'Delivery_Time' in self.df.columns:
                delivery_times = pd.to_numeric(self.df['Delivery_Time'], errors='coerce')
                delivery_times = delivery_times.fillna(delivery_times.median())
                
                time_quantiles = delivery_times.quantile([0.33, 0.66])
                self.df['time_score'] = pd.cut(
                    delivery_times,
                    bins=[0, time_quantiles[0.33], time_quantiles[0.66], float('inf')],
                    labels=[3, 2, 1]
                ).astype(float)
                self.df['priority_score'] += self.df['time_score'] * 0.4
                weights_used.append("Delivery Time (40%)")
                print("Added Delivery Time factor (40%)")
            
            if 'Distance_km' in self.df.columns:
                distance_quantiles = self.df['Distance_km'].quantile([0.33, 0.66])
                self.df['dist_score'] = pd.cut(
                    self.df['Distance_km'],
                    bins=[0, distance_quantiles[0.33], distance_quantiles[0.66], float('inf')],
                    labels=[3, 2, 1]
                ).astype(float)
                self.df['priority_score'] += self.df['dist_score'] * 0.2
                weights_used.append("Distance (20%)")
                print("Added Distance factor (20%)")
            
            if 'priority_score' in self.df.columns and self.df['priority_score'].sum() > 0:
                score_quantiles = self.df['priority_score'].quantile([0.33, 0.66])
                self.df['Priority'] = pd.cut(
                    self.df['priority_score'],
                    bins=[0, score_quantiles[0.33], score_quantiles[0.66], float('inf')],
                    labels=['Low', 'Medium', 'High']
                )
            else:
                distance_quantiles = self.df['Distance_km'].quantile([0.33, 0.66])
                self.df['Priority'] = pd.cut(
                    self.df['Distance_km'],
                    bins=[0, distance_quantiles[0.33], distance_quantiles[0.66], float('inf')],
                    labels=['High', 'Medium', 'Low']
                )
            
            if weights_used:
                print(f"Combined factors: {', '.join(weights_used)}")
        
        elif method == 'distance_based':
            distance_quantiles = self.df['Distance_km'].quantile([0.33, 0.66])
            self.df['Priority'] = pd.cut(
                self.df['Distance_km'],
                bins=[0, distance_quantiles[0.33], distance_quantiles[0.66], float('inf')],
                labels=['High', 'Medium', 'Low']
            )
        
        print(f"\nPriority Distribution:")
        priority_counts = self.df['Priority'].value_counts()
        for priority in ['High', 'Medium', 'Low']:
            count = priority_counts.get(priority, 0)
            percentage = (count / len(self.df)) * 100 if len(self.df) > 0 else 0
            print(f"{priority}: {count} deliveries ({percentage:.1f}%)")
        
        return self.df
    
    def create_location_ids(self):
        if 'Location_ID' in self.df.columns:
            print(f"Using existing Location IDs")
        elif 'Order_ID' in self.df.columns:
            self.df['Location_ID'] = self.df['Order_ID']
            print(f"Using Order_ID as Location ID")
        else:
            self.df['Location_ID'] = [f'DLV_{i+1:05d}' for i in range(len(self.df))]
            print(f"Created {len(self.df)} new Location IDs")
        
        return self.df
    
    def save_transformed_data(self, output_path):
        required_cols = ['Location_ID', 'Distance_km', 'Priority']
        for col in required_cols:
            if col not in self.df.columns:
                print(f"Warning: {col} not found, creating it")
                if col == 'Location_ID':
                    self.create_location_ids()
                elif col == 'Distance_km':
                    self.df['Distance_km'] = np.random.uniform(5, 30, len(self.df))
                elif col == 'Priority':
                    self.df['Priority'] = np.random.choice(['High', 'Medium', 'Low'], len(self.df), p=[0.2, 0.3, 0.5])
        
        result = self.df[['Location_ID', 'Distance_km', 'Priority']].copy()
        result['Distance_km'] = result['Distance_km'].round(2)
        
        priority_order = {'High': 1, 'Medium': 2, 'Low': 3}
        result['sort_key'] = result['Priority'].map(priority_order)
        result = result.sort_values('sort_key').drop('sort_key', axis=1)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        result.to_csv(output_path, index=False)
        print(f"\nTransformed data saved to: {output_path}")
        
        print("\nSample of transformed data (first 10 rows):")
        print(result.head(10))
        
        return result
    
    def run_transformation(self, input_file, output_file, priority_method='balanced'):
        print("\n" + "="*60)
        print("STARTING DATA TRANSFORMATION")
        print("="*60)
        
        self.load_data(input_file)
        self.calculate_distances()
        self.assign_priorities(method=priority_method)
        self.create_location_ids()
        result = self.save_transformed_data(output_file)
        
        print("\n" + "="*60)
        print("TRANSFORMATION COMPLETE")
        print("="*60)
        
        return result


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTING WITH SAMPLE DATA")
    print("="*60)
    
    sample_with_coords = pd.DataFrame({
        'Store_Latitude': [22.745049, 12.913041],
        'Store_Longitude': [75.892471, 77.683237],
        'Drop_Latitude': [22.765049, 13.043041],
        'Drop_Longitude': [75.912471, 77.813237],
        'Traffic': ['High', 'Jam'],
        'Delivery_Time': [120, 165]
    })
    
    os.makedirs("data", exist_ok=True)
    sample_with_coords.to_csv("data/test_coords.csv", index=False)
    
    transformer = AmazonDeliveryTransformer()
    transformed = transformer.run_transformation(
        input_file="data/test_coords.csv",
        output_file="data/test_output.csv",
        priority_method='balanced'
    )
    
    print("\nTest completed successfully!")