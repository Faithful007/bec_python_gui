# speed_grade_tables.py
"""
Module for managing speed-grade correction factor table overrides.
Handles PM, CO, and NOx pollutant table overrides.
"""

from typing import Dict, Any, Optional

# Global storage for table overrides
_table_overrides: Dict[str, Dict[str, Any]] = {}


def build_override_from_structured_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a table override from structured JSON data.
    
    Args:
        data: Raw JSON data from imported file
        
    Returns:
        Structured override dictionary
    """
    # Simply return the data as-is for now
    # Can be extended to transform data structure if needed
    return data


def set_table_override(pollutant: str, override: Dict[str, Any]) -> None:
    """
    Set a table override for a specific pollutant.
    
    Args:
        pollutant: Pollutant name (PM, CO, NOx)
        override: Override table data
    """
    if pollutant not in ["PM", "CO", "NOx"]:
        raise ValueError(f"Invalid pollutant: {pollutant}")
    _table_overrides[pollutant] = override


def clear_table_override(pollutant: str) -> None:
    """
    Clear the table override for a specific pollutant.
    
    Args:
        pollutant: Pollutant name (PM, CO, NOx)
    """
    if pollutant in _table_overrides:
        del _table_overrides[pollutant]


def get_table_override(pollutant: str) -> Optional[Dict[str, Any]]:
    """
    Get the table override for a specific pollutant.
    
    Args:
        pollutant: Pollutant name (PM, CO, NOx)
        
    Returns:
        Override table data or None if not set
    """
    return _table_overrides.get(pollutant)


def clear_all_overrides() -> None:
    """Clear all table overrides."""
    _table_overrides.clear()


def get_all_overrides() -> Dict[str, Dict[str, Any]]:
    """Get all current table overrides."""
    return _table_overrides.copy()
