import platform
import subprocess
import requests
from shared import binance_ticker_price_url


def clear_terminal():
    if platform.system() == 'Windows':
        subprocess.call('cls', shell=True)
    else:
        subprocess.call('clear', shell=True)


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
    except Exception as e:
        return float(0.00)