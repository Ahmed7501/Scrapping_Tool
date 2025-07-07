#!/usr/bin/env python3
"""
Comprehensive error checking script for the email scraper
"""

import sys
import os
import importlib
import traceback

def check_imports():
    """Check if all required modules can be imported"""
    print("Checking imports...")
    print("=" * 40)
    
    required_modules = [
        'streamlit',
        'pandas',
        'aiohttp',
        'asyncio',
        'bs4',
        're',
        'tempfile',
        'os',
        'time',
        'docx',
        'io'
    ]
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
    
    print()

def check_scraper():
    """Check if the scraper can be imported and instantiated"""
    print("Checking scraper...")
    print("=" * 40)
    
    try:
        from email_scraper.scraper import EmailScraper
        print("✅ EmailScraper imported successfully")
        
        scraper = EmailScraper()
        print("✅ EmailScraper instantiated successfully")
        
        # Test email extraction
        test_text = "Contact us at test@example.com"
        emails = scraper.extract_emails(test_text)
        if emails:
            print(f"✅ Email extraction working: {emails}")
        else:
            print("❌ Email extraction not working")
            
    except Exception as e:
        print(f"❌ Scraper error: {e}")
        traceback.print_exc()
    
    print()

def check_app():
    """Check if the app can be imported"""
    print("Checking app...")
    print("=" * 40)
    
    try:
        # Add current directory to path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Try to import app components
        import streamlit as st
        print("✅ Streamlit imported")
        
        # Test if we can access the app file
        if os.path.exists('app.py'):
            print("✅ app.py exists")
        else:
            print("❌ app.py not found")
            
    except Exception as e:
        print(f"❌ App error: {e}")
        traceback.print_exc()
    
    print()

def check_files():
    """Check if all required files exist"""
    print("Checking files...")
    print("=" * 40)
    
    required_files = [
        'app.py',
        'requirements.txt',
        'email_scraper/scraper.py',
        'email_scraper/__init__.py',
        '.streamlit/config.toml'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
    
    print()

def check_dependencies():
    """Check if all dependencies are installed"""
    print("Checking dependencies...")
    print("=" * 40)
    
    try:
        import pkg_resources
        
        with open('requirements.txt', 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        for req in requirements:
            try:
                pkg_resources.require(req)
                print(f"✅ {req}")
            except pkg_resources.DistributionNotFound:
                print(f"❌ {req} - Not installed")
            except pkg_resources.VersionConflict as e:
                print(f"⚠️ {req} - Version conflict: {e}")
                
    except Exception as e:
        print(f"❌ Dependency check error: {e}")
    
    print()

if __name__ == "__main__":
    print("Email Scraper Error Check")
    print("=" * 50)
    
    check_files()
    check_imports()
    check_dependencies()
    check_scraper()
    check_app()
    
    print("Error check completed!") 