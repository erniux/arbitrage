import ccxt

e_kucoin = ccxt.kucoin()
e_kucoin.set_sandbox_mode(True)

"""e_bitmart = ccxt.bitmart()
e_bitmart.set_sandbox_mode(True)"""

"""e_ftx = ccxt.ftx()
e_ftx.set_sandbox_mode(True)"""

"""e_huobi = ccxt.huobi()
e_huobi.set_sandbox_mode(True)"""

e_okex = ccxt.okex()
e_okex.set_sandbox_mode(True)

e_coinbasepro = ccxt.coinbasepro()
e_coinbasepro.set_sandbox_mode(True)

e_bitmex = ccxt.bitmex()
e_bitmex.set_sandbox_mode(True)

"""e_poloniex = ccxt.poloniex()
e_poloniex.set_sandbox_mode(True)"""

e_idex = ccxt.idex()
e_idex.set_sandbox_mode(True)

"""e_cex = ccxt.cex()
e_cex.set_sandbox_mode(True)"""

"""e_bittrex = ccxt.bittrex()
e_bittrex.set_sandbox_mode(True)"""

"""e_kraken = ccxt.kraken()
e_kraken.set_sandbox_mode(True)"""

e_crypto = ccxt.cryptocom()
e_crypto.set_sandbox_mode(True)

e_gemini = ccxt.gemini()
e_gemini.set_sandbox_mode(True)

e_binance = ccxt.binance()
e_binance.set_sandbox_mode(True)
print(e_binance.fetch_tickers("BTC/USDT"))
print(e_binance.fetch_ohlcv("BTC/USDT", "1m", limit=5))
