import os

# shared data
host = "https://api.gateio.ws"
prefix = "/api/v4"
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
spot_ticker_info_url = '/spot/tickers'
spot_currency_pairs_url = '/spot/currency_pairs'
spot_order_book_url = '/spot/order_book'
spot_candlestick_url = '/spot/candlesticks'
btc_eth_list = ['BTC_USDT', 'ETH_USDT']
quote_list = ['_USDT', '_ETH', '_BTC']
binance_ticker_price_url = "https://api.binance.com/api/v3/ticker/price?symbol="
pantry_id = "4122e2b2-0c3d-44e3-87dd-5dcd191d1b38"  # No personal data has been uploaded
folder_name = "JSON"
file_name = "arb_df_bak.json"
file_path = os.path.join(os.getcwd(), folder_name, file_name)
sleep_timer = 1800
max_usdt_price = 10.00  # filter coins less than max_usdt_price
trade_amount = 10.00  # every trade will be of worth of trade_amount
exclude_price_diffr = 0.2
exclude_price_diffr_pct = 2
assumed_usdt_fee = 0.04  # fee on one complete Transaction (buy and sell == one Transaction)

'''
SPOT ORDERS
'''
spot_create_order_url = '/spot/orders'
track_single_order_url = '/spot/orders/'
spot_accounts_url = '/spot/accounts'

