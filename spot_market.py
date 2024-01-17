import time
from shared import *
import requests


# whole list of spot markets
def spot_markets_list():
    return requests.request('GET', host + prefix + spot_currency_pairs_url, headers=headers).json()


'''
spot usdt markets-filtered from spot_market_list
param: quote - USDT/BTC/ETH
'''


def spot_quote_tradable_markets(spot_market_list):
    return [quote_market for quote_market in spot_market_list if
            quote_market.get('quote') in ('USDT', 'BTC', 'ETH') and quote_market['trade_status'] == 'tradable']


# spot ticker information to get last price of ticker
def spot_ticker_information(ticker):
    query_param = {"currency_pair": ticker}
    try:
        spot_ticker_info = requests.request('GET', host + prefix + spot_ticker_info_url, headers=headers,
                                            params=query_param).json()
        if float(spot_ticker_info[0]['last']) > max_usdt_price:  # if price is more than $10 then ignore it
            return False, False
        return float(spot_ticker_info[0]['last'])
    except Exception:
        return False, False


# spot ticker order book to get low asks and high bids
def spot_order_book(ticker, order_initialized=False):
    query_param = f'currency_pair={ticker}'
    try:
        ticker_order_book = requests.request('GET', host + prefix + spot_order_book_url + "?" + query_param,
                                             headers=headers).json()
        if order_initialized:
            return ticker_order_book['asks'][0], ticker_order_book['bids'][0]
        return ticker_order_book['asks'][0][0], ticker_order_book['bids'][0][0]
    except Exception:
        return 0, 0


# live spot ticker data(10s) to be used with live future data (close price as last_price)
def live_spot_data(ticker):
    try:
        query_param = {
            'currency_pair': ticker,
            'interval': '10s',
            'limit': 1}
        live_spot = requests.request('GET', host + prefix + spot_candlestick_url, params=query_param,
                                     headers=headers).json()
        return live_spot[0][2]
    except Exception:
        time.sleep(5)
        return spot_ticker_information(ticker)
