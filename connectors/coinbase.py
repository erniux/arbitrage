import logging
from urllib.parse import urlencode
import json, hmac, hashlib, time, requests
from requests.auth import AuthBase


logger = logging.getLogger()

'''
class CoinbaseClient:
    def __init__(self, public_key, secret_key, testnet):

        if testnet:
            self._base_url = "https://api-public.sandbox.exchange.coinbase.com"
            self._wss_url = "wss://ws-feed-public.sandbox.exchange.coinbase.com"
        else:
            self._base_url = "https://api.exchange.coinbase.com"
            self._wallet_base_url = 'https://api.coinbase.com'
            self._wss_url = "wss://fstream.binance.com/ws" #¿?

        self._public_key = public_key
        self._secret_key = secret_key
        self._api_version = '2021-11-23'



class CoinbaseWalletAuth(AuthBase):
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    def __call__(self, request):
        timestamp = str(int(time.time()))
        message = timestamp + request.method + request.path_url + (request.body or '')
        signature = hmac.new(self.secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()

        request.headers.update({
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
        })
        return request

api_url = 'https://api.coinbase.com/v2/'
auth = CoinbaseWalletAuth(API_KEY, API_SECRET)


r = requests.get(api_url + 'user', auth=auth)
print(r.json())

