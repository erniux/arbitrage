import logging
import tkinter as tk
from connectors.binance_client import BinanceClient
from connectors.bitmex_client import BitmexClient

import pprint

logger = logging.getLogger()

logger.setLevel(logging.DEBUG)

stream_handler=logging.StreamHandler()
file_handler = logging.FileHandler('info.log')

formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s')
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

if __name__ == '__main__':

    binance = BinanceClient(True)
    bitmex = BitmexClient(True)

    print(bitmex.get_open_orders())

    root = tk.Tk()
    root.mainloop()
