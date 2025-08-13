# src/clustering.py

import pandas as pd
from sklearn.cluster import KMeans

class DeliveryClusterer:
    def __init__(self):
        pass

    def create_clusters(self, data, num_clusters=3):
        """
        Performs K-Means clustering on delivery locations.

        Args:
            data (pd.DataFrame): DataFrame with 'latitude' and 'longitude' columns.
            num_clusters (int): The number of clusters to form.

        Returns:
            pd.DataFrame: The original DataFrame with an added 'cluster' column.
        """
        # Exclude the depot from clustering
        delivery_points = data[data['delivery_id'] != 'DEPOT'].copy()
        
        # Perform K-Means clustering on the coordinates
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        delivery_points['cluster'] = kmeans.fit_predict(delivery_points[['latitude', 'longitude']])
        
        # Merge the clusters back into the original data, handling the depot
        data = pd.merge(data, delivery_points[['delivery_id', 'cluster']], on='delivery_id', how='left')
        data.loc[data['delivery_id'] == 'DEPOT', 'cluster'] = -1  # Assign a special ID for the depot
        
        return data
