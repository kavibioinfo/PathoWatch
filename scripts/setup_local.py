# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
PathoWatch Setup Script
Run this once to initialize the project on your system.
"""

import subprocess
import sys
from pathlib import Path

print("=" * 60)
print("   PATHOWATCH SETUP")
print("   Optimized for Intel i3-2310M + 9GB RAM")
print("=" * 60)

# Check Python version
print("\n  Checking Python version...")
version = sys.version_info
if version.major < 3 or (version.major == 3 and version.minor < 10):
    print("   ERROR: Python 3.10+ required.")
    sys.exit(1)
print(f"   Python {version.major}.{version.minor}.{version.micro}")

# Install dependencies
print("\nInstalling dependencies (this may take a few minutes)...")
try:
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    print(" Dependencies installed")
except subprocess.CalledProcessError:
    print("   Failed to install dependencies")
    sys.exit(1)

# Create data directories
print("\n Creating data directories...")
Path("data/raw").mkdir(parents=True, exist_ok=True)
Path("data/processed").mkdir(parents=True, exist_ok=True)
print("   Directories created")

# Fetch initial data
print("\nFetching initial data (lightweight API calls)...")
try:
    subprocess.run([sys.executable, "scripts/fetch_data.py"], check=True)
    print("   Initial data fetched")
except:
    print("   Some data sources may be unavailable. This is OK.")

# Process data
print("\nProcessing data...")
try:
    subprocess.run([sys.executable, "scripts/process_data.py"], check=True)
    print("   Data processed")
except:
    print("   Processing incomplete. Check raw data availability.")

print("\n" + "=" * 60)
print("   SETUP COMPLETE!")
print("=" * 60)
print("\n To start the dashboard, run:")
print("   streamlit run dashboard/app.py")
print("\n Then open: http://localhost:8501")
print("\n Next steps:")
print("   1. Push to GitHub")
print("   2. Connect to Streamlit Cloud (free)")
print("   3. Point hub.ayushnexa.com to your deployment")
