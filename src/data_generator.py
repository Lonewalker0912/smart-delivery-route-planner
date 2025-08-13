import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

class DeliveryDataGenerator:
    def __init__(self, num_deliveries=50, city_bounds=None):
        self.num_deliveries = num_deliveries
        self.city_bounds = city_bounds or {
            'lat_min': 40.7128, 'lat_max': 40.7789,  # NYC bounds
            'lon_min': -74.0060, 'lon_max': -73.9352
        }
    
    def generate_delivery_points(self):
        """Generate random delivery points with realistic constraints"""
        data = []
        base_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        for i in range(self.num_deliveries):
            # Generate coordinates
            lat = np.random.uniform(self.city_bounds['lat_min'], self.city_bounds['lat_max'])
            lon = np.random.uniform(self.city_bounds['lon_min'], self.city_bounds['lon_max'])
            
            # Generate time windows
            start_offset = random.randint(0, 8)  # 0-8 hours from 9 AM
            window_start = base_time + timedelta(hours=start_offset)
            window_duration = random.choice([2, 3, 4])  # 2-4 hour windows
            window_end = window_start + timedelta(hours=window_duration)
            
            # Generate package details
            weight = round(random.uniform(0.5, 15.0), 2)  # kg
            priority = random.choice(['standard', 'express', 'same_day'])
            
            data.append({
                'delivery_id': f'DEL_{i+1:03d}',
                'latitude': round(lat, 6),
                'longitude': round(lon, 6),
                'weight_kg': weight,
                'priority': priority,
                'time_window_start': window_start.strftime('%H:%M'),
                'time_window_end': window_end.strftime('%H:%M'),
                'estimated_service_time': random.randint(5, 20)  # minutes
            })
        
        return pd.DataFrame(data)
    
    def add_depot(self, df):
        """Add depot (warehouse) location"""
        depot = {
            'delivery_id': 'DEPOT',
            'latitude': (self.city_bounds['lat_min'] + self.city_bounds['lat_max']) / 2,
            'longitude': (self.city_bounds['lon_min'] + self.city_bounds['lon_max']) / 2,
            'weight_kg': 0,
            'priority': 'depot',
            'time_window_start': '06:00',
            'time_window_end': '22:00',
            'estimated_service_time': 0
        }
        return pd.concat([pd.DataFrame([depot]), df], ignore_index=True)