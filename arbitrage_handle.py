import pandas as pd
import spot_market
from tqdm import tqdm

btc_price_diff_pct = eth_price_diff_pct = usdc_price_diff_pct = 0


# create quote df for each quote asset
def create_quote_df(spot_quote_market):
    spot_USDT_df = pd.DataFrame()
    spot_BTC_df = pd.DataFrame()
    spot_ETH_df = pd.DataFrame()
    spot_USDC_df = pd.DataFrame()
    spot_USDT_last = []
    spot_USDT_ticker = []
    spot_BTC_last = []
    spot_BTC_ticker = []
    spot_ETH_last = []
    spot_ETH_ticker = []
    spot_USDC_last = []
    spot_USDC_ticker = []
    for ticker in tqdm(enumerate(spot_quote_market), desc="quoting tickers", total=len(spot_quote_market)):
        try:
            spot_ticker_info = spot_market.spot_ticker_information(ticker[1]['id'])
            if ticker[1]['quote'] == 'USDT':
                spot_USDT_ticker.append(ticker[1]['id'])
                spot_USDT_last.append(spot_ticker_info)
            elif ticker[1]['quote'] == 'BTC':
                spot_BTC_ticker.append(ticker[1]['id'])
                spot_BTC_last.append(spot_ticker_info)
            elif ticker[1]['quote'] == 'ETH':
                spot_ETH_ticker.append(ticker[1]['id'])
                spot_ETH_last.append(spot_ticker_info)
            else:
                spot_USDC_ticker.append(ticker[1]['id'])
                spot_USDC_last.append(spot_ticker_info)
        except Exception as e:
            print(f'\n{e}')

    spot_USDT_df['ticker'] = spot_USDT_ticker
    spot_USDT_df['last'] = spot_USDT_last
    spot_BTC_df['ticker'] = spot_BTC_ticker
    spot_BTC_df['last'] = spot_BTC_last
    spot_ETH_df['ticker'] = spot_ETH_ticker
    spot_ETH_df['last'] = spot_ETH_last
    spot_USDC_df['ticker'] = spot_USDC_ticker
    spot_USDC_df['last'] = spot_USDC_last
    return create_possible_df(spot_USDT_df, spot_BTC_df, spot_ETH_df, spot_USDC_df)


# create combined df of quote asset with last price
def create_possible_df(spot_USDT_df, spot_BTC_df, spot_ETH_df, spot_USDC_df):
    arb_df = pd.DataFrame()
    arb_df_ticker = []
    arb_df_usdt_last = []
    arb_df_btc_last = []
    arb_df_eth_last = []
    arb_df_usdc_last = []

    for market in tqdm(enumerate(spot_USDT_df), desc="getting market price", total=len(spot_USDT_df)):
        try:
            arb_df_usdt_last = market[1]['last']
            arb_df_ticker = market[1]['ticker']
            if market[1]['ticker'] in spot_BTC_df['ticker'].values:
                arb_df_btc_last.append(
                    spot_BTC_df.loc[spot_BTC_df['ticker'] == market[1]['ticker'], 'last_price'].values[0])
            else:
                arb_df_btc_last.append(0.00)
            if market[1]['ticker'] in spot_ETH_df['ticker'].values:
                arb_df_eth_last.append(
                    spot_ETH_df.loc[spot_ETH_df['ticker'] == market[1]['ticker'], 'last_price'].values[0])
            else:
                arb_df_eth_last.append(0.00)
            if market[1]['ticker'] in spot_USDC_df['ticker'].values:
                arb_df_usdc_last.append(
                    spot_USDC_df.loc[spot_USDC_df['ticker'] == market[1]['ticker'], 'last_price'].values[0])
            else:
                arb_df_usdc_last.append(0.00)
        except Exception as e:
            print(f"\n {e}")

    arb_df['ticker'] = arb_df_ticker
    arb_df['usdt_last'] = arb_df_usdt_last
    arb_df['btc_last'] = arb_df_btc_last
    arb_df['eth_last'] = arb_df_eth_last
    arb_df['usdc_last'] = arb_df_usdc_last
    return remove_unwanted_from_df(arb_df)


# remove tickers with price diff less than 5% or last price is 0
def remove_unwanted_from_df(arb_df):
    global btc_price_diff_pct, eth_price_diff_pct, usdc_price_diff_pct
    filtered_arb_df = arb_df[~((arb_df['btc_last'] == 0) & (arb_df['eth_last'] == 0) & (arb_df['usdc_last'] == 0))]
    rows_to_remove = []
    for index, market in tqdm(filtered_arb_df.iterrows(), total=len(filtered_arb_df), desc='df updation'):
        btc_last_price = market['btc_last']
        eth_last_price = market['eth_last']
        usdc_last_price = market['usdc_last']
        usdt_last_price = market['usdt_last']
        if btc_last_price:
            numerator = abs(btc_last_price - usdt_last_price)
            denominator = btc_last_price if btc_last_price > usdt_last_price else usdt_last_price
            btc_price_diff_pct = (numerator / denominator) * 100
        elif eth_last_price:
            numerator = abs(eth_last_price - usdt_last_price)
            denominator = eth_last_price if eth_last_price > usdt_last_price else usdt_last_price
            eth_price_diff_pct = (numerator / denominator) * 100
        elif usdc_last_price:
            numerator = abs(usdc_last_price - usdt_last_price)
            denominator = usdc_last_price if usdc_last_price > usdt_last_price else usdt_last_price
            usdc_price_diff_pct = (numerator / denominator) * 100
        else:
            pass
        if btc_price_diff_pct < 5 and eth_price_diff_pct < 5 and usdc_price_diff_pct < 5:
            rows_to_remove.append(index)
        else:
            filtered_arb_df.loc[index, 'btc_pct'] = btc_price_diff_pct
            filtered_arb_df.loc[index, 'eth_pct'] = eth_price_diff_pct
            filtered_arb_df.loc[index, 'usdc_pct'] = usdc_price_diff_pct

    return filtered_arb_df.drop(rows_to_remove)

