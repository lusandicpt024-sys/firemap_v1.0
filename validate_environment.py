#!/usr/bin/env python3
"""
Environment Validation Script
Tests that all required libraries and components are working properly
"""

import sys
import traceback

def test_imports():
    """Test all required library imports"""
    print("Testing library imports...")
    
    # Core libraries
    try:
        import pandas as pd
        print(f"  pandas {pd.__version__} - OK")
    except ImportError as e:
        print(f"  pandas - FAILED: {e}")
        return False
    
    try:
        import numpy as np
        print(f"  numpy {np.__version__} - OK")
    except ImportError as e:
        print(f"  numpy - FAILED: {e}")
        return False
    
    try:
        import folium
        print(f"  folium {folium.__version__} - OK")
    except ImportError as e:
        print(f"  folium - FAILED: {e}")
        return False
    
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        print(f"  matplotlib {matplotlib.__version__} - OK")
    except ImportError as e:
        print(f"  matplotlib - FAILED: {e}")
        return False
    
    # AI/ML libraries
    try:
        import torch
        print(f"  torch {torch.__version__} - OK")
    except ImportError as e:
        print(f"  torch - FAILED: {e}")
        return False
    
    # Geospatial libraries
    try:
        import osmium
        print(f"  osmium - OK")
    except ImportError as e:
        print(f"  osmium - FAILED: {e}")
        return False
    
    try:
        import branca
        print(f"  branca - OK")
    except ImportError as e:
        print(f"  branca - FAILED: {e}")
        return False
    
    # Standard library modules used in the project
    try:
        import json, csv, random, math
        from datetime import datetime, timedelta
        from collections import deque
        import os, sys, subprocess
        from pathlib import Path
        print("  Standard library modules - OK")
    except ImportError as e:
        print(f"  Standard library modules - FAILED: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality of key libraries"""
    print("\nTesting basic functionality...")
    
    try:
        # Test pandas
        import pandas as pd
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        assert len(df) == 3
        print("  pandas DataFrame creation - OK")
        
        # Test numpy
        import numpy as np
        arr = np.array([1, 2, 3])
        assert arr.sum() == 6
        print("  numpy array operations - OK")
        
        # Test folium map creation
        import folium
        m = folium.Map(location=[-33.9249, 18.4241], zoom_start=10)
        assert m is not None
        print("  folium map creation - OK")
        
        # Test torch tensor creation
        import torch
        tensor = torch.tensor([1.0, 2.0, 3.0])
        assert tensor.sum().item() == 6.0
        print("  torch tensor operations - OK")
        
        return True
    except Exception as e:
        print(f"  Basic functionality test - FAILED: {e}")
        traceback.print_exc()
        return False

def check_project_files():
    """Check that key project files exist"""
    print("\nChecking project files...")
    
    from pathlib import Path
    
    required_files = [
        "suppress_and_visualise_forest_fire_vehicles_Version3.py",
        "ai_fire_suppression_trainer.py", 
        "gis_enhanced_forest_fire_simulation.py",
        "create_osm_fire_visualisation.py",
        "run_all_simple.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
            print(f"  {file} - MISSING")
        else:
            print(f"  {file} - OK")
    
    return len(missing_files) == 0

def main():
    """Run all validation tests"""
    print("=== FireMap Project Environment Validation ===")
    print(f"Python version: {sys.version}")
    print()
    
    success = True
    
    # Test imports
    success &= test_imports()
    
    # Test functionality 
    success &= test_basic_functionality()
    
    # Check project files
    success &= check_project_files()
    
    print("\n" + "="*50)
    if success:
        print("SUCCESS: All components are working properly!")
        print("Your FireMap project environment is ready to use.")
        print("\nYou can now run:")
        print("  python run_all_simple.py")
    else:
        print("FAILURE: Some components need attention.")
        print("Please check the errors above and install missing dependencies.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)