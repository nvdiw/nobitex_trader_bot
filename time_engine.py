import datetime

def get_current_and_past_timestamps():
    """
    This function returns the current Unix timestamp and the timestamp for exactly 24 hours ago.

    Returns:
    A tuple containing two integers: (current_timestamp, past_timestamp).
    """
    # Get the current time
    now = datetime.datetime.now()
    current_timestamp = int(now.timestamp())

    # Calculate the time exactly 24 hours ago
    past_time = now - datetime.timedelta(days=1)
    past_timestamp = int(past_time.timestamp())

    return current_timestamp, past_timestamp

# # Example usage func: get_current_and_past_timestamps():
# current_ts, past_ts = get_current_and_past_timestamps()
# print(f"Current Timestamp: {current_ts}")
# print(f"Timestamp 24 hours ago: {past_ts}")