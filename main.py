import requests
import json

market_history_url = "https://apiv2.nobitex.ir/market/udf/history"

def get_market_history_symbol(symbol: str = "BTCUSDT", fromm= 1775867700, to= 1775954100):
    '''
    get market history of symbol that you need in fromm time and to time
    for example:\n
        symbol= "BTCUSDT",
        fromm= "1775867700",
        to= "1775954100"
    '''
    params = {
        "symbol": "BTCUSDT",
        "resolution": "15",
        "from": "1775867700",
        "to": "1775954100"
    }

    # Fetch market history
    market_history_response = requests.get(market_history_url, params=params, json={})
    market_history_data = market_history_response.json()

    with open("market_history.json", "w") as file:
        json.dump(market_history_data, file, indent=4)
    if market_history_data["s"] == "ok":
        print("market history saved to market_history.json")
        return True
    else:
        print("market history didn't save")
        return False

get_market_history_symbol()

import datetime

# The timestamp provided
timestamp = 1562230967

# Convert to datetime object (UTC time)
dt_object = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)

# Format the output as a readable string
formatted_date = dt_object.strftime('%Y-%m-%d %H:%M:%S')

print(f"Date and Time: {formatted_date}")


# Define the input datetime string
# Format: YYYY-MM-DD HH:MM:SS
# Example: '2019-07-04 09:02:47'
input_datetime_str = '2026-04-11 04:05:00'

# Convert the datetime string to a datetime object
# Assuming the input is in local time.
# If you need to consider UTC, use: dt_object = datetime.datetime.strptime(input_datetime_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc)
dt_object = datetime.datetime.strptime(input_datetime_str, '%Y-%m-%d %H:%M:%S')

# Convert the datetime object to a Unix timestamp
# .timestamp() returns a float, so we convert it to an integer.
timestamp = int(dt_object.timestamp())

print(f"The timestamp for '{input_datetime_str}' is: {timestamp}")
