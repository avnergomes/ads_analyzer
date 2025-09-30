"""
Test script to verify installation and basic functionality
Run with: python test_installation.py
"""

import sys
import importlib.util

def check_import(package_name: str, display_name: str = None) -> bool:
    """Check if a package can be imported"""
    if display_name is None:
        display_name = package_name
    
    try:
        spec = importlib.util.find_spec(package_name)
        if spec is None:
            print(f"❌ {display_name} - NOT FOUND")
            return False
        
        # Try to actually import it
        importlib.import_module(package_name)
        print(f"✅ {display_name} - OK")
        return True
    except Exception as e:
        print(f"❌ {display_name} - ERROR: {e}")
        return False

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"\n🐍 Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("⚠️  Warning: Python 3.8+ is recommended")
        return False
    else:
        print("✅ Python version is compatible")
        return True

def test_basic_functionality():
    """Test basic data processing functionality"""
    print("\n🧪 Testing Basic Functionality...")
    
    try:
        import pandas as pd
        import numpy as np
        
        # Test DataFrame creation
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'impressions': [1000, 2000],
            'clicks': [50, 100],
            'spend': [10.5, 20.3]
        })
        
        # Test calculations
        df['ctr'] = (df['clicks'] / df['impressions']) * 100
        df['cpc'] = df['spend'] / df['clicks']
        
        assert len(df) == 2
        assert 'ctr' in df.columns
        assert 'cpc' in df.columns
        
        print("✅ Basic data processing works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_file_structure():
    """Check if required files exist"""
    print("\n📁 Checking File Structure...")
    
    import os
    
    required_files = [
        'app.py',
        'public_sheets_connector.py',
        'requirements.txt',
        'README.md',
    ]
    
    all_present = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            all_present = False
    
    return all_present

def main():
    """Main test function"""
    print("="*80)
    print("ADS ANALYZER v2.0 - INSTALLATION TEST")
    print("="*80)
    
    results = []
    
    # Check Python version
    results.append(check_python_version())
    
    # Check required packages
    print("\n📦 Checking Required Packages...")
    packages = [
        ('streamlit', 'Streamlit'),
        ('pandas', 'Pandas'),
        ('numpy', 'NumPy'),
        ('plotly', 'Plotly'),
        ('requests', 'Requests'),
        ('openpyxl', 'OpenPyXL'),
    ]
    
    for package, display_name in packages:
        results.append(check_import(package, display_name))
    
    # Check optional packages
    print("\n📦 Checking Optional Packages...")
    optional_packages = [
        ('statsmodels', 'Statsmodels'),
        ('scipy', 'SciPy'),
        ('sklearn', 'Scikit-learn'),
    ]
    
    for package, display_name in optional_packages:
        check_import(package, display_name)
    
    # Test basic functionality
    results.append(test_basic_functionality())
    
    # Check file structure
    results.append(test_file_structure())
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("\n🚀 You're ready to run the application!")
        print("   Run: streamlit run app.py")
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total} passed)")
        print("\n📝 Please fix the issues above before running the application.")
        print("   Install missing packages with: pip install -r requirements.txt")
    
    print("="*80 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
