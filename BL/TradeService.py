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

def GetServerTime():
    # check server time
    response = requests.get(url + '/api/servertime')
    return int(response.text)

def GetLatestPrice(name):
    # get latest price
    response = requests.get(url + '/api/market/ticker?sym=' + name)
    result = json.loads(response.text)
    return result[name]['last']
def GetMyBalances():
    ts = GetServerTime()
    # check balances
    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-BTK-APIKEY': key,
    }
    data = {
        'ts': ts,
    }
    signature = sign(data)
    data['sig'] = signature
    response = requests.post(url + '/api/market/wallet', headers=header, data=json_encode(data))
    print(response.text)
    return json.loads(response.text)
def GetMyOpenOrder(symbol):
    ts = GetServerTime()
    # check balances
    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-BTK-APIKEY': key,
    }
    data = {
        'ts': ts,
        'sym': symbol
    }
    signature = sign(data)
    data['sig'] = signature
    response = requests.post(url + '/api/market/my-open-orders', headers=header, data=json_encode(data))
    print(response.text)
    return json.loads(response.text)

def BuyOrder(symbol,amt,rat):
    ts = GetServerTime()
    # check balances
    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-BTK-APIKEY': key,
    }
    data = {
        'ts': ts,
       	'sym': symbol,
        'amt': amt,
        'rat': rat,
        'typ': 'limit',
    }
    signature = sign(data)
    data['sig'] = signature
    response = requests.post(url + '/api/market/v2/place-bid', headers=header, data=json_encode(data))
    print(response.text)
    return json.loads(response.text)
def SellOrder(symbol,amt,rat):
    ts = GetServerTime()
    # check balances
    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-BTK-APIKEY': key,
    }
    data = {
        'ts': ts,
       	'sym': symbol,
        'amt': amt,
        'rat': rat,
        'typ': 'limit',
    }
    signature = sign(data)
    data['sig'] = signature
    response = requests.post(url + '/api/market/v2/place-ask', headers=header, data=json_encode(data))
    print(response.text)
    return json.loads(response.text)
def CancelOrder(symbol,id,sd,hashkey):
    ts = GetServerTime()
    # check balances
    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-BTK-APIKEY': key,
    }
    data = {
        'ts': ts,
       	'sym': symbol,
        'id': id,
        'sd': sd,
        'hash ': hashkey,
        'typ': 'limit',
    }
    signature = sign(data)
    data['sig'] = signature
    response = requests.post(url + '/api/market/v2/cancel-order', headers=header, data=json_encode(data))
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
    orders = GetMyOpenOrder(symbol)
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
                    CancelOrder(symbol,id,ordertype,hashkey)
                    msg = f'Order {targetname} Was Cancel Sell'
                    print(msg)
                    SendLineNotify(msg)
            if(ordertype == 'BUY'):
                if(diff >= targetlost):
                    # Cancel Order
                    CancelOrder(symbol,id,ordertype,hashkey)
                    msg = f'Order {targetname} Was Cancel Buy'
                    print(msg)
                    SendLineNotify(msg)

    # balance > 0 place order
    if(balance > 0):
        BuyOrder(symbol, balance, rate)
        msg = f'Create Buy Order {targetname} with rate = {rate} balance = {balance}'
        print(msg)
        SendLineNotify(msg)

    elif (amt > 0):
        # Create SELL Order
        SellOrder(symbol, amt, profitcal)
        msg = f'Create Sell Order {targetname} with rate = {profitcal} balance = {balance}'
        print(msg)
        SendLineNotify(msg)

    return "OK"
