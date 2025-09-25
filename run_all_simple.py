#!/usr/bin/env python3
"""
Enhanced Forest Fire Simulation Suite - Clean Pipeline
Updated to use only current, working files with realistic fire truck capabilities.

🔥 FEATURES:
- Realistic fire truck ranges (50km operational radius)  
- Water capacities: 3,785-18,927 liters (1,000-5,000 gallons)
- Real Cape Town fire stations within bounds
- Enhanced AI fire suppression capabilities
- Precise land-only fire generation within specified coordinates

🎯 PIPELINE:
1. Generate precise fire coordinates (land-only, within bounds)
2. Run GIS simulation with real Cape Town fire stations  
3. Create interactive visualization with enhanced suppression
4. Vehicle deployment simulation with realistic capabilities
5. Optional AI training demonstration
"""

import subprocess
import sys
import os
from pathlib import Path

def run_script(script_name):
    """Run a single Python script with error handling"""
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        print(f"⚠️ {script_name} not found - skipping")
        return False
        
    print(f"🚀 Running {script_name}...")
    
    try:
        result = subprocess.run([sys.executable, str(script_path)], 
                              cwd=Path(__file__).parent,
                              check=True)
        print(f"✅ {script_name} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {script_name} failed with error code {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def show_current_files():
    """Show status of current working files"""
    print("� CURRENT PIPELINE FILES:")
    print("-" * 40)
    
    files = [
        "generate_forest_fire_data_Version2_precise.py",
        "gis_enhanced_forest_fire_simulation.py", 
        "create_osm_fire_visualisation.py",
        "suppress_and_visualise_forest_fire_vehicles_Version3.py",
        "ai_fire_demo.py"
    ]
    
    for file in files:
        status = "✅" if os.path.exists(file) else "❌"
        print(f"   {status} {file}")

def main():
    """Run the enhanced fire simulation pipeline"""
    print("🔥 ENHANCED TABLE MOUNTAIN FIRE SIMULATION SUITE")
    print("🎯 Realistic Capabilities | Precise Coordinates | Real Fire Stations")
    print("=" * 70)
    
    show_current_files()
    print()
    
    # Essential pipeline scripts
    scripts = [
        "generate_forest_fire_data_Version2_precise.py",  # Fire data generation
        "gis_enhanced_forest_fire_simulation.py",         # GIS simulation  
        "create_osm_fire_visualisation.py",               # OSM Visualization
        "suppress_and_visualise_forest_fire_vehicles_Version3.py", # Vehicle simulation
        "ai_fire_demo.py"  # AI demonstration (optional)
    ]
    
    successful = 0
    total = len(scripts)
    
    for i, script in enumerate(scripts, 1):
        print(f"\n[{i}/{total}] {script}")
        
        if run_script(script):
            successful += 1
        else:
            if i <= 3:  # Essential scripts
                print(f"💥 Stopping due to error in essential script: {script}")
                break
            else:  # Optional scripts
                print(f"⚠️ Optional script failed, continuing...")
    
    print("\n" + "=" * 70)
    print(f"📊 EXECUTION SUMMARY: {successful}/{total} scripts completed")
    
    if successful >= 3:  # At least essential scripts ran
        print("🎉 SIMULATION COMPLETE! Generated files:")
        print("   🗺️  gis_enhanced_fire_map.html - GIS-enhanced fire suppression map")
        print("   📊 gis_enhanced_fire_suppression.csv - Detailed simulation data")
        print("   🚁 fire_suppression_vehicles_map.html - Vehicle deployment visualization")
        print("   🌍 osm_integrated_fire_map.html - OSM-integrated fire map")
        if successful >= 5:
            print("   🤖 AI training demonstration results")
        print("\n💡 Open the HTML files in your web browser to view results!")
    else:
        print("⚠️ Essential scripts failed. Check error messages above.")
        print("💡 Run 'python cleanup_codebase.py' to clean outdated files")

if __name__ == "__main__":
    main()