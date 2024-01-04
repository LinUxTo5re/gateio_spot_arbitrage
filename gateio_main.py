import asyncio
import json
import time
import os
import requests
import pandas as pd
from shared import *
import spot_market
from tqdm import tqdm
import arbitrage_handle
import live_market


# common markets from spot and future
def common_markets_filtering():
    pass


if __name__ == '__main__':
    file_exists = os.path.exists('arb_df_bak.json')
    if file_exists:
        with open('arb_df_bak.json', 'r') as file:
            arb_df = json.load(file)
    else:
        spot_market_list = spot_market.spot_markets_list()
        spot_market_list = [market for market in spot_market_list if market['trade_status'] == 'tradable']
        spot_quote_market = spot_market.spot_quote_tradable_markets(spot_market_list)
        # returns df with combinations of all usdt and remove unwanted rows from df
        arb_df = arbitrage_handle.create_quote_df(spot_quote_market)
        arb_df.to_json('arb_df_bak.json', orient='records')  # Overwrite existing file if exists

    while True:
        print("\033[H\033[J")  # clear terminal
        print(arb_df)
        print("Live Market Prices:")
        print(live_market.live_market_price(arb_df))
        time.sleep(5)

