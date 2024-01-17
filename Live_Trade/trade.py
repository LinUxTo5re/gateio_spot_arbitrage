import sys
import spot_market
from gen_sign import gen_sign
from shared import *
import requests
from spot_extra_operations import check_account_balance

is_arbitrage_completed = 0

'''
currency_pair: BTC_USDT
price: ask_bid_price for limit order
BUY:
    side: buy
    amount: quote asset ex- 10 USDT
SELL:
    side: sell
    amount: 0 (to sell all available coins of that pair)
'''


def create_an_order(currency_pair, side, ask_bid_price, amount):
    query_param = ''
    amount = 0 if side == 'sell' else amount
    body = f'{"currency_pair":{currency_pair},"type":"limit","account":"spot","side":{side},"amount":{amount},"price":{ask_bid_price}}'
    # for `gen_sign` implementation, refer to section `Authentication` above
    sign_headers = gen_sign('POST', prefix + spot_create_order_url, query_param, body)
    headers.update(sign_headers)
    order_response = requests.request('POST', host + prefix + spot_create_order_url, headers=headers, data=body).json()
    print(order_response)
    return order_response


def track_buy_order(currency_pair, side, ask_bid_price):
    order_response = create_an_order(currency_pair, side, ask_bid_price, trade_amount)
    order_id = order_response['id']
    query_param = f'currency_pair={order_response['currency_pair']}'
    # for `gen_sign` implementation, refer to section `Authentication` above
    sign_headers = gen_sign('GET', prefix + track_single_order_url + order_id, query_param)
    headers.update(sign_headers)
    status_finished = False
    while not status_finished:
        tracker_response = requests.request('GET',
                                            host + prefix + track_single_order_url + order_id + "?" + query_param,
                                            headers=headers).json()
        print(tracker_response)
        status_finished = True if tracker_response['status'] == 'finished' else False
    return True


'''
ask: sellers are willing to sell
bid: buyers are willing to buy
'''


def order_initialization(market, buy_quote_name, sell_quote_name=''):
    available_bal = check_account_balance(buy_quote_name)
    if available_bal >= trade_amount:
        ask_data, bid_data = spot_market.spot_order_book(market.upper() + '_' + buy_quote_name.upper(), True)
        if float(ask_data[0]) * float(ask_data[1]) >= trade_amount:  # buy order
            track_buy_order(market.upper() + '_' + buy_quote_name.upper(), 'buy', float(ask_data[0]))
        ask_data, bid_data = spot_market.spot_order_book(market.upper() + '_' + sell_quote_name.upper(), True)
        if float(bid_data[0]) * float(bid_data[1]) >= trade_amount:  # sell order
            track_buy_order(market.upper() + '_' + buy_quote_name.upper(), 'buy', float(bid_data[0]))
        print(f"\n Trade executed successfully \n PNL: ")  # TO DO
    else:
        print(f"\n Insufficient {buy_quote_name}  Avl Bal: {available_bal} \n Existing.....")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        market_name = sys.argv[1]
        if len(sys.argv) > 3:
            buy_quote = sys.argv[2]
            sell_quote = sys.argv[3]
            order_initialization(market_name, buy_quote)
    # create_an_order()
