import pandas as pd
import live_market
import spot_market
from tqdm import tqdm
from shared import exclude_price_diffr_pct, quote_list, max_usdt_price

# global variables
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
    usdt_bases = []
    eth_bases = []
    btc_bases = []

    for entry in spot_quote_market:
        if entry['quote'] == 'USDT':
            usdt_bases.append(entry['base'])
        elif entry['quote'] == 'ETH':
            eth_bases.append(entry['base'])
        elif entry['quote'] == 'BTC':
            btc_bases.append(entry['base'])

    spot_markets = set(usdt_bases).intersection(set(eth_bases + btc_bases))
    spot_ticker_info = spot_market.spot_ticker_information()
    for i, ticker in tqdm(enumerate(spot_markets), desc="Tickers Quotation", total=len(spot_markets), colour='green',
                          disable=False):
        try:
            if (i+1) % 100 == 0:
                spot_ticker_info = spot_market.spot_ticker_information()
            for quote in quote_list:
                quote_ticker = ticker + quote
                last_price = next((entry.get('last', None) for entry in spot_ticker_info if
                                   quote_ticker in entry.get('currency_pair', '')), None)
                if last_price:
                    if float(last_price) > max_usdt_price:
                        break
                    if quote == '_USDT':
                        spot_USDT_ticker.append(ticker)
                        spot_USDT_last.append(float(last_price))
                    elif quote == '_BTC':
                        spot_BTC_ticker.append(ticker)
                        spot_BTC_last.append(float(last_price))
                    elif quote == '_ETH':
                        spot_ETH_ticker.append(ticker)
                        spot_ETH_last.append(float(last_price))
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
    for index, market in tqdm(enumerate(spot_USDT_df.iterrows()), desc="Acquiring Price", total=len(spot_USDT_df),
                              colour='red', disable=False):
        try:
            if (index + 1) % 20 == 0:
                btc_usdt_price, eth_usdt_price = live_market.quote_live_market_price()
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
    for index, market in tqdm(filtered_arb_df.iterrows(), total=len(filtered_arb_df), desc='DF Creation',
                              colour='white', disable=True):
        try:
            btc_last_price = market['btc_last']
            eth_last_price = market['eth_last']
            usdt_last_price = market['usdt_last']
            # for the purpose of getting only ticker, we're not going to implement deep math formulas
            if btc_last_price:
                numerator = abs(btc_last_price - usdt_last_price)
                denominator = (btc_last_price + usdt_last_price) / 2
                btc_price_diff_pct = round((numerator / denominator) * 100, 2)
            if eth_last_price:
                numerator = abs(eth_last_price - usdt_last_price)
                denominator = (eth_last_price + usdt_last_price) / 2
                eth_price_diff_pct = round((numerator / denominator) * 100, 2)

            if btc_price_diff_pct < exclude_price_diffr_pct and eth_price_diff_pct < exclude_price_diffr_pct:
                rows_to_remove.append(index)
                btc_price_diff_pct = eth_price_diff_pct = 0.00
        except Exception as e:
            print(f"\n {e}")
    return filtered_arb_df.drop(rows_to_remove)
