

class Balance:
    def __init__(self, info, exchange):
        if exchange == 'binance':
            self.asset = info['asset']
            self.free = float(info['free'])
            self.locked = float(info['locked'])
        elif exchange == 'bitmex':
            self.asset = info['asset']
            self.free = float(info['free'])
            self.locked = float(info['locked'])


class Candle:
    def __init__(self, info):
        self.timestamp = info[0]
        self.open = float(info[1])
        self.high = float(info[2])
        self.low = float(info[3])
        self.close = float(info[4])
        self.volume = float(info[5])


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
    def __init__(self, order_info):
        self.order_id = order_info['orderId']
        self.status = order_info['status']
        self.price = order_info['price']
        self.original_qty = order_info['origQty']
        self.execued_qty = order_info['executedQty']