import json
import spot_market
import arbitrage_handle
import live_market
import asyncio
import os

# global variables
arb_df = ""
existing_json = new_json = ""


async def arbitrage_json():
    global arb_df
    spot_market_list = spot_market.spot_markets_list()
    spot_market_list = [market for market in spot_market_list if market['trade_status'] == 'tradable']
    spot_quote_market = spot_market.spot_quote_tradable_markets(spot_market_list)
    new_arb_df = await arbitrage_handle.create_quote_df(spot_quote_market[:20])
    new_arb_df['ticker'].to_json('arb_df_bak.json', orient='records')  # Overwrite existing file if exists
    await arbitrage_existing_json()


async def arbitrage_existing_json():
    global arb_df
    with open('arb_df_bak.json', 'r') as file:
        arb_df = json.load(file)


async def run_arbitrage_json_periodically():
    while True:
        await asyncio.sleep(5400)  # sleep of 1.5 hrs
        await arbitrage_json()


async def while_loop():
    global arb_df
    while True and arb_df is not None and not arb_df == "":
        print("\033[H\033[J")  # clear terminal
        # print(arb_df)
        print("Live Market Prices:")
        print(live_market.live_market_price(arb_df))
        await asyncio.sleep(5)


async def main():
    if os.path.exists('arb_df_bak.json'):
        await arbitrage_existing_json()
        await while_loop()
    else:
        await arbitrage_json()
        await arbitrage_existing_json()
        await while_loop()
    asyncio.create_task(run_arbitrage_json_periodically())


if __name__ == '__main__':
    asyncio.run(main())
