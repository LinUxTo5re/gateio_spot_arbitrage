from spot_market import live_spot_data
import pandas as pd


def live_market_price(arb_df):
    live_prices_df = pd.DataFrame(columns=['ticker', 'live_price'])

    for index, market in arb_df.iterrows():
        live_data = live_spot_data(market['ticker'])
        live_prices_df = live_prices_df.append({'ticker': live_data['ticker'], 'live_price': live_data['live_price']},
                                               ignore_index=True)
    return live_prices_df
