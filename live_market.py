import warnings
import extra_operations
from spot_market import spot_ticker_information, spot_order_book
import pandas as pd
from shared import btc_eth_list, quote_list, assumed_usdt_fee, exclude_price_diffr, max_usdt_price
from tqdm import tqdm


def live_market_price(arb_df):
    live_data_dict = ''
    # Suppress FutureWarnings
    warnings.simplefilter(action='ignore', category=FutureWarning)
    live_prices_df = pd.DataFrame(
        columns=['ticker', 'min_max', 'diffr(fee_included)'])
    btc_usdt_price, eth_usdt_price = quote_live_market_price()
    try:
        for index, market in tqdm(enumerate(arb_df), desc="Live Price", total=len(arb_df), disable=False):
            # tqdm bar has been disabled
            try:
                if (index + 1) % 5 == 0:
                    btc_usdt_price, eth_usdt_price = quote_live_market_price()
                min_variable_name, min_variable_value, max_variable_name, max_variable_value = live_market_price_ext(
                    market,
                    btc_usdt_price,
                    eth_usdt_price)
                min_price, max_price = min_variable_value, max_variable_value
                if min_variable_name == 'eth':
                    min_price = str(min_variable_value / eth_usdt_price)
                elif max_variable_name == 'eth':
                    max_price = str(max_variable_value / eth_usdt_price)
                if min_variable_name == 'btc':
                    min_price = str(min_variable_value / btc_usdt_price)
                elif max_variable_name == 'btc':
                    max_price = str(max_variable_value / btc_usdt_price)
                live_data_dict = {
                    'ticker': market,
                    'min_max': f"{min_variable_name}({min_price})->{max_variable_name}({max_price})",  # usdt -> btc
                    'diffr(fee_included)': ((max_variable_value - min_variable_value) * (
                            max_usdt_price / min_variable_value) - assumed_usdt_fee)
                    # profit on $10 trade with 0.04 fee (assumed)
                }
            except Exception as e:
                pass
            live_data_tmp = pd.DataFrame(live_data_dict, index=[0])
            live_data_tmp.dropna(axis=1, how='all', inplace=True)
            live_prices_df = pd.concat([live_prices_df, live_data_tmp], ignore_index=True)
        # return only diffr >= $0.2 (2% of 10)
        live_prices_df = live_prices_df[live_prices_df['diffr(fee_included)'] >= exclude_price_diffr]
        live_prices_df = live_prices_df.sort_values(by='diffr(fee_included)', ascending=False).copy()
        if len(live_prices_df) > 0:
            print(f"\n max_usdt_price: {max_usdt_price} \n Total Fetched: {len(live_prices_df)} Markets")
        else:
            print(f"\n No Arbitrage Founded")
        return live_prices_df
    except Exception:
        pass


# extension for live_market_price() for more readability
def live_market_price_ext(market, btc_usdt_price, eth_usdt_price):
    usdt_live_data_min = eth_live_data_min = btc_live_data_min = 0
    usdt_live_data_max = eth_live_data_max = btc_live_data_max = 0
    try:
        for quote in quote_list:
            try:
                # getting asks and bids price resp.
                # I'll buy at seller price(asks) and sell at buyer price(bids)
                live_data_seller_price, live_data_buyer_price = spot_order_book(market + quote)
                # _min: seller price(asks)..buy at this price
                # _max: buyer price(bids)..sell at this price
                if quote == '_USDT':
                    usdt_live_data_min = float(live_data_seller_price)
                    usdt_live_data_max = float(live_data_buyer_price)
                if quote == '_ETH':
                    eth_live_data_min = float(live_data_seller_price) * eth_usdt_price
                    eth_live_data_max = float(live_data_buyer_price) * eth_usdt_price
                if quote == '_BTC':
                    btc_live_data_min = float(live_data_seller_price) * btc_usdt_price
                    btc_live_data_max = float(live_data_buyer_price) * btc_usdt_price
            except Exception:
                pass
    except Exception:
        extra_operations.clear_terminal()
    try:
        min_variables_value = [('usdt', usdt_live_data_min), ('eth', eth_live_data_min), ('btc', btc_live_data_min)]
        min_variables_value = list(filter(lambda x: x[1] != 0, min_variables_value))  # remove variable with zero value
        max_variables_value = [('usdt', usdt_live_data_max), ('eth', eth_live_data_max), ('btc', btc_live_data_max)]
        max_variables_value = list(filter(lambda x: x[1] != 0, max_variables_value))
        min_variable_tuple = min(min_variables_value, key=lambda x: x[1])
        min_variable_name, min_variable_value = min_variable_tuple

        # remove common quote from max_ list
        if min_variable_name == 'usdt':
            max_variables_value.pop(0)
        elif min_variable_name == 'eth':
            max_variables_value.pop(1)
        elif min_variable_name == 'btc':
            if len(max_variables_value) == 3:
                max_variables_value.pop(2)
            else:
                max_variables_value.pop(1)
        max_variable_tuple = max(max_variables_value, key=lambda x: x[1])
        max_variable_name, max_variable_value = max_variable_tuple
        return min_variable_name, min_variable_value, max_variable_name, max_variable_value
    except Exception:
        return '', 0, '', 0


def quote_live_market_price():
    btc_usdt_price = eth_usdt_price = 0.00
    for ticker in btc_eth_list:
        try:
            if ticker == 'BTC_USDT':
                btc_usdt_price = spot_ticker_information(ticker)
                if isinstance(btc_usdt_price, tuple):
                    raise ValueError
            if ticker == 'ETH_USDT':
                eth_usdt_price = spot_ticker_information(ticker)
                if isinstance(eth_usdt_price, tuple):
                    raise ValueError
        except Exception:
            if ticker == 'BTC_USDT':
                btc_usdt_price = extra_operations.binance_ticker(ticker)
            if ticker == 'ETH_USDT':
                eth_usdt_price = extra_operations.binance_ticker(ticker)
    return float(btc_usdt_price), float(eth_usdt_price)
