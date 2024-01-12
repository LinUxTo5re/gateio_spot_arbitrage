import warnings
import extra_operations
from spot_market import live_spot_data
import pandas as pd
from shared import btc_eth_list, quote_list
from tqdm import tqdm


def live_market_price(arb_df):
    # Suppress FutureWarnings
    warnings.simplefilter(action='ignore', category=FutureWarning)
    live_prices_df = pd.DataFrame(
        columns=['ticker', 'usdt_lp', 'eth_lp', 'btc_lp'])
    usdt_live_data = eth_live_data = btc_live_data = ""
    btc_usdt_price, eth_usdt_price = quote_live_market_price()
    for market in tqdm(arb_df, desc="Live Price", total=len(arb_df)):
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
        min_quote_price = min(usdt_live_data, btc_live_data, eth_live_data)
        max_quote_price = max(usdt_live_data, btc_live_data, eth_live_data)
        live_data_dict = {
            'ticker': market,  # _lp - last price
            'usdt_lp': usdt_live_data,
            'eth_lp': eth_live_data,
            'btc_lp': btc_live_data,
            'diffr($10)': (max_quote_price - min_quote_price) * 10  # profit on $10 trade (assumed)
        }
        live_data_tmp = pd.DataFrame(live_data_dict, index=[0])
        live_data_tmp.dropna(axis=1, how='all', inplace=True)
        live_prices_df = pd.concat([live_prices_df, live_data_tmp], ignore_index=True)
    return live_prices_df


def quote_live_market_price():
    btc_usdt_price = eth_usdt_price = 0.00
    for ticker in btc_eth_list:
        try:
            if ticker == 'BTC_USDT':
                btc_usdt_price = live_spot_data(ticker)
                if isinstance(btc_usdt_price, tuple):
                    raise ValueError
            if ticker == 'ETH_USDT':
                eth_usdt_price = live_spot_data(ticker)
                if isinstance(eth_usdt_price, tuple):
                    raise ValueError
        except Exception:
            if ticker == 'BTC_USDT':
                btc_usdt_price = extra_operations.binance_ticker(ticker)
            if ticker == 'ETH_USDT':
                eth_usdt_price = extra_operations.binance_ticker(ticker)
    return float(btc_usdt_price), float(eth_usdt_price)
