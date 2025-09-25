#!/usr/bin/env python3
"""
Interactive Fire Incident Response System
Click-to-Start Fire with Real-time AI Response Recommendations

Features:
- Interactive map with click-to-start fire capability
- Real-time fire spread simulation
- AI-powered response recommendations
- Vehicle deployment optimization
- Station response coordination
"""

import json
import math
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
import webbrowser
import threading
import http.server
import socketserver
from urllib.parse import parse_qs, urlparse

class InteractiveFireResponseSystem:
    def __init__(self):
        self.active_fires = {}
        self.fire_stations = self.load_fire_stations()
        self.vehicle_fleet = self.load_vehicle_fleet()
        self.deployed_vehicles = {}
        self.fire_history = []
        self.response_log = []
        self.tracking_active = False
        self.last_update_time = {}
        self.recommendation_intervals = {}  # Store when to update recommendations
        
        # Enhanced fire growth parameters for faster, realistic spread
        self.fire_growth_constants = {
            'base_spread_rate': 3.0,  # hectares per hour in calm conditions (increased)
            'wind_multiplier': 5.0,   # wind can quintuple spread rate
            'slope_multiplier': 3.0,  # uphill spread 200% faster
            'fuel_load_factor': 2.5,  # vegetation density factor
            'humidity_factor': 0.3,   # high humidity slows spread significantly
            'temperature_factor': 2.5, # high temp more than doubles spread
            'suppression_effectiveness': 0.8,  # how effective suppression is
            'wind_shape_factor': 4.0,  # how much wind affects fire shape
            'terrain_shape_factor': 2.5  # how terrain affects spread pattern
        }
        
        # Critical areas for multi-front analysis
        self.critical_areas = self.define_critical_areas()
        
    def load_fire_stations(self):
        """Load fire station data with real Cape Town stations"""
        return {
            "roeland_street": {
                "name": "Roeland Street Fire Station",
                "lat": -33.926, "lon": 18.421,
                "vehicles": ["Heavy-Duty Fire Engine", "Rapid Intervention Vehicle", "Incident Command Vehicle"],
                "response_time_base": 5,  # minutes
                "coverage_radius": 8  # km
            },
            "sea_point": {
                "name": "Sea Point Fire Station", 
                "lat": -33.921, "lon": 18.384,
                "vehicles": ["4x4 Wildland Vehicle", "Water Tanker", "CAFS Unit"],
                "response_time_base": 6,
                "coverage_radius": 7
            },
            "constantia": {
                "name": "Constantia Fire Station",
                "lat": -34.004, "lon": 18.441,
                "vehicles": ["Heavy-Duty Fire Engine", "4x4 Wildland Vehicle", "Dive Vehicle"],
                "response_time_base": 8,
                "coverage_radius": 12
            },
            "salt_river": {
                "name": "Salt River Fire Station",
                "lat": -33.930, "lon": 18.465,
                "vehicles": ["Water Tanker", "Rapid Intervention Vehicle", "4x4 Wildland Vehicle"],
                "response_time_base": 7,
                "coverage_radius": 9
            },
            "wynberg": {
                "name": "Wynberg Fire Station",
                "lat": -34.001, "lon": 18.475,
                "vehicles": ["Heavy-Duty Fire Engine", "CAFS Unit", "Incident Command Vehicle"],
                "response_time_base": 9,
                "coverage_radius": 10
            }
        }
    
    def load_vehicle_fleet(self):
        """Load vehicle specifications"""
        return {
            "Heavy-Duty Fire Engine": {
                "capacity": 4000, "speed": 40, "effectiveness": 0.40,
                "terrain": ["road"], "crew": 4, "cost_per_hour": 500
            },
            "4x4 Wildland Vehicle": {
                "capacity": 2000, "speed": 30, "effectiveness": 0.35,
                "terrain": ["road", "rough"], "crew": 3, "cost_per_hour": 300
            },
            "Water Tanker": {
                "capacity": 10000, "speed": 30, "effectiveness": 0.20,
                "terrain": ["road"], "crew": 2, "cost_per_hour": 400
            },
            "Rapid Intervention Vehicle": {
                "capacity": 750, "speed": 60, "effectiveness": 0.20,
                "terrain": ["road", "rough"], "crew": 2, "cost_per_hour": 250
            },
            "Incident Command Vehicle": {
                "capacity": 0, "speed": 50, "effectiveness": 0,
                "terrain": ["road"], "crew": 3, "cost_per_hour": 200
            },
            "Dive Vehicle": {
                "capacity": 0, "speed": 40, "effectiveness": 0.15,
                "terrain": ["water", "coast"], "crew": 4, "cost_per_hour": 350
            },
            "CAFS Unit": {
                "capacity": 1200, "speed": 30, "effectiveness": 0.50,
                "terrain": ["road", "rough"], "crew": 3, "cost_per_hour": 450
            }
        }
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points in kilometers"""
        R = 6371  # Earth's radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    def get_terrain_type(self, lat, lon):
        """Determine terrain type based on coordinates"""
        # Table Mountain area terrain classification
        if lat <= -34.355 and lon <= 18.425:
            return "coast"
        elif lat >= -34.345 and lon >= 18.445:
            return "water"
        elif -34.355 < lat < -34.345 and 18.425 < lon < 18.445:
            return "rough"
        else:
            return "road"
    
    def calculate_spread_vectors(self):
        """Calculate realistic fire spread vectors in different directions"""
        # 8 directional vectors (N, NE, E, SE, S, SW, W, NW)
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        vectors = {}
        
        for direction in directions:
            # Base spread rate with random variation
            base_rate = 0.8 + random.random() * 0.4  # 0.8 to 1.2 multiplier
            
            # Add directional preferences based on wind, terrain, etc.
            if direction in ['NE', 'E', 'SE']:  # Common wind directions
                base_rate *= 1.2 + random.random() * 0.3
            elif direction in ['SW', 'W', 'NW']:  # Against prevailing wind
                base_rate *= 0.7 + random.random() * 0.2
            
            vectors[direction] = base_rate
            
        return vectors
    
    def define_critical_areas(self):
        """Define critical areas that require priority fire protection"""
        return {
            "residential_zones": [
                {"name": "Camps Bay Residential", "lat": -33.9553, "lon": 18.3773, "radius": 1.5, "priority": "HIGH"},
                {"name": "Hout Bay Township", "lat": -34.0487, "lon": 18.3563, "radius": 2.0, "priority": "HIGH"},
                {"name": "Constantia Valley", "lat": -34.0275, "lon": 18.4182, "radius": 1.8, "priority": "HIGH"},
                {"name": "Newlands Suburbs", "lat": -33.9712, "lon": 18.4276, "radius": 1.2, "priority": "MEDIUM"},
                {"name": "Rondebosch East", "lat": -33.9581, "lon": 18.4692, "radius": 1.0, "priority": "MEDIUM"}
            ],
            "forest_areas": [
                {"name": "Table Mountain National Park", "lat": -33.9628, "lon": 18.4098, "radius": 3.0, "priority": "HIGH"},
                {"name": "Kirstenbosch Botanical Garden", "lat": -33.9882, "lon": 18.4324, "radius": 1.5, "priority": "HIGH"},
                {"name": "Constantia Forest", "lat": -34.0156, "lon": 18.4089, "radius": 2.2, "priority": "MEDIUM"},
                {"name": "Tokai Forest", "lat": -34.0767, "lon": 18.4089, "radius": 1.8, "priority": "MEDIUM"}
            ],
            "infrastructure": [
                {"name": "University of Cape Town", "lat": -33.9579, "lon": 18.4612, "radius": 0.8, "priority": "HIGH"},
                {"name": "Groote Schuur Hospital", "lat": -33.9394, "lon": 18.4653, "radius": 0.5, "priority": "CRITICAL"},
                {"name": "Cape Town CBD", "lat": -33.9249, "lon": 18.4241, "radius": 2.5, "priority": "HIGH"},
                {"name": "V&A Waterfront", "lat": -33.9017, "lon": 18.4197, "radius": 1.0, "priority": "MEDIUM"}
            ]
        }
    
    def analyze_fire_fronts(self, fire):
        """Analyze different fronts of the fire based on its realistic shape"""
        if "shape_points" not in fire:
            # If no shape points yet, use basic analysis
            return self.basic_front_analysis(fire)
        
        shape_points = fire["shape_points"]
        wind_direction = fire["wind_direction"]
        
        # Divide fire perimeter into fronts
        fronts = {
            "head_fire": [],      # Leading edge (downwind)
            "flanking_fires": [], # Side edges
            "backing_fire": [],   # Rear edge (upwind)
            "spot_fires": fire.get("spot_fires", [])
        }
        
        # Classify each perimeter point into fronts based on wind direction
        for i, point in enumerate(shape_points):
            # Calculate bearing from fire center to this point
            bearing = self.calculate_bearing(fire["lat"], fire["lon"], point["lat"], point["lon"])
            
            # Determine front type based on bearing relative to wind direction
            angle_diff = abs(bearing - wind_direction)
            if angle_diff > 180:
                angle_diff = 360 - angle_diff
            
            point_info = {
                "lat": point["lat"], 
                "lon": point["lon"],
                "bearing": bearing,
                "distance_from_center": self.calculate_distance(fire["lat"], fire["lon"], point["lat"], point["lon"]),
                "threat_level": self.calculate_point_threat_level(point, fire)
            }
            
            if angle_diff <= 45:  # Within 45° of wind direction
                fronts["head_fire"].append(point_info)
            elif angle_diff >= 135:  # Opposite to wind direction
                fronts["backing_fire"].append(point_info)
            else:  # Side areas
                fronts["flanking_fires"].append(point_info)
        
        # Calculate priority and threat assessment for each front
        for front_name, points in fronts.items():
            if front_name != "spot_fires" and points:
                fronts[front_name] = {
                    "points": points,
                    "priority": self.assess_front_priority(front_name, points, fire),
                    "recommended_resources": self.recommend_front_resources(front_name, points, fire),
                    "threat_assessment": self.assess_front_threats(points, fire)
                }
        
        return fronts
    
    def basic_front_analysis(self, fire):
        """Basic front analysis when detailed shape data isn't available"""
        return {
            "primary_front": {
                "priority": "HIGH",
                "location": "Fire center",
                "threat_level": fire["intensity"],
                "recommended_resources": ["Initial Attack Team", "Fire Engine"]
            }
        }
    
    def calculate_bearing(self, lat1, lon1, lat2, lon2):
        """Calculate bearing between two points"""
        dlon = math.radians(lon2 - lon1)
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        
        y = math.sin(dlon) * math.cos(lat2_rad)
        x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)
        
        bearing = math.atan2(y, x)
        bearing = math.degrees(bearing)
        bearing = (bearing + 360) % 360
        
        return bearing
    
    def calculate_point_threat_level(self, point, fire):
        """Calculate threat level for a specific perimeter point"""
        base_threat = fire["intensity"]
        
        # Check proximity to critical areas
        min_distance_to_critical = float('inf')
        nearest_critical = None
        
        for category, areas in self.critical_areas.items():
            for area in areas:
                distance = self.calculate_distance(point["lat"], point["lon"], area["lat"], area["lon"])
                if distance < min_distance_to_critical:
                    min_distance_to_critical = distance
                    nearest_critical = area
        
        # Increase threat based on proximity to critical areas
        if min_distance_to_critical < 0.5:  # Within 500m
            base_threat += 30
        elif min_distance_to_critical < 1.0:  # Within 1km
            base_threat += 20
        elif min_distance_to_critical < 2.0:  # Within 2km
            base_threat += 10
        
        return {
            "level": min(100, base_threat),
            "nearest_critical": nearest_critical,
            "distance_to_critical": min_distance_to_critical
        }
    
    def assess_front_priority(self, front_name, points, fire):
        """Assess priority level for a fire front"""
        priorities = {"HEAD": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        
        # Head fire (main advancing front) is always highest priority
        if front_name == "head_fire":
            return "HEAD"
        
        # Calculate average threat level for this front
        avg_threat = sum(p["threat_level"]["level"] for p in points) / len(points)
        
        if avg_threat > 80:
            return "HIGH"
        elif avg_threat > 60:
            return "MEDIUM"
        else:
            return "LOW"
    
    def recommend_front_resources(self, front_name, points, fire):
        """Recommend specific resources for each fire front"""
        resources = []
        avg_threat = sum(p["threat_level"]["level"] for p in points) / len(points)
        
        if front_name == "head_fire":
            resources.extend(["Heavy-Duty Fire Engine", "Rapid Intervention Vehicle", "Aerial Support"])
            if avg_threat > 80:
                resources.append("Emergency Evacuation Team")
        elif front_name == "flanking_fires":
            resources.extend(["4x4 Wildland Vehicle", "Ground Crew"])
            if avg_threat > 70:
                resources.append("Additional Fire Engine")
        elif front_name == "backing_fire":
            resources.extend(["Ground Crew", "Monitoring Team"])
        
        # Add specialized resources based on nearby critical areas
        critical_nearby = any(p["threat_level"]["distance_to_critical"] < 1.0 for p in points)
        if critical_nearby:
            resources.extend(["Structure Protection Unit", "Evacuation Coordinator"])
        
        return resources
    
    def assess_front_threats(self, points, fire):
        """Assess specific threats for a fire front"""
        threats = []
        
        for point in points:
            threat_info = point["threat_level"]
            if threat_info["nearest_critical"] and threat_info["distance_to_critical"] < 2.0:
                threats.append({
                    "type": threat_info["nearest_critical"]["name"],
                    "category": self.get_area_category(threat_info["nearest_critical"]),
                    "distance": threat_info["distance_to_critical"],
                    "priority": threat_info["nearest_critical"]["priority"]
                })
        
        return threats
    
    def get_area_category(self, area):
        """Get the category of a critical area"""
        for category, areas in self.critical_areas.items():
            if area in areas:
                return category
        return "unknown"
    
    def assess_critical_area_threats(self, fire, fire_fronts):
        """Assess threats to all critical areas from different fire fronts"""
        threats = {}
        
        for category, areas in self.critical_areas.items():
            threats[category] = []
            
            for area in areas:
                area_threat = self.calculate_area_threat(area, fire, fire_fronts)
                if area_threat["threat_level"] > 0:
                    threats[category].append(area_threat)
        
        return threats
    
    def calculate_area_threat(self, area, fire, fire_fronts):
        """Calculate threat level to a specific critical area"""
        min_distance = float('inf')
        threatening_front = None
        
        # Check distance to each fire front
        for front_name, front_data in fire_fronts.items():
            if front_name == "spot_fires":
                for spot in front_data:
                    distance = self.calculate_distance(area["lat"], area["lon"], spot["lat"], spot["lon"])
                    if distance < min_distance:
                        min_distance = distance
                        threatening_front = f"spot_fire"
            elif isinstance(front_data, dict) and "points" in front_data:
                for point in front_data["points"]:
                    distance = self.calculate_distance(area["lat"], area["lon"], point["lat"], point["lon"])
                    if distance < min_distance:
                        min_distance = distance
                        threatening_front = front_name
        
        # Calculate threat level based on distance and area priority
        threat_level = 0
        if min_distance < area["radius"]:
            threat_level = 100  # Critical - fire within area
        elif min_distance < area["radius"] * 2:
            threat_level = 80   # High - fire very close
        elif min_distance < area["radius"] * 4:
            threat_level = 50   # Medium - fire approaching
        elif min_distance < area["radius"] * 8:
            threat_level = 20   # Low - fire in region
        
        # Adjust based on area priority
        priority_multipliers = {"CRITICAL": 1.5, "HIGH": 1.2, "MEDIUM": 1.0}
        threat_level *= priority_multipliers.get(area["priority"], 1.0)
        threat_level = min(100, threat_level)
        
        return {
            "area_name": area["name"],
            "category": self.get_area_category(area),
            "threat_level": threat_level,
            "distance": min_distance,
            "threatening_front": threatening_front,
            "priority": area["priority"],
            "recommended_action": self.recommend_area_protection(area, threat_level, min_distance)
        }
    
    def recommend_area_protection(self, area, threat_level, distance):
        """Recommend protection actions for a threatened area"""
        if threat_level >= 80:
            return f"IMMEDIATE EVACUATION and structure protection for {area['name']}"
        elif threat_level >= 50:
            return f"Deploy structure protection teams to {area['name']}, prepare evacuation"
        elif threat_level >= 20:
            return f"Monitor {area['name']}, position resources for rapid response"
        else:
            return f"Continue monitoring {area['name']}"
    
    def recommend_priority_deployment(self, fire, fire_fronts, critical_threats, sorted_stations):
        """Recommend strategic deployment based on multi-front analysis"""
        deployments = []
        
        # Sort fronts by priority
        front_priorities = []
        for front_name, front_data in fire_fronts.items():
            if isinstance(front_data, dict) and "priority" in front_data:
                front_priorities.append((front_name, front_data))
        
        # Sort by priority (HEAD > HIGH > MEDIUM > LOW)
        priority_order = {"HEAD": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        front_priorities.sort(key=lambda x: priority_order.get(x[1]["priority"], 4))
        
        station_idx = 0
        for front_name, front_data in front_priorities:
            if station_idx < len(sorted_stations):
                station_id = sorted_stations[station_idx][0]
                station = self.fire_stations[station_id]
                
                deployment = {
                    "front": front_name,
                    "priority": front_data["priority"],
                    "station": station["name"],
                    "resources": front_data["recommended_resources"],
                    "threat_assessment": front_data.get("threat_assessment", []),
                    "tactical_approach": self.recommend_tactical_approach(front_name, front_data, fire)
                }
                deployments.append(deployment)
                station_idx += 1
        
        # Add critical area protection deployments
        for category, threats in critical_threats.items():
            for threat in threats:
                if threat["threat_level"] >= 50 and station_idx < len(sorted_stations):
                    station_id = sorted_stations[station_idx][0]
                    station = self.fire_stations[station_id]
                    
                    deployment = {
                        "front": f"protection_{threat['area_name']}",
                        "priority": "CRITICAL_PROTECTION",
                        "station": station["name"],
                        "resources": ["Structure Protection Unit", "Evacuation Team"],
                        "target": threat["area_name"],
                        "action": threat["recommended_action"]
                    }
                    deployments.append(deployment)
                    station_idx += 1
        
        return deployments
    
    def recommend_tactical_approach(self, front_name, front_data, fire):
        """Recommend tactical approach for each front"""
        if front_name == "head_fire":
            return "Direct attack on advancing front, establish firebreaks, aerial water drops"
        elif front_name == "flanking_fires":
            return "Parallel attack along flanks, prevent lateral spread"
        elif front_name == "backing_fire":
            return "Monitor and mop-up, prevent spot fire generation"
        else:
            return "Assess and contain based on local conditions"
    
    def calculate_fire_shape(self, fire):
        """Calculate realistic non-circular fire shape based on environmental factors"""
        wind_direction = fire["wind_direction"]
        wind_speed = fire["wind_speed"] 
        shape_factor = fire["shape_factor"]
        
        # Calculate elliptical fire shape
        # Major axis in wind direction, minor axis perpendicular
        wind_effect = 1.0 + (wind_speed / 30.0)  # 30 km/h max wind for calculation
        
        # Calculate fire perimeter points for irregular shape
        shape_points = []
        for angle in range(0, 360, 30):  # 12 points around perimeter
            # Base radius from fire size
            base_radius = math.sqrt(fire["size"] / math.pi) * 1000  # meters
            
            # Apply wind stretching
            angle_from_wind = abs(angle - wind_direction)
            if angle_from_wind > 180:
                angle_from_wind = 360 - angle_from_wind
            
            # Stretch in wind direction, compress against wind
            if angle_from_wind < 90:  # Downwind side
                radius_factor = wind_effect * (1.0 + 0.5 * (90 - angle_from_wind) / 90)
            else:  # Upwind side
                radius_factor = 1.0 / wind_effect * (0.5 + 0.5 * (angle_from_wind - 90) / 90)
            
            # Apply shape factor and random variation for irregularity
            radius_factor *= shape_factor * (0.8 + random.random() * 0.4)
            
            # Calculate point coordinates
            point_radius = base_radius * radius_factor
            lat_offset = point_radius * math.cos(math.radians(angle)) / 111000  # degrees
            lon_offset = point_radius * math.sin(math.radians(angle)) / (111000 * math.cos(math.radians(fire["lat"])))
            
            shape_points.append({
                'lat': fire["lat"] + lat_offset,
                'lon': fire["lon"] + lon_offset
            })
        
        return shape_points
    
    def generate_spot_fires(self, fire):
        """Generate spot fires from ember transport"""
        spot_fires = []
        
        # Probability of spot fires based on wind and intensity
        spot_probability = (fire["wind_speed"] / 30.0) * (fire["intensity"] / 100.0) * 0.3
        
        if random.random() < spot_probability:
            # Generate 1-3 spot fires
            num_spots = random.randint(1, 3)
            
            for _ in range(num_spots):
                # Spot fires generally occur downwind
                wind_rad = math.radians(fire["wind_direction"])
                
                # Distance based on wind speed and fire intensity (100m to 2km)
                max_distance = min(2000, 100 + fire["wind_speed"] * 30 + fire["intensity"] * 10)
                distance = random.uniform(100, max_distance)
                
                # Add some randomness to direction (±45 degrees from wind direction)
                direction_variance = random.uniform(-45, 45)
                spot_direction = fire["wind_direction"] + direction_variance
                
                # Calculate spot fire location
                lat_offset = distance * math.cos(math.radians(spot_direction)) / 111000
                lon_offset = distance * math.sin(math.radians(spot_direction)) / (111000 * math.cos(math.radians(fire["lat"])))
                
                spot_fires.append({
                    'lat': fire["lat"] + lat_offset,
                    'lon': fire["lon"] + lon_offset,
                    'size': random.uniform(0.001, 0.01),  # Very small initially
                    'intensity': random.randint(10, 30)
                })
        
        return spot_fires
    
    def start_fire(self, lat, lon, initial_intensity=None, weather_factor=1.0):
        """Start a new fire at clicked coordinates with realistic parameters"""
        fire_id = f"fire_{len(self.active_fires) + 1}_{int(time.time())}"
        
        terrain = self.get_terrain_type(lat, lon)
        
        # Realistic initial conditions
        if initial_intensity is None:
            # Random initial intensity based on ignition source
            ignition_types = {
                'small': (10, 30),   # Cigarette, small campfire
                'medium': (30, 60),  # Lightning, electrical
                'large': (60, 90)    # Arson, industrial accident
            }
            ignition_type = random.choice(['small', 'medium', 'large'])
            min_int, max_int = ignition_types[ignition_type]
            initial_intensity = random.randint(min_int, max_int)
        
        initial_size = 0.01 + (random.random() * 0.09)  # 0.01 to 0.1 hectares
        
        fire_data = {
            "id": fire_id,
            "lat": lat,
            "lon": lon,
            "start_time": datetime.now(),
            "last_update": datetime.now(),
            "intensity": initial_intensity,
            "size": initial_size,
            "perimeter": math.sqrt(initial_size) * 112,  # Approximate perimeter in meters
            "growth_rate": self.calculate_growth_rate(terrain, weather_factor, initial_size),
            "terrain": terrain,
            "weather_factor": weather_factor,
            "status": "active",
            "suppression_progress": 0.0,
            "suppression_start_time": None,
            "wind_direction": random.randint(0, 360),  # degrees
            "wind_speed": 5 + random.random() * 25,  # km/h (5-30 km/h)
            "shape_factor": random.uniform(0.6, 1.2),  # elliptical ratio
            "spread_vectors": self.calculate_spread_vectors(),  # directional spread
            "spot_fires": [],  # secondary fires from embers
            "fuel_moisture": 0.1 + random.random() * 0.3,  # 10-40%
            "slope_factor": 1.0 + (random.random() * 0.5),  # terrain slope effect
            "containment_percentage": 0.0,
            "resources_deployed": [],
            "next_recommendation_time": datetime.now() + timedelta(minutes=2)
        }
        
        self.active_fires[fire_id] = fire_data
        self.fire_history.append(fire_data.copy())
        
        # Immediate AI analysis and recommendations
        recommendations = self.analyze_fire_and_recommend_response(fire_id)
        
        return {
            "fire_id": fire_id,
            "fire_data": fire_data,
            "recommendations": recommendations
        }
    
    def calculate_growth_rate(self, terrain, weather_factor, fire_size=0.1):
        """Calculate realistic fire growth rate based on multiple factors"""
        # Base spread rates (hectares per hour) for much faster fire growth
        terrain_rates = {
            "road": 2.0,    # Low fuel load, but still spreads fast
            "rough": 15.0,  # High fuel load, very difficult access - very fast
            "coast": 8.0,   # Moderate fuel, windy conditions - fast
            "water": 0.5    # Minimal spread near water but not negligible
        }
        
        base_rate = terrain_rates.get(terrain, 1.0)
        
        # Environmental factors
        wind_factor = 1.0 + (random.random() * 0.8)  # 1.0 to 1.8 (calm to windy)
        humidity = 0.3 + (random.random() * 0.4)     # 30% to 70% humidity
        temperature = 15 + (random.random() * 25)     # 15°C to 40°C
        
        # Calculate realistic growth rate
        environmental_multiplier = (
            wind_factor * 
            (2.0 - humidity) *  # Lower humidity = faster spread
            (temperature / 25)  # Higher temp = faster spread
        )
        
        # Fire size affects spread rate (larger fires spread faster)
        size_multiplier = 1.0 + (fire_size / 10)  # Larger fires create their own weather
        
        # Time of day factor (fires spread faster in afternoon heat)
        import datetime
        current_hour = datetime.datetime.now().hour
        time_factor = 1.0
        if 12 <= current_hour <= 16:  # Peak fire weather
            time_factor = 1.4
        elif 6 <= current_hour <= 11 or 17 <= current_hour <= 20:  # Moderate
            time_factor = 1.1
        else:  # Night/early morning
            time_factor = 0.6
        
        final_rate = (
            base_rate * 
            environmental_multiplier * 
            size_multiplier * 
            time_factor * 
            weather_factor
        )
        
        return max(0.01, final_rate)  # Minimum growth rate
    
    def analyze_fire_and_recommend_response(self, fire_id):
        """AI-powered fire analysis and response recommendations"""
        fire = self.active_fires[fire_id]
        
        # Calculate distances to all stations
        station_distances = {}
        for station_id, station in self.fire_stations.items():
            distance = self.calculate_distance(
                fire["lat"], fire["lon"],
                station["lat"], station["lon"]
            )
            station_distances[station_id] = distance
        
        # Sort stations by distance and capability
        sorted_stations = sorted(
            station_distances.items(),
            key=lambda x: (x[1], -len(self.fire_stations[x[0]]["vehicles"]))
        )
        
        # Enhanced multi-front analysis
        fire_fronts = self.analyze_fire_fronts(fire)
        critical_threats = self.assess_critical_area_threats(fire, fire_fronts)
        
        recommendations = {
            "timestamp": datetime.now().isoformat(),
            "fire_assessment": self.assess_fire_threat(fire),
            "multi_front_analysis": fire_fronts,
            "critical_area_threats": critical_threats,
            "priority_deployment": self.recommend_priority_deployment(fire, fire_fronts, critical_threats, sorted_stations),
            "primary_response": self.recommend_primary_response(fire, sorted_stations),
            "vehicle_deployment": self.recommend_vehicle_deployment(fire, sorted_stations),
            "timeline": self.create_response_timeline(fire, sorted_stations),
            "risk_analysis": self.analyze_risks(fire),
            "resource_optimization": self.optimize_resources(fire, sorted_stations)
        }
        
        self.response_log.append({
            "fire_id": fire_id,
            "timestamp": datetime.now(),
            "recommendations": recommendations
        })
        
        return recommendations
    
    def assess_fire_threat(self, fire):
        """Assess fire threat level and characteristics"""
        threat_level = "LOW"
        
        if fire["intensity"] > 70:
            threat_level = "HIGH"
        elif fire["intensity"] > 40:
            threat_level = "MEDIUM"
        
        # Adjust based on terrain and growth potential
        if fire["terrain"] == "rough" and fire["growth_rate"] > 1.0:
            if threat_level == "LOW":
                threat_level = "MEDIUM"
            elif threat_level == "MEDIUM":
                threat_level = "HIGH"
        
        return {
            "level": threat_level,
            "intensity": fire["intensity"],
            "size_hectares": fire["size"],
            "growth_rate": fire["growth_rate"],
            "terrain": fire["terrain"],
            "projected_size_1h": fire["size"] + (fire["growth_rate"] * 60),
            "containment_difficulty": self.calculate_containment_difficulty(fire)
        }
    
    def calculate_containment_difficulty(self, fire):
        """Calculate how difficult the fire will be to contain"""
        difficulty_score = 0
        
        # Terrain difficulty
        terrain_scores = {"road": 1, "coast": 2, "rough": 4, "water": 0}
        difficulty_score += terrain_scores.get(fire["terrain"], 2)
        
        # Intensity factor
        difficulty_score += fire["intensity"] / 20
        
        # Growth rate factor
        difficulty_score += fire["growth_rate"] * 2
        
        if difficulty_score < 3:
            return "EASY"
        elif difficulty_score < 6:
            return "MODERATE"
        else:
            return "DIFFICULT"
    
    def recommend_primary_response(self, fire, sorted_stations):
        """Recommend primary responding station and strategy"""
        primary_station_id = sorted_stations[0][0]
        primary_station = self.fire_stations[primary_station_id]
        distance = sorted_stations[0][1]
        
        # Calculate response time
        response_time = primary_station["response_time_base"] + (distance / 10) * 2  # 2 min per 10km
        
        strategy = "STANDARD"
        if fire["intensity"] > 60:
            strategy = "AGGRESSIVE_ATTACK"
        elif fire["terrain"] == "rough":
            strategy = "PERIMETER_CONTROL"
        elif fire["terrain"] == "water" or fire["terrain"] == "coast":
            strategy = "WATER_ACCESS"
        
        return {
            "station": primary_station["name"],
            "station_id": primary_station_id,
            "distance_km": round(distance, 1),
            "estimated_response_time": round(response_time, 1),
            "strategy": strategy,
            "rationale": self.generate_strategy_rationale(fire, strategy, distance)
        }
    
    def generate_strategy_rationale(self, fire, strategy, distance):
        """Generate explanation for chosen strategy"""
        rationales = {
            "STANDARD": f"Standard response appropriate for {fire['terrain']} terrain with {fire['intensity']}% intensity",
            "AGGRESSIVE_ATTACK": f"High intensity fire ({fire['intensity']}%) requires immediate aggressive suppression",
            "PERIMETER_CONTROL": f"Rough terrain limits access - focus on containment and perimeter control",
            "WATER_ACCESS": f"Coastal/water location allows for water access operations"
        }
        
        base_rationale = rationales.get(strategy, "Standard response protocol")
        
        if distance > 15:
            base_rationale += f". Distance ({distance:.1f}km) may delay response - consider aerial support."
        
        return base_rationale
    
    def recommend_vehicle_deployment(self, fire, sorted_stations):
        """Recommend specific vehicles to deploy"""
        deployments = []
        
        # Check if stations are available
        if not sorted_stations:
            return [{
                "vehicle_type": "Emergency Response Unit",
                "priority": 1,
                "rationale": "No fire stations available - dispatch emergency response"
            }]
        
        # Primary response (closest station)
        primary_station_id = sorted_stations[0][0]
        primary_station = self.fire_stations[primary_station_id]
        
        # Select vehicles based on fire characteristics
        recommended_vehicles = []
        
        if fire["intensity"] > 60:
            # High intensity - need heavy suppression
            if "Heavy-Duty Fire Engine" in primary_station["vehicles"]:
                recommended_vehicles.append("Heavy-Duty Fire Engine")
            if "CAFS Unit" in primary_station["vehicles"]:
                recommended_vehicles.append("CAFS Unit")
        
        # Always include rapid response for early intervention
        if "Rapid Intervention Vehicle" in primary_station["vehicles"]:
            recommended_vehicles.insert(0, "Rapid Intervention Vehicle")
        
        # Terrain-specific vehicles
        if fire["terrain"] in ["rough"]:
            if "4x4 Wildland Vehicle" in primary_station["vehicles"]:
                recommended_vehicles.append("4x4 Wildland Vehicle")
        
        # Water supply for larger fires
        if fire["size"] > 1.0:  # More than 1 hectare
            if "Water Tanker" in primary_station["vehicles"]:
                recommended_vehicles.append("Water Tanker")
        
        # Command and control for complex incidents
        if fire["intensity"] > 50:
            if "Incident Command Vehicle" in primary_station["vehicles"]:
                recommended_vehicles.append("Incident Command Vehicle")
        
        for vehicle in recommended_vehicles[:3]:  # Limit to 3 vehicles per station
            deployments.append({
                "vehicle_type": vehicle,
                "station": primary_station["name"],
                "station_id": primary_station_id,
                "priority": len(deployments) + 1,
                "rationale": self.get_vehicle_rationale(vehicle, fire)
            })
        
        # Secondary response if fire is severe
        if fire["intensity"] > 70 and len(sorted_stations) > 1:
            secondary_station_id = sorted_stations[1][0]
            secondary_station = self.fire_stations[secondary_station_id]
            
            # Add backup heavy suppression
            backup_vehicles = ["Heavy-Duty Fire Engine", "Water Tanker", "4x4 Wildland Vehicle"]
            for vehicle in backup_vehicles:
                if vehicle in secondary_station["vehicles"] and len(deployments) < 5:
                    deployments.append({
                        "vehicle_type": vehicle,
                        "station": secondary_station["name"],
                        "station_id": secondary_station_id,
                        "priority": len(deployments) + 1,
                        "rationale": f"Secondary response - backup {vehicle.lower()}"
                    })
        
        return deployments
    
    def get_vehicle_rationale(self, vehicle, fire):
        """Get rationale for deploying specific vehicle type"""
        rationales = {
            "Rapid Intervention Vehicle": "First response for rapid intervention and assessment",
            "Heavy-Duty Fire Engine": f"Primary suppression for {fire['intensity']}% intensity fire",
            "4x4 Wildland Vehicle": f"Terrain access for {fire['terrain']} conditions",
            "Water Tanker": f"Water supply for extended operations on {fire['size']:.1f}ha fire",
            "CAFS Unit": f"Enhanced foam suppression for high-intensity fire",
            "Incident Command Vehicle": f"Command and coordination for complex incident",
            "Dive Vehicle": "Water access operations for coastal incidents"
        }
        return rationales.get(vehicle, f"Standard deployment of {vehicle}")
    
    def create_response_timeline(self, fire, sorted_stations):
        """Create detailed response timeline"""
        timeline = []
        
        # Immediate actions (0-5 minutes)
        timeline.append({
            "time_range": "0-2 minutes",
            "actions": [
                "Alert primary station and dispatch rapid response",
                "Notify incident commander",
                "Begin route calculation and traffic coordination"
            ]
        })
        
        # Initial response (5-15 minutes)
        primary_station = self.fire_stations[sorted_stations[0][0]]
        response_time = primary_station["response_time_base"] + (sorted_stations[0][1] / 10) * 2
        
        timeline.append({
            "time_range": f"2-{int(response_time)} minutes",
            "actions": [
                f"Units en route from {primary_station['name']}",
                "Aerial reconnaissance if available",
                "Establish water supply points",
                "Coordinate with local authorities"
            ]
        })
        
        # On-scene operations (15+ minutes)
        timeline.append({
            "time_range": f"{int(response_time)}+ minutes",
            "actions": [
                "Establish incident command post",
                "Begin direct fire suppression",
                "Set up perimeter control",
                "Monitor fire behavior and weather",
                "Deploy additional resources as needed"
            ]
        })
        
        return timeline
    
    def analyze_risks(self, fire):
        """Analyze risks and potential escalation factors"""
        risks = []
        
        # Spread risk
        if fire["growth_rate"] > 1.0:
            risks.append({
                "type": "RAPID_SPREAD",
                "severity": "HIGH" if fire["growth_rate"] > 2.0 else "MEDIUM",
                "description": f"Fire growth rate of {fire['growth_rate']:.1f} indicates rapid spread potential"
            })
        
        # Terrain risks
        if fire["terrain"] == "rough":
            risks.append({
                "type": "ACCESS_DIFFICULTY",
                "severity": "MEDIUM",
                "description": "Rough terrain may limit vehicle access and evacuation routes"
            })
        
        # Structural threat (simplified - based on coordinates)
        if -34.0 < fire["lat"] < -33.9 and 18.4 < fire["lon"] < 18.5:
            risks.append({
                "type": "STRUCTURAL_THREAT",
                "severity": "HIGH",
                "description": "Fire location near residential/commercial areas"
            })
        
        # Resource strain
        if fire["intensity"] > 70:
            risks.append({
                "type": "RESOURCE_STRAIN",
                "severity": "MEDIUM",
                "description": "High-intensity fire may require significant resource commitment"
            })
        
        return risks
    
    def optimize_resources(self, fire, sorted_stations):
        """Provide resource optimization recommendations"""
        optimization = {
            "cost_projection": self.calculate_response_cost(fire),
            "efficiency_score": self.calculate_efficiency_score(fire, sorted_stations),
            "recommendations": []
        }
        
        # Efficiency recommendations
        if sorted_stations[0][1] > 20:  # Distance > 20km
            optimization["recommendations"].append(
                "Consider aerial resources due to long ground response distance"
            )
        
        if fire["terrain"] == "rough":
            optimization["recommendations"].append(
                "Deploy 4x4 vehicles early to establish access routes"
            )
        
        if fire["growth_rate"] > 1.5:
            optimization["recommendations"].append(
                "Pre-position additional resources for rapid escalation scenario"
            )
        
        return optimization
    
    def calculate_response_cost(self, fire):
        """Calculate estimated response cost"""
        base_cost = 5000  # Base incident cost
        
        # Vehicle costs (estimated 2-hour deployment)
        vehicle_cost = len(self.recommend_vehicle_deployment(fire, [])) * 500 * 2
        
        # Intensity multiplier
        intensity_multiplier = 1 + (fire["intensity"] / 100)
        
        total_cost = (base_cost + vehicle_cost) * intensity_multiplier
        
        return {
            "estimated_total": round(total_cost),
            "breakdown": {
                "base_operations": base_cost,
                "vehicle_deployment": vehicle_cost,
                "intensity_factor": round(total_cost - base_cost - vehicle_cost)
            }
        }
    
    def calculate_efficiency_score(self, fire, sorted_stations):
        """Calculate response efficiency score"""
        score = 100
        
        # Distance penalty
        distance = sorted_stations[0][1] if sorted_stations else 10
        score -= min(distance * 2, 30)
        
        # Terrain difficulty
        terrain_penalties = {"road": 0, "coast": -5, "rough": -15, "water": -10}
        score += terrain_penalties.get(fire["terrain"], -5)
        
        # Intensity factor
        score -= max((fire["intensity"] - 50) * 0.5, 0)
        
        return max(score, 0)
    
    def update_fire_simulation(self):
        """Update all active fires with realistic growth and continuous monitoring"""
        current_time = datetime.now()
        
        for fire_id, fire in self.active_fires.items():
            if fire["status"] == "active":
                # Time elapsed since last update (in hours for realistic calculation)
                time_elapsed = (current_time - fire["last_update"]).total_seconds() / 3600
                
                if time_elapsed > 0:  # Only update if time has passed
                    # Realistic fire growth calculation
                    current_growth_rate = self.calculate_growth_rate(
                        fire["terrain"], 
                        fire["weather_factor"], 
                        fire["size"]
                    )
                    
                    # Update growth rate (weather changes over time)
                    fire["growth_rate"] = current_growth_rate
                    
                    # Calculate new size based on realistic spread
                    size_increase = current_growth_rate * time_elapsed
                    
                    # Suppression effect (if resources are deployed)
                    if fire["suppression_progress"] > 0:
                        suppression_rate = fire["suppression_progress"] / 100 * 0.5  # hectares/hour suppressed
                        size_increase -= suppression_rate * time_elapsed
                        size_increase = max(0, size_increase)  # Can't have negative growth
                    
                    # Apply size increase
                    fire["size"] += size_increase
                    fire["size"] = max(0.01, fire["size"])  # Minimum fire size
                    
                    # Update realistic fire shape and perimeter
                    fire_shape = self.calculate_fire_shape(fire)
                    fire["shape_points"] = fire_shape
                    
                    # Calculate irregular perimeter from shape points
                    perimeter = 0
                    for i in range(len(fire_shape)):
                        p1 = fire_shape[i]
                        p2 = fire_shape[(i + 1) % len(fire_shape)]
                        dist = self.calculate_distance(p1['lat'], p1['lon'], p2['lat'], p2['lon']) * 1000
                        perimeter += dist
                    fire["perimeter"] = perimeter
                    
                    # Generate potential spot fires from embers
                    if fire["intensity"] > 40 and random.random() < 0.1:  # 10% chance per update cycle
                        new_spots = self.generate_spot_fires(fire)
                        fire["spot_fires"].extend(new_spots)
                    
                    # Update intensity based on size, weather, and suppression
                    base_intensity = min(100, 20 + (fire["size"] * 15) + (fire["wind_speed"] * 2))
                    suppression_reduction = fire["suppression_progress"] * 0.8
                    fire["intensity"] = max(5, base_intensity - suppression_reduction)
                    
                    # Update containment percentage based on suppression efforts
                    if fire["suppression_progress"] > 0:
                        containment_increase = (fire["suppression_progress"] / 100) * time_elapsed * 20
                        fire["containment_percentage"] = min(100, fire["containment_percentage"] + containment_increase)
                    
                    # Check fire status transitions
                    if fire["containment_percentage"] >= 100:
                        fire["status"] = "extinguished"
                        fire["intensity"] = 0
                    elif fire["containment_percentage"] >= 75:
                        fire["status"] = "controlled"
                    elif fire["suppression_progress"] > 30 and fire["intensity"] < 30:
                        fire["status"] = "contained"
                    
                    # Update last update time
                    fire["last_update"] = current_time
                    
                    # Check if new recommendations are needed
                    if current_time >= fire["next_recommendation_time"]:
                        self.generate_updated_recommendations(fire_id)
                        # Schedule next recommendation (every 5-15 minutes depending on fire severity)
                        interval = 5 if fire["intensity"] > 60 else 10 if fire["intensity"] > 30 else 15
                        fire["next_recommendation_time"] = current_time + timedelta(minutes=interval)
    
    def generate_updated_recommendations(self, fire_id):
        """Generate updated recommendations based on current fire status"""
        fire = self.active_fires[fire_id]
        current_time = datetime.now()
        
        print(f"\n🔄 LIVE UPDATE - Fire {fire_id}")
        print(f"📊 Current Status: {fire['size']:.2f} ha, {fire['intensity']:.0f}% intensity, {fire['containment_percentage']:.0f}% contained")
        
        # Generate adaptive recommendations based on current state
        recommendations = []
        
        if fire["size"] > 5:
            recommendations.append("🚁 REQUEST: Aerial suppression resources needed")
        
        if fire["intensity"] > 70:
            recommendations.append("🚒 ESCALATE: Deploy additional heavy suppression units")
        
        if fire["containment_percentage"] < 25 and fire["size"] > 1:
            recommendations.append("🎯 TACTICAL: Establish firebreaks and control lines")
        
        if fire["containment_percentage"] > 50:
            recommendations.append("✅ MAINTAIN: Current suppression efforts showing success")
        
        if fire["size"] > 10:
            recommendations.append("⚠️ ALERT: Large fire protocol - consider evacuation zones")
        
        if not recommendations:
            recommendations.append("📋 MONITOR: Continue current operations")
        
        # Print live recommendations
        print("🎯 Updated Recommendations:")
        for rec in recommendations:
            print(f"   {rec}")
        
        # Log the update
        update_data = {
            "fire_id": fire_id,
            "timestamp": current_time,
            "update_type": "live_tracking",
            "fire_status": {
                "size_hectares": round(fire["size"], 2),
                "intensity": round(fire["intensity"]),
                "containment": round(fire["containment_percentage"]),
                "status": fire["status"]
            },
            "recommendations": recommendations
        }
        
        self.response_log.append(update_data)
        return update_data
    
    def generate_interactive_map(self):
        """Generate interactive HTML map with click-to-start fire capability"""
        html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Interactive Fire Response System - Table Mountain</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <style>
        body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
        #map {{ height: 70vh; width: 100%; }}
        #control-panel {{ padding: 20px; background: #f0f0f0; height: 30vh; overflow-y: auto; }}
        .fire-info {{ background: white; margin: 10px 0; padding: 15px; border-radius: 5px; 
                     border-left: 4px solid #ff4444; }}
        .recommendation {{ background: #e8f4ff; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        .vehicle-deployment {{ background: #fff2e8; padding: 8px; margin: 3px 0; border-radius: 3px; }}
        .status-active {{ border-left-color: #ff4444; }}
        .status-contained {{ border-left-color: #ffaa44; }}
        .status-extinguished {{ border-left-color: #44ff44; }}
        .click-instruction {{ background: #ffffcc; padding: 15px; margin: 10px 0; 
                             border-radius: 5px; text-align: center; font-weight: bold; }}
    </style>
</head>
<body>
    <div id="control-panel">
        <h2>🔥 Interactive Fire Response System</h2>
        <div class="click-instruction">
            Click anywhere on the map to start a fire and receive AI response recommendations!
        </div>
        <div id="fire-status">
            <p><em>No active fires. Click on the map to simulate a fire incident.</em></p>
        </div>
    </div>
    
    <div id="map"></div>
    
    <script>
        // Initialize map centered on Table Mountain
        var map = L.map('map').setView([-33.95, 18.43], 12);
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap contributors'
        }}).addTo(map);
        
        // Fire stations
        var fireStations = {json.dumps(self.fire_stations)};
        var activeFireMarkers = {{}};
        
        // Add fire stations to map
        Object.keys(fireStations).forEach(function(stationId) {{
            var station = fireStations[stationId];
            L.marker([station.lat, station.lon], {{
                icon: L.divIcon({{
                    className: 'fire-station-icon',
                    html: '🚒',
                    iconSize: [30, 30],
                    iconAnchor: [15, 15]
                }})
            }}).addTo(map).bindPopup('<b>' + station.name + '</b><br>Fire Station<br>Vehicles: ' + station.vehicles.length);
        }});
        
        // Click handler for starting fires
        map.on('click', function(e) {{
            var lat = e.latlng.lat;
            var lon = e.latlng.lng;
            
            // Start fire at clicked location
            startFire(lat, lon);
        }});
        
        function startFire(lat, lon) {{
            // Send request to Python backend (simplified - in real implementation)
            var fireData = simulateFireStart(lat, lon);
            
            // Add fire marker to map
            var fireMarker = L.circleMarker([lat, lon], {{
                color: 'red',
                fillColor: 'orange',
                fillOpacity: 0.7,
                radius: 10,
                weight: 3
            }}).addTo(map);
            
            activeFireMarkers[fireData.fire_id] = fireMarker;
            
            // Update control panel
            updateControlPanel(fireData);
            
            // Simulate fire growth
            simulateFireGrowth(fireData.fire_id, fireMarker);
        }}
        
        function simulateFireStart(lat, lon) {{
            // Simulate fire data (in real implementation, this would call Python backend)
            var fireId = 'fire_' + Date.now();
            var intensity = Math.floor(Math.random() * 60) + 30; // 30-90% intensity
            
            return {{
                fire_id: fireId,
                fire_data: {{
                    lat: lat,
                    lon: lon,
                    intensity: intensity,
                    size: 0.1,
                    terrain: getTerrainType(lat, lon),
                    status: 'active'
                }},
                recommendations: generateRecommendations(lat, lon, intensity)
            }};
        }}
        
        function getTerrainType(lat, lon) {{
            if (lat <= -34.355 && lon <= 18.425) return "coast";
            if (lat >= -34.345 && lon >= 18.445) return "water";
            if (lat > -34.355 && lat < -34.345 && lon > 18.425 && lon < 18.445) return "rough";
            return "road";
        }}
        
        function generateRecommendations(lat, lon, intensity) {{
            // Find closest fire station
            var closestStation = null;
            var minDistance = Infinity;
            
            Object.keys(fireStations).forEach(function(stationId) {{
                var station = fireStations[stationId];
                var distance = calculateDistance(lat, lon, station.lat, station.lon);
                if (distance < minDistance) {{
                    minDistance = distance;
                    closestStation = station;
                }}
            }});
            
            var responseTime = Math.round(closestStation.response_time_base + (minDistance / 10) * 2);
            var threatLevel = intensity > 70 ? "HIGH" : intensity > 40 ? "MEDIUM" : "LOW";
            
            return {{
                fire_assessment: {{
                    level: threatLevel,
                    intensity: intensity
                }},
                primary_response: {{
                    station: closestStation.name,
                    distance_km: Math.round(minDistance * 10) / 10,
                    estimated_response_time: responseTime
                }},
                vehicle_deployment: generateVehicleDeployment(intensity, closestStation),
                timeline: [
                    {{time_range: "0-2 minutes", actions: ["Alert and dispatch", "Route calculation"]}},
                    {{time_range: "2-" + responseTime + " minutes", actions: ["Units en route", "Establish command"]}},
                    {{time_range: responseTime + "+ minutes", actions: ["On-scene operations", "Fire suppression"]}}
                ]
            }};
        }}
        
        function generateVehicleDeployment(intensity, station) {{
            var vehicles = [];
            
            if (station.vehicles.includes("Rapid Intervention Vehicle")) {{
                vehicles.push({{vehicle_type: "Rapid Intervention Vehicle", priority: 1}});
            }}
            
            if (intensity > 60 && station.vehicles.includes("Heavy-Duty Fire Engine")) {{
                vehicles.push({{vehicle_type: "Heavy-Duty Fire Engine", priority: 2}});
            }}
            
            if (station.vehicles.includes("4x4 Wildland Vehicle")) {{
                vehicles.push({{vehicle_type: "4x4 Wildland Vehicle", priority: 3}});
            }}
            
            return vehicles.slice(0, 3); // Max 3 vehicles
        }}
        
        function calculateDistance(lat1, lon1, lat2, lon2) {{
            var R = 6371; // Earth's radius in km
            var dLat = (lat2 - lat1) * Math.PI / 180;
            var dLon = (lon2 - lon1) * Math.PI / 180;
            var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                    Math.sin(dLon/2) * Math.sin(dLon/2);
            var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
            return R * c;
        }}
        
        function updateFireShape(fireData, fireCenter) {{
            // Remove previous fire shape
            if (fireData.fireShape) {{
                map.removeLayer(fireData.fireShape);
            }}
            
            // Calculate realistic fire perimeter points
            var shapePoints = [];
            var baseRadius = Math.sqrt(fireData.size / Math.PI) * 200; // meters to pixels scale
            
            // Create irregular elliptical shape based on wind
            for (var angle = 0; angle < 360; angle += 20) {{
                var angleRad = angle * Math.PI / 180;
                var windRad = fireData.windDirection * Math.PI / 180;
                
                // Calculate distance from wind direction
                var angleFromWind = Math.abs(angle - fireData.windDirection);
                if (angleFromWind > 180) angleFromWind = 360 - angleFromWind;
                
                // Wind effect: stretch in wind direction, compress against wind
                var windEffect = 1.0 + (fireData.windSpeed / 30.0);
                var radiusFactor;
                
                if (angleFromWind < 90) {{ // Downwind side
                    radiusFactor = windEffect * (1.0 + 0.7 * (90 - angleFromWind) / 90);
                }} else {{ // Upwind side
                    radiusFactor = (1.0 / windEffect) * (0.4 + 0.6 * (angleFromWind - 90) / 90);
                }}
                
                // Add irregularity and shape factor
                radiusFactor *= fireData.shapeFactor * (0.7 + Math.random() * 0.6);
                
                var pointRadius = baseRadius * radiusFactor;
                var latOffset = pointRadius * Math.cos(angleRad) / 111000;
                var lonOffset = pointRadius * Math.sin(angleRad) / (111000 * Math.cos(fireCenter.lat * Math.PI / 180));
                
                shapePoints.push([fireCenter.lat + latOffset, fireCenter.lng + lonOffset]);
            }}
            
            // Create polygon for fire shape
            fireData.fireShape = L.polygon(shapePoints, {{
                color: '#ff4444',
                fillColor: fireData.intensity > 70 ? '#ff0000' : fireData.intensity > 40 ? '#ff6600' : '#ffaa00',
                fillOpacity: 0.6 + (fireData.intensity / 200),
                weight: 2
            }}).addTo(map);
            
            // Generate spot fires occasionally
            if (fireData.intensity > 50 && Math.random() < 0.15) {{ // 15% chance per update
                generateSpotFires(fireData, fireCenter);
            }}
            
            // Update spot fires
            fireData.spotFires.forEach(function(spot) {{
                if (!spot.marker) {{
                    spot.marker = L.circle([spot.lat, spot.lon], {{
                        radius: 30 + spot.size * 100,
                        color: '#ff8800',
                        fillColor: '#ffaa00',
                        fillOpacity: 0.7
                    }}).addTo(map);
                }} else {{
                    // Grow spot fires
                    spot.size += 0.01;
                    spot.marker.setRadius(30 + spot.size * 100);
                }}
            }});
        }}
        
        function generateSpotFires(fireData, fireCenter) {{
            // Generate 1-2 spot fires from ember transport
            var numSpots = Math.random() < 0.7 ? 1 : 2;
            
            for (var i = 0; i < numSpots; i++) {{
                // Spot fires generally occur downwind
                var maxDistance = Math.min(1000, 200 + fireData.windSpeed * 20 + fireData.intensity * 8); // meters
                var distance = 150 + Math.random() * maxDistance;
                
                // Direction: mostly downwind with some variance
                var directionVariance = Math.random() * 90 - 45; // ±45 degrees
                var spotDirection = fireData.windDirection + directionVariance;
                
                var latOffset = distance * Math.cos(spotDirection * Math.PI / 180) / 111000;
                var lonOffset = distance * Math.sin(spotDirection * Math.PI / 180) / (111000 * Math.cos(fireCenter.lat * Math.PI / 180));
                
                fireData.spotFires.push({{
                    lat: fireCenter.lat + latOffset,
                    lon: fireCenter.lng + lonOffset,
                    size: Math.random() * 0.02,  // Small initial size
                    marker: null
                }});
            }}
        }}
        
        function updateControlPanel(fireData) {{
            var statusDiv = document.getElementById('fire-status');
            var fire = fireData.fire_data;
            var rec = fireData.recommendations;
            
            var html = '<div class="fire-info status-' + fire.status + '">';
            html += '<h3>🔥 Multi-Front Fire Analysis: ' + fireData.fire_id + '</h3>';
            html += '<p><strong>Location:</strong> ' + fire.lat.toFixed(4) + ', ' + fire.lon.toFixed(4) + '</p>';
            html += '<p><strong>Threat Level:</strong> ' + rec.fire_assessment.level + ' (' + fire.intensity + '% intensity)</p>';
            html += '<p><strong>Wind:</strong> ' + (fire.wind_speed || 'Unknown') + ' km/h from ' + (fire.wind_direction || 'N/A') + '°</p>';
            html += '<p><strong>Terrain:</strong> ' + fire.terrain + '</p>';
            
            // Multi-front analysis display
            if (rec.multi_front_analysis) {{
                html += '<div class="multi-front-analysis">';
                html += '<h4>🎯 Fire Front Analysis</h4>';
                
                // Priority deployment
                if (rec.priority_deployment && rec.priority_deployment.length > 0) {{
                    html += '<div class="priority-deployment">';
                    html += '<h5>⚡ Priority Deployments</h5>';
                    rec.priority_deployment.forEach(function(deployment) {{
                        var priorityColor = deployment.priority === 'HEAD' ? '#ff0000' : 
                                          deployment.priority === 'HIGH' ? '#ff6600' : 
                                          deployment.priority === 'CRITICAL_PROTECTION' ? '#cc0000' : '#ffaa00';
                        html += '<div style="border-left: 4px solid ' + priorityColor + '; padding: 8px; margin: 5px 0; background: #f9f9f9;">';
                        html += '<strong>' + deployment.priority + ' PRIORITY:</strong> ' + (deployment.front || 'Protection') + '<br>';
                        html += '<strong>Station:</strong> ' + deployment.station + '<br>';
                        if (deployment.target) {{
                            html += '<strong>Target:</strong> ' + deployment.target + '<br>';
                        }}
                        if (deployment.tactical_approach) {{
                            html += '<strong>Tactic:</strong> ' + deployment.tactical_approach + '<br>';
                        }}
                        if (deployment.action) {{
                            html += '<strong>Action:</strong> ' + deployment.action + '<br>';
                        }}
                        html += '<strong>Resources:</strong> ' + deployment.resources.join(', ');
                        html += '</div>';
                    }});
                    html += '</div>';
                }}
                
                // Critical area threats
                if (rec.critical_area_threats) {{
                    html += '<div class="critical-threats">';
                    html += '<h5>🏠 Critical Area Threats</h5>';
                    
                    Object.keys(rec.critical_area_threats).forEach(function(category) {{
                        var threats = rec.critical_area_threats[category];
                        if (threats && threats.length > 0) {{
                            html += '<div class="threat-category">';
                            html += '<strong>' + category.replace('_', ' ').toUpperCase() + ':</strong>';
                            threats.forEach(function(threat) {{
                                var threatColor = threat.threat_level >= 80 ? '#ff0000' : 
                                                threat.threat_level >= 50 ? '#ff6600' : '#ffaa00';
                                html += '<div style="margin: 3px 0; padding: 4px; background: ' + threatColor + '20; border: 1px solid ' + threatColor + ';">';
                                html += '<strong>' + threat.area_name + '</strong> - Threat: ' + Math.round(threat.threat_level) + '%<br>';
                                html += 'Distance: ' + threat.distance.toFixed(2) + ' km | Front: ' + (threat.threatening_front || 'Multiple') + '<br>';
                                html += '<em>' + threat.recommended_action + '</em>';
                                html += '</div>';
                            }});
                            html += '</div>';
                        }}
                    }});
                    html += '</div>';
                }}
                html += '</div>';
            }}
            
            html += '<div class="recommendation">';
            html += '<h4>🚨 Primary Response</h4>';
            html += '<p><strong>Station:</strong> ' + rec.primary_response.station + '</p>';
            html += '<p><strong>Distance:</strong> ' + rec.primary_response.distance_km + ' km</p>';
            html += '<p><strong>ETA:</strong> ' + rec.primary_response.estimated_response_time + ' minutes</p>';
            html += '</div>';
            
            html += '<div class="recommendation">';
            html += '<h4>🚒 Vehicle Deployment</h4>';
            rec.vehicle_deployment.forEach(function(vehicle) {{
                html += '<div class="vehicle-deployment">';
                html += '<strong>Priority ' + vehicle.priority + ':</strong> ' + vehicle.vehicle_type;
                html += '</div>';
            }});
            html += '</div>';
            
            html += '<div class="recommendation">';
            html += '<h4>⏱️ Response Timeline</h4>';
            rec.timeline.forEach(function(phase) {{
                html += '<p><strong>' + phase.time_range + ':</strong></p>';
                html += '<ul>';
                phase.actions.forEach(function(action) {{
                    html += '<li>' + action + '</li>';
                }});
                html += '</ul>';
            }});
            html += '</div>';
            
            html += '</div>';
            
            statusDiv.innerHTML = html;
        }}
        
        function simulateFireGrowth(fireId, marker) {{
            var fireData = {{
                size: 0.05 + Math.random() * 0.05,  // 0.05-0.1 hectares initial
                intensity: Math.floor(Math.random() * 60) + 20,
                growthRate: 3.0 + Math.random() * 4.0, // 3.0-7.0 hectares/hour (much faster)
                suppressionProgress: 0,
                status: 'active',
                startTime: new Date(),
                lastUpdate: new Date(),
                updateCount: 0,
                containment: 0,
                windDirection: Math.floor(Math.random() * 360),
                windSpeed: 5 + Math.random() * 25,  // 5-30 km/h
                shapeFactor: 0.6 + Math.random() * 0.6,  // 0.6-1.2 elliptical ratio
                fireShape: null,
                spotFires: []
            }};
            
            // Remove initial circular marker
            map.removeLayer(marker);
            
            var growthInterval = setInterval(function() {{
                if (fireData.status === 'extinguished') {{
                    clearInterval(growthInterval);
                    return;
                }}
                
                var currentTime = new Date();
                var minutesElapsed = (currentTime - fireData.startTime) / (1000 * 60);
                var timeElapsed = (currentTime - fireData.lastUpdate) / (1000 * 60 * 60); // hours
                
                // Much faster fire growth per update (scaled for visualization)
                var hourlyGrowth = fireData.growthRate * timeElapsed * 20; // 20x speed for fast demo
                
                // Environmental factors affecting growth
                var hour = currentTime.getHours();
                var timeOfDayFactor = 1.0;
                if (hour >= 12 && hour <= 16) timeOfDayFactor = 1.6; // Higher afternoon peak
                else if (hour >= 22 || hour <= 6) timeOfDayFactor = 0.7; // Night slowdown
                
                // Apply growth with environmental factors
                fireData.size += hourlyGrowth * timeOfDayFactor;
                
                // Update fire shape to be realistic (non-circular)
                updateFireShape(fireData, marker.getLatLng());
                
                // Suppression starts after realistic response time (3-8 minutes)
                if (minutesElapsed > (3 + Math.random() * 5)) {{
                    if (fireData.suppressionProgress === 0) {{
                        // First suppression units arrive
                        var statusDiv = document.getElementById('fire-status');
                        statusDiv.innerHTML += '<div style="background: #e3f2fd; padding: 8px; margin: 3px 0; border-radius: 3px;"><b>🚒 Suppression units arriving on scene!</b></div>';
                    }}
                    
                    // Realistic suppression progress (2-8% per update cycle)
                    var suppressionRate = 2 + Math.random() * 6;
                    fireData.suppressionProgress = Math.min(100, fireData.suppressionProgress + suppressionRate);
                    
                    // Suppression reduces growth rate
                    hourlyGrowth *= (1 - fireData.suppressionProgress / 150);
                    fireData.size += Math.max(0, hourlyGrowth);
                    
                    // Update containment
                    fireData.containment = Math.min(100, fireData.suppressionProgress * 0.8);
                }}
                
                // Update intensity based on size and suppression
                fireData.intensity = Math.max(5, 
                    30 + (fireData.size * 8) - (fireData.suppressionProgress * 0.6)
                );
                
                // Update fire shape color based on status and intensity
                if (fireData.fireShape) {{
                    var color = '#ff4444';
                    var fillColor = '#ff6600';
                    
                    if (fireData.containment > 75) {{
                        color = '#4444ff';
                        fillColor = '#88ccff';
                    }} else if (fireData.containment > 50) {{
                        color = '#ff8800';
                        fillColor = '#ffcc00';
                    }} else if (fireData.intensity > 70) {{
                        color = '#cc0000';
                        fillColor = '#ff0000';
                    }}
                    
                    var opacity = Math.min(fireData.intensity / 100, 0.8);
                    fireData.fireShape.setStyle({{
                        fillOpacity: 0.4 + (opacity * 0.4),
                        color: color,
                        fillColor: fillColor,
                        weight: fireData.size > 1 ? 3 : 2
                    }});
                }}
                
                // Update popup with comprehensive live data
                if (fireData.fireShape) {{
                    var popupContent = `
                        <div style="min-width: 250px;">
                            <b>🔥 Live Fire Incident</b><br>
                            <b>ID:</b> ${{fireId}}<br>
                            <b>Size:</b> ${{fireData.size.toFixed(3)}} hectares<br>
                            <b>Perimeter:</b> ${{Math.round(2 * Math.PI * Math.sqrt(fireData.size * 10000 / Math.PI))}}m<br>
                            <b>Intensity:</b> ${{Math.round(fireData.intensity)}}%<br>
                            <b>Growth Rate:</b> ${{fireData.growthRate.toFixed(1)}} ha/hr<br>
                            <b>Wind:</b> ${{Math.round(fireData.windSpeed)}} km/h @ ${{Math.round(fireData.windDirection)}}°<br>
                            <b>Shape Factor:</b> ${{fireData.shapeFactor.toFixed(2)}}<br>
                            <b>Spot Fires:</b> ${{fireData.spotFires.length}}<br>
                            <b>Suppression:</b> ${{Math.round(fireData.suppressionProgress)}}%<br>
                            <b>Containment:</b> ${{Math.round(fireData.containment)}}%<br>
                            <b>Status:</b> ${{fireData.status.toUpperCase()}}<br>
                            <b>Duration:</b> ${{Math.round(minutesElapsed)}} minutes<br>
                            <b>Time Factor:</b> ${{timeOfDayFactor.toFixed(1)}}x
                        </div>
                    `;
                    fireData.fireShape.setPopupContent(popupContent);
                }}
                
                // Generate updated recommendations every 2nd update (~10 seconds)
                fireData.updateCount++;
                if (fireData.updateCount % 2 === 0) {{
                    updateLiveRecommendations(fireId, fireData, minutesElapsed);
                }}
                
                // Status transitions
                if (fireData.containment >= 100) {{
                    fireData.status = 'extinguished';
                    
                    var statusDiv = document.getElementById('fire-status');
                    var extinguishedMsg = `
                        <div style="background: #e8f5e8; padding: 12px; margin: 5px 0; border-radius: 5px; border-left: 4px solid green;">
                            <b>✅ FIRE ${{fireId}} EXTINGUISHED</b><br>
                            <b>Final Size:</b> ${{fireData.size.toFixed(3)}} hectares<br>
                            <b>Duration:</b> ${{Math.round(minutesElapsed)}} minutes<br>
                            <b>Peak Intensity:</b> ${{Math.round(fireData.intensity)}}%<br>
                            <b>Resources:</b> Suppression successful
                        </div>
                    `;
                    statusDiv.innerHTML += extinguishedMsg;
                    statusDiv.scrollTop = statusDiv.scrollHeight;
                    
                    clearInterval(growthInterval);
                }} else if (fireData.containment >= 75) {{
                    fireData.status = 'controlled';
                }} else if (fireData.containment >= 50) {{
                    fireData.status = 'contained';
                }}
                
                fireData.lastUpdate = currentTime;
                
            }}, 5000); // Update every 5 seconds for realistic pacing
        }}
        
        function updateLiveRecommendations(fireId, fireData, minutesElapsed) {{
            var recommendations = [];
            
            // Size-based recommendations
            if (fireData.size > 2) {{
                recommendations.push('🚁 REQUEST: Aerial suppression resources');
            }}
            
            if (fireData.size > 5) {{
                recommendations.push('⚠️ MAJOR INCIDENT: Implement large fire protocols');
            }}
            
            // Intensity-based recommendations
            if (fireData.intensity > 80) {{
                recommendations.push('🚒 URGENT: Deploy all available heavy suppression units');
            }} else if (fireData.intensity > 60) {{
                recommendations.push('🚒 ESCALATE: Additional suppression resources needed');
            }}
            
            // Progress-based recommendations
            if (fireData.suppressionProgress > 0 && fireData.suppressionProgress < 30) {{
                recommendations.push('🎯 TACTICAL: Establish stronger perimeter control');
            }} else if (fireData.suppressionProgress >= 50) {{
                recommendations.push('✅ EFFECTIVE: Current suppression showing good progress');
            }}
            
            // Time-based recommendations
            if (minutesElapsed > 30 && fireData.containment < 25) {{
                recommendations.push('📞 COORDINATE: Request mutual aid from neighboring departments');
            }}
            
            // Environmental recommendations
            var hour = new Date().getHours();
            if ((hour >= 12 && hour <= 16) && fireData.size > 1) {{
                recommendations.push('🌡️ WEATHER ALERT: Peak fire weather conditions - expect increased activity');
            }}
            
            if (recommendations.length === 0) {{
                recommendations.push('📋 MONITOR: Maintain current suppression operations');
            }}
            
            // Display live update
            var statusDiv = document.getElementById('fire-status');
            var updateHtml = `
                <div style="background: linear-gradient(90deg, #fff3e0, #ffe0b2); padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #ff9800;">
                    <b>📊 LIVE UPDATE - Fire ${{fireId}}</b> <small>(${{Math.round(minutesElapsed)}} min)</small><br>
                    <div style="display: flex; justify-content: space-between; margin: 5px 0;">
                        <span><b>Size:</b> ${{fireData.size.toFixed(3)}} ha</span>
                        <span><b>Intensity:</b> ${{Math.round(fireData.intensity)}}%</span>
                        <span><b>Contained:</b> ${{Math.round(fireData.containment)}}%</span>
                    </div>
                    <div style="margin-top: 8px;">
                        <b>🎯 Live Priorities:</b><br>
                        ${{recommendations.map(r => `<div style="margin-left: 10px; font-size: 0.9em;">• ${{r}}</div>`).join('')}}
                    </div>
                </div>
            `;
            statusDiv.innerHTML += updateHtml;
            
            // Auto-scroll to latest updates
            statusDiv.scrollTop = statusDiv.scrollHeight;
        }}
    </script>
</body>
</html>
'''
        
        return html_content
    
    def run_interactive_system(self):
        """Run the interactive fire response system"""
        print("🔥 Starting Interactive Fire Response System...")
        
        # Generate interactive map
        map_html = self.generate_interactive_map()
        
        # Save to file
        map_file = Path("interactive_fire_response_map.html")
        map_file.write_text(map_html, encoding='utf-8')
        
        print(f"✅ Interactive map saved as: {map_file.name}")
        print(f"📍 Coverage area: Table Mountain National Park")
        print(f"🚒 Fire stations loaded: {len(self.fire_stations)}")
        print(f"🚛 Vehicle types available: {len(self.vehicle_fleet)}")
        
        # Open in browser
        try:
            webbrowser.open(f"file://{map_file.absolute()}")
            print(f"🌐 Opening interactive map in your default browser...")
        except Exception as e:
            print(f"❌ Could not open browser automatically: {e}")
            print(f"📂 Please manually open: {map_file.absolute()}")
        
        print("\n" + "="*60)
        print("🎯 INTERACTIVE FEATURES:")
        print("• Click anywhere on the map to start a fire")
        print("• Get instant AI response recommendations")
        print("• See optimal vehicle deployment strategies")
        print("• View real-time response timelines")
        print("• Monitor fire growth and suppression")
        print("="*60)
        
        return map_file

def main():
    """Main function to run the interactive fire response system"""
    print("🔥 INTERACTIVE FIRE INCIDENT RESPONSE SYSTEM")
    print("=" * 50)
    
    # Initialize system
    fire_system = InteractiveFireResponseSystem()
    
    # Run interactive system
    map_file = fire_system.run_interactive_system()
    
    print(f"\n✅ System ready! Interactive map available at:")
    print(f"   {map_file.absolute()}")
    print("\n🔥 Click on the map to simulate fire incidents and get AI recommendations!")
    
    # Keep system running for real-time updates and continuous monitoring
    try:
        print("\n⏱️  System running with live fire tracking... Press Ctrl+C to exit")
        print("🔄 Monitoring active fires and generating updated recommendations...")
        
        update_counter = 0
        while True:
            fire_system.update_fire_simulation()
            update_counter += 1
            
            # Print system status every 30 seconds
            if update_counter % 6 == 0:
                active_fires = len([f for f in fire_system.active_fires.values() if f["status"] == "active"])
                total_fires = len(fire_system.active_fires)
                print(f"\n📊 System Status: {active_fires} active fires, {total_fires} total incidents tracked")
                
                if active_fires > 0:
                    for fire_id, fire in fire_system.active_fires.items():
                        if fire["status"] == "active":
                            print(f"   🔥 {fire_id}: {fire['size']:.2f}ha, {fire['intensity']:.0f}% intensity")
            
            time.sleep(5)  # Update every 5 seconds for responsive tracking
            
    except KeyboardInterrupt:
        print("\n🛑 System shutdown requested")
        
        # Final summary
        if fire_system.active_fires:
            print("\n📋 Final Fire Summary:")
            for fire_id, fire in fire_system.active_fires.items():
                duration = (datetime.now() - fire["start_time"]).total_seconds() / 60
                print(f"   {fire_id}: {fire['status']}, {fire['size']:.2f}ha, {duration:.1f} minutes")
        
        print("✅ Interactive Fire Response System stopped")
        print(f"📊 Total incidents tracked: {len(fire_system.fire_history)}")
        print(f"📝 Recommendations generated: {len(fire_system.response_log)}")

if __name__ == "__main__":
    main()