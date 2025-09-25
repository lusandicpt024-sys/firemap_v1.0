#!/usr/bin/env python3
"""
Robust FireMap Pipeline Runner
Handles all components gracefully with proper error handling and timeouts
"""

import subprocess
import sys
import os
from pathlib import Path
import time

def run_script_with_timeout(script_name, timeout=120):
    """Run a script with timeout and proper error handling"""
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        return False, f"Script {script_name} not found"
        
    print(f"\n[RUNNING] {script_name}")
    start_time = time.time()
    
    try:
        result = subprocess.run([
            "C:/Users/wtc/Downloads/python.exe", 
            str(script_path)
        ], capture_output=True, text=True, timeout=timeout, cwd=Path(__file__).parent)
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"[SUCCESS] {script_name} completed in {duration:.1f}s")
            return True, "Success"
        else:
            error_msg = result.stderr.strip()[:200] + "..." if len(result.stderr) > 200 else result.stderr.strip()
            print(f"[FAILED] {script_name} failed with code {result.returncode}")
            print(f"Error: {error_msg}")
            return False, f"Exit code {result.returncode}: {error_msg}"
            
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        print(f"[TIMEOUT] {script_name} exceeded {timeout}s timeout")
        return False, f"Timeout after {duration:.1f}s"
    except Exception as e:
        duration = time.time() - start_time
        print(f"[ERROR] Failed to run {script_name}: {e}")
        return False, str(e)

def main():
    """Run the complete FireMap pipeline"""
    print("=" * 60)
    print("🔥 FIREMAP v1.0 - COMPLETE PIPELINE")
    print("=" * 60)
    
    # Pipeline configuration
    # Format: (script_name, description, timeout, required)
    pipeline = [
        ("generate_forest_fire_data_Version2_precise.py", "Fire Data Generation", 60, True),
        ("gis_enhanced_forest_fire_simulation.py", "GIS Enhanced Simulation", 120, True), 
        ("create_osm_fire_visualisation.py", "OSM Fire Visualization", 180, False),
        ("suppress_and_visualise_forest_fire_vehicles_Version3.py", "Vehicle Suppression", 60, False),
        ("ai_fire_demo.py", "AI Fire Demo", 60, False),
    ]
    
    results = {}
    total = len(pipeline)
    successful = 0
    
    print(f"\nPipeline contains {total} components:")
    for script, desc, timeout, required in pipeline:
        status = "[EXISTS]" if Path(script).exists() else "[MISSING]"
        req_text = "[REQUIRED]" if required else "[OPTIONAL]"
        print(f"  {status} {req_text} {script} - {desc}")
    
    print(f"\n{'='*60}")
    print("EXECUTION PHASE")
    print('='*60)
    
    for i, (script, description, timeout, required) in enumerate(pipeline, 1):
        print(f"\n[{i}/{total}] {description}")
        
        success, message = run_script_with_timeout(script, timeout)
        results[script] = {'success': success, 'message': message, 'required': required}
        
        if success:
            successful += 1
        elif required:
            print(f"\n[CRITICAL] Required component {script} failed: {message}")
            print("Pipeline cannot continue without this component.")
            break
        else:
            print(f"[WARNING] Optional component failed, continuing...")
    
    # Final summary
    print(f"\n{'='*60}")
    print("PIPELINE SUMMARY")
    print('='*60)
    print(f"Completed: {successful}/{total} components")
    
    # Detailed results
    required_success = sum(1 for r in results.values() if r['success'] and r['required'])
    required_total = sum(1 for r in results.values() if r['required'])
    optional_success = sum(1 for r in results.values() if r['success'] and not r['required'])
    optional_total = sum(1 for r in results.values() if not r['required'])
    
    print(f"Required: {required_success}/{required_total}")
    print(f"Optional: {optional_success}/{optional_total}")
    
    print(f"\nComponent Status:")
    for script, result in results.items():
        status = "[OK]" if result['success'] else "[FAIL]"
        req = "[REQ]" if result['required'] else "[OPT]"
        print(f"  {status} {req} {script}")
    
    # Check output files
    print(f"\nGenerated Files:")
    output_files = [
        "simulated_forest_fire_table_mountain.csv",
        "gis_enhanced_fire_suppression.csv", 
        "fire_suppression_vehicles_map.html",
        "osm_integrated_fire_map.html"
    ]
    
    for file in output_files:
        if Path(file).exists():
            size = Path(file).stat().st_size
            print(f"  [YES] {file} ({size:,} bytes)")
        else:
            print(f"  [NO]  {file}")
    
    # Final status
    if required_success == required_total:
        print(f"\n🎉 SUCCESS! All required components completed successfully!")
        if optional_success > 0:
            print(f"Plus {optional_success} optional components also working.")
        print("Your FireMap system is fully operational!")
    else:
        print(f"\n⚠️ PARTIAL SUCCESS: {required_total - required_success} required components failed.")
        print("Some functionality may not be available.")
    
    return required_success == required_total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)