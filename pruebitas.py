import time
import requests
import hashlib
import hmac
import secrets

def hashing(query_string):
    return hmac.new(secrets.BINANCE_SPOT_TESTNET_SECRET_KEY.encode('utf-8'),
                    query_string.encode('utf-8'),
                    hashlib.sha256).hexdigest()

base_url = "https://testnet.binance.vision"
api_path = "/api/v3/order"
timestamp = int(time.time()*1000)
msg = "symbol=BNBUSDT&side=BUY&type=LIMIT&quantity=1&timeInForce=GTC&price=200&timestamp={}".format(timestamp)
msg_hash = hashing(msg)

url = f"{base_url}{api_path}?{msg}&signature={msg_hash}"

print(url)

headers = {'Content-Type': 'application/json;charset=utf-8',
                    'X-MBX-APIKEY': secrets.BINANCE_SPOT_TESTNET_API_KEY}

print("nusing python-requests")
with requests.Session() as session:
    session.headers.update(headers)
    resp = session.put(url)
    print(resp)


print("nusing curl")
# curl -H "X-MBX-APIKEY: {API_KEY}" -X POST "{url}"