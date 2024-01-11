import requests
from spot_market import live_spot_data
import pandas as pd
from shared import btc_eth_usdc_list, quote_list, binance_ticker_price_url


def live_market_price(arb_df):
    live_prices_df = pd.DataFrame(
        columns=['ticker', 'usdt_lp', 'eth_lp', 'btc_lp', 'usdc_lp'])
    usdt_live_data = eth_live_data = btc_live_data = usdc_live_data = ""
    btc_usdt_price, eth_usdt_price, usdc_usdt_price = quote_live_market_price()
    for market in arb_df:
        for quote in quote_list:
            live_data = live_spot_data(market + quote)
            if isinstance(live_data, tuple):
                live_data = 0.00
            if quote == '_USDT':
                usdt_live_data = float(live_data)
            if quote == '_ETH':
                eth_live_data = float(live_data) * eth_usdt_price
            if quote == '_BTC':
                btc_live_data = float(live_data) * btc_usdt_price
            if quote == '_USDC':
                usdc_live_data = float(live_data) * usdc_usdt_price
        live_data_dict = {
            'ticker': market,  # _lp - last price
            'usdt_lp': usdt_live_data,
            'eth_lp': eth_live_data,
            'btc_lp': btc_live_data,
            'usdc_lp': usdc_live_data
        }
        live_data_tmp = pd.DataFrame(live_data_dict, index=[0])
        live_data_tmp.dropna(axis=1, how='all',inplace=True)
        live_prices_df = pd.concat([live_prices_df, live_data_tmp], ignore_index=True)

    return live_prices_df


def quote_live_market_price():
    btc_usdt_price = eth_usdt_price = usdc_usdt_price = 0.00
    for ticker in btc_eth_usdc_list:
        try:
            if ticker == 'BTC_USDT':
                btc_usdt_price = live_spot_data(ticker)
            if ticker == 'ETH_USDT':
                eth_usdt_price = live_spot_data(ticker)
            if ticker == 'USDC_USDT':
                usdc_usdt_price = live_spot_data(ticker)
        except Exception as e:
            if ticker == 'BTC_USDT':
                api_call = requests.get(binance_ticker_price_url+"BTCUSDT")
                if api_call.status_code == 200:
                    btc_usdt_price = api_call.json()['price']
                else:
                    btc_usdt_price = 0.00
            if ticker == 'ETH_USDT':
                api_call = requests.get(binance_ticker_price_url+"ETHUSDT")
                if api_call.status_code == 200:
                    eth_usdt_price = api_call.json()['price']
                else:
                    eth_usdt_price = 0.00
            if ticker == 'USDC_USDT':
                api_call = requests.get(binance_ticker_price_url+"USDCUSDT")
                if api_call.status_code == 200:
                    usdc_usdt_price = api_call.json()['price']
                else:
                    usdc_usdt_price = 0.00

    return float(btc_usdt_price), float(eth_usdt_price), float(usdc_usdt_price)
