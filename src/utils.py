"""
PathoWatch Utility Functions
"""

import json
from datetime import datetime
from pathlib import Path

def save_json(data, filepath):
    """Save data to JSON with timestamp."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def load_json(filepath):
    """Load JSON data."""
    try:
        with open(filepath) as f:
            return json.load(f)
    except:
        return None

def format_number(n):
    """Format large numbers with K/M suffix."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)
