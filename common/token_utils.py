import requests
from common import data_config


def get_token():
    result = requests.post(url=data_config.access_token, headers=data_config.headers, data=data_config.data)
    access_token = result.json()['access_token']
    token_type = result.json()['token_type']
    authorization = token_type + " " + access_token
    return authorization



