#!/usr/bin/env python3
"""
Enhanced Visualization for GIS-Based Forest Fire Simulation
This file creates interactive maps and visualizations using the GIS-enhanced fire data.
"""

import csv
import json
from math import sqrt

def create_enhanced_visualization():
    """Create enhanced HTML visualization with GIS data"""
    
    # Read the enhanced fire data
    try:
        with open("gis_enhanced_fire_suppression.csv", "r") as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except FileNotFoundError:
        print("Enhanced fire data not found. Please run gis_enhanced_forest_fire_simulation.py first.")
        return
    
    if not data:
        print("No data available for visualization")
        return
    
    # Get the latest time step
    latest_time = max(row["Time"] for row in data)
    latest_data = [row for row in data if row["Time"] == latest_time]
    
    # Calculate map center
    avg_lat = sum(float(row["Latitude"]) for row in latest_data) / len(latest_data)
    avg_lon = sum(float(row["Longitude"]) for row in latest_data) / len(latest_data)
    
    # Real Cape Town fire stations serving your area
    fire_stations = [
        {"name": "Roeland Street Fire Station", "lat": -33.926, "lon": 18.421},
        {"name": "Sea Point Fire Station", "lat": -33.921, "lon": 18.384},
        {"name": "Constantia Fire Station", "lat": -34.004, "lon": 18.441},
        {"name": "Salt River Fire Station", "lat": -33.930, "lon": 18.465},
        {"name": "Wynberg Fire Station", "lat": -34.001, "lon": 18.475}
    ]
    
    # Water sources
    water_sources = [
        {"name": "Woodhead Reservoir", "lat": -34.345, "lon": 18.445},
        {"name": "Hely-Hutchinson Reservoir", "lat": -34.348, "lon": 18.447},
        {"name": "De Villiers Reservoir", "lat": -34.352, "lon": 18.442}
    ]
    
    # Create HTML content
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>GIS-Enhanced Forest Fire Suppression - Table Mountain</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <style>
        body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
        #map {{ height: 70vh; width: 100%; }}
        #info {{ padding: 20px; background: #f5f5f5; }}
        .legend {{ background: white; padding: 10px; border-radius: 5px; 
                   box-shadow: 0 0 15px rgba(0,0,0,0.2); }}
        .legend-item {{ margin: 5px 0; }}
        .legend-color {{ width: 20px; height: 20px; display: inline-block; 
                         margin-right: 10px; border-radius: 50%; }}
        .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .stat-box {{ background: white; padding: 15px; border-radius: 5px; 
                     box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }}
    </style>
</head>
<body>
    <div id="info">
        <h1>GIS-Enhanced Forest Fire Suppression - Table Mountain National Park</h1>
        <p>Latest simulation time: {latest_time}</p>
        
        <div class="stats">
            <div class="stat-box">
                <h3>{len([r for r in latest_data if int(r["Fire_Present"]) == 1])}</h3>
                <p>Active Fires</p>
            </div>
            <div class="stat-box">
                <h3>{len([r for r in latest_data if r["Fire_Temperature"] == "0" and r["Rate_of_Spread"] == "0"])}</h3>
                <p>Extinguished</p>
            </div>
            <div class="stat-box">
                <h3>{len([r for r in latest_data if r["Has_Water_Access"] == "True"])}</h3>
                <p>Water Access Points</p>
            </div>
            <div class="stat-box">
                <h3>{len(set(r["Terrain"] for r in latest_data))}</h3>
                <p>Terrain Types</p>
            </div>
        </div>
    </div>
    
    <div id="map"></div>
    
    <script>
        // Initialize map
        var map = L.map('map').setView([{avg_lat}, {avg_lon}], 13);
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap contributors'
        }}).addTo(map);
        
        // Add satellite view option
        var satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
            attribution: 'Tiles © Esri'
        }});
        
        var baseMaps = {{
            "Street Map": L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png'),
            "Satellite": satellite
        }};
        
        // Fire stations
        var fireStationIcon = L.divIcon({{
            className: 'fire-station-icon',
            html: '🚒',
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        }});
        
        var fireStations = L.layerGroup();
"""
    
    # Add fire stations to map
    for station in fire_stations:
        html_content += f"""
        L.marker([{station['lat']}, {station['lon']}], {{icon: fireStationIcon}})
            .bindPopup('<b>{station['name']}</b><br>Fire Station')
            .addTo(fireStations);
"""
    
    # Add water sources
    html_content += """
        var waterIcon = L.divIcon({
            className: 'water-icon',
            html: '💧',
            iconSize: [25, 25],
            iconAnchor: [12, 12]
        });
        
        var waterSources = L.layerGroup();
"""
    
    for water in water_sources:
        html_content += f"""
        L.marker([{water['lat']}, {water['lon']}], {{icon: waterIcon}})
            .bindPopup('<b>{water['name']}</b><br>Water Source')
            .addTo(waterSources);
"""
    
    # Add fire data points
    html_content += """
        var fireData = L.layerGroup();
        var suppressedData = L.layerGroup();
        var safeData = L.layerGroup();
"""
    
    # Process each data point
    for row in latest_data:
        lat, lon = float(row["Latitude"]), float(row["Longitude"])
        fire_present = int(row["Fire_Present"])
        fire_temp = float(row["Fire_Temperature"])
        spread_rate = float(row["Rate_of_Spread"])
        terrain = row["Terrain"]
        station = row["Nearest_Fire_Station"]
        water_access = row["Has_Water_Access"]
        
        popup_content = f"""
<b>Location:</b> {lat:.3f}, {lon:.3f}<br>
<b>Terrain:</b> {terrain}<br>
<b>Fire Temperature:</b> {fire_temp}°C<br>
<b>Spread Rate:</b> {spread_rate} m/h<br>
<b>Nearest Station:</b> {station}<br>
<b>Water Access:</b> {water_access}<br>
<b>Station Distance:</b> {row['Station_Distance_KM']} km
"""
        
        if fire_present:
            # Active fire - red
            color = "red"
            radius = max(8, min(15, fire_temp / 60))  # Scale radius with temperature
            layer = "fireData"
        elif fire_temp == 0 and spread_rate == 0:
            # Extinguished - blue
            color = "blue"
            radius = 6
            layer = "suppressedData"
        else:
            # Safe area - green
            color = "green"
            radius = 4
            layer = "safeData"
        
        html_content += f"""
        L.circleMarker([{lat}, {lon}], {{
            color: '{color}',
            fillColor: '{color}',
            fillOpacity: 0.7,
            radius: {radius},
            weight: 2
        }}).bindPopup(`{popup_content}`).addTo({layer});
"""
    
    # Complete the HTML
    html_content += f"""
        // Add layers to map
        fireStations.addTo(map);
        waterSources.addTo(map);
        fireData.addTo(map);
        suppressedData.addTo(map);
        safeData.addTo(map);
        
        // Layer control
        var overlayMaps = {{
            "Fire Stations": fireStations,
            "Water Sources": waterSources,
            "Active Fires": fireData,
            "Extinguished": suppressedData,
            "Safe Areas": safeData
        }};
        
        L.control.layers(baseMaps, overlayMaps).addTo(map);
        
        // Legend
        var legend = L.control({{position: 'bottomright'}});
        legend.onAdd = function (map) {{
            var div = L.DomUtil.create('div', 'legend');
            div.innerHTML = `
                <h4>Legend</h4>
                <div class="legend-item">
                    <span class="legend-color" style="background-color: red;"></span>
                    Active Fire
                </div>
                <div class="legend-item">
                    <span class="legend-color" style="background-color: blue;"></span>
                    Extinguished
                </div>
                <div class="legend-item">
                    <span class="legend-color" style="background-color: green;"></span>
                    Safe Area
                </div>
                <div class="legend-item">
                    🚒 Fire Station
                </div>
                <div class="legend-item">
                    💧 Water Source
                </div>
            `;
            return div;
        }};
        legend.addTo(map);
        
        // Add Table Mountain outline (approximate)
        var tableMountainOutline = [
            [-34.37, 18.40], [-34.33, 18.40], [-34.33, 18.47], [-34.37, 18.47], [-34.37, 18.40]
        ];
        
        L.polygon(tableMountainOutline, {{
            color: 'purple',
            weight: 3,
            opacity: 0.6,
            fill: false,
            dashArray: '10, 10'
        }}).addTo(map).bindPopup('Table Mountain National Park Boundary');
    </script>
</body>
</html>
"""
    
    # Save the HTML file
    with open("gis_enhanced_fire_map.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("Enhanced visualization saved as gis_enhanced_fire_map.html")
    
    # Create a simple text-based visualization as well
    create_text_visualization(latest_data)

def create_text_visualization(data):
    """Create a text-based visualization for terminals without graphics"""
    
    print("\n" + "="*80)
    print("TEXT-BASED FIRE MAP - TABLE MOUNTAIN")
    print("="*80)
    
    # Create a grid representation
    lat_min = min(float(row["Latitude"]) for row in data)
    lat_max = max(float(row["Latitude"]) for row in data)
    lon_min = min(float(row["Longitude"]) for row in data)
    lon_max = max(float(row["Longitude"]) for row in data)
    
    # Create grid
    grid_size = 20
    lat_step = (lat_max - lat_min) / grid_size
    lon_step = (lon_max - lon_min) / grid_size
    
    grid = [['.' for _ in range(grid_size)] for _ in range(grid_size)]
    
    # Populate grid
    for row in data:
        lat = float(row["Latitude"])
        lon = float(row["Longitude"])
        
        # Convert to grid coordinates
        grid_lat = int((lat - lat_min) / lat_step)
        grid_lon = int((lon - lon_min) / lon_step)
        
        # Ensure within bounds
        grid_lat = max(0, min(grid_size - 1, grid_lat))
        grid_lon = max(0, min(grid_size - 1, grid_lon))
        
        # Set symbol based on status
        if int(row["Fire_Present"]):
            grid[grid_lat][grid_lon] = 'X'  # Active fire
        elif float(row["Fire_Temperature"]) == 0:
            grid[grid_lat][grid_lon] = 'E'  # Extinguished fire
        else:
            grid[grid_lat][grid_lon] = '🌿'  # Safe
    
    # Add fire stations and water sources
    stations = [(-34.355, 18.430), (-34.345, 18.445), (-34.36, 18.42)]
    waters = [(-34.345, 18.445), (-34.348, 18.447), (-34.352, 18.442)]
    
    for station_lat, station_lon in stations:
        grid_lat = int((station_lat - lat_min) / lat_step)
        grid_lon = int((station_lon - lon_min) / lon_step)
        if 0 <= grid_lat < grid_size and 0 <= grid_lon < grid_size:
            grid[grid_lat][grid_lon] = 'S'
    
    for water_lat, water_lon in waters:
        grid_lat = int((water_lat - lat_min) / lat_step)
        grid_lon = int((water_lon - lon_min) / lon_step)
        if 0 <= grid_lat < grid_size and 0 <= grid_lon < grid_size:
            grid[grid_lat][grid_lon] = 'W'
    
    # Print grid
    print(f"Coordinates: {lat_min:.3f},{lon_min:.3f} to {lat_max:.3f},{lon_max:.3f}")
    print("\nLegend: X=Fire E=Extinguished .=Safe S=Station W=Water .=Empty")
    print("-" * (grid_size * 2))
    
    for row in reversed(grid):  # Reverse to match normal map orientation
        print(' '.join(row))
    
    print("-" * (grid_size * 2))

def main():
    """Main function to create all visualizations"""
    print("Creating GIS-Enhanced Forest Fire Visualizations...")
    create_enhanced_visualization()
    print("\\nVisualization complete!")
    print("Open 'gis_enhanced_fire_map.html' in a web browser to view the interactive map.")

if __name__ == "__main__":
    main()