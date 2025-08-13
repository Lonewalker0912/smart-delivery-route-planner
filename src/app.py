# app.py

import pandas as pd
from src.data_loader import load_delivery_data
from src.clustering import find_clusters
from src.optimization import find_optimal_route
from src.visualization import plot_routes_on_map # We'll create this next

def main():
    """
    Main function to run the delivery route planner.
    """
    # Step 1: Load the data
    file_path = 'data/synthetic_data.csv'
    delivery_data = load_delivery_data(file_path)

    if delivery_data is None:
        return

    # Step 2: Cluster the delivery locations
    num_vehicles = 3
    clustered_data = find_clusters(delivery_data, num_vehicles)

    if clustered_data is None:
        return

    all_routes = []
    # Step 3: Optimize the route for each cluster (vehicle)
    for cluster_id in range(num_vehicles):
        cluster_data = clustered_data[clustered_data['cluster'] == cluster_id]
        if not cluster_data.empty:
            optimal_route_indices = find_optimal_route(cluster_data)
            optimal_route_points = cluster_data.iloc[optimal_route_indices]
            all_routes.append(optimal_route_points)

    print("All routes planned successfully.")

    # Step 4: Visualize the results (to be implemented next)
    # plot_routes_on_map(all_routes)

if __name__ == "__main__":
    main()
