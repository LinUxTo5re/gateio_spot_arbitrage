import pandas as pd
import live_market
import spot_market
from tqdm import tqdm

btc_price_diff_pct = eth_price_diff_pct = 0


# create quote df for each quote asset
def create_quote_df(spot_quote_market):
    spot_USDT_df = pd.DataFrame()
    spot_BTC_df = pd.DataFrame()
    spot_ETH_df = pd.DataFrame()
    spot_USDT_last = []
    spot_USDT_ticker = []
    spot_BTC_last = []
    spot_BTC_ticker = []
    spot_ETH_last = []
    spot_ETH_ticker = []
    for ticker in tqdm(enumerate(spot_quote_market), desc="Tickers Quotation", total=len(spot_quote_market)):
        try:
            spot_ticker_info = spot_market.spot_ticker_information(ticker[1]['id'])
            if not isinstance(spot_ticker_info, tuple):
                if ticker[1]['quote'] == 'USDT':
                    spot_USDT_ticker.append(ticker[1]['base'])
                    spot_USDT_last.append(spot_ticker_info)
                elif ticker[1]['quote'] == 'BTC':
                    spot_BTC_ticker.append(ticker[1]['base'])
                    spot_BTC_last.append(spot_ticker_info)
                elif ticker[1]['quote'] == 'ETH':
                    spot_ETH_ticker.append(ticker[1]['base'])
                    spot_ETH_last.append(spot_ticker_info)
                else:
                    pass
            else:
                pass
        except Exception as e:
            print(f'\n{e}')
    # base == ticker
    spot_USDT_df['ticker'] = spot_USDT_ticker
    spot_USDT_df['last'] = spot_USDT_last
    spot_BTC_df['ticker'] = spot_BTC_ticker
    spot_BTC_df['last'] = spot_BTC_last
    spot_ETH_df['ticker'] = spot_ETH_ticker
    spot_ETH_df['last'] = spot_ETH_last
    return create_possible_df(spot_USDT_df, spot_BTC_df, spot_ETH_df)


# create combined df of quote asset with last price
def create_possible_df(spot_USDT_df, spot_BTC_df, spot_ETH_df):
    arb_df = pd.DataFrame()
    arb_df_ticker = []
    arb_df_usdt_last = []
    arb_df_btc_last = []
    arb_df_eth_last = []
    btc_usdt_price, eth_usdt_price = live_market.quote_live_market_price()
    for market in tqdm(spot_USDT_df.iterrows(), desc="Acquiring Price", total=len(spot_USDT_df)):
        try:
            arb_df_usdt_last.append(market[1]['last'])
            arb_df_ticker.append(market[1]['ticker'])
            if market[1]['ticker'] in spot_BTC_df['ticker'].values:
                arb_df_btc_last.append(
                    spot_BTC_df.loc[spot_BTC_df['ticker'] == market[1]['ticker'], 'last'].values[0] * btc_usdt_price)
            else:
                arb_df_btc_last.append(0.00)
            if market[1]['ticker'] in spot_ETH_df['ticker'].values:
                arb_df_eth_last.append(
                    spot_ETH_df.loc[spot_ETH_df['ticker'] == market[1]['ticker'], 'last'].values[0] * eth_usdt_price)
            else:
                arb_df_eth_last.append(0.00)
        except Exception as e:
            print(f"\n {e}")

    arb_df['ticker'] = arb_df_ticker
    arb_df['usdt_last'] = arb_df_usdt_last
    arb_df['btc_last'] = arb_df_btc_last
    arb_df['eth_last'] = arb_df_eth_last
    return remove_unwanted_from_df(arb_df)


# remove tickers with price diff less than 5% or last price is 0
def remove_unwanted_from_df(arb_df):
    global btc_price_diff_pct, eth_price_diff_pct
    filtered_arb_df = arb_df[~((arb_df['btc_last'] == 0) & (arb_df['eth_last'] == 0))]
    rows_to_remove = []
    for index, market in tqdm(filtered_arb_df.iterrows(), total=len(filtered_arb_df), desc='DF Creation'):
        btc_last_price = market['btc_last']
        eth_last_price = market['eth_last']
        usdt_last_price = market['usdt_last']
        if btc_last_price:
            numerator = abs(btc_last_price - usdt_last_price)
            denominator = btc_last_price if btc_last_price > usdt_last_price else usdt_last_price
            btc_price_diff_pct = (numerator / denominator) * 100
        if eth_last_price:
            numerator = abs(eth_last_price - usdt_last_price)
            denominator = eth_last_price if eth_last_price > usdt_last_price else usdt_last_price
            eth_price_diff_pct = (numerator / denominator) * 100

        if btc_price_diff_pct < 0.1 and eth_price_diff_pct < 0.1:
            rows_to_remove.append(index)
            btc_price_diff_pct = eth_price_diff_pct = 0.00

    return filtered_arb_df.drop(rows_to_remove)
