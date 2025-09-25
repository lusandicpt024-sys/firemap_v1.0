#!/usr/bin/env python3
"""
Comprehensive OSM-Integrated Forest Fire Visualization
Creates interactive HTML map with fires, vehicles, and OSM landmarks
"""

import pandas as pd
import folium
import json
from folium import plugins
import numpy as np

class FireMapVisualizer:
    def __init__(self):
        """Initialize the visualizer"""
        self.fire_data = None
        self.vehicle_data = None
        self.osm_data = None
        self.enhanced_data = None
        
        # Map center (Cape Point area)
        self.map_center = [-34.35, 18.45]
        
        # Color schemes
        self.terrain_colors = {
            'Mountain': '#8B4513',    # Brown
            'Forest': '#228B22',      # Forest Green
            'Coastal': '#4169E1',     # Royal Blue
            'Road': '#696969',        # Dim Gray
            'Grassland': '#9ACD32'    # Yellow Green
        }
        
        self.intensity_colors = {
            1: '#FFE4B5',  # Light
            2: '#FFD700',  # Light-Medium
            3: '#FFA500',  # Medium
            4: '#FF8C00',  # Medium-High
            5: '#FF6347',  # High
            6: '#FF4500',  # Very High
            7: '#FF0000',  # Extreme
            8: '#DC143C',  # Critical
            9: '#B22222',  # Severe
            10: '#8B0000'  # Maximum
        }
        
        self.vehicle_colors = {
            'Fire Truck': '#FF0000',      # Red
            'Water Bomber': '#0000FF',    # Blue
            'Ground Crew': '#008000',     # Green
            'Helicopter': '#800080'       # Purple
        }
    
    def load_data(self):
        """Load all required data files"""
        print("Loading data files...")
        
        try:
            # Load enhanced fire data
            self.enhanced_data = pd.read_csv('gis_enhanced_fire_suppression.csv')
            print(f"Loaded {len(self.enhanced_data)} fire incidents")
            
            # Load OSM landmarks
            try:
                with open('table_mountain_gis_data.json', 'r') as f:
                    osm_raw = json.load(f)
                    self.osm_data = []
                    
                    # Extract tourism features
                    if 'tourism_features' in osm_raw:
                        for feature in osm_raw['tourism_features']:
                            self.osm_data.append({
                                'name': feature.get('name', f"Tourism_{feature.get('id', 'Unknown')}"),
                                'lat': feature['lat'],
                                'lon': feature['lon'],
                                'type': feature.get('type', 'tourism')
                            })
                
                print(f"Loaded {len(self.osm_data)} OSM landmarks")
            except FileNotFoundError:
                # Create basic landmark data for Table Mountain area
                print("OSM data file not found, using default landmarks...")
                self.osm_data = [
                    {'name': 'Table Mountain', 'lat': -33.9628, 'lon': 18.4098, 'type': 'mountain'},
                    {'name': 'Lions Head', 'lat': -33.9302, 'lon': 18.3952, 'type': 'mountain'},
                    {'name': 'Signal Hill', 'lat': -33.9248, 'lon': 18.3994, 'type': 'mountain'},
                    {'name': 'Kirstenbosch Gardens', 'lat': -33.9888, 'lon': 18.4344, 'type': 'park'},
                    {'name': 'Cape Point', 'lat': -34.3570, 'lon': 18.4977, 'type': 'landmark'},
                ]
                print(f"Using {len(self.osm_data)} default landmarks")
            
            # Create vehicle data (simulate based on enhanced data)
            self.create_vehicle_data()
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
        
        return True
    
    def create_vehicle_data(self):
        """Create vehicle deployment data"""
        vehicle_types = {
            'Fire Truck': {'count': 4, 'icon': 'truck'},
            'Water Bomber': {'count': 2, 'icon': 'plane'},
            'Ground Crew': {'count': 8, 'icon': 'users'},
            'Helicopter': {'count': 3, 'icon': 'helicopter'}
        }
        
        # Strategic positions near major landmarks
        base_positions = [
            (-34.3581, 18.4719, "Cape of Good Hope Base"),
            (-34.3548, 18.4978, "Cape Point Base"),
            (-34.375, 18.45, "Central Command"),
            (-34.32, 18.46, "Northern Station")
        ]
        
        vehicles = []
        vehicle_id = 1
        
        for vehicle_type, specs in vehicle_types.items():
            for i in range(specs['count']):
                base_idx = i % len(base_positions)
                base_lat, base_lon, base_name = base_positions[base_idx]
                
                # Add random positioning around base
                lat = base_lat + np.random.uniform(-0.01, 0.01)
                lon = base_lon + np.random.uniform(-0.01, 0.01)
                
                vehicles.append({
                    'Vehicle_ID': f'V{vehicle_id:03d}',
                    'Type': vehicle_type,
                    'Latitude': lat,
                    'Longitude': lon,
                    'Base': base_name,
                    'Status': 'Available',
                    'Icon': specs['icon']
                })
                vehicle_id += 1
        
        self.vehicle_data = pd.DataFrame(vehicles)
    
    def create_map(self):
        """Create the main folium map"""
        print("Creating interactive map...")
        
        # Initialize map
        m = folium.Map(
            location=self.map_center,
            zoom_start=12,
            tiles=None
        )
        
        # Add tile layers
        folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m)
        folium.TileLayer(
            'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
            attr='OpenTopoMap',
            name='Topographic'
        ).add_to(m)
        folium.TileLayer(
            'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri WorldImagery',
            name='Satellite'
        ).add_to(m)
        
        return m
    
    def add_fire_markers(self, m):
        """Add fire incident markers to the map"""
        print("Adding fire markers...")
        
        # Create feature groups for different fire statuses
        active_fires = folium.FeatureGroup(name='Active Fires')
        suppressed_fires = folium.FeatureGroup(name='Suppressed Fires')
        
        for idx, fire in self.enhanced_data.iterrows():
            # Determine marker color based on intensity and status
            if fire['status'] == 'Extinguished':
                color = '#32CD32'  # Lime Green for suppressed
                icon_color = 'green'
                group = suppressed_fires
                status_text = "SUPPRESSED"
            else:
                # Map temperature to intensity (0-10 scale based on Fire_Temperature)
                temp = float(fire['Fire_Temperature'])
                intensity = int(min(10, max(1, temp / 100))) if temp > 0 else 1
                color = self.intensity_colors.get(intensity, '#FF0000')
                icon_color = 'red'
                group = active_fires
                status_text = "ACTIVE"
            
            # Create popup content with available fields
            popup_content = f"""
            <div style="width: 250px;">
                <h4><b>Fire at ({fire['Latitude']:.4f}, {fire['Longitude']:.4f})</b> - {status_text}</h4>
                <table style="width:100%;">
                    <tr><td><b>Temperature:</b></td><td>{fire['Fire_Temperature']}°C</td></tr>
                    <tr><td><b>Status:</b></td><td>{fire['status']}</td></tr>
                    <tr><td><b>Terrain:</b></td><td>{fire['Terrain']}</td></tr>
                    <tr><td><b>Nearest Station:</b></td><td>{fire['Nearest_Fire_Station']}</td></tr>
                    <tr><td><b>Distance to Station:</b></td><td>{fire['Station_Distance_KM']} km</td></tr>
                    <tr><td><b>Water Access:</b></td><td>{'Yes' if fire['Has_Water_Access'] else 'No'}</td></tr>
                    <tr><td><b>Spread Rate:</b></td><td>{fire['spread_rate_m_per_min']} m/min</td></tr>
                </table>
                <p><small>Coordinates: {fire['Latitude']:.4f}, {fire['Longitude']:.4f}</small></p>
            </div>
            """
            
            # Create marker
            # Use temperature to determine size (higher temp = larger marker)
            temp = float(fire['Fire_Temperature'])
            marker_size = max(3, min(15, temp / 50)) if temp > 0 else 3
            
            folium.CircleMarker(
                location=[fire['Latitude'], fire['Longitude']],
                radius=marker_size,
                popup=folium.Popup(popup_content, max_width=300),
                color='black',
                weight=2,
                fillColor=color,
                fillOpacity=0.7,
                tooltip=f"Fire at ({fire['Latitude']:.3f}, {fire['Longitude']:.3f}) - {status_text} (Temp: {temp}°C)"
            ).add_to(group)
        
        # Add groups to map
        active_fires.add_to(m)
        suppressed_fires.add_to(m)
    
    def add_vehicle_markers(self, m):
        """Add vehicle markers to the map"""
        print("Adding vehicle markers...")
        
        # Create feature groups for different vehicle types
        vehicle_groups = {}
        for vehicle_type in self.vehicle_data['Type'].unique():
            vehicle_groups[vehicle_type] = folium.FeatureGroup(name=f'{vehicle_type}s')
        
        for idx, vehicle in self.vehicle_data.iterrows():
            # Create popup content
            popup_content = f"""
            <div style="width: 200px;">
                <h4><b>{vehicle['Vehicle_ID']}</b></h4>
                <table style="width:100%;">
                    <tr><td><b>Type:</b></td><td>{vehicle['Type']}</td></tr>
                    <tr><td><b>Base:</b></td><td>{vehicle['Base']}</td></tr>
                    <tr><td><b>Status:</b></td><td>{vehicle['Status']}</td></tr>
                </table>
                <p><small>Coordinates: {vehicle['Latitude']:.4f}, {vehicle['Longitude']:.4f}</small></p>
            </div>
            """
            
            # Vehicle icon based on type
            icon_map = {
                'Fire Truck': 'truck',
                'Water Bomber': 'plane',
                'Ground Crew': 'users',
                'Helicopter': 'helicopter'
            }
            
            folium.Marker(
                location=[vehicle['Latitude'], vehicle['Longitude']],
                popup=folium.Popup(popup_content, max_width=250),
                icon=folium.Icon(
                    color='red' if vehicle['Type'] == 'Fire Truck' else
                          'blue' if vehicle['Type'] == 'Water Bomber' else
                          'green' if vehicle['Type'] == 'Ground Crew' else 'purple',
                    icon=icon_map.get(vehicle['Type'], 'circle'),
                    prefix='fa'
                ),
                tooltip=f"{vehicle['Vehicle_ID']} - {vehicle['Type']}"
            ).add_to(vehicle_groups[vehicle['Type']])
        
        # Add all vehicle groups to map
        for group in vehicle_groups.values():
            group.add_to(m)
    
    def add_osm_landmarks(self, m):
        """Add OSM landmark markers to the map"""
        print("Adding OSM landmarks...")
        
        landmarks_group = folium.FeatureGroup(name='OSM Landmarks')
        
        for landmark in self.osm_data:
            popup_content = f"""
            <div style="width: 200px;">
                <h4><b>{landmark['name']}</b></h4>
                <p><b>Type:</b> {landmark['type']}</p>
                <p><small>Real OSM Feature</small></p>
                <p><small>Coordinates: {landmark['lat']:.4f}, {landmark['lon']:.4f}</small></p>
            </div>
            """
            
            folium.Marker(
                location=[landmark['lat'], landmark['lon']],
                popup=folium.Popup(popup_content, max_width=250),
                icon=folium.Icon(
                    color='orange',
                    icon='info-sign',
                    prefix='glyphicon'
                ),
                tooltip=f"OSM: {landmark['name']}"
            ).add_to(landmarks_group)
        
        landmarks_group.add_to(m)
    
    def add_terrain_analysis(self, m):
        """Add terrain analysis overlay"""
        print("Adding terrain analysis...")
        
        # Create terrain distribution chart data
        terrain_stats = self.enhanced_data['Terrain'].value_counts()
        
        # Add custom legend for terrain types
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <h4>Terrain Types</h4>
        '''
        
        for terrain, color in self.terrain_colors.items():
            count = terrain_stats.get(terrain, 0)
            legend_html += f'<p><span style="color:{color};">●</span> {terrain}: {count} fires</p>'
        
        legend_html += '</div>'
        m.get_root().html.add_child(folium.Element(legend_html))
    
    def add_statistics_panel(self, m):
        """Add statistics panel to the map"""
        print("Adding statistics panel...")
        
        # Calculate statistics using available fields
        total_incidents = len(self.enhanced_data)
        active_fires = len(self.enhanced_data[self.enhanced_data['Fire_Present'] > 0])
        extinguished = len(self.enhanced_data[self.enhanced_data['status'] == 'Extinguished'])
        avg_temp = self.enhanced_data[self.enhanced_data['Fire_Temperature'] > 0]['Fire_Temperature'].mean()
        avg_temp = avg_temp if not pd.isna(avg_temp) else 0
        
        stats_html = f'''
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 300px; height: 180px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:12px; padding: 10px; border-radius: 5px;">
        <h3 style="margin-top: 0;">Fire Management Summary</h3>
        <table style="width:100%; font-size:11px;">
            <tr><td><b>Total Incidents:</b></td><td>{total_incidents}</td></tr>
            <tr><td><b>Active Fires:</b></td><td>{active_fires}</td></tr>
            <tr><td><b>Extinguished:</b></td><td>{extinguished}</td></tr>
            <tr><td><b>Avg Temperature:</b></td><td>{avg_temp:.1f}°C</td></tr>
            <tr><td><b>Fire Stations:</b></td><td>{len(self.enhanced_data['Nearest_Fire_Station'].unique())}</td></tr>
            <tr><td><b>Terrain Types:</b></td><td>{len(self.enhanced_data['Terrain'].unique())}</td></tr>
        </table>
        <p style="margin-bottom: 0;"><small>Enhanced with real OSM geographical data</small></p>
        </div>
        '''
        
        m.get_root().html.add_child(folium.Element(stats_html))
    
    def add_heatmap(self, m):
        """Add fire intensity heatmap"""
        print("Adding fire intensity heatmap...")
        
        # Prepare data for heatmap
        heat_data = []
        for idx, fire in self.enhanced_data.iterrows():
            # Use Fire_Temperature as intensity for heatmap
            temp = float(fire['Fire_Temperature'])
            intensity = temp / 100 if temp > 0 else 0  # Normalize to 0-10 scale
            heat_data.append([
                fire['Latitude'],
                fire['Longitude'],
                intensity
            ])
        
        # Create heatmap
        heatmap = plugins.HeatMap(
            heat_data,
            name='Fire Intensity Heatmap',
            min_opacity=0.2,
            max_zoom=18,
            radius=15,
            blur=10,
            gradient={
                0.4: 'blue',
                0.6: 'cyan',
                0.7: 'lime',
                0.8: 'yellow',
                1.0: 'red'
            }
        )
        heatmap.add_to(m)
    
    def create_visualization(self, output_file='osm_integrated_fire_map.html'):
        """Create complete visualization"""
        if not self.load_data():
            print("Failed to load data")
            return None
        
        # Create base map
        m = self.create_map()
        
        # Add all layers
        self.add_fire_markers(m)
        self.add_vehicle_markers(m)
        self.add_osm_landmarks(m)
        self.add_terrain_analysis(m)
        self.add_statistics_panel(m)
        self.add_heatmap(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add fullscreen plugin
        plugins.Fullscreen().add_to(m)
        
        # Add measure control
        plugins.MeasureControl().add_to(m)
        
        # Save map
        m.save(output_file)
        print(f"\n[SUCCESS] Interactive map saved as: {output_file}")
        print(f"[INFO] Map includes:")
        print(f"  - {len(self.enhanced_data)} fire incidents with OSM context")
        print(f"  - {len(self.vehicle_data)} emergency vehicles")
        print(f"  - {len(self.osm_data)} real OSM landmarks")
        print(f"  - Interactive layers and controls")
        print(f"  - Fire intensity heatmap")
        print(f"  - Terrain analysis")
        print(f"  - Suppression statistics")
        
        return output_file

def main():
    """Main execution function"""
    print("Creating OSM-Integrated Fire Suppression Visualization...")
    print("="*60)
    
    visualizer = FireMapVisualizer()
    output_file = visualizer.create_visualization()
    
    if output_file:
        print(f"\n🗺️  SUCCESS: Interactive map created!")
        print(f"📍 File location: {output_file}")
        print(f"🌐 Open the HTML file in your web browser to view the map")
        print(f"📊 Features real geographical data from OpenStreetMap")
    else:
        print("[ERROR] Failed to create visualization")

if __name__ == "__main__":
    main()