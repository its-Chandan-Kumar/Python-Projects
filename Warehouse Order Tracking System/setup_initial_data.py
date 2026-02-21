"""
Auto-populate database with initial data on first run
This script can be called automatically or manually to populate the database
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from generate_dummy_data import main as generate_data

if __name__ == "__main__":
    print("🚀 Starting automatic database population...")
    generate_data()
