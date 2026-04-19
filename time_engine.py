import datetime

# get current time and by default 1 day ago
def get_current_and_past_timestamps(days_ago=1):
    """
    This function returns the current Unix timestamp and the timestamp for exactly 24 hours ago.

    Returns:
    A tuple containing two integers: (current_timestamp, past_timestamp).
    """
    # Get the current time
    now = datetime.datetime.now()
    current_timestamp = int(now.timestamp())

    # Calculate the time exactly 24 hours ago
    past_time = now - datetime.timedelta(days=days_ago)
    past_timestamp = int(past_time.timestamp())

    return current_timestamp, past_timestamp


# get time with number and returns date/time
def timestamp_to_datetime(timestamp):
    """
    Convert Unix timestamp to readable datetime string.
    
    Args:
        timestamp (int or float): Unix timestamp (e.g., 1776636000)
    
    Returns:
        str: Formatted datetime string (YYYY-MM-DD HH:MM:SS)
    """
    import datetime
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')