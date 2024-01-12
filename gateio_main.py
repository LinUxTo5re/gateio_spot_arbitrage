import json
import sys
import time
import extra_operations
import pantry_cloud
import spot_market
import arbitrage_handle
import live_market
from multiprocessing import Process
from shared import file_path, sleep_timer
import os

# global variables
arb_df = ""
sleep_timer_half = sleep_timer


def arbitrage_json():
    global arb_df
    while True:
        spot_market_list = spot_market.spot_markets_list()
        spot_market_list = [market for market in spot_market_list if market['trade_status'] == 'tradable']
        spot_quote_market = spot_market.spot_quote_tradable_markets(spot_market_list)
        new_arb_df = arbitrage_handle.create_quote_df(spot_quote_market)
        new_arb_df['ticker'].to_json(file_path, orient='records')  # Overwrite existing file if exists
        pantry_cloud.create_replace_basket(new_arb_df)
        arbitrage_existing_json()
        # 900 == 15 minutes
        time.sleep(sleep_timer)  # sleeping to avoid more api calls and data get renewed to find fresh data


def arbitrage_existing_json():
    global arb_df
    pantry_cloud.create_replace_basket(is_download=True)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            arb_df = json.load(file)


def while_loop(timer=20):  # timer == sleep_time
    global arb_df, sleep_timer_half
    arbitrage_existing_json()
    while True:
        arbitrage_existing_json()
        if len(arb_df):
            print("Live Market Prices:")
            print("\n", live_market.live_market_price(arb_df).to_string(index=False))
            time.sleep(timer)  # take a breath
            extra_operations.clear_terminal()  # clear terminal
        else:
            print("sleeping for half............")
            sleep_timer_half = sleep_timer_half / 2
            time.sleep(sleep_timer_half)


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
