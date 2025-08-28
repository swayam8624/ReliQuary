"""
Time utility functions for ReliQuary platform.
Provides functions for time handling, formatting, and timezone management.
"""

import time
import datetime
from typing import Union, Optional, Dict, Any
from datetime import timezone


def get_current_timestamp() -> int:
    """
    Get the current Unix timestamp.
    
    Returns:
        int: Current Unix timestamp (seconds since epoch)
    """
    return int(time.time())


def get_current_timestamp_ms() -> int:
    """
    Get the current Unix timestamp in milliseconds.
    
    Returns:
        int: Current Unix timestamp in milliseconds
    """
    return int(time.time() * 1000)


def timestamp_to_iso(timestamp: Union[int, float], tz: Optional[timezone] = None) -> str:
    """
    Convert a Unix timestamp to ISO 8601 format.
    
    Args:
        timestamp (Union[int, float]): Unix timestamp
        tz (Optional[timezone]): Timezone to use (default: UTC)
        
    Returns:
        str: ISO 8601 formatted datetime string
    """
    if tz is None:
        tz = timezone.utc
    
    dt = datetime.datetime.fromtimestamp(timestamp, tz=tz)
    return dt.isoformat()


def iso_to_timestamp(iso_string: str) -> int:
    """
    Convert an ISO 8601 formatted string to Unix timestamp.
    
    Args:
        iso_string (str): ISO 8601 formatted datetime string
        
    Returns:
        int: Unix timestamp
        
    Raises:
        ValueError: If the ISO string is invalid
    """
    dt = datetime.datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    return int(dt.timestamp())


def get_time_range(days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0) -> Dict[str, int]:
    """
    Get a time range relative to the current time.
    
    Args:
        days (int): Number of days
        hours (int): Number of hours
        minutes (int): Number of minutes
        seconds (int): Number of seconds
        
    Returns:
        Dict[str, int]: Dictionary with 'start' and 'end' timestamps
    """
    now = get_current_timestamp()
    duration = (days * 24 * 60 * 60) + (hours * 60 * 60) + (minutes * 60) + seconds
    start_time = now - duration
    
    return {
        "start": start_time,
        "end": now
    }


def format_duration(seconds: int) -> str:
    """
    Format a duration in seconds to a human-readable string.
    
    Args:
        seconds (int): Duration in seconds
        
    Returns:
        str: Human-readable duration string
    """
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minutes"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hours"
    else:
        days = seconds // 86400
        return f"{days} days"


def is_within_time_window(start_time: Union[int, float], 
                         end_time: Union[int, float], 
                         check_time: Optional[Union[int, float]] = None) -> bool:
    """
    Check if a given time is within a specified time window.
    
    Args:
        start_time (Union[int, float]): Start of the time window (timestamp)
        end_time (Union[int, float]): End of the time window (timestamp)
        check_time (Optional[Union[int, float]]): Time to check (default: current time)
        
    Returns:
        bool: True if check_time is within the window, False otherwise
    """
    if check_time is None:
        check_time = time.time()
    
    return start_time <= check_time <= end_time


def get_timezone_offset(tz_name: str = "UTC") -> int:
    """
    Get the timezone offset in seconds for a given timezone.
    
    Args:
        tz_name (str): Timezone name (default: "UTC")
        
    Returns:
        int: Timezone offset in seconds
    """
    if tz_name.upper() == "UTC":
        return 0
    
    # For simplicity, we'll return common timezone offsets
    # In a real implementation, you might use pytz or similar
    timezone_offsets = {
        "EST": -18000,  # UTC-5
        "CST": -21600,  # UTC-6
        "MST": -25200,  # UTC-7
        "PST": -28800,  # UTC-8
        "GMT": 0,       # UTC+0
        "CET": 3600,    # UTC+1
        "EET": 7200,    # UTC+2
        "MSK": 10800,   # UTC+3
        "IST": 19800,   # UTC+5:30
        "JST": 32400,   # UTC+9
        "AEST": 36000,  # UTC+10
    }
    
    return timezone_offsets.get(tz_name.upper(), 0)


def get_expiration_time(duration_seconds: int, 
                       start_time: Optional[Union[int, float]] = None) -> int:
    """
    Calculate expiration time based on a duration.
    
    Args:
        duration_seconds (int): Duration in seconds
        start_time (Optional[Union[int, float]]): Start time (default: current time)
        
    Returns:
        int: Expiration timestamp
    """
    if start_time is None:
        start_time = time.time()
    
    return int(start_time + duration_seconds)


def is_expired(expiration_time: Union[int, float]) -> bool:
    """
    Check if a given expiration time has passed.
    
    Args:
        expiration_time (Union[int, float]): Expiration timestamp
        
    Returns:
        bool: True if expired, False otherwise
    """
    return time.time() > expiration_time


def get_business_hours_timestamps(date: Optional[datetime.date] = None) -> Dict[str, int]:
    """
    Get start and end timestamps for business hours (9 AM to 5 PM) on a given date.
    
    Args:
        date (Optional[datetime.date]): Date to use (default: today)
        
    Returns:
        Dict[str, int]: Dictionary with 'start' and 'end' timestamps for business hours
    """
    if date is None:
        date = datetime.date.today()
    
    # Start of business day (9 AM UTC)
    start_dt = datetime.datetime.combine(date, datetime.time(9, 0), tzinfo=timezone.utc)
    start_timestamp = int(start_dt.timestamp())
    
    # End of business day (5 PM UTC)
    end_dt = datetime.datetime.combine(date, datetime.time(17, 0), tzinfo=timezone.utc)
    end_timestamp = int(end_dt.timestamp())
    
    return {
        "start": start_timestamp,
        "end": end_timestamp
    }


# Example usage
if __name__ == "__main__":
    # Get current timestamp
    ts = get_current_timestamp()
    print(f"Current timestamp: {ts}")
    
    # Convert to ISO format
    iso = timestamp_to_iso(ts)
    print(f"ISO format: {iso}")
    
    # Get time range
    range_ = get_time_range(hours=1)
    print(f"Last hour range: {range_}")
    
    # Format duration
    duration_str = format_duration(3661)
    print(f"Duration: {duration_str}")
    
    # Check if time is within window
    within_window = is_within_time_window(ts - 100, ts + 100)
    print(f"Within time window: {within_window}")
    
    # Get expiration time
    expires = get_expiration_time(3600)  # 1 hour from now
    print(f"Expires at: {timestamp_to_iso(expires)}")
    
    # Check if expired
    expired = is_expired(ts - 100)  # 100 seconds ago
    print(f"Expired: {expired}")