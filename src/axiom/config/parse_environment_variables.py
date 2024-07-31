import os
import json
from typing import Dict, List, Any, Optional, Union

def parse_int(value):
    """Convert a Int String to a Python Int type"""
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Invalid Int value: {value}.")
    
def parse_boolean(value):
    """Convert environment string to a boolean."""
    value_lower = value.lower()
    if value_lower in ['true', '1', 't', 'y', 'yes']:
        return True
    elif value_lower in ['false', '0', 'f', 'n', 'no']:
        return False
    raise ValueError(f"Invalid boolean value: {value}")

def parse_json(value):
    """Parse a JSON string into a Python dictionary."""
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
    
# TODO
# proper error handling & checks
# what if the user accidentally used the wrong delimiter, etc
def parse_list(value):
    """Parse a list string to a Python list"""
    return [item.strip() for item in value.split(',')]
