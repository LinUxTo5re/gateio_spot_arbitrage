import json
import spot_market
import arbitrage_handle
import live_market
import asyncio

# global variables
arb_df = ""
existing_json = new_json = ""


async def arbitrage_json():
    global arb_df
    spot_market_list = spot_market.spot_markets_list()
    spot_market_list = [market for market in spot_market_list if market['trade_status'] == 'tradable']
    spot_quote_market = spot_market.spot_quote_tradable_markets(spot_market_list)
    new_arb_df = await arbitrage_handle.create_quote_df(spot_quote_market)
    new_arb_df.to_json('arb_df_bak.json', orient='records')  # Overwrite existing file if exists
    await arbitrage_existing_json()


async def arbitrage_existing_json():
    global arb_df
    with open('arb_df_bak.json', 'r') as file:
        arb_df = json.load(file)


async def main():
    global existing_json, new_json
    try:
        try:
            new_json = asyncio.create_task(arbitrage_json())
        except Exception as e:
            print("\n", e)
        existing_json = asyncio.create_task(arbitrage_existing_json())
    except Exception as ex:
        print("\n", ex)

    await new_json
    await existing_json


async def while_loop():
    print()
    global arb_df
    while True and arb_df is not None and not arb_df == "":
        print("\033[H\033[J")  # clear terminal
        print(arb_df)
        print("Live Market Prices:")
        print(live_market.live_market_price(arb_df))
        await asyncio.sleep(5)


async def run_program():
    await asyncio.gather(main(), while_loop())


if __name__ == '__main__':
    asyncio.run(run_program())
