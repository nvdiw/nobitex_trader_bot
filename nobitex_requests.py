import requests
import datetime
import time


# requests to get some candles data:
def get_market_history_symbol_nobitex(symbol: str = "BTCUSDT", fromm=1775867700, to=1775954100):
    '''
    get market history of symbol that you need in fromm time and to time
    for example:\n
        symbol= "BTCUSDT",
        fromm= "1775867700",
        to= "1775954100"
    '''
    market_history_url = "https://apiv2.nobitex.ir/market/udf/history"
    params = {
        "symbol": symbol,
        "resolution": "15",
        "from": fromm,
        "to": to
    }
    
    max_retries = 3
    retry_count = 0
    retry_delay = 30  # seconds
    
    while retry_count < max_retries:
        try:
            # requests market history:
            market_history_response = requests.get(market_history_url, params=params, json={}, timeout=10)
            market_history_data = market_history_response.json()
            print(f"Data was fetched from Nobitex on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return market_history_data
        
        except Exception as e:
            retry_count += 1
            print(f"Attempt {retry_count} failed: {e}")
            
            if retry_count < max_retries:
                print(f"Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
            else:
                print(f"All {max_retries} attempts failed. Please check your internet connection.")
                return None


# get orderbooks: bids/ asks
def get_orderbook_symbol_nobitex(symbol="BTCUSDT"):
    """
    Get orderbook from Nobitex exchange
    :param symbol: Trading pair like BTCUSDT, ETHIRT, etc.
    :param base_url: API base URL
    :return: Dictionary containing orderbook or error
    """

    url = f"https://apiv2.nobitex.ir/v3/orderbook/{symbol}"

    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                return data
            else:
                return {"error": f"API returned non-success: {data.get('status')}"}
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
    
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection error: {str(e)}"}


# add order in nobitex
def open_order_symbol_nobitex(type: str, execution: str, symbol: str, amount: float, price: float, id: str):
    '''
    for example:
        type= "buy" or "sell",
        execution= "limit" or "market",
        symbol= "btc" or "eth" or "arb", NOTE: low verbs
        amount= 0.000132,
        price= 75345,
        clientOrderId= "order1"   
    '''
    url = "https://apiv2.nobitex.ir/market/orders/add"
    headers = {
        "Authorization": "Token ef69caac13015974006aac99149432ba4da4bbc9",
        "content-type": "application/json",
    }

    data = {
        "type": type,
        "execution": execution,
        "srcCurrency": symbol,
        "dstCurrency": "usdt",
        "amount": amount,
        "price": price,
        "clientOrderId": id
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    except Exception as e:
        price(f"order didn't set in nobitex ERROR: {e}")
        return None

    
# check symbol wallet balance
def symbol_wallet_balance_nobitex(symbol: str = "usdt"):
    url = "https://apiv2.nobitex.ir/users/wallets/balance"

    headers = {
        "Authorization": "Token ef69caac13015974006aac99149432ba4da4bbc9",
    }

    data = {
        "currency": symbol
    }

    response = requests.post(url, headers=headers, data=data)
    data = response.json()
    return data["balance"]

