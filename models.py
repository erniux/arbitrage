from datetime import datetime

BITMEX_MULTIPLIER = 0.00000001


class Balance:
    def __init__(self, info, exchange):
        if exchange == 'binance':
            self.asset = info['asset']
            self.free = float(info['free'])
            self.locked = float(info['locked'])
        elif exchange == 'bitmex':
            self.currency = info['currency']
            self.amount = (info['amount']) * BITMEX_MULTIPLIER
            self.free = (info['availableMargin']) * BITMEX_MULTIPLIER


class Candle:
    def __init__(self, info, exchange):
        if exchange == 'binance':
            self.timestamp = datetime.fromtimestamp(int(info[0]/1000))
            self.open = float(info[1])
            self.high = float(info[2])
            self.low = float(info[3])
            self.close = float(info[4])
            self.volume = float(info[5])
        elif exchange == 'bitmex':
            self.timestamp = datetime.fromtimestamp(int(info[0]/1000))
            self.open = info[1]
            self.high = info[2]
            self.low = info[3]
            self.close = info[4]
            self.volume = info[5]


def tick_to_decimals(tick_size: float) -> int:
    tick_size_str = "{0:.8f}".format(tick_size)
    while tick_size_str[-1] == "0":
        tick_size_str = tick_size_str[:-1]

    split_tick = tick_size_str.split(".")

    if len(split_tick) > 1:
        return len(split_tick[1])
    else:
        return 0


class Contract:
    def __init__(self, contract_info, exchange):
        if exchange == 'binance':
            self.symbol = contract_info['symbol']
            self.base = contract_info['baseAsset']
            self.quote = contract_info['quoteAsset']
            self.filters = contract_info['filters']
            self.price_decimals = 1
            filters = contract_info['filters']
            for f in filters:
                if f['filterType'] == 'PRICE_FILTER':
                    self.tick_size = f['tickSize']

        elif exchange == 'bitmex':
            self.symbol = contract_info['symbol']
            self.base = contract_info['rootSymbol']
            self.quote = contract_info['quoteCurrency']
            self.tick_size = contract_info["tickSize"]
            self.lot_size = contract_info["lotSize"]
            self.price_decimals = tick_to_decimals(contract_info['tickSize'])


class OrderStatus:
    def __init__(self, order_info, exchange):
        if exchange == 'binance':
            self.order_id = order_info['orderId']
            self.status = order_info['status']
            self.price = order_info['price']
            self.original_qty = order_info['origQty']
            self.execued_qty = order_info['executedQty']
        elif exchange == 'bitmex':
            self.order_id = order_info['orderID']
            self.status = order_info['ordStatus']
            self.avg_price = order_info['avgPx']

