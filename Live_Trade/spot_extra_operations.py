from shared import *
from gen_sign import gen_sign
import requests


def check_account_balance(currency):
    query_param = ''
    sign_headers = gen_sign('GET', prefix + spot_accounts_url, query_param)
    headers.update(sign_headers)
    balance_response = requests.request('GET', host + prefix + spot_accounts_url, headers=headers).json()
    return next((i['available'] for i in balance_response if i['currency'] == currency.upper()), None)
