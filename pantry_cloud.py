import time

import requests
import json
from shared import pantry_id, file_name as basket_name, file_path
import os


#  get account details and list of baskets
def get_account_details():
    url = f'https://getpantry.cloud/apiv1/pantry/{pantry_id}'
    return requests.get(url).json()


# create or replace existing basket with new data
def create_replace_basket(json_data=None, is_download=False):
    if is_download:
        try:
            downloaded_json_data = download_file()
            if not downloaded_json_data == "NO DATA":
                dict_data = list(downloaded_json_data.json().keys())
                with open(file_path, 'w') as file:
                    json.dump(dict_data, file)
        except Exception as e:
            print(f"\n Warning: can't load data from pantry cloud to {basket_name}, sleeping: 30s ")
            time.sleep(30)
    else:
        upload_file(json_data)


# upload json to pantry cloud
def upload_file(json_data=None):
    headers = {
        'Content-Type': 'application/json'
    }
    url = f'https://getpantry.cloud/apiv1/pantry/{pantry_id}/basket/{basket_name}'
    json_data = handle_json_for_upload(json_data)
    payload = json.dumps(json_data)
    requests.request("POST", url, headers=headers, data=payload)


# transfer json into compatible json format for pantry cloud
def handle_json_for_upload(json_data):
    data_with_ticker_parent = {}
    for element in json_data["ticker"]:
        data_with_ticker_parent[element] = element
    return data_with_ticker_parent


# download json from pantry cloud
def download_file():
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
        url = f"https://getpantry.cloud/apiv1/pantry/{pantry_id}/basket/{basket_name}"
        payload = ""
        headers = {
            'Content-Type': 'application/json'
        }
        return requests.request("GET", url, headers=headers, data=payload)
    except Exception as e:
        return "NO DATA"
