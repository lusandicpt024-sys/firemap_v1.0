#!/usr/bin/env python3
"""
Cleanup script to archive outdated files from the firemap project.
This moves old/redundant files to an archive folder to keep the codebase clean.
"""

import os
import shutil
from pathlib import Path

def main():
    """Archive outdated files"""
    print("🧹 FIREMAP CODEBASE CLEANUP")
    print("=" * 40)
    
    # Create archive directory
    archive_dir = Path("archive")
    archive_dir.mkdir(exist_ok=True)
    
    # Files to archive (outdated/redundant)
    files_to_archive = [
        "generate_forest_fire_data_Version2.py",  # Superseded by precise version
        "generate_forest_fire_data_Version2_fixed.py",  # Outdated version  
        "osm_integrated_fire_simulation_fixed_corrupted.py",  # Corrupted
        "osm_integrated_fire_simulation_fixed_backup.py",  # Backup not needed
        "extract_osm_data.py",  # Replaced by fast version
        "analyze_stations.py",  # Temporary analysis
        "analyze_real_stations.py",  # Temporary analysis
        "test_vehicles.py",  # Temporary test
        "run_all_scripts.py"  # Replaced by simplified version
    ]
    
    # Move files to archive
    moved = 0
    for file_name in files_to_archive:
        file_path = Path(file_name)
        if file_path.exists():
            archive_path = archive_dir / file_name
            try:
                shutil.move(str(file_path), str(archive_path))
                print(f"📦 Moved {file_name} to archive/")
                moved += 1
            except Exception as e:
                print(f"❌ Error moving {file_name}: {e}")
        else:
            print(f"✅ {file_name} - already clean")
    
    print(f"\n📊 Archived {moved} outdated files")
    
    # Show current clean structure
    print("\n📁 CURRENT WORKING FILES:")
    print("-" * 30)
    
    current_files = [
        "generate_forest_fire_data_Version2_precise.py",
        "gis_enhanced_forest_fire_simulation.py", 
        "visualize_gis_enhanced_fire.py",
        "suppress_and_visualise_forest_fire_vehicles_Version3.py",
        "ai_fire_suppression_trainer.py",
        "ai_fire_demo.py",
        "run_all_simple.py",
        "requirements.txt"
    ]
    
    for file_name in current_files:
        if Path(file_name).exists():
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name} - MISSING")
    
    print(f"\n🎯 Codebase cleanup complete!")
    print(f"📦 Archived files moved to: {archive_dir.absolute()}")

if __name__ == "__main__":
    main()