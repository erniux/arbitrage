
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
            self.timestamp = info[0]
            self.open = float(info[1])
            self.high = float(info[2])
            self.low = float(info[3])
            self.close = float(info[4])
            self.volume = float(info[5])
        elif exchange == 'bitmex':
            self.timestamp = info['timestamp']
            self.open = info['open']
            self.high = info['high']
            self.low = info['low']
            self.close = info['close']
            self.volume = info['volume']


class Contract:
    def __init__(self, contract_info, exchange):
        if exchange == 'binance':
            self.symbol = contract_info['symbol']
            self.base = contract_info['baseAsset']
            self.quote = contract_info['quoteAsset']
            self.base_asset_precision = contract_info['baseAssetPrecision']
            self.base_commission_precission = contract_info['baseCommissionPrecision']
        elif exchange == 'bitmex':
            self.symbol = contract_info['symbol']
            self.base = contract_info['rootSymbol']
            self.quote = contract_info['quoteCurrency']
            self.base_asset_precision = contract_info["tickSize"]
            self.quote_precision = contract_info["lotSize"]


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

