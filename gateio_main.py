import json
import sys
import time
import extra_operations
import spot_market
import arbitrage_handle
import live_market
from multiprocessing import Process

# global variables
arb_df = ""


def arbitrage_json():
    global arb_df
    while True:
        spot_market_list = spot_market.spot_markets_list()
        spot_market_list = [market for market in spot_market_list if market['trade_status'] == 'tradable']
        spot_quote_market = spot_market.spot_quote_tradable_markets(spot_market_list)
        new_arb_df = arbitrage_handle.create_quote_df(spot_quote_market)
        new_arb_df['ticker'].to_json('arb_df_bak.json', orient='records')  # Overwrite existing file if exists
        arbitrage_existing_json()
        # 900 == 15 m
        time.sleep(900)  # sleeping to avoid more api calls and data get renewed to find fresh data


def arbitrage_existing_json():
    global arb_df
    with open('arb_df_bak.json', 'r') as file:
        arb_df = json.load(file)


def while_loop(timer=5):  # timer == sleep_time
    global arb_df
    arbitrage_existing_json()
    while True and arb_df is not None and not arb_df == "":
        arbitrage_existing_json()
        if len(arb_df):
            print("Live Market Prices:")
            print("\n", live_market.live_market_price(arb_df).to_string(index=False))
            time.sleep(timer)  # take a breath
            extra_operations.clear_terminal()  # clear terminal
        else:
            time.sleep(timer*5)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        function_name = sys.argv[1]
        if function_name == 'while_loop':
            if len(sys.argv) > 2:
                sleep_time = int(sys.argv[2])
                while_loop(sleep_time)
    else:
        process_while_loop = Process(target=while_loop)
        process_new_json = Process(target=arbitrage_json)
        process_while_loop.start()
        process_new_json.start()
        # no needed in our case, it blocks the execution of rest of code after .start()
        '''
        process_while_loop.join()
        process_new_json.join()
        '''
