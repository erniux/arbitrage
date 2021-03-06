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
from strategies import TechnicalStrategy, BreakoutStrategy

logger = logging.getLogger()


class BinanceClient:
    def __init__(self, testnet: bool):

        if testnet:
            self._base_url = secrets.BINANCE_SPOT_TESTNET_URL
            self._wss_url = secrets.BINANCE_SPOT_TESTNET_WS_URL
            self._api_key = secrets.BINANCE_SPOT_TESTNET_API_KEY
            self._secret_key = secrets.BINANCE_SPOT_TESTNET_SECRET_KEY
            self._e_binance = ccxt.binance({
                'apiKey': secrets.BINANCE_SPOT_TESTNET_API_KEY,
                'secret': secrets.BINANCE_SPOT_TESTNET_SECRET_KEY,
                'enableRateLimit': True})

            self._e_binance.set_sandbox_mode(testnet)
        else:
            self._api_key = secrets.BINANCE_SPOT_API_URL
            self._secret_key = secrets.BINANCE_SPOT_SECRET_KEY
            self._base_url = secrets.BINANCE_SPOT_API_URL
            self._wss_url = secrets.BINANCE_SPOT_WS_URL
            self._e_binance = ccxt.binance({
                'apiKey': secrets.BINANCE_SPOT_TESTNET_API_KEY,
                'secret': secrets.BINANCE_SPOT_TESTNET_SECRET_KEY,
                'enableRateLimit': True})

        self.headers = {'X-MBX-APIKEY': self._api_key}
        self.contracts = self.get_contracts()
        self.balances = self.get_balances()
        self.prices = dict()
        self.strategies: typing.Dict[int, typing.Union[TechnicalStrategy, BreakoutStrategy]] = dict()

        self.logs = []

        self._ws_id = 1
        self._ws = None

        t = threading.Thread(target=self._start_ws)
        t.start()

        logger.info("BINANCE SE HA INICIADO...")

    def _add_log(self, msg: str):
        self.logs.append({"log": msg, "displayed": False})

    def _generate_signature(self, data: typing.Dict):
        return hmac.new(self._secret_key.encode("utf-8"), urlencode(data).encode("utf-8"), hashlib.sha256).hexdigest()

    def _make_request(self, method: str, endpoint: str, data: typing.Dict):
        if method == 'GET':
            try:
                response = requests.get(self._base_url + endpoint, params=data, headers=self.headers)
            except Exception as e:
                logger.error(f"Error en conexion al hacer {method} a {endpoint} : {e}")
        elif method == 'POST':
            try:
                response = requests.post(self._base_url + endpoint, params=data, headers=self.headers)
            except Exception as e:
                logger.error(f"Error en conexion al hacer {method} a {endpoint} : {e}")
        elif method == 'DELETE':
            try:
                response = requests.delete(self._base_url + endpoint, params=data, headers=self.headers)
            except Exception as e:
                logger.error(f"Error en conexion al hacer {method} a {endpoint} : {e}")
        else:
            raise ValueError()

        if response.status_code == 200:
            return response.json()
        else:
            logger.error("CANT DETERMNE WHAT HAPPENED %s", response.status_code)

    def get_contracts(self):
        exchange_info = self._make_request("GET", "/api/v3/exchangeInfo", None)
        contracts = dict()

        if exchange_info is not None:
            for contract_data in exchange_info['symbols']:
                contracts[contract_data['symbol']] = Contract(contract_data, "binance")

        return contracts

    def get_balances(self):
        data = dict()
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self._generate_signature(data)
        account_data = self._make_request("GET", "/api/v3/account", data)
        balances = dict()
        if account_data is not None:
            for a in account_data['balances']:
                balances[a['asset']] = Balance(a, "binance")

        return balances

    def get_historical_candles(self, contract: Contract, interval: str, limit=1000):

        raw_candles = self._e_binance.fetch_ohlcv(contract.symbol, interval, limit)
        candles = []
        if raw_candles is not None:
            for c in raw_candles:
                candles.append(Candle(c, 'binance'))

        return candles

    def get_bid_ask(self, contract: Contract):
        tickers = self._e_binance.fetch_ticker(contract.symbol)

        if tickers is not None:
            if contract.symbol not in self.prices:
                self.prices[contract.symbol] = {'bid': float(tickers['bid']), 'ask': float(tickers['ask'])}
            else:
                self.prices[contract.symbol]['bid'] = float(tickers['bid'])
                self.prices[contract.symbol]['ask'] = float(tickers['ask'])

            return self.prices[contract.symbol]

    def place_order(self, contract: Contract, side: str, quantity: float, order_type: str, price=None, tif=None):
        data = dict()
        data['symbol'] = contract.symbol
        data['side'] = side
        data['quantity'] = quantity
        data['type'] = order_type

        if price is not None:
            data['price'] = price

        if tif is not None:
            data['timeInForce'] = tif

        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self._generate_signature(data)

        order_status = self._make_request("POST", "/api/v3/order", data)

        if order_status is not None:
            order_status = OrderStatus(order_status, 'binance')

        return order_status

    def cancel_order(self, contract: Contract, order_id: int):
        data = dict()
        data['orderId'] = order_id
        data['symbol'] = contract.symbol
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self._generate_signature(data)

        order_status = self._make_request("DELETE", "/api/v3/order", data)

        if order_status is not None:
            order_status = OrderStatus(order_status, 'binance')

        return order_status

    def get_order_status(self, contract: Contract, order_id: id):
        data = dict()
        data['orderId'] = order_id
        data['symbol'] = contract.symbol
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self._generate_signature(data)

        order_status = self._make_request("GET", "/api/v3/order", data)
        if order_status is not None:
            order_status = OrderStatus(order_status, 'binance')

        return order_status

    def get_current_open_orders(self):
        data = dict()
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self._generate_signature(data)

        orders_open = self._make_request("GET", "/api/v3/openOrders", data)

        if orders_open is not None:
            return orders_open

    def get_cancel_open_orders(self, contract: Contract):
        data = dict()
        data['symbol'] = contract.symbol
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self._generate_signature(data)

        orders_cancel = self._make_request("DELETE", "/api/v3/openOrders", data)

        if orders_cancel is not None:
            return orders_cancel

    def _start_ws(self):
        self._ws = websocket.WebSocketApp(self._wss_url, on_open=self._on_open, on_close=self._on_close,
                                          on_error=self._on_error, on_message=self._on_message)
        while True:
            try:
                self._ws.run_forever()
            except Exception as e:
                logger.error("Binance error in run_forever() method: %s", e)
            time.sleep(2)

    def _on_open(self, ws):
        logger.info("Binance connection opened")

        self.subscribe_channel(list(self.contracts.values()), "bookTicker")

    def _on_close(self, ws):
        logger.warning("Binance Websocket connection closed")

    def _on_error(self, ws, msg: str):
        logger.error("Binance connection error: %s", msg)

    def _on_message(self, ws, msg: str):

        data = json.loads(msg)

        if "u" in data:
            symbol = data['s']

            if symbol not in self.prices:
                self.prices[symbol] = {'bid': float(data['b']), 'ask': float(data['a'])}
            else:
                self.prices[symbol]['bid'] = float(data['b'])
                self.prices[symbol]['ask'] = float(data['a'])

            # self._add_log(f"BINANCE::: {symbol} ::: BID :::: {str(self.prices[symbol]['bid'])} | "
            #               f" ASK :::: {str(self.prices[symbol]['ask'])}")

    def subscribe_channel(self, contracts: typing.List[Contract], channel: str):
        data = dict()
        data['method'] = "SUBSCRIBE"
        data['params'] = []
        for contract in contracts:
            data['params'].append(contract.symbol.lower() + "@" + channel)
        data['id'] = self._ws_id

        try:
            self._ws.send(json.dumps(data))
        except Exception as e:
            logger.error("Websocket error while subscribing to %s %s updates: %s", len(contracts), channel, e)

        self._ws_id += 1
