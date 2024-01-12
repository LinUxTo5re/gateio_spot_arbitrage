import platform
import subprocess
import requests
from shared import binance_ticker_price_url
from datetime import datetime, timedelta


def clear_terminal():
    if platform.system() == 'Windows':
        subprocess.call('cls', shell=True)
    else:
        subprocess.call('clear', shell=True)


def wake_up_bro(second):
    current_datetime = datetime.now()
    added_seconds = timedelta(seconds=second)
    new_datetime = current_datetime + added_seconds
    return new_datetime.hour, new_datetime.minute


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
