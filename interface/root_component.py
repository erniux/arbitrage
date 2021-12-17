import tkinter as tk
from interface.styling import *
from interface.logging_component import Logging
from connectors.binance import BinanceClient


class Root(tk.Tk):
    def __init__(self, binance: BinanceClient):
        super().__init__()
        self.binance = binance
        self.title("Arbitrage Bot")
        self.configure(bg = BG)
        

        self._left_frame = tk.Frame(self, bg=BG)
        self._left_frame.pack(side=tk.LEFT)

        self._right_frame = tk.Frame(self, bg=BG)
        self._right_frame.pack(side=tk.RIGHT)

        self._logging_frame = Logging(self._left_frame, bg=BG)
        self._logging_frame.pack(side=tk.TOP)

        self._update_ui()

    def _update_ui(self):
        for log in self.binance.logs:
            if not log['displayed']:
                self._logging_frame.add_log(log['log'])
                log['displayed'] = True

        self.after(1500, self._update_ui)