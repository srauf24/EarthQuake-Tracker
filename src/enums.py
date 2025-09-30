"""
Defines enumerated types for the application.
"""
from enum import Enum

class TimePeriod(Enum):
    """Enumeration for the USGS data time periods."""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
