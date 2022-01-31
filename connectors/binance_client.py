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


class BinanceClient:
    def __init__(self, testnet: bool):

        logger.info("BINANCE SE HA INICIADO...")

        if testnet:
            self.base_url = secrets.BINANCE_SPOT_TESTNET_URL
            self.wss_url = secrets.BINANCE_SPOT_TESTNET_WS_URL
            self.api_key = secrets.BINANCE_SPOT_TESTNET_API_KEY
            self.secret_key = secrets.BINANCE_SPOT_TESTNET_SECRET_KEY
            self.e_binance = ccxt.binance({
                'apiKey': secrets.BINANCE_SPOT_TESTNET_API_KEY,
                'secret': secrets.BINANCE_SPOT_TESTNET_SECRET_KEY,
                'enableRateLimit': True})

            self.e_binance.set_sandbox_mode(testnet)
        else:
            self.api_key = secrets.BINANCE_SPOT_API_URL
            self.secret_key = secrets.BINANCE_SPOT_SECRET_KEY
            self.base_url = secrets.BINANCE_SPOT_API_URL
            self.wss_url = secrets.BINANCE_SPOT_WS_URL
            self.e_binance = ccxt.binance({
                'apiKey': secrets.BINANCE_SPOT_TESTNET_API_KEY,
                'secret': secrets.BINANCE_SPOT_TESTNET_SECRET_KEY,
                'enableRateLimit': True})

        self.headers = {'X-MBX-APIKEY': self.api_key}
        self.contracts = self.get_contracts()
        self.balances = self.get_balances()
        self.prices = dict()

        self.id = 1
        self.ws = None

        t = threading.Thread(target=self.start_ws())
        t.start

    def generate_signature(self, data: typing.Dict):
        return hmac.new(self.secret_key.encode("utf-8"), urlencode(data).encode("utf-8"), hashlib.sha256).hexdigest()

    def get_timestamp(self):
        server_time = self.make_request("GET", "/api/v3/time", None)
        return server_time['serverTime']

    def make_request(self, method: str, endpoint: str, data: typing.Dict):
        if method == 'GET':
            response = requests.get(self.base_url + endpoint, params=data, headers=self.headers)
        elif method == 'POST':
            response = requests.post(self.base_url + endpoint, params=data, headers=self.headers)
        elif method == 'DELETE':
            response = requests.delete(self.base_url + endpoint, params=data, headers=self.headers)
        else:
            raise ValueError()

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"ERROR EN REQUEST {method}, {endpoint}: {response.json()}, {response.status_code} ")

    def get_contracts(self):
        markets = self.make_request("GET", "/api/v3/exchangeInfo", None)
        contracts = dict()

        if markets is not None:
            for m in markets['symbols']:
                print(m['quoteAsset'], m)
                contracts[m['symbol']] = m  # Contract(m)

        return contracts

    def get_historical_candles(self, contract: Contract, interval: str, limit=1000):

        raw_candles = self.e_binance.fetch_ohlcv(contract.symbol, interval, limit)
        candles = []
        if raw_candles is not None:
            for c in raw_candles:
                candles.append(Candle(c))

        return candles

    def get_bid_ask(self, contract: Contract):
        tickers = self.e_binance.fetch_ticker(contract.symbol)

        if tickers is not None:
            if contract.symbol not in self.prices:
                self.prices[contract.symbol] = {'bid': float(tickers['bid']), 'ask': float(tickers['ask'])}
            else:
                self.prices[contract.symbol]['bid'] = float(tickers['bid'])
                self.prices[contract.symbol]['ask'] = float(tickers['ask'])

            return self.prices[contract.symbol]

    def get_balances(self):
        balances = dict()
        account_data = self.e_binance.fetch_balance()
        if account_data is not None:
            for a in account_data['info']['balances']:
                balances[a['asset']] = Balance(a)

        return balances

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
        data['signature'] = self.generate_signature(data)

        order_status = self.make_request("POST", "/api/v3/order", data)

        if order_status is not None:
            order_status = OrderStatus(order_status)

        return order_status

    def cancel_order(self, contract: Contract, order_id: int):
        data = dict()
        data['orderId'] = order_id
        data['symbol'] = contract.symbol
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self.generate_signature(data)

        order_status = self.make_request("DELETE", "/api/v3/order", data)

        if order_status is not None:
            order_status = OrderStatus(order_status)

        return order_status

    def get_order_status(self, contract: Contract, order_id: id):
        data = dict()
        data['orderId'] = order_id
        data['symbol'] = contract.symbol
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self.generate_signature(data)

        order_status = self.make_request("GET", "/api/v3/order", data)
        if order_status is not None:
            order_status = OrderStatus(order_status)

        return order_status

    def get_current_open_orders(self):
        data = dict()
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self.generate_signature(data)

        orders_open = self.make_request("GET", "/api/v3/openOrders", data)

        if orders_open is not None:
            return orders_open

    def cancel_open_orders(self, contract: Contract):
        data = dict()
        data['symbol'] = contract.symbol
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self.generate_signature(data)

        orders_cancel = self.make_request("DELETE", "/api/v3/openOrders", data)

        if orders_cancel is not None:
            return orders_cancel

    def start_ws(self):
        self.ws = websocket.WebSocketApp(self.wss_url, on_open=self.on_open, on_close=self.on_close,
                                         on_message=self.on_message, on_error=self.on_error)
        self.ws.run_forever()
        return

    def on_open(self, ws):
        logger.info("Conexion abierta en Binance")
        self.subscribe_channel("BTCUSDT")

    def on_close(self, ws):
        logger.info("Conexion cerrada en Binance")

    def on_error(self, msg: str):
        logger.error(f"Error de conexión Binance {msg}")

    def on_message(self, ws, msg: str):
        data = json.loads(msg)
        if "s" in data:
            symbol = data['s']
            if symbol not in self.prices:
                self.prices[symbol] = {'bid': float(data['b']), 'ask': float(data['a'])}
            else:
                self.prices[symbol]['bid'] = float(data['b'])
                self.prices[symbol]['ask'] = float(data['a'])

                print(symbol, self.prices[symbol])

    def subscribe_channel(self, contract: Contract):
        data = dict()
        data['method'] = "SUBSCRIBE"
        data['params'] = []
        data['params'].append(contract.symbol.lower() + "@bookTicker")
        data['id'] = self.id

        self.ws.send(json.dumps(data))

        self.id = self.id + 1
