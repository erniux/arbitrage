import tkinter as tk
import logging
import secrets
from connectors.binance import BinanceClient

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

if __name__=='__main__':

    binance = BinanceClient(secrets.BINANCE_FUTURE_TESTNET_API_KEY, secrets.BINANCE_FUTURE_TESTNET_SECRET_KEY, True) 

    binance.get_balances()
    root = tk.Tk()
    root.mainloop()
