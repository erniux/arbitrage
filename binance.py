import logging
import requests

logger = logging.getLogger()


def get_contracts():
    response = requests.get("https://fapi.binance.com/fapi/v1/exchangeInfo")
    print(response.status_code, response.json())


get_contracts()