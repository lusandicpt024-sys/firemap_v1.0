#!/usr/bin/env python3
"""
Quick Component Test Script - Fast Testing with Short Timeouts
"""

import subprocess
import sys
from pathlib import Path

def quick_test_script(script_name, description, timeout=30):
    """Run a Python script with shorter timeout for quick testing"""
    print(f"\n{'='*50}")
    print(f"Testing: {description}")
    print(f"Script: {script_name}")
    print('='*50)
    
    if not Path(script_name).exists():
        print(f"[SKIP] {script_name} not found")
        return False
    
    try:
        python_exe = "C:/Users/wtc/Downloads/python.exe"
        result = subprocess.run([python_exe, script_name], 
                              capture_output=True, text=True, timeout=timeout)
        
        if result.returncode == 0:
            print(f"[SUCCESS] {script_name} completed successfully")
            return True
        else:
            print(f"[FAILED] {script_name} failed with error code {result.returncode}")
            if result.stderr.strip():
                # Show only first few lines of error
                error_lines = result.stderr.strip().split('\n')
                print("Error summary:", error_lines[-1] if error_lines else "Unknown error")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {script_name} exceeded {timeout}s timeout - but may still be working")
        return "timeout"
    except Exception as e:
        print(f"[ERROR] Failed to run {script_name}: {e}")
        return False

def main():
    print("[FIRE][TEST] QUICK COMPONENT TESTING")
    print("Testing with shorter timeouts for faster feedback...")
    
    components = [
        ("ai_fire_demo.py", "AI Fire Demo", 45),
        ("create_osm_fire_visualisation.py", "OSM Fire Visualization", 60),
        ("generate_forest_fire_data_Version2_precise.py", "Fire Data Generation", 30),
        ("suppress_and_visualise_forest_fire_vehicles_Version3.py", "Fire Suppression", 30),
    ]
    
    results = {}
    for script, description, timeout in components:
        results[script] = quick_test_script(script, description, timeout)
    
    print(f"\n{'='*50}")
    print("QUICK TEST SUMMARY")
    print('='*50)
    
    success_count = sum(1 for result in results.values() if result is True)
    timeout_count = sum(1 for result in results.values() if result == "timeout")
    fail_count = sum(1 for result in results.values() if result is False)
    
    print(f"[SUCCESS] Working: {success_count}")
    print(f"[TIMEOUT] May be working (timeout): {timeout_count}")
    print(f"[FAILED] Failed: {fail_count}")
    
    for script, result in results.items():
        status = "[OK]" if result is True else "[TIMEOUT]" if result == "timeout" else "[FAIL]"
        print(f"  {status} {script}")
    
    print(f"\n[INFO] Generated files:")
    files = [
        "fire_suppression_vehicles_map.html",
        "osm_integrated_fire_map.html", 
        "simulated_forest_fire_table_mountain.csv"
    ]
    
    for file in files:
        exists = "[YES]" if Path(file).exists() else "[NO]"
        print(f"  {exists} {file}")

if __name__ == "__main__":
    main()