#!/usr/bin/env python3
"""
Enhanced Forest Fire Simulation Suite - Clean Version
Updated to use only current, working files with realistic capabilities.

Current Working Pipeline:
1. Generate precise land-only fire coordinates
2. Run GIS simulation with real Cape Town fire stations  
3. Create interactive visualization
4. Enhanced vehicle suppression simulation
5. Optional AI training demonstration
"""

import subprocess
import sys
import os
from pathlib import Path

def run_script(script_name):
    """Run a single Python script"""
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        print(f"[WARN] {script_name} not found - skipping")
        return False
        
    print(f"[RUN] {script_name}...")
    
    try:
        result = subprocess.run([sys.executable, str(script_path)], 
                              cwd=Path(__file__).parent,
                              check=True,
                              capture_output=True,
                              text=True)
        print(f"[OK] {script_name} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {script_name} failed with error code {e.returncode}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"[ERROR] Error running {script_name}: {e}")
        return False

def show_current_files():
    """Show current working files status"""
    print("=== CURRENT WORKING FILES ===")
    print("=" * 50)
    
    working_files = {
        "generate_forest_fire_data_Version2_precise.py": "Fire data generation with precise bounds",
        "gis_enhanced_forest_fire_simulation.py": "GIS simulation with real fire stations", 
        "visualize_gis_enhanced_fire.py": "Interactive map visualization",
        "suppress_and_visualise_forest_fire_vehicles_Version3.py": "Vehicle suppression simulation",
        "ai_fire_suppression_trainer.py": "AI training system",
        "ai_fire_demo.py": "AI demonstration"
    }
    
    for file, description in working_files.items():
        if os.path.exists(file):
            print(f"[+] {file:<50} - {description}")
        else:
            print(f"[-] {file:<50} - MISSING")

def main():
    """Run the enhanced fire simulation suite"""
    print(">>> ENHANCED TABLE MOUNTAIN FIRE SIMULATION SUITE <<<")
    print(">>> Realistic Fire Truck Capabilities | Precise Cape Town Coordinates")  
    print(">>> 50km Range | 3,785-18,927L Capacity | Real Fire Stations")
    print("=" * 70)
    
    # Show current file status
    show_current_files()
    print()
    
    # Essential working scripts in execution order
    essential_scripts = [
        ("generate_forest_fire_data_Version2_precise.py", "Generating precise fire coordinates"),
        ("gis_enhanced_forest_fire_simulation.py", "Running GIS-enhanced simulation"),
        ("visualize_gis_enhanced_fire.py", "Creating interactive visualization")
    ]
    
    # Optional enhancement scripts  
    optional_scripts = [
        ("suppress_and_visualise_forest_fire_vehicles_Version3.py", "Enhanced vehicle simulation"),
        ("ai_fire_demo.py", "AI fire suppression demo")
    ]
    
    successful = 0
    total_essential = len(essential_scripts)
    
    # Run essential scripts
    print(">>> RUNNING ESSENTIAL SCRIPTS:")
    print("-" * 40)
    for i, (script, description) in enumerate(essential_scripts, 1):
        print(f"\n[{i}/{total_essential}] {description}")
        if run_script(script):
            successful += 1
        else:
            print(f"[STOP] Stopping due to error in {script}")
            break
    
    # Run optional scripts if essentials succeeded
    if successful == total_essential:
        print(f"\n>>> RUNNING OPTIONAL ENHANCEMENTS:")
        print("-" * 40)
        optional_success = 0
        for script, description in optional_scripts:
            print(f"\n[OPTIONAL] {description}")
            if run_script(script):
                optional_success += 1
        
        print(f"\n[INFO] Optional scripts: {optional_success}/{len(optional_scripts)} completed")
    
    # Final report
    print("\n" + "=" * 70)
    print(f"=== EXECUTION SUMMARY ===")
    print(f"Essential scripts: {successful}/{total_essential} ({'SUCCESS' if successful == total_essential else 'FAILED'})")
    
    if successful == total_essential:
        print("🎉 SIMULATION COMPLETE! Generated files:")
        print("   [MAP] gis_enhanced_fire_map.html - Interactive fire suppression map")
        print("   [DATA] gis_enhanced_fire_suppression.csv - Detailed simulation data")
        print("   [VEH] fire_suppression_vehicles_map.html - Vehicle deployment visualization")
        print("   📈 AI training results (if AI demo ran)")
        print("\n[TIP] Open the HTML files in your web browser to view the results!")
    else:
        print("[WARN] Essential scripts failed. Check error messages above.")
        print("[TIP] Ensure all required files exist and dependencies are installed.")

if __name__ == "__main__":
    main()