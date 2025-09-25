import pandas as pd
import folium
import matplotlib.pyplot as plt
import random
from math import hypot

# Define vehicle types and their properties
VEHICLE_TYPES = {
    "Heavy-Duty Fire Engine": {
        "count": 4, "capacity": 4000, "speed": 40, "effective_rate": 0.40,
        "terrain": ["road"], "range": 0.01  # ~1km radius
    },
    "4x4 Wildland Vehicle": {
        "count": 6, "capacity": 2000, "speed": 30, "effective_rate": 0.35,
        "terrain": ["road", "rough"], "range": 0.015
    },
    "Water Tanker": {
        "count": 2, "capacity": 10000, "speed": 30, "effective_rate": 0.20,
        "terrain": ["road"], "range": 0.02
    },
    "Rapid Intervention Vehicle": {
        "count": 3, "capacity": 750, "speed": 60, "effective_rate": 0.20,
        "terrain": ["road", "rough"], "range": 0.02
    },
    "Incident Command Vehicle": {
        "count": 1, "capacity": 0, "speed": 50, "effective_rate": 0,
        "terrain": ["road"], "range": 0.03
    },
    "Dive Vehicle": {
        "count": 2, "capacity": 0, "speed": 40, "effective_rate": 0.15,
        "terrain": ["water", "coast"], "range": 0.03
    },
    "CAFS Unit": {
        "count": 2, "capacity": 1200, "speed": 30, "effective_rate": 0.50,
        "terrain": ["road", "rough"], "range": 0.01
    },
}

# Load fire dataset
df = pd.read_csv("simulated_forest_fire_table_mountain.csv")

# Ensure numeric columns have proper dtypes to avoid pandas warnings
numeric_columns = ['Fire_Temperature', 'Rate_of_Spread', 'Fire_Present']
for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)

# Assign terrain based on supplied geography (Table Mountain National Park area)
# For demonstration, assign terrain based on location bounding boxes
def assign_terrain(lat, lon):
    # Coastal, water, rough, and road assignment based on latitude/longitude
    # These boundaries are approximate and can be refined with actual GIS data
    if lat <= -34.355 and lon <= 18.425:
        return "coast"  # Western edge
    elif lat >= -34.345 and lon >= 18.445:
        return "water"  # Eastern edge near reservoirs/dams
    elif (lat > -34.355 and lat < -34.345) and (lon > 18.425 and lon < 18.445):
        return "rough"  # Central mountainous
    else:
        return "road"   # All other accessible areas

df["Terrain"] = df.apply(lambda r: assign_terrain(r["Latitude"], r["Longitude"]), axis=1)

# Find all time steps
timesteps = sorted(df["Time"].unique())

# Fire suppression logic
SUPPRESSION_START_TIME = "2025-09-23T12:00:00Z"
suppressed = set()

def can_vehicle_reach(vehicle, terrain):
    return terrain in VEHICLE_TYPES[vehicle]["terrain"]

def get_distance(lat1, lon1, lat2, lon2):
    # Approximate Euclidean distance (degrees, for small area)
    return hypot(lat2 - lat1, lon2 - lon1)

# Vehicle bases (simulate bases at accessible points within area - could be refined)
VEHICLE_BASES = [
    (-34.355, 18.430),  # Central base near road
    (-34.345, 18.445),  # East base near water/road
    (-34.36, 18.42),    # West base near coast/road
]

for t_idx, t in enumerate(timesteps):
    if t >= SUPPRESSION_START_TIME:
        burning_cells = df[(df["Time"] == t) & (df["Fire_Present"] == 1)]
        # Track used vehicles per time step
        vehicle_used = {v: 0 for v in VEHICLE_TYPES}
        # For each burning cell, assign best vehicle available
        for i, cell in burning_cells.iterrows():
            assigned = False
            # Try all vehicle types
            for vtype, props in VEHICLE_TYPES.items():
                if vehicle_used[vtype] < props["count"] and can_vehicle_reach(vtype, cell["Terrain"]):
                    # Try all bases to find one within range
                    for base_lat, base_lon in VEHICLE_BASES:
                        distance = get_distance(base_lat, base_lon, cell["Latitude"], cell["Longitude"])
                        if distance <= props["range"]:
                            # Vehicle assigned from this base
                            vehicle_used[vtype] += 1
                            effective_rate = props["effective_rate"]
                            # Suppress fire: reduce temp/spread, extinguish probabilistically
                            df.at[i, "Fire_Temperature"] = float(df.at[i, "Fire_Temperature"] * (1 - effective_rate))
                            df.at[i, "Rate_of_Spread"] = float(df.at[i, "Rate_of_Spread"] * (1 - effective_rate))
                            extinguish_chance = effective_rate + (cell["Precipitation"] * 2)
                            if random.random() < extinguish_chance:
                                df.at[i, "Fire_Present"] = 0.0
                                df.at[i, "Fire_Temperature"] = 0.0
                                df.at[i, "Rate_of_Spread"] = 0.0
                                suppressed.add((cell["Latitude"], cell["Longitude"], t))
                            assigned = True
                            break
                    if assigned:
                        break
            # If no vehicle could reach, fire continues
            if not assigned:
                continue

# Save suppressed results
df.to_csv("simulated_forest_fire_table_mountain_suppressed_vehicles.csv", index=False)
print("Suppressed fire data saved as simulated_forest_fire_table_mountain_suppressed_vehicles.csv")

# Visualize the latest time step after suppression
latest_time = df["Time"].max()
df_latest = df[df["Time"] == latest_time]

# Folium map visualization
m = folium.Map(location=[df_latest["Latitude"].mean(), df_latest["Longitude"].mean()], zoom_start=13)
for _, row in df_latest.iterrows():
    if row["Fire_Present"]:
        color = "red"
    elif row["Fire_Temperature"] == 0 and row["Rate_of_Spread"] == 0:
        color = "blue"  # Extinguished by suppression
    else:
        color = "green" # Not burned
    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=6 if row["Fire_Present"] else 3,
        color=color,
        fill=True,
        fill_color=color,
        popup=(
            f"Temp: {row['Fire_Temperature']}°C\nSpread: {row['Rate_of_Spread']}m/h\n"
            f"Terrain: {row['Terrain']}"
        )
    ).add_to(m)
m.save("fire_suppression_vehicles_map.html")
print("Suppression map saved as fire_suppression_vehicles_map.html")

# Static scatter plot
plt.figure(figsize=(8, 7))
colors = []
for _, row in df_latest.iterrows():
    if row["Fire_Present"]:
        colors.append("red")
    elif row["Fire_Temperature"] == 0 and row["Rate_of_Spread"] == 0:
        colors.append("blue")
    else:
        colors.append("green")
plt.scatter(df_latest["Longitude"], df_latest["Latitude"], c=colors, s=50)
plt.title("Forest Fire Spread After Suppression (Vehicles) - Latest Time Step")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.show()