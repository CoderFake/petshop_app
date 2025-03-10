import pytz
import os
from datetime import datetime, timedelta
from flask import current_app

# Get timezone from environment variable, default to Asia/Ho_Chi_Minh if not set
DEFAULT_TIMEZONE = 'Asia/Ho_Chi_Minh'


def get_timezone():
    """
    Get the application timezone from environment variable
    Returns a pytz timezone object
    """
    timezone_str = os.environ.get('TIMEZONE', DEFAULT_TIMEZONE)
    return pytz.timezone(timezone_str)


def get_current_time():
    """
    Get the current time in the application timezone
    Returns a timezone-aware datetime object
    """
    timezone = get_timezone()
    return datetime.now(timezone)


def format_datetime(dt, format='%d/%m/%Y %H:%M:%S'):
    """
    Format a datetime object or timestamp to string using application timezone

    Args:
        dt: A datetime object or timestamp
        format: The format string

    Returns:
        Formatted datetime string
    """
    if not dt:
        return ""

    timezone = get_timezone()

    # If dt is naive (no timezone info), assume it's UTC and convert
    if isinstance(dt, datetime) and dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
        dt = dt.astimezone(timezone)

    # If it's already a timezone-aware datetime, convert to app timezone
    elif isinstance(dt, datetime) and dt.tzinfo is not None:
        dt = dt.astimezone(timezone)

    return dt.strftime(format)


def localize_datetime(dt):
    """
    Convert a naive datetime to the application timezone

    Args:
        dt: A naive datetime object (without timezone info)

    Returns:
        Timezone-aware datetime in application timezone
    """
    if dt.tzinfo is not None:
        return dt.astimezone(get_timezone())

    timezone = get_timezone()
    return timezone.localize(dt)


def utc_to_local(utc_dt):
    """
    Convert UTC datetime to local timezone

    Args:
        utc_dt: A UTC datetime (timezone-aware or naive)

    Returns:
        Datetime in application timezone
    """
    if utc_dt.tzinfo is None:
        utc_dt = pytz.UTC.localize(utc_dt)
    return utc_dt.astimezone(get_timezone())


def local_to_utc(local_dt):
    """
    Convert local datetime to UTC

    Args:
        local_dt: A local datetime (timezone-aware or naive)

    Returns:
        Datetime in UTC
    """
    timezone = get_timezone()

    if local_dt.tzinfo is None:
        local_dt = timezone.localize(local_dt)

    return local_dt.astimezone(pytz.UTC)


def add_to_requirements():
    """
    Add pytz to requirements.txt if not present
    This is a helper function for development
    """
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()

        if 'pytz' not in requirements:
            with open('requirements.txt', 'a') as f:
                f.write('\npytz==2023.3\n')

            print("Added pytz to requirements.txt")

    except Exception as e:
        print(f"Error updating requirements.txt: {str(e)}")