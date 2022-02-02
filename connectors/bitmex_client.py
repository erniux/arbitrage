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
            self._api_key = ''
            self._secret_key = ''
            self._e_bitmex = ccxt.bitmex({
                'apiKey': secrets.BITMEX_SPOT_TESTNET_API_KEY,
                'secret': secrets.BITMEX_SPOT_TESTNET_SECRET_KEY,
                'enableRateLimit': True})

        self._ws = None

        self.contracts = self.get_contracts()
        self.balances = self.get_balances()

        self.prices = dict()

        self.logs = []

        t = threading.Thread(target=self._start_ws)
        t.start()

        logger.info("BITMEX SE HA INICIADO...")

    def _add_log(self, msg: str):
        logger.info(f"{msg}")
        self.logs.append({"log": msg, "displayed": False})

    def _generate_signature(self, method: str, endpoint: str, expires: str, data: typing.Dict):
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
            logger.error(
                f"ERROR EN REQUEST {method}, {endpoint}: {response.json()}, {response.status_code}, {response.request.headers} ")

    def get_contracts(self) -> typing.Dict[str, Contract]:
        instruments = self._make_request("GET", "/api/v1/instrument/active", dict())

        contracts = dict()

        if instruments is not None:

            for contract_data in instruments:
                contracts[contract_data['symbol']] = Contract(contract_data, 'bitmex')

        return contracts

    def get_balances(self) -> typing.Dict[str, Balance]:
        data = dict()
        data['currency'] = "all"
        account_data = self._make_request("GET", "/api/v1/user/margin", data)

        balances = dict()
        if account_data is not None:
            for a in account_data:
                balances[a['currency']] = Balance(a, "bitmex")

        return balances

    def get_historical_candles(self, contract: Contract, timeframe: str):
        raw_candles = self._e_bitmex.fetch_ohlcv(contract.symbol, timeframe)
        candles = []
        if raw_candles is not None:
            for c in raw_candles:
                candles.append(Candle(c, 'bitmex'))

        return candles

    def place_order(self, contract: Contract, order_type: str, quantity: int, side: str, price=None, tif=None):
        data = dict()
        data['symbol'] = contract.symbol
        data['side'] = side.capitalize()
        data['orderQty'] = quantity
        data['orderType'] = order_type.capitalize()

        if price is not None:
            data['price'] = price

        if tif is not None:
            data['timeInForce'] = tif

        order_status = self._make_request("POST", "/api/v1/order", data)

        if order_status is not None:
            order_status = OrderStatus(order_status, "bitmex")

        return order_status

    def cancel_order(self, order_id: str):
        data = dict()
        data['orderID'] = order_id

        order_status = self._make_request("DELETE", "/api/v1/order", data)

        if order_status is not None:
            order_status = OrderStatus(order_status[0], "bitmex")

        return order_status

    def get_order_status(self, order_id: str, contract: Contract):
        data = dict()
        data['symbol'] = contract.symbol
        data['reverse'] = True

        order_status = self._make_request("GET", "/api/v1/order", data)

        if order_status is not None:
            for order in order_status:
                if order['orderID'] == order_id:
                    return OrderStatus(order, 'bitmex')

    def _start_ws(self):
        self._ws = websocket.WebSocketApp(self._wss_url, on_open=self._on_open, on_close=self._on_close,
                                          on_message=self._on_message, on_error=self._on_error)
        while True:
            try:
                self._ws.run_forever()
            except Exception as e:
                logger.error(f"Error en el metodo 'run_forever' Bitmex: {e}")
            time.sleep(2)

    def _on_open(self, _ws):
        logger.info("Conexion abierta en Bitmex")
        self.subscribe_channel("instrument")

    def _on_close(self, _ws):
        logger.info("Conexion cerrada en Bitmex")

    def _on_error(self, msg):
        logger.error(f"Error de conexión Bitmex {msg}")

    def _on_message(self, _ws, msg: str):
        data = json.loads(msg)
        if "table" in data:
            if data['table'] == "instrument":
                for d in data['data']:
                    symbol = d['symbol']

                    if symbol not in self.prices:
                        self.prices[symbol] = {'bid': None, 'ask': None}

                    if 'bidPrice' in d:
                        self.prices[symbol]['bid'] = d['bidPrice']

                    if 'askPrice' in d:
                        self.prices[symbol]['ask'] = d['askPrice']

    def subscribe_channel(self, topic: str):
        data = dict()
        data['op'] = "subscribe"
        data['args'] = []
        data['args'].append(topic)

        try:
            self._ws.send(json.dumps(data))
        except Exception as e:
            logger.error(f"Error en websocket de Bitmex al actualizar {topic} :: {e}")
