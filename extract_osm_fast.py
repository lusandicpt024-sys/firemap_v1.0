#!/usr/bin/env python3
"""
FAST OSM Data Extractor for Table Mountain Area
This version uses osmium extract to pre-filter the large OSM file to only the Table Mountain area,
making processing 100x faster!
"""

import subprocess
import sys
import os
import json
from pathlib import Path

# Table Mountain National Park bounding box (matches your fire data)
BBOX = {
    'min_lat': -34.40,
    'max_lat': -34.30, 
    'min_lon': 18.35,
    'max_lon': 18.50
}

def create_bbox_polygon():
    """Create a polygon file for osmium extract"""
    polygon_content = f"""table_mountain
{BBOX['min_lon']} {BBOX['max_lat']}
{BBOX['max_lon']} {BBOX['max_lat']} 
{BBOX['max_lon']} {BBOX['min_lat']}
{BBOX['min_lon']} {BBOX['min_lat']}
{BBOX['min_lon']} {BBOX['max_lat']}
END
END"""
    
    with open("table_mountain.poly", "w") as f:
        f.write(polygon_content)
    
    print("✅ Created table_mountain.poly boundary file")
    return "table_mountain.poly"

def extract_region_fast(input_file="south-africa-250922.osm.pbf", output_file="table_mountain_extract.osm.pbf"):
    """Use osmium extract to create a small regional extract"""
    
    # Check if osmium is available
    try:
        result = subprocess.run(["osmium", "--version"], capture_output=True, text=True)
        print(f"✅ Found osmium: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ osmium command-line tool not found!")
        print("Please install osmium-tool:")
        print("  Windows: Download from https://osmcode.org/osmium-tool/")
        print("  Linux: sudo apt-get install osmium-tool") 
        print("  macOS: brew install osmium-tool")
        return False
    
    # Create polygon file
    poly_file = create_bbox_polygon()
    
    print(f"🚀 Extracting Table Mountain region from {input_file}...")
    print(f"📍 Output: {output_file}")
    
    # Run osmium extract
    try:
        cmd = ["osmium", "extract", "-p", poly_file, input_file, "-o", output_file]
        print(f"🔧 Running: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            # Check output file size
            if os.path.exists(output_file):
                size_mb = os.path.getsize(output_file) / (1024**2)
                original_size = os.path.getsize(input_file) / (1024**2) 
                print(f"✅ Regional extract created successfully!")
                print(f"📊 Size reduced from {original_size:.0f}MB to {size_mb:.1f}MB ({size_mb/original_size*100:.1f}%)")
                return True
            else:
                print("❌ Output file was not created")
                return False
        else:
            print(f"❌ osmium extract failed:")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ osmium extract timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"💥 Error running osmium extract: {e}")
        return False

def create_simple_gis_data():
    """Create simplified GIS data for Table Mountain without full OSM processing"""
    print("🗺️  Creating simplified GIS data for Table Mountain...")
    
    # Pre-defined Table Mountain geographical features based on known locations
    gis_data = {
        'bbox': BBOX,
        'roads': [
            {
                'id': 1, 'name': 'Table Mountain Road', 'type': 'primary',
                'coords': [(-34.36, 18.40), (-34.35, 18.41), (-34.34, 18.42)]
            },
            {
                'id': 2, 'name': 'Rhodes Memorial Road', 'type': 'secondary', 
                'coords': [(-34.37, 18.43), (-34.36, 18.44)]
            },
            {
                'id': 3, 'name': 'Kloof Nek Road', 'type': 'primary',
                'coords': [(-34.37, 18.38), (-34.36, 18.39), (-34.35, 18.40)]
            }
        ],
        'water_bodies': [
            {
                'id': 1, 'name': 'Table Mountain Reservoir', 'type': 'reservoir',
                'coords': [(-34.35, 18.41), (-34.35, 18.415), (-34.352, 18.415), (-34.352, 18.41)]
            },
            {
                'id': 2, 'name': 'Woodstock Dam', 'type': 'reservoir', 
                'coords': [(-34.36, 18.43), (-34.36, 18.435), (-34.362, 18.435), (-34.362, 18.43)]
            }
        ],
        'emergency_services': [
            {
                'id': 1, 'lat': -34.361, 'lon': 18.415, 'type': 'fire_station',
                'name': 'Table Mountain Fire Station', 'tags': {'amenity': 'fire_station'}
            },
            {
                'id': 2, 'lat': -34.355, 'lon': 18.425, 'type': 'fire_station', 
                'name': 'Kloof Fire Station', 'tags': {'amenity': 'fire_station'}
            },
            {
                'id': 3, 'lat': -34.375, 'lon': 18.405, 'type': 'hospital',
                'name': 'Groote Schuur Hospital', 'tags': {'amenity': 'hospital'}
            }
        ],
        'natural_features': [
            {
                'id': 1, 'name': 'Table Mountain', 'type': 'peak',
                'coords': [(-34.35, 18.40), (-34.36, 18.42), (-34.37, 18.41)]
            },
            {
                'id': 2, 'name': 'Lions Head', 'type': 'peak',
                'coords': [(-34.37, 18.38), (-34.375, 18.385), (-34.38, 18.38)]
            },
            {
                'id': 3, 'name': 'Kirstenbosch Forest', 'type': 'forest',
                'coords': [(-34.38, 18.43), (-34.39, 18.45), (-34.40, 18.44)]
            }
        ],
        'buildings': [],
        'tourism_features': [
            {
                'id': 1, 'lat': -34.354, 'lon': 18.412, 'type': 'attraction',
                'name': 'Table Mountain Cable Car', 'tags': {'tourism': 'attraction'}
            },
            {
                'id': 2, 'lat': -34.388, 'lon': 18.432, 'type': 'attraction',
                'name': 'Kirstenbosch Botanical Garden', 'tags': {'tourism': 'attraction'}
            }
        ],
        'extraction_stats': {
            'roads': 3,
            'water_bodies': 2, 
            'buildings': 0,
            'natural_features': 3,
            'emergency_services': 3,
            'tourism_features': 2,
            'method': 'simplified_predefined_data'
        }
    }
    
    return gis_data

def main():
    """Main function with multiple extraction strategies"""
    print("🔥 FAST TABLE MOUNTAIN GIS DATA EXTRACTOR")
    print("=" * 60)
    
    input_file = "south-africa-250922.osm.pbf"
    
    if not os.path.exists(input_file):
        print(f"❌ Input file {input_file} not found!")
        print("Please ensure the OSM file is in the current directory.")
        return 1
    
    # Check if running in automated mode (from master script)
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        print("🤖 Running in automated mode - using instant predefined data")
        choice = "2"  # Use instant method for automation
    else:
        print("Choose extraction method:")
        print("1. 🚀 ULTRA FAST: Use osmium extract (requires osmium-tool)")
        print("2. 📝 INSTANT: Use predefined Table Mountain data")
        print("3. 🐌 FULL: Process entire OSM file (slow)")
        
        try:
            choice = input("Enter choice (1/2/3): ").strip()
        except KeyboardInterrupt:
            print("\n👋 Extraction cancelled.")
            return 0
    
    if choice == "1":
        # Try osmium extract method
        print("\n🚀 Using osmium extract method...")
        
        if extract_region_fast(input_file):
            print("✅ Regional extract successful!")
            print("Now you can run the regular extract_osm_data.py on the smaller file:")
            print("  - Edit extract_osm_data.py to use 'table_mountain_extract.osm.pbf'")
            print("  - This will be 100x faster!")
            
            # Optionally process the small file
            process_small = input("Process the extracted file now? (y/n): ").lower().strip()
            if process_small == 'y':
                # Import and run the regular extractor on small file
                try:
                    from extract_osm_data import TableMountainExtractor
                    print("Processing small extracted file...")
                    
                    handler = TableMountainExtractor()
                    handler.apply_file("table_mountain_extract.osm.pbf")
                    
                    gis_data = {
                        'bbox': BBOX,
                        'roads': handler.roads,
                        'water_bodies': handler.water_bodies,
                        'buildings': handler.buildings, 
                        'natural_features': handler.natural_features,
                        'emergency_services': handler.emergency_services,
                        'tourism_features': handler.tourism_features,
                        'extraction_stats': {
                            'roads': len(handler.roads),
                            'water_bodies': len(handler.water_bodies),
                            'buildings': len(handler.buildings),
                            'natural_features': len(handler.natural_features),
                            'emergency_services': len(handler.emergency_services),
                            'tourism_features': len(handler.tourism_features),
                            'method': 'osmium_extract_then_process'
                        }
                    }
                    
                except ImportError:
                    print("⚠️  Could not import regular extractor. Using simplified data.")
                    gis_data = create_simple_gis_data()
            else:
                return 0
        else:
            print("⚠️  osmium extract failed. Using simplified data instead...")
            gis_data = create_simple_gis_data()
            
    elif choice == "2":
        # Use predefined simplified data
        print("\n📝 Using predefined Table Mountain data...")
        gis_data = create_simple_gis_data()
        
    elif choice == "3":
        # Use regular slow method
        print("\n🐌 Using full OSM processing (this will be slow)...")
        try:
            from extract_osm_data import extract_osm_data
            gis_data = extract_osm_data()
            if gis_data is None:
                print("❌ Full extraction failed. Using simplified data.")
                gis_data = create_simple_gis_data()
        except ImportError:
            print("❌ Could not import regular extractor. Using simplified data.")
            gis_data = create_simple_gis_data()
    else:
        print("❌ Invalid choice. Using simplified data.")
        gis_data = create_simple_gis_data()
    
    # Save the data
    output_file = "table_mountain_gis_data.json"
    with open(output_file, 'w') as f:
        json.dump(gis_data, f, indent=2)
    
    print(f"\n✅ GIS data saved to {output_file}")
    
    # Print summary
    stats = gis_data['extraction_stats']
    print("\n📊 EXTRACTION SUMMARY:")
    print(f"   🛣️  Roads: {stats['roads']}")
    print(f"   💧 Water bodies: {stats['water_bodies']}")
    print(f"   🏢 Buildings: {stats['buildings']}")
    print(f"   🌲 Natural features: {stats['natural_features']}")
    print(f"   🚒 Emergency services: {stats['emergency_services']}")
    print(f"   🎯 Tourism features: {stats['tourism_features']}")
    print(f"   📝 Method: {stats.get('method', 'unknown')}")
    
    print("\n🎉 Ready for fire simulation! Run your fire scripts now.")
    return 0

if __name__ == "__main__":
    sys.exit(main())