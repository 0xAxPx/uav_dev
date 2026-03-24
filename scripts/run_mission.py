#!/usr/bin/env python3
"""
Run Mission - Main Entry Point

Executes autonomous grid inspection mission.
"""

import sys
import os

# Add src/ to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import and run
from src.mission.mission_executor import main

if __name__ == "__main__":
    main()