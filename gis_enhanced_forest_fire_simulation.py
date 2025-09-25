#!/usr/bin/env python3
"""
GIS-Enhanced Forest Fire Simulation for Table Mountain National Park
This version incorporates real geographical knowledge about Table Mountain area
to provide more accurate terrain classification and vehicle deployment strategies.
"""

import csv
import json
import random
from math import hypot, sin, cos, radians, sqrt, atan2
from datetime import datetime, timedelta

# Realistic vehicle types based on actual fire truck capabilities
# Enhanced effectiveness based on large water capacity and extended operational range
# Water capacity: 3,785-18,927 liters allows for sustained fire suppression
VEHICLE_TYPES = {
    "Heavy-Duty Fire Engine": {
        "count": 4, "capacity": 11356, "speed": 60, "effective_rate": 0.75,
        "terrain": ["road", "urban"], "range": 0.45, "water_source_dependent": False,
        "max_range_km": 50, "description": "3,000 gallon capacity, 75% effectiveness",
        "suppression_duration": 45, "refill_time": 15  # minutes of continuous suppression
    },
    "4x4 Wildland Vehicle": {
        "count": 6, "capacity": 7571, "speed": 45, "effective_rate": 0.70,
        "terrain": ["road", "rough", "mountain"], "range": 0.45, "water_source_dependent": False,
        "max_range_km": 50, "description": "2,000 gallon capacity, 70% effectiveness, all-terrain",
        "suppression_duration": 30, "refill_time": 10
    },
    "Water Tanker": {
        "count": 2, "capacity": 18927, "speed": 50, "effective_rate": 0.85,
        "terrain": ["road"], "range": 0.45, "water_source_dependent": False,
        "max_range_km": 50, "description": "5,000 gallon capacity, 85% effectiveness, self-sufficient",
        "suppression_duration": 90, "refill_time": 25  # Longest duration, highest effectiveness
    },
    "Rapid Intervention Vehicle": {
        "count": 3, "capacity": 3785, "speed": 80, "effective_rate": 0.60,
        "terrain": ["road", "rough"], "range": 0.45, "water_source_dependent": True,
        "max_range_km": 50, "description": "1,000 gallon capacity, 60% effectiveness, fastest response",
        "suppression_duration": 20, "refill_time": 8  # Fast but limited duration
    },
    "Incident Command Vehicle": {
        "count": 1, "capacity": 0, "speed": 70, "effective_rate": 0.15,
        "terrain": ["road"], "range": 0.45, "water_source_dependent": False,
        "max_range_km": 50, "description": "Coordination and communication, minor suppression",
        "suppression_duration": 0, "refill_time": 0  # Coordination multiplier for other units
    },
    "Helicopter Water Bucket": {
        "count": 2, "capacity": 3785, "speed": 150, "effective_rate": 0.90,
        "terrain": ["all"], "range": 0.90, "water_source_dependent": True,
        "max_range_km": 100, "description": "1,000 gallon bucket, 90% effectiveness, aerial advantage",
        "suppression_duration": 15, "refill_time": 12  # Quick drops, high effectiveness
    },
    "CAFS Unit": {
        "count": 2, "capacity": 7571, "speed": 55, "effective_rate": 0.80,
        "terrain": ["road", "rough"], "range": 0.45, "water_source_dependent": False,
        "max_range_km": 50, "description": "2,000 gallon CAFS, 80% effectiveness, foam enhancement",
        "suppression_duration": 40, "refill_time": 12  # Enhanced foam effectiveness
    },
}

# Real geographical features of Table Mountain National Park area
class TableMountainGIS:
    def __init__(self):
        # Define actual geographical boundaries and features (expanded to cover full park)
        # Table Mountain National Park extends from Constantia to Signal Hill
        # Using precise rectangular bounds from corner coordinates
        self.bounds = {
            'lat_min': -33.977523, 'lat_max': -33.937334,
            'lon_min': 18.391285, 'lon_max': 18.437977
        }
        
        # Major roads in Table Mountain National Park area (expanded coverage)
        self.major_roads = [
            # M3 Highway (Southern Suburbs to City)
            [(-34.40, 18.42), (-34.36, 18.42), (-34.35, 18.43), (-34.34, 18.44), (-34.32, 18.45)],
            # Tafelberg Road to Table Mountain
            [(-34.355, 18.415), (-34.352, 18.418), (-34.350, 18.420), (-34.347, 18.422)],
            # Rhodes Memorial and University area
            [(-34.345, 18.445), (-34.347, 18.448), (-34.349, 18.450)],
            # Signal Hill Road
            [(-34.325, 18.410), (-34.330, 18.415), (-34.335, 18.420)],
            # Kirstenbosch access roads
            [(-34.388, 18.430), (-34.385, 18.432), (-34.382, 18.435)],
            # Constantia area roads
            [(-34.395, 18.420), (-34.390, 18.425), (-34.385, 18.430)],
            # Camp Bay and Clifton coastal roads
            [(-34.345, 18.375), (-34.350, 18.380), (-34.355, 18.385)]
        ]
        
        # Water sources (reservoirs, dams, rivers) across expanded park area
        self.water_sources = [
            {"name": "Woodhead Reservoir", "lat": -34.345, "lon": 18.445, "radius": 0.003},
            {"name": "Hely-Hutchinson Reservoir", "lat": -34.348, "lon": 18.447, "radius": 0.002},
            {"name": "De Villiers Reservoir", "lat": -34.352, "lon": 18.442, "radius": 0.002},
            {"name": "Kirstenbosch Dam", "lat": -34.388, "lon": 18.432, "radius": 0.002},
            {"name": "Constantia Uitsig Dam", "lat": -34.395, "lon": 18.425, "radius": 0.002},
            {"name": "Lions Head Reservoir", "lat": -34.335, "lon": 18.405, "radius": 0.001},
            {"name": "Camps Bay Tidal Pool", "lat": -34.345, "lon": 18.378, "radius": 0.001},
            {"name": "Liesbeek River", "lat": -34.365, "lon": 18.435, "radius": 0.001},
            {"name": "Silvermine Dam", "lat": -34.365, "lon": 18.390, "radius": 0.003},
            {"name": "Cecilia Forest Water Point", "lat": -34.375, "lon": 18.415, "radius": 0.001}
        ]
        
        # Real Cape Town fire stations serving your bounds area
        self.fire_stations = [
            {"name": "Roeland Street Fire Station", "lat": -33.926, "lon": 18.421, "vehicles": ["all"]},
            {"name": "Sea Point Fire Station", "lat": -33.921, "lon": 18.384, "vehicles": ["all"]},
            {"name": "Constantia Fire Station", "lat": -34.004, "lon": 18.441, "vehicles": ["all"]},
            {"name": "Salt River Fire Station", "lat": -33.930, "lon": 18.465, "vehicles": ["all"]},
            {"name": "Wynberg Fire Station", "lat": -34.001, "lon": 18.475, "vehicles": ["all"]},
            {"name": "Brooklyn Fire Station", "lat": -33.906, "lon": 18.509, "vehicles": ["4x4", "rapid_intervention"]},
            {"name": "Ottery Fire Station", "lat": -34.001, "lon": 18.504, "vehicles": ["all"]},
            {"name": "Hout Bay Fire Station", "lat": -34.043, "lon": 18.351, "vehicles": ["4x4", "water_tanker"]},
            {"name": "Lakeside Fire Station", "lat": -34.053, "lon": 18.452, "vehicles": ["helicopter"]}
        ]
        
        # Terrain elevation zones (expanded to cover full Table Mountain National Park)
        self.elevation_zones = {
            "coastal": {"min_lat": -34.40, "max_lat": -34.36, "min_lon": 18.35, "max_lon": 18.42},
            "foothills": {"min_lat": -34.38, "max_lat": -34.32, "min_lon": 18.38, "max_lon": 18.48},
            "mountain": {"min_lat": -34.37, "max_lat": -34.30, "min_lon": 18.40, "max_lon": 18.47},
            "urban": {"min_lat": -34.36, "max_lat": -34.31, "min_lon": 18.42, "max_lon": 18.50},
            "peninsula": {"min_lat": -34.40, "max_lat": -34.35, "min_lon": 18.35, "max_lon": 18.45}
        }

    def get_terrain_type(self, lat, lon):
        """Enhanced terrain classification based on real Table Mountain geography"""
        
        # Check if near water sources
        for water in self.water_sources:
            if self.get_distance_km(lat, lon, water["lat"], water["lon"]) <= water["radius"] * 111:  # Convert degrees to km
                return "water"
        
        # Check if near major roads
        for road in self.major_roads:
            for point in road:
                if self.get_distance_km(lat, lon, point[0], point[1]) <= 0.5:  # Within 500m of road
                    return "road"
        
        # Check elevation zones
        for zone_name, zone in self.elevation_zones.items():
            if (zone["min_lat"] <= lat <= zone["max_lat"] and 
                zone["min_lon"] <= lon <= zone["max_lon"]):
                return zone_name
        
        # Default classification based on position in expanded park area
        if lat <= -34.38 and lon <= 18.40:
            return "peninsula"  # Cape Peninsula area
        elif lat <= -34.36 and lon <= 18.42:
            return "coastal"    # Coastal strip
        elif lat >= -34.32 and lon >= 18.45:
            return "mountain"   # Table Mountain massif
        elif -34.38 < lat < -34.32 and 18.40 < lon < 18.48:
            return "rough"      # Foothills and forest areas
        else:
            return "road"       # Urban and road areas

    def get_distance_km(self, lat1, lon1, lat2, lon2):
        """Calculate distance in kilometers using Haversine formula"""
        R = 6371  # Earth's radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c

    def get_nearest_fire_station(self, lat, lon):
        """Find the nearest fire station to a given location"""
        min_distance = float('inf')
        nearest_station = None
        
        for station in self.fire_stations:
            distance = self.get_distance_km(lat, lon, station["lat"], station["lon"])
            if distance < min_distance:
                min_distance = distance
                nearest_station = station
                
        return nearest_station, min_distance

    def get_water_access(self, lat, lon, max_distance_km=2.0):
        """Check if location has access to water sources within specified distance"""
        for water in self.water_sources:
            distance = self.get_distance_km(lat, lon, water["lat"], water["lon"])
            if distance <= max_distance_km:
                return True, water["name"], distance
        return False, None, None
    
    def is_within_bounds(self, lat, lon):
        """Check if coordinates are within the specified geographical bounds"""
        return (self.bounds['lat_min'] <= lat <= self.bounds['lat_max'] and 
                self.bounds['lon_min'] <= lon <= self.bounds['lon_max'])

def load_and_enhance_fire_data():
    """Load the simulated fire data and enhance with GIS terrain classification"""
    gis = TableMountainGIS()
    
    # Read the generated fire data
    enhanced_data = []
    
    try:
        with open("simulated_forest_fire_table_mountain.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                lat = float(row["Latitude"])
                lon = float(row["Longitude"])
                
                # Only process fires within the specified bounds
                if not gis.is_within_bounds(lat, lon):
                    continue  # Skip fires outside bounds
                
                # Enhanced terrain classification
                terrain = gis.get_terrain_type(lat, lon)
                
                # Add GIS-enhanced fields
                nearest_station, station_distance = gis.get_nearest_fire_station(lat, lon)
                has_water, water_source, water_distance = gis.get_water_access(lat, lon)
                
                enhanced_row = {
                    **row,
                    "Terrain": terrain,
                    "Nearest_Fire_Station": nearest_station["name"] if nearest_station else "Unknown",
                    "Station_Distance_KM": round(station_distance, 2) if nearest_station else 999,
                    "Has_Water_Access": has_water,
                    "Water_Source": water_source if water_source else "None",
                    "Water_Distance_KM": round(water_distance, 2) if water_distance else 999
                }
                
                enhanced_data.append(enhanced_row)
                
    except FileNotFoundError:
        print("Fire data file not found. Please run the data generation script first.")
        return []
    
    return enhanced_data

def prepare_data_for_suppression(enhanced_data):
    """Prepare enhanced data with status and normalized field names for suppression simulation"""
    prepared_data = []
    
    for row in enhanced_data:
        # Add missing fields expected by the suppression algorithm
        prepared_row = dict(row)
        
        # Add fire status based on Fire_Present and Fire_Temperature
        fire_present = float(row.get("Fire_Present", 0))
        fire_temp = float(row.get("Fire_Temperature", 0))
        
        if fire_present > 0 and fire_temp > 0:
            if fire_temp >= 800:
                prepared_row["status"] = "Critical"
            elif fire_temp >= 400:
                prepared_row["status"] = "Active"
            else:
                prepared_row["status"] = "Smoldering"
        else:
            prepared_row["status"] = "No Fire"
        
        # Add temperature_c field (normalized from Fire_Temperature)
        prepared_row["temperature_c"] = str(fire_temp)
        
        # Map Rate_of_Spread to spread_rate_m_per_min
        prepared_row["spread_rate_m_per_min"] = str(row.get("Rate_of_Spread", 0))
        
        # Map Humidity to humidity_percent
        prepared_row["humidity_percent"] = str(row.get("Humidity", 50))
        
        prepared_data.append(prepared_row)
    
    return prepared_data

def enhanced_fire_suppression(data):
    """Enhanced fire suppression simulation using GIS data"""
    gis = TableMountainGIS()
    suppression_start_time = "2025-09-23T12:00:00Z"
    suppressed_locations = set()
    
                # Group data by time
    time_groups = {}
    for row in data:
        time = row["Time"]
        if time not in time_groups:
            time_groups[time] = []
        time_groups[time].append(row)
    
    # Process each time step
    for time in sorted(time_groups.keys()):
        if time >= suppression_start_time:
            burning_cells = [row for row in time_groups[time] if row["status"] in ["Active", "Critical"]]
            
            # Track vehicle usage per station
            station_vehicles = {}
            for station in gis.fire_stations:
                station_vehicles[station["name"]] = {v: 0 for v in VEHICLE_TYPES}
            
            # Prioritize fires by severity and accessibility
            burning_cells.sort(key=lambda x: (
                -float(x["temperature_c"]),  # Higher temperature first
                float(x["Station_Distance_KM"]),  # Closer fires first
                -int(x["Has_Water_Access"])  # Water access priority
            ))
            
            for cell in burning_cells:
                lat, lon = float(cell["Latitude"]), float(cell["Longitude"])
                terrain = cell["Terrain"]
                station_name = cell["Nearest_Fire_Station"]
                
                # Try to assign vehicles from nearest station
                assigned = False
                for vehicle_type, props in VEHICLE_TYPES.items():
                    # Check if vehicle can operate on this terrain
                    if terrain in props["terrain"] or "all" in props["terrain"]:
                        # Check if vehicle is available at station
                        if station_vehicles[station_name][vehicle_type] < props["count"]:
                            # Check if vehicle can reach the location (realistic 50km range)
                            station_distance = float(cell["Station_Distance_KM"])
                            max_range_km = props["max_range_km"]  # Use realistic range values
                            
                            if station_distance <= max_range_km:
                                # Check water dependency - large trucks carry substantial water
                                if props["water_source_dependent"]:
                                    # Large capacity trucks (>10,000L) are less water dependent
                                    if props["capacity"] < 10000:
                                        if not cell["Has_Water_Access"] or float(cell["Water_Distance_KM"]) > 15:
                                            continue  # Smaller trucks need closer water access
                                    # Large tankers can operate independently for longer
                                
                                # Assign vehicle
                                station_vehicles[station_name][vehicle_type] += 1
                                
                                # Calculate enhanced suppression effectiveness
                                base_effectiveness = props["effective_rate"]
                                
                                # Large water capacity bonus (more sustained suppression)
                                capacity_bonus = min(0.2, props["capacity"] / 100000)  # Up to 20% bonus for large capacity
                                
                                # Response time bonus (faster vehicles are more effective)
                                response_time_bonus = min(0.15, (props["speed"] - 40) / 200)  # Up to 15% bonus for fast response
                                
                                # Adjust for terrain difficulty (improved with better vehicles)
                                terrain_modifier = {
                                    "road": 1.0, "urban": 1.0, "rough": 0.9,  # Better performance on rough terrain
                                    "mountain": 0.8, "coastal": 0.95, "water": 0.4  # Improved mountain performance
                                }.get(terrain, 0.8)
                                
                                # Adjust for weather (enhanced capabilities handle weather better)
                                weather_modifier = 1.0
                                if float(cell["Precipitation"]) > 0:
                                    weather_modifier += 0.4  # Better in rain
                                if float(cell["Wind_Speed"]) > 30:
                                    weather_modifier -= 0.1  # Less wind impact due to better equipment
                                
                                # Check for coordination bonus (multiple vehicle types at same fire)
                                coordination_bonus = 0
                                active_vehicles_at_fire = sum(1 for v_type in VEHICLE_TYPES 
                                                            if station_vehicles[station_name][v_type] > 0)
                                if active_vehicles_at_fire > 1:
                                    coordination_bonus = min(0.2, active_vehicles_at_fire * 0.05)  # Up to 20% coordination bonus
                                
                                # Calculate final effectiveness (can exceed 90% with realistic capabilities)
                                effective_rate = (base_effectiveness + capacity_bonus + response_time_bonus + coordination_bonus) * terrain_modifier * weather_modifier
                                effective_rate = max(0.2, min(0.95, effective_rate))  # Clamp between 20-95% (improved range)
                                
                                # Apply enhanced suppression with realistic vehicle capabilities
                                suppression_factor = 1 - effective_rate
                                new_temp = float(cell["temperature_c"]) * suppression_factor
                                new_spread = float(cell["spread_rate_m_per_min"]) * suppression_factor
                                
                                # Enhanced extinguish probability based on vehicle capabilities
                                base_extinguish_chance = effective_rate
                                
                                # Large capacity vehicles have higher complete extinguish probability
                                capacity_extinguish_bonus = min(0.3, props["capacity"] / 60000)  # Up to 30% bonus for largest tankers
                                
                                # CAFS and foam units have enhanced extinguish capability
                                foam_bonus = 0.2 if "CAFS" in vehicle_type else 0
                                
                                # Helicopter aerial advantage
                                aerial_bonus = 0.25 if "Helicopter" in vehicle_type else 0
                                
                                # Weather assistance (using humidity as proxy for precipitation)
                                weather_extinguish_bonus = (100 - float(cell["humidity_percent"])) / 200  # Dry conditions make suppression harder
                                
                                # Calculate total extinguish probability (can be quite high with good vehicles)
                                extinguish_chance = base_extinguish_chance + capacity_extinguish_bonus + foam_bonus + aerial_bonus + weather_extinguish_bonus
                                extinguish_chance = min(0.85, extinguish_chance)  # Cap at 85% (realistic maximum)
                                
                                if random.random() < extinguish_chance:
                                    cell["status"] = "Extinguished"
                                    cell["temperature_c"] = "0"
                                    cell["spread_rate_m_per_min"] = "0"
                                    suppressed_locations.add((lat, lon, time))
                                    # Log successful suppression
                                    print(f"[EXTINGUISHED] {vehicle_type} suppressed fire at ({lat:.3f}, {lon:.3f}) - {extinguish_chance:.1%} success rate")
                                else:
                                    cell["temperature_c"] = str(round(new_temp, 1))
                                    cell["spread_rate_m_per_min"] = str(round(new_spread, 2))
                                
                                assigned = True
                                break
                
                if not assigned:
                    # Fire continues uncontrolled
                    print(f"Warning: Fire at ({lat}, {lon}) could not be reached by available vehicles")
    
    return data, suppressed_locations

def save_enhanced_results(data, filename="gis_enhanced_fire_suppression.csv"):
    """Save the enhanced fire suppression results"""
    if not data:
        print("No data to save")
        return
    
    fieldnames = data[0].keys()
    
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Enhanced fire suppression data saved as {filename}")

def create_gis_enhanced_map(data, suppressed_locations, filename="gis_enhanced_fire_map.html"):
    """Create an interactive HTML map showing GIS-enhanced fire suppression results"""
    try:
        import folium
        from folium import plugins
        
        # Create base map centered on Table Mountain
        m = folium.Map(
            location=[-33.955, 18.42],  # Table Mountain center
            zoom_start=12,
            tiles='OpenStreetMap'
        )
        
        # Add terrain layer with proper attribution
        folium.TileLayer(
            'https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg',
            attr='Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap contributors',
            name='Terrain'
        ).add_to(m)
        
        # Create feature groups
        active_fires = folium.FeatureGroup(name='Active Fires')
        suppressed_fires = folium.FeatureGroup(name='Suppressed Fires')
        fire_stations = folium.FeatureGroup(name='Fire Stations')
        water_sources = folium.FeatureGroup(name='Water Sources')
        
        # Add fire markers
        for row in data:
            if float(row['Fire_Present']) > 0:  # Only show actual fires
                lat, lon = float(row['Latitude']), float(row['Longitude'])
                temp = float(row['Fire_Temperature'])
                
                # Determine fire status and color
                if row['status'] == 'Extinguished':
                    color = '#00FF00'  # Green for suppressed
                    group = suppressed_fires
                    status = 'SUPPRESSED'
                elif row['status'] in ['Active', 'Critical']:
                    color = '#FF4500' if temp > 500 else '#FF8C00'  # Red/Orange for active
                    group = active_fires
                    status = 'ACTIVE'
                else:
                    continue  # Skip non-fires
                
                # Create popup with GIS information
                popup_html = f"""
                <div style="width: 250px;">
                    <h4>{status} Fire</h4>
                    <b>Temperature:</b> {temp}°C<br>
                    <b>Terrain:</b> {row['Terrain']}<br>
                    <b>Station:</b> {row['Nearest_Fire_Station']}<br>
                    <b>Distance to Station:</b> {row['Station_Distance_KM']} km<br>
                    <b>Water Access:</b> {'Yes' if row['Has_Water_Access'] else 'No'}<br>
                    <b>Coordinates:</b> ({lat:.4f}, {lon:.4f})
                </div>
                """
                
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=max(3, temp/100),  # Size based on temperature
                    popup=folium.Popup(popup_html, max_width=300),
                    color='black',
                    weight=1,
                    fillColor=color,
                    fillOpacity=0.7
                ).add_to(group)
        
        # Add fire stations
        gis = TableMountainGIS()
        for station in gis.fire_stations:
            folium.Marker(
                location=[station['lat'], station['lon']],
                popup=f"<b>{station['name']}</b><br>Vehicles: {', '.join(station['vehicles'])}",
                icon=folium.Icon(color='red', icon='home')
            ).add_to(fire_stations)
        
        # Add water sources
        for water in gis.water_sources:
            folium.CircleMarker(
                location=[water['lat'], water['lon']],
                radius=8,
                popup=f"<b>{water['name']}</b><br>Water Source",
                color='blue',
                fillColor='lightblue',
                fillOpacity=0.7
            ).add_to(water_sources)
        
        # Add all groups to map
        active_fires.add_to(m)
        suppressed_fires.add_to(m)
        fire_stations.add_to(m)
        water_sources.add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:12px; padding: 10px;">
        <h4>Legend</h4>
        <p><span style="color:#FF4500;">●</span> Active Fires</p>
        <p><span style="color:#00FF00;">●</span> Suppressed Fires</p>
        <p><span style="color:red;">📍</span> Fire Stations</p>
        <p><span style="color:blue;">●</span> Water Sources</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Save map
        m.save(filename)
        print(f"GIS-enhanced fire map saved as {filename}")
        
    except ImportError:
        print("Folium not available - skipping map generation")
    except Exception as e:
        print(f"Error creating map: {e}")

def generate_gis_report(data, suppressed_locations):
    """Generate a comprehensive GIS analysis report"""
    if not data:
        return
    
    print("\n" + "="*60)
    print("GIS-ENHANCED FIRE SUPPRESSION ANALYSIS REPORT")
    print("="*60)
    
    # Basic statistics
    total_locations = len(set((row["Latitude"], row["Longitude"]) for row in data))
    total_suppressed = len(suppressed_locations)
    
    print(f"Total fire locations: {total_locations}")
    print(f"Successfully suppressed: {total_suppressed}")
    print(f"Suppression success rate: {(total_suppressed/total_locations)*100:.1f}%")
    
    # Terrain analysis
    terrain_stats = {}
    for row in data:
        terrain = row["Terrain"]
        if terrain not in terrain_stats:
            terrain_stats[terrain] = {"total": 0, "fires": 0}
        terrain_stats[terrain]["total"] += 1
        if row["status"] in ["Active", "Critical"]:
            terrain_stats[terrain]["fires"] += 1
    
    print("\nTerrain Analysis:")
    for terrain, stats in terrain_stats.items():
        fire_rate = (stats["fires"]/stats["total"])*100 if stats["total"] > 0 else 0
        print(f"  {terrain.title()}: {stats['fires']}/{stats['total']} locations with fire ({fire_rate:.1f}%)")
    
    # Water access analysis
    water_access_fires = sum(1 for row in data if row["status"] in ["Active", "Critical"] and row["Has_Water_Access"] == True)
    total_fires = sum(1 for row in data if row["status"] in ["Active", "Critical"])
    
    print(f"\nWater Access Analysis:")
    print(f"  Fires with water access: {water_access_fires}/{total_fires} ({(water_access_fires/total_fires)*100:.1f}%)")
    
    # Station effectiveness
    station_stats = {}
    for row in data:
        station = row["Nearest_Fire_Station"]
        if station not in station_stats:
            station_stats[station] = {"total": 0, "fires": 0}
        station_stats[station]["total"] += 1
        if row["status"] in ["Active", "Critical"]:
            station_stats[station]["fires"] += 1
    
    print(f"\nFire Station Coverage:")
    for station, stats in station_stats.items():
        coverage = (stats["fires"]/stats["total"])*100 if stats["total"] > 0 else 0
        print(f"  {station}: {stats['fires']} fires in coverage area of {stats['total']} locations")

def main():
    """Main execution function"""
    print("GIS-Enhanced Forest Fire Simulation for Table Mountain")
    print("Loading and enhancing fire data with real geographical information...")
    
    # Load and enhance data
    enhanced_data = load_and_enhance_fire_data()
    if not enhanced_data:
        return
    
    print(f"Loaded {len(enhanced_data)} data points")
    
    # Prepare data for suppression simulation
    print("Preparing data for suppression simulation...")
    prepared_data = prepare_data_for_suppression(enhanced_data)
    
    # Run enhanced suppression simulation
    print("Running enhanced fire suppression simulation...")
    final_data, suppressed_locations = enhanced_fire_suppression(prepared_data)
    
    # Save results
    save_enhanced_results(final_data)
    
    # Create interactive HTML map
    print("Creating GIS-enhanced interactive map...")
    create_gis_enhanced_map(final_data, suppressed_locations)
    
    # Generate comprehensive report
    generate_gis_report(final_data, suppressed_locations)
    
    print(f"\nSimulation complete. Results saved to:")
    print("- gis_enhanced_fire_suppression.csv (detailed data)")
    print("- gis_enhanced_fire_map.html (interactive map)")
    print("\nEnhanced visualization features include:")
    print("- Real terrain classification based on Table Mountain geography")
    print("- Actual fire station locations and vehicle deployment")
    print("- Water source accessibility analysis")
    print("- Distance-based response effectiveness")
    print("- Weather and terrain impact on suppression success")

if __name__ == "__main__":
    main()