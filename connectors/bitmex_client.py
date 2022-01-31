import time
import requests
from urllib.parse import urlencode
import hmac
import hashlib
import ccxt
import websocket
import threading
import json
import logging
import typing

import secrets
from models import Balance, Candle, Contract, OrderStatus

logger = logging.getLogger()


class BitmexClient:
    def __init__(self, testnet: bool):

        if testnet:
            self._base_url = secrets.BITMEX_SPOT_TESTNET_URL
            self._wss_url = secrets.BITMEX_SPOT_TESTNET_WS_URL
            self._api_key = secrets.BITMEX_SPOT_TESTNET_API_KEY
            self._secret_key = secrets.BITMEX_SPOT_TESTNET_SECRET_KEY
            self._e_bitmex = ccxt.bitmex({
                'apiKey': secrets.BITMEX_SPOT_TESTNET_API_KEY,
                'secret': secrets.BITMEX_SPOT_TESTNET_SECRET_KEY,
                'enableRateLimit': True})

            self._e_bitmex.set_sandbox_mode(testnet)
        else:
            self._base_url = secrets.BITMEX_SPOT_API_URL
            self._wss_url = secrets.BITMEX_SPOT_WS_URL
            self._api_key = secrets.BITMEX_SPOT_API_URL
            self._secret_key = secrets.BITMEX_SPOT_SECRET_KEY
            self._e_bitmex = ccxt.bitmex({
                'apiKey': secrets.BITMEX_SPOT_TESTNET_API_KEY,
                'secret': secrets.BITMEX_SPOT_TESTNET_SECRET_KEY,
                'enableRateLimit': True})

        self._ws = None

        self.contracts = self.get_contracts()
        self.balances = self.get_balances()

        self.prices = dict()

        # t = threading.Thread(target=self._self.start_ws)
        # t.start()

        logger.info("BITMEX SE HA INICIADO...")

    def _generate_signature(self, method: str, endpoint: str,  expires: str, data: typing.Dict):
        message = method + endpoint + "?" + urlencode(data) + expires if len(data) > 0 else method + endpoint + expires
        return hmac.new(self._secret_key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest()

    def _make_request(self, method: str, endpoint: str, data: typing.Dict):

        headers = dict()
        expires = str(int(time.time() + 5))
        headers['api-expires'] = expires
        headers['api-key'] = self._api_key
        headers['api-signature'] = self._generate_signature(method, endpoint, expires, data)
        if method == 'GET':
            try:
                response = requests.get(self._base_url + endpoint, params=data, headers=headers)
            except Exception as e:
                logger.error(f"Error en conexion al hacer {method} a {endpoint} : {e}")
        elif method == 'POST':
            try:
                response = requests.post(self._base_url + endpoint, params=data, headers=headers)
            except Exception as e:
                logger.error(f"Error en conexion al hacer {method} a {endpoint} : {e}")
        elif method == 'DELETE':
            try:
                response = requests.delete(self._base_url + endpoint, params=data, headers=headers)
            except Exception as e:
                logger.error(f"Error en conexion al hacer {method} a {endpoint} : {e}")
        else:
            raise ValueError()

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"ERROR EN REQUEST {method}, {endpoint}: {response.json()}, {response.status_code} ")

    def get_contracts(self) -> typing.Dict[str, Contract]:
        instruments = self._make_request("GET", "/api/v1/instrument/active", dict())

        contracts = dict()

        if instruments is not None:

            for contract_data in instruments:
                contracts[contract_data['symbol']] = contract_data  # Contract(contract_data, 'bitmex')

        return contracts

    def get_balances(self) -> typing.Dict[str, Balance]:
        data = dict()
        data['currency'] = "all"

        margin_data = self._make_request("GET", "/api/v1/user/margin", data)
        account_data = self._e_bitmex.fetch_balance(data)

        return margin_data


