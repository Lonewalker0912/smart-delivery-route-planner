# src/optimization.py

import pandas as pd
from scipy.spatial.distance import cdist
import numpy as np

class RouteOptimizer:
    def __init__(self):
        pass

    def calculate_distance(self, p1, p2):
        """Calculate Euclidean distance between two points."""
        return np.linalg.norm(np.array(p1) - np.array(p2))

    def get_route_distance(self, route_df):
        """Calculate the total distance of a given route DataFrame."""
        total_distance = 0
        if len(route_df) < 2:
            return 0
        
        coords = route_df[['latitude', 'longitude']].values
        for i in range(len(coords) - 1):
            total_distance += self.calculate_distance(coords[i], coords[i+1])
            
        return total_distance

    def find_optimal_route(self, cluster_data, start_point_id='DEPOT'):
        """
        Finds an optimized route for a single cluster using the Nearest Neighbor algorithm.

        Args:
            cluster_data (pd.DataFrame): DataFrame for a single cluster including the depot.
            start_point_id (str): The ID of the starting location (e.g., 'DEPOT').

        Returns:
            pd.DataFrame: The route DataFrame with locations in optimized order.
            float: The total distance of the optimized route.
        """
        if cluster_data.empty:
            return pd.DataFrame(), 0.0

        # Get the coordinates as a NumPy array and a map for quick lookups
        coords_df = cluster_data.set_index('delivery_id')[['latitude', 'longitude']]
        coords = coords_df.values
        delivery_ids = coords_df.index.tolist()
        
        # Find the starting point
        try:
            start_idx = delivery_ids.index(start_point_id)
        except ValueError:
            print(f"Start point {start_point_id} not found in cluster.")
            return pd.DataFrame(), 0.0

        route_indices = [start_idx]
        unvisited_indices = set(range(len(delivery_ids)))
        unvisited_indices.remove(start_idx)
        current_idx = start_idx

        while unvisited_indices:
            # Find the nearest neighbor to the current point
            unvisited_list = list(unvisited_indices)
            distances = cdist([coords[current_idx]], coords[unvisited_list], metric='euclidean')[0]
            nearest_neighbor_idx_in_unvisited = np.argmin(distances)
            nearest_neighbor_idx = unvisited_list[nearest_neighbor_idx_in_unvisited]

            # Add the nearest neighbor to the route
            route_indices.append(nearest_neighbor_idx)
            unvisited_indices.remove(nearest_neighbor_idx)
            current_idx = nearest_neighbor_idx
            
        # Add the depot at the end to complete the round trip
        route_indices.append(start_idx)
        
        # Construct the final route DataFrame
        optimized_route_df = cluster_data.iloc[route_indices]
        total_distance = self.get_route_distance(optimized_route_df)
        
        return optimized_route_df, total_distance
