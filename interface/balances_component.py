import tkinter as tk
import typing

from interface.styling import *

from connectors.binance_client import BinanceClient
from connectors.bitmex_client import BitmexClient


class StrategyEditor(tk.Frame):
    def __init__(self, root, binance: BinanceClient, bitmex: BitmexClient, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.root = root

        self._exchanges = {"Binance": binance, "Bitmex": bitmex}
        for exchange, client in self._exchanges.items():
            for symbol, contract in client.balances.items():
                self._all_contracts.append(symbol + "_" + exchange.capitalize())