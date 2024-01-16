import json
import sys
import time
import pantry_cloud
import spot_market
import arbitrage_handle
import live_market
from multiprocessing import Process
from shared import file_path, sleep_timer, file_name
import os
import signal
from extra_operations import wake_up_bro, clear_terminal, signal_handler

# global variables
updated_arb_df = ""
sleep_timer_half = sleep_timer


def arbitrage_json():
    global updated_arb_df
    while True:
        try:
            print("\n [new json data] Fetching Started............")
            spot_market_list = spot_market.spot_markets_list()
            spot_market_list = [market for market in spot_market_list if market['trade_status'] == 'tradable']
            spot_quote_market = spot_market.spot_quote_tradable_markets(spot_market_list)
            new_arb_df = arbitrage_handle.create_quote_df(spot_quote_market)
            new_arb_df['ticker'].to_json(file_path, orient='records')  # Overwrite existing file if exists
            pantry_cloud.create_replace_basket(new_arb_df)
            arbitrage_existing_json()
            print(f"\n [new json data] Total Live Markets(>2%): {len(updated_arb_df)}")
            new_datetime = wake_up_bro(sleep_timer)
            print(f"\n [new json data] will wake up at: {new_datetime[0]}:{new_datetime[1]}:{new_datetime[2]}")
            # 1800 == 30 minutes
            time.sleep(sleep_timer)  # sleeping to avoid more api calls and data get renewed to find fresh data
        except Exception:
            clear_terminal()  # clear terminal


def arbitrage_existing_json():
    global updated_arb_df
    print(f"\n Downloading {file_name} ..........")
    pantry_cloud.create_replace_basket(is_download=True)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            updated_arb_df = json.load(file)
    print(f"\n Download Completed for {file_name}")


def while_loop(timer=20):  # timer == sleep_time
    global sleep_timer_half, updated_arb_df
    arbitrage_existing_json()
    arb_df = updated_arb_df
    while True:
        try:
            if len(arb_df):
                if len(updated_arb_df) > 0:
                    arb_df = updated_arb_df
                    updated_arb_df = ""
                print(f"\n Fetching {len(arb_df)} Live Market Started .......")
                print("\n", live_market.live_market_price(arb_df).to_string(index=False))
                while_new_datetime = wake_up_bro(timer)
                print(
                    f"\n [while_loop] will wake up at: {while_new_datetime[0]}:{while_new_datetime[1]}:{while_new_datetime[2]}")
                time.sleep(timer)  # take a breath
            else:
                sleep_timer_half = sleep_timer_half / 2
                print(f"\n [while_loop] sleeping for {sleep_timer_half} seconds............")
                time.sleep(sleep_timer_half)
        except Exception:
            clear_terminal()  # clear terminal


if __name__ == '__main__':
    try:
        signal.signal(signal.SIGINT, signal_handler)  # Terminate on CTRL + C
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
    except Exception:
        clear_terminal()  # clear terminal
