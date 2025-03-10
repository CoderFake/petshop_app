import pytz
import os
from datetime import datetime, timedelta
DEFAULT_TIMEZONE = 'Asia/Ho_Chi_Minh'


def get_timezone():
    timezone_str = os.environ.get('TIMEZONE', DEFAULT_TIMEZONE)
    return pytz.timezone(timezone_str)


def get_current_time():

    timezone = get_timezone()
    return datetime.now(timezone)


def format_datetime(dt, format='%d/%m/%Y %H:%M:%S'):
    if not dt:
        return ""

    timezone = get_timezone()
    if isinstance(dt, datetime) and dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
        dt = dt.astimezone(timezone)

    elif isinstance(dt, datetime) and dt.tzinfo is not None:
        dt = dt.astimezone(timezone)

    return dt.strftime(format)


def localize_datetime(dt):
    if dt.tzinfo is not None:
        return dt.astimezone(get_timezone())

    timezone = get_timezone()
    return timezone.localize(dt)


def utc_to_local(utc_dt):
    if utc_dt.tzinfo is None:
        utc_dt = pytz.UTC.localize(utc_dt)
    return utc_dt.astimezone(get_timezone())


def local_to_utc(local_dt):
    timezone = get_timezone()

    if local_dt.tzinfo is None:
        local_dt = timezone.localize(local_dt)

    return local_dt.astimezone(pytz.UTC)


def add_to_requirements():
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()

        if 'pytz' not in requirements:
            with open('requirements.txt', 'a') as f:
                f.write('\npytz==2023.3\n')

            print("Added pytz to requirements.txt")

    except Exception as e:
        print(f"Error updating requirements.txt: {str(e)}")