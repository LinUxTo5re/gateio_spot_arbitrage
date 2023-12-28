import asyncio
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
    spot_market_list = spot_market.spot_markets_list()
    spot_market_list = [market for market in spot_market_list if market['trade_status'] == 'tradable']
    spot_quote_market = spot_market.spot_quote_tradable_markets(spot_market_list)
    # returns df with combinations of all usdt and remove unwanted rows from df
    arb_df = arbitrage_handle.create_quote_df(spot_quote_market)
##