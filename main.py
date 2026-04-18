API_KEY = "2ee30ea71645ba96e42c1f5b100d0a4bc59b57a9"
import requests
import json
import datetime

# my codes :
from time_engine import get_current_and_past_timestamps
from database_engine import database_process_symbol_data

market_history_url = "https://apiv2.nobitex.ir/market/udf/history"
symbol = "BTCUSDT"


# requests to get some candles data:
def get_market_history_symbol(symbol: str = "BTCUSDT", fromm= 1775867700, to= 1775954100):
    '''
    get market history of symbol that you need in fromm time and to time
    for example:\n
        symbol= "BTCUSDT",
        fromm= "1775867700",
        to= "1775954100"
    '''
    params = {
        "symbol": symbol,
        "resolution": "15",
        "from": fromm,
        "to": to
    }
    try:
        # requests market history:
        market_history_response = requests.get(market_history_url, params=params, json={})
        market_history_data = market_history_response.json()
        print(f"Data was fetched from Nobitex on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return market_history_data
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def main():
    current_ts, past_ts = get_current_and_past_timestamps()
    symbol_ohlcv_data = get_market_history_symbol(symbol= symbol, fromm= past_ts, to= current_ts)
    database_process_symbol_data(data=symbol_ohlcv_data, db_file='database.db', symbol=symbol)

main()