import tkinter as tk

from interface.styling import *
import typing
from models import *


class ExchangesBalances(tk.Frame):
    def __init__(self, binance_balances: typing.Dict[str, Balance], bitmex_balances: typing.Dict[str, Balance],
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.binance_symbols = list(binance_balances.items())
        self.bitmex_symbols = list(bitmex_balances.items())



