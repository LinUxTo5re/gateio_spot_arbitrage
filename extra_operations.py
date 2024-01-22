from platform import system
from subprocess import call
import requests
import spot_market
from shared import binance_ticker_price_url
from datetime import datetime, timedelta


def clear_terminal():
    if system() == 'Windows':
        call('cls', shell=True)
    else:
        call('clear', shell=True)


def wake_up_bro(second):
    new_current_datetime = datetime.now()
    added_seconds = timedelta(seconds=second)
    new_datetime = new_current_datetime + added_seconds
    return new_datetime.hour, new_datetime.minute, new_datetime.second


def binance_ticker(ticker):
    # using binance for ticker price
    try:
        if ticker == 'BTC_USDT':
            api_call = requests.get(binance_ticker_price_url + "BTCUSDT")
            if api_call.status_code == 200:
                btc_usdt_price = api_call.json()['price']
            else:
                btc_usdt_price = 0.00
            return float(btc_usdt_price)
        if ticker == 'ETH_USDT':
            api_call = requests.get(binance_ticker_price_url + "ETHUSDT")
            if api_call.status_code == 200:
                eth_usdt_price = api_call.json()['price']
            else:
                eth_usdt_price = 0.00
            return float(eth_usdt_price)
    except Exception:
        return float(0.00)


# Terminate application with 'SIGINT'(Ctrl + C) (only parameterized calling)
def signal_handler(signum, frame):
    print("\n Exiting Application....")
    exit(0)


#  crypto quanty/price = avl for bid/ask
def get_total_bid_ask_on_diff(market):
    ticker = market[1][0]
    min_var = market[1][3]
    max_var = market[1][4]
    non_usdt_price = market[1][5]
    ask_data, bid_data = spot_market.spot_order_book(ticker + '_' + min_var, True)
    if not min_var == 'usdt':
        buy_total_USDT = float(ask_data[1]) * float(non_usdt_price)
    else:
        buy_total_USDT = float(ask_data[1]) * float(ask_data[0])
    ask_data, bid_data = spot_market.spot_order_book(ticker + '_' + max_var, True)
    if not max_var == 'usdt':
        sell_total_USDT = float(bid_data[1]) * float(non_usdt_price)
    else:
        sell_total_USDT = float(bid_data[1]) * float(bid_data[0])
    min_pnl_last_total = min(buy_total_USDT, sell_total_USDT)
    return min_pnl_last_total
