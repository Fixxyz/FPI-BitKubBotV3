import os
import requests
import json
import hmac
import hashlib
from dotenv import load_dotenv
from BL.LineNotifyService import SendLineNotify
load_dotenv()

url = 'https://api.bitkub.com'
key = os.environ.get('KEY')
secret = os.environ.get('SECRET').encode('utf-8')

def json_encode(data):
	return json.dumps(data, separators=(',', ':'), sort_keys=True)

def sign(data):
	j = json_encode(data)
	h = hmac.new(secret, msg=j.encode(), digestmod=hashlib.sha256)
	return h.hexdigest()

def gen_sign(api_secret, payload_string=None):
    return hmac.new(api_secret, payload_string.encode('utf-8'), hashlib.sha256).hexdigest()

def gen_query_param(url, query_param):
    req = requests.PreparedRequest()
    req.prepare_url(url, query_param)
    return req.url.replace(url,"")

def GetServerTime():
    # check server time
    response = requests.get(url + '/api/v3/servertime')
    return response.text

def GetLatestPrice(name):
    # get latest price
    response = requests.get(url + '/api/market/ticker?sym=' + name)
    result = json.loads(response.text)
    return result[name]['last']
def GetMyBalances():
    path = '/api/v3/market/wallet'
    ts = GetServerTime()
    payload = []
    payload.append(ts)
    payload.append('POST')
    payload.append(path)
    signature = gen_sign(secret,''.join(payload))
    # check balances
    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-BTK-APIKEY': key,
        'X-BTK-TIMESTAMP': ts,
        'X-BTK-SIGN': signature
    }
    response = requests.post(url + path, headers=header,data={})
    print(response.text)
    return json.loads(response.text)
def GetMyOpenOrder(symbol):
    path = '/api/v3/market/my-open-orders'
    ts = GetServerTime()
    param = {
        'sym': symbol
    }
    query_param = gen_query_param(url+path, param)
    payload = []
    payload.append(ts)
    payload.append('GET')
    payload.append(path)
    payload.append(query_param)
    signature = gen_sign(secret,''.join(payload))
    # check balances
    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-BTK-APIKEY': key,
        'X-BTK-TIMESTAMP': ts,
        'X-BTK-SIGN': signature
    }
    response = requests.get(url + path + query_param, headers=header)
    print(response.text)
    return json.loads(response.text)

def BuyOrder(symbol,amt,rat):
    ts = GetServerTime()
    path = '/api/v3/market/place-bid'
    data = {
       	'sym': symbol,
        'amt': amt,
        'rat': rat,
        'typ': 'limit',
    }
    payload = []
    payload.append(ts)
    payload.append('POST')
    payload.append(path)
    payload.append(json.dumps(data))

    signature = gen_sign(secret, ''.join(payload))
    # check balances
    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-BTK-APIKEY': key,
        'X-BTK-TIMESTAMP': ts,
        'X-BTK-SIGN': signature
    }
    response = requests.post(url + path, headers=header, data=json.dumps(data))
    print(response.text)
    return json.loads(response.text)
def SellOrder(symbol,amt,rat):
    ts = GetServerTime()
    path = '/api/v3/market/place-ask'
    data = {
       	'sym': symbol,
        'amt': amt,
        'rat': rat,
        'typ': 'limit',
    }
    payload = []
    payload.append(ts)
    payload.append('POST')
    payload.append(path)
    payload.append(json.dumps(data))
    signature = gen_sign(secret, ''.join(payload))
    # check balances
    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-BTK-APIKEY': key,
        'X-BTK-TIMESTAMP': ts,
        'X-BTK-SIGN': signature
    }
    response = requests.post(url + path, headers=header, data=json.dumps(data))
    print(response.text)
    return json.loads(response.text)
def CancelOrder(symbol,id,sd,hashkey):
    ts = GetServerTime()
    path = '/api/v3/market/cancel-order'
    data = {
       	'sym': symbol,
        'id': id,
        'sd': sd,
        'hash ': hashkey
    }
    # check balances
    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-BTK-APIKEY': key,
        'X-BTK-TIMESTAMP': ts,
        'X-BTK-SIGN': signature
    }
    response = requests.post(url + path, headers=header, data=json.dumps(data))
    print(response.text)
    return json.loads(response.text)


def CryptoTrade(targetname, targetprofit, targetlost, buyprice):
    # Get Target Price,Trade
    profitcal = 0
    msg = ""
    symbol = 'THB_' + targetname
    latestprice = GetLatestPrice(symbol)
    print(f'{targetname} Lastest price = {latestprice}')
    rate = latestprice - buyprice
    print(f'Rate = {rate}')
     # Get MyWallet
    wallet = GetMyBalances()
    amt = float(wallet['result'][targetname])
    print(f'{targetname} in my wallet amount = {amt}')
    balance = float(wallet['result']['THB'])
    print(f'My wallet THB balance = {balance}')
     # CalProfit
    if(amt > 0):
        profitcal = latestprice + targetprofit
        print(f'ProfitCal = {profitcal}')
    # Get Pending Order
    orders = GetMyOpenOrder(targetname.lower()+'_thb')
    print(f'My pending order = {orders}')
    if(any(orders['result'])):
        for order in orders['result']:
            hashkey = order['hash']
            orderRate = float(order['rate'])
            ordertype = order['side']
            id = order['id']
            profitcal = (orderRate*targetprofit) / 100
            diff = latestprice - orderRate
            print(f'ProfitCal = {profitcal} Different = {diff}')
            if(ordertype == 'SELL'):
                if(diff >= targetprofit):
                    # Cancel Order
                    CancelOrder(targetname.lower()+'_thb',id,ordertype,hashkey)
                    msg = f'Order {targetname} Was Cancel Sell'
                    print(msg)
                    SendLineNotify(msg)
            if(ordertype == 'BUY'):
                if(diff >= targetlost):
                    # Cancel Order
                    CancelOrder(targetname.lower()+'_thb',id,ordertype,hashkey)
                    msg = f'Order {targetname} Was Cancel Buy'
                    print(msg)
                    SendLineNotify(msg)

    # balance > 0 place order
    if(balance > 0):
        BuyOrder(targetname.lower()+'_thb', balance, rate)
        msg = f'Create Buy Order {targetname} with rate = {rate} balance = {balance}'
        print(msg)
        SendLineNotify(msg)

    elif (amt > 0):
        # Create SELL Order
        SellOrder(targetname.lower()+'_thb', amt, profitcal)
        msg = f'Create Sell Order {targetname} with rate = {profitcal} balance = {balance}'
        print(msg)
        SendLineNotify(msg)

    return "OK"
