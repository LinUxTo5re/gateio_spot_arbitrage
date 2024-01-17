from gen_sign import gen_sign
from shared import *
import requests

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


def create_an_order(currency_pair, side, ask_bid_price, amount=0):
    query_param = ''
    body = f'{"currency_pair":{currency_pair},"type":"limit","account":"spot","side":{side},"amount":{amount},"price":{ask_bid_price}}'
    # for `gen_sign` implementation, refer to section `Authentication` above
    sign_headers = gen_sign('POST', prefix + spot_create_order_url, query_param, body)
    headers.update(sign_headers)
    order_response = requests.request('POST', host + prefix + spot_create_order_url, headers=headers, data=body).json()
    print(order_response)


if __name__ == '__main__':
    pass
    # create_an_order()
