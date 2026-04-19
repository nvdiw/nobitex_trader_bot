import requests
import datetime

market_history_url = "https://apiv2.nobitex.ir/market/udf/history"

# requests to get some candles data:
def get_market_history_symbol_nobitex(symbol: str = "BTCUSDT", fromm= 1775867700, to= 1775954100):
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
