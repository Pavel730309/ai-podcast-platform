"""
Database model utilities for safe field access
"""

from typing import Optional, Any
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column

Base = declarative_base()


def get_column_value(model: Any, field_name: str, default: Any = None) -> Any:
    """Safely get value from model field (handles Column types)"""
    value = getattr(model, field_name, default)
    if value is None:
        return default
    # If it's still a Column (not loaded), return default
    if hasattr(value, "__class__") and "Column" in value.__class__.__name__:
        return default
    return value


def set_column_value(model: Any, field_name: str, value: Any) -> None:
    """Safely set value to model field"""
    setattr(model, field_name, value)


def to_str(value: Any, default: str = "") -> str:
    """Convert value to string safely"""
    if value is None:
        return default
    if hasattr(value, "__class__") and "Column" in value.__class__.__name__:
        return default
    return str(value)


def to_int(value: Any, default: int = 0) -> int:
    """Convert value to int safely"""
    if value is None:
        return default
    if hasattr(value, "__class__") and "Column" in value.__class__.__name__:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def to_bool(value: Any) -> bool:
    """Check if value is truthy (safe for Column types)"""
    if value is None:
        return False
    if hasattr(value, "__class__") and "Column" in value.__class__.__name__:
        return False
    return bool(value)
