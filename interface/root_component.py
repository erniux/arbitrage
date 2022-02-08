import logging
import tkinter as tk
from connectors.bitmex_client import BitmexClient
from connectors.binance_client import BinanceClient

from interface.styling import *
from interface.logging_component import Logging
from interface.watchlist_component import Watchlist
from interface.balances_component import ExchangesBalances

logger = logging.getLogger()


class Root(tk.Tk):
    def __init__(self, binance: BinanceClient, bitmex: BitmexClient):
        super().__init__()

        self.binance = binance
        self.bitmex = bitmex

        self.bid_binance = None
        self.bid_bitmex = None
        self.ask_binance = None
        self.ask_bitmex = None

        self.title("Trading Bot")

        self.configure(bg=BG_COLOR)

        self._left_frame = tk.Frame(self, bg=BG_COLOR)
        self._left_frame.pack(side=tk.LEFT)

        self._right_frame = tk.Frame(self, bg=BG_COLOR)
        self._right_frame.pack(side=tk.LEFT)

        self._watchlist_frame = Watchlist(self.binance.contracts, self.bitmex.contracts, self._left_frame, bg=BG_COLOR)
        self._watchlist_frame.pack(side=tk.TOP)

        self.logging_frame = Logging(self._left_frame, bg=BG_COLOR)
        self.logging_frame.pack(side=tk.TOP)

        self._balances_frame = ExchangesBalances(self.binance.balances, self.bitmex.balances, self._right_frame,
                                                 bg=BG_COLOR)
        self._balances_frame.pack(side=tk.TOP)

        self._update_ui()

    def _update_ui(self):

        # Logs

        for log in self.bitmex.logs:
            if not log['displayed']:
                self.logging_frame.add_log(log['log'])
                log['displayed'] = True

        for log in self.binance.logs:
            if not log['displayed']:
                self.logging_frame.add_log(log['log'])
                log['displayed'] = True

        # Watchlist prices

        try:
            for key, value in self._watchlist_frame.body_widgets['symbol'].items():

                symbol = self._watchlist_frame.body_widgets['symbol'][key].cget("text")
                exchange = self._watchlist_frame.body_widgets['exchange'][key].cget("text")

                if exchange == "Binance":
                    if symbol not in self.binance.contracts:
                        continue

                    if symbol not in self.binance.prices:
                        self.binance.get_bid_ask(self.binance.contracts[symbol])
                        continue

                    precision = self.binance.contracts[symbol].price_decimals

                    prices_binance = self.binance.prices[symbol]

                    if prices_binance['bid'] is not None:
                        self.bid_binance = prices_binance['bid']
                        price_str = "{0:.{prec}f}".format(prices_binance['bid'], prec=precision)
                        self._watchlist_frame.body_widgets['bid_var'][key].set(price_str)

                    if prices_binance['ask'] is not None:
                        self.ask_binance = prices_binance['ask']
                        price_str = "{0:.{prec}f}".format(prices_binance['ask'], prec=precision)
                        self._watchlist_frame.body_widgets['ask_var'][key].set(price_str)

                elif exchange == "Bitmex":
                    if symbol not in self.bitmex.contracts:
                        continue

                    if symbol not in self.bitmex.prices:
                        continue

                    precision = self.bitmex.contracts[symbol].price_decimals

                    prices_bitmex = self.bitmex.prices[symbol]

                    if prices_bitmex['bid'] is not None:
                        self.bid_bitmex = prices_bitmex['bid']
                        price_str = "{0:.{prec}f}".format(prices_bitmex['bid'], prec=precision)
                        self._watchlist_frame.body_widgets['bid_var'][key].set(price_str)
                    if prices_bitmex['ask'] is not None:
                        self.ask_bitmex = prices_bitmex['ask']
                        price_str = "{0:.{prec}f}".format(prices_bitmex['ask'], prec=precision)
                        self._watchlist_frame.body_widgets['ask_var'][key].set(price_str)

                else:
                    continue

                if self.ask_binance is not None and self.ask_bitmex is not None:
                    if self.ask_binance < self.ask_bitmex:  # (comprar en binance vender en bitmex)
                        diferencia = self.ask_bitmex - self.ask_binance
                        if diferencia >= 10:
                            self.logging_frame.add_log(f"Compra en Binance ::: {diferencia}")
                    else:
                        diferencia = self.ask_binance - self.ask_bitmex
                        if diferencia >= 10:
                            self.logging_frame.add_log(f"Compra en Bitmex ::: {diferencia}")

                if self.bid_binance is not None and self.bid_bitmex is not None:
                    if self.bid_binance < self.bid_bitmex:
                        diferencia = self.bid_bitmex - self.bid_binance
                        if diferencia >= 10:
                            self.logging_frame.add_log(f"Vende en Bitmex ::: {diferencia}")
                    else:
                        diferencia = self.bid_binance - self.bid_bitmex
                        if diferencia >= 10:
                            self.logging_frame.add_log(f"Vende en Binance ::: {diferencia}")

        except RuntimeError as e:
            logger.error(f"Error al actualizar el watchlist: {e}")

        self.after(1000, self._update_ui)
