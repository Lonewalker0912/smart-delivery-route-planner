import folium
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

class RouteVisualizer:
    def __init__(self):
        self.colors = [
            'red', 'blue', 'green', 'purple', 'orange', 
            'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen'
        ]
    
    def create_delivery_map(self, data, routes=None, center=None):
        """Create interactive map with delivery points and routes"""
        if center is None:
            center = [data['latitude'].mean(), data['longitude'].mean()]
        
        m = folium.Map(location=center, zoom_start=12)
        
        # Add depot
        depot = data[data['delivery_id'] == 'DEPOT']
        if not depot.empty:
            folium.Marker(
                [depot.iloc[0]['latitude'], depot.iloc[0]['longitude']],
                popup='DEPOT',
                icon=folium.Icon(color='black', icon='home')
            ).add_to(m)
        
        # Add delivery points
        delivery_data = data[data['delivery_id'] != 'DEPOT']
        
        if 'cluster' in delivery_data.columns:
            # Color by cluster
            for idx, row in delivery_data.iterrows():
                cluster_id = row['cluster']
                color = self.colors[cluster_id % len(self.colors)]
                
                popup_text = f"""
                ID: {row['delivery_id']}<br>
                Cluster: {cluster_id}<br>
                Weight: {row['weight_kg']} kg<br>
                Priority: {row['priority']}<br>
                Time Window: {row['time_window_start']} - {row['time_window_end']}
                """
                
                folium.CircleMarker(
                    [row['latitude'], row['longitude']],
                    radius=8,
                    popup=popup_text,
                    color=color,
                    fillColor=color,
                    fillOpacity=0.7
                ).add_to(m)
        else:
            # Default markers
            for idx, row in delivery_data.iterrows():
                folium.CircleMarker(
                    [row['latitude'], row['longitude']],
                    radius=6,
                    popup=f"ID: {row['delivery_id']}",
                    color='blue',
                    fillColor='blue',
                    fillOpacity=0.5
                ).add_to(m)
        
        # Add routes if provided
        if routes:
            for route_name, route_info in routes.items():
                locations = route_info['locations']
                color = self.colors[hash(route_name) % len(self.colors)]
                
                # Create route line
                route_coords = [
                    [row['latitude'], row['longitude']] 
                    for _, row in locations.iterrows()
                ]
                
                folium.PolyLine(
                    route_coords,
                    color=color,
                    weight=3,
                    opacity=0.8,
                    popup=f"{route_name}: {route_info['total_distance']:.2f} km"
                ).add_to(m)
        
        return m
    
    def create_cluster_visualization(self, data):
        """Create cluster visualization using Plotly"""
        if 'cluster' not in data.columns:
            return None
        
        delivery_data = data[data['delivery_id'] != 'DEPOT']
        depot_data = data[data['delivery_id'] == 'DEPOT']
        
        fig = go.Figure()
        
        # Add delivery points by cluster
        for cluster_id in delivery_data['cluster'].unique():
            cluster_data = delivery_data[delivery_data['cluster'] == cluster_id]
            
            fig.add_trace(go.Scatter(
                x=cluster_data['longitude'],
                y=cluster_data['latitude'],
                mode='markers',
                name=f'Cluster {cluster_id}',
                marker=dict(size=10),
                text=cluster_data['delivery_id'],
                hovertemplate='<b>%{text}</b><br>Lat: %{y}<br>Lon: %{x}<extra></extra>'
            ))
        
        # Add depot
        if not depot_data.empty:
            fig.add_trace(go.Scatter(
                x=depot_data['longitude'],
                y=depot_data['latitude'],
                mode='markers',
                name='Depot',
                marker=dict(size=15, color='black', symbol='square'),
                text='DEPOT',
                hovertemplate='<b>%{text}</b><br>Lat: %{y}<br>Lon: %{x}<extra></extra>'
            ))
        
        fig.update_layout(
            title='Delivery Point Clustering',
            xaxis_title='Longitude',
            yaxis_title='Latitude',
            hovermode='closest'
        )
        
        return fig
    
    def create_performance_dashboard(self, routes, original_distance=None):
        """Create performance metrics dashboard"""
        if not routes:
            return None
        
        # Calculate metrics
        total_distance = sum(route['total_distance'] for route in routes.values())
        total_deliveries = sum(route['delivery_count'] for route in routes.values())
        num_routes = len(routes)
        avg_distance_per_route = total_distance / num_routes if num_routes > 0 else 0
        
        # Route distances
        route_names = list(routes.keys())
        route_distances = [routes[name]['total_distance'] for name in route_names]
        route_deliveries = [routes[name]['delivery_count'] for name in route_names]
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Route Distances', 'Deliveries per Route', 
                          'Performance Metrics', 'Distance Distribution'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "indicator"}, {"type": "histogram"}]]
        )
        
        # Route distances bar chart
        fig.add_trace(
            go.Bar(x=route_names, y=route_distances, name='Distance (km)'),
            row=1, col=1
        )
        
        # Deliveries per route
        fig.add_trace(
            go.Bar(x=route_names, y=route_deliveries, name='Deliveries'),
            row=1, col=2
        )
        
        # Performance indicators
        improvement = 0
        if original_distance:
            improvement = ((original_distance - total_distance) / original_distance) * 100
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=improvement,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Distance Improvement %"},
                gauge={'axis': {'range': [0, 50]},
                      'bar': {'color': "darkgreen"},
                      'steps': [{'range': [0, 25], 'color': "lightgray"},
                               {'range': [25, 50], 'color': "gray"}],
                      'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 30}}
            ),
            row=2, col=1
        )
        
        # Distance distribution
        fig.add_trace(
            go.Histogram(x=route_distances, name='Distance Distribution'),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text="Route Optimization Performance Dashboard",
            showlegend=False
        )
        
        return fig
    
    def save_map(self, map_obj, filename):
        """Save map to HTML file"""
        map_obj.save(filename)
        return filename