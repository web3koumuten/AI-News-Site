#!/usr/bin/env python3
"""
Setup checker for AI Updates 72 scraper
Verifies all dependencies and configurations are correct
"""
import sys
import importlib
from pathlib import Path


def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False


def check_dependencies():
    """Check required dependencies"""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        'requests',
        'beautifulsoup4', 
        'feedparser',
        'pytz',
        'lxml'
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\n💡 Install missing packages with:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True


def check_files():
    """Check required files exist"""
    print("\n📁 Checking files...")
    
    script_dir = Path(__file__).parent
    
    required_files = [
        'config.py',
        'utils.py', 
        'main_scraper.py',
        'scrapers/__init__.py',
        'scrapers/base_scraper.py',
        'scrapers/itmedia_scraper.py',
        'scrapers/ascii_scraper.py',
        'scrapers/cnet_scraper.py',
        'scrapers/techcrunch_scraper.py',
        'scrapers/ai_scholar_scraper.py',
        'scrapers/ledge_ai_scraper.py'
    ]
    
    missing = []
    
    for file_path in required_files:
        full_path = script_dir / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (missing)")
            missing.append(file_path)
    
    return len(missing) == 0


def check_data_directory():
    """Check data directory exists"""
    print("\n📂 Checking data directory...")
    
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / 'data'
    
    if data_dir.exists():
        print(f"   ✅ {data_dir}")
        return True
    else:
        print(f"   ⚠️ {data_dir} (missing, will be created)")
        try:
            data_dir.mkdir(exist_ok=True)
            print(f"   ✅ Created {data_dir}")
            return True
        except Exception as e:
            print(f"   ❌ Failed to create {data_dir}: {e}")
            return False


def check_internet():
    """Check internet connectivity"""
    print("\n🌐 Checking internet connectivity...")
    
    try:
        import requests
        response = requests.get('https://httpbin.org/get', timeout=5)
        if response.status_code == 200:
            print("   ✅ Internet connection OK")
            return True
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False


def check_imports():
    """Check if all modules can be imported"""
    print("\n🔧 Checking module imports...")
    
    # Add scripts directory to path
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    
    modules_to_test = [
        'config',
        'utils',
        'scrapers',
        'main_scraper'
    ]
    
    all_good = True
    
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            print(f"   ✅ {module}")
        except Exception as e:
            print(f"   ❌ {module}: {e}")
            all_good = False
    
    return all_good


def main():
    """Run all checks"""
    print("=" * 50)
    print("AI Updates 72 Scraper - Setup Check")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Files", check_files),
        ("Data Directory", check_data_directory),
        ("Internet", check_internet),
        ("Module Imports", check_imports)
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ Error during {name} check: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Summary")
    print("=" * 50)
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n🎯 Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 Setup is ready! You can now run:")
        print("   python main_scraper.py")
        print("   python test_scrapers.py")
        print("   python example_usage.py")
    else:
        print("\n⚠️ Setup incomplete. Please fix the issues above.")
        return False
    
    print("=" * 50)
    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Setup check interrupted")
        sys.exit(1)