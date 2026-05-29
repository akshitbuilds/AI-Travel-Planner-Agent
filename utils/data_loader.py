"""
utils/data_loader.py
---------------------
Utility module for loading and accessing JSON datasets.
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def load_flights() -> list[dict]:
    """Load flights dataset from JSON file."""
    with open(os.path.join(DATA_DIR, "flights.json"), "r") as f:
        return json.load(f)


def load_hotels() -> list[dict]:
    """Load hotels dataset from JSON file."""
    with open(os.path.join(DATA_DIR, "hotels.json"), "r") as f:
        return json.load(f)


def load_places() -> list[dict]:
    """Load places/POI dataset from JSON file."""
    with open(os.path.join(DATA_DIR, "places.json"), "r") as f:
        return json.load(f)