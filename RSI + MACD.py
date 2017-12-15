import urllib
import urllib2
import json
import time
import hmac,hashlib
import sys
import datetime
sys.setrecursionlimit(1000000000)


def createTimeStamp(datestr, format="%Y-%m-%d %H:%M:%S"):
    return time.mktime(time.strptime(datestr, format))

class poloniex:
    def __init__(self, APIKey, Secret):
        self.APIKey = APIKey
        self.Secret = Secret

    def post_process(self, before):
        after = before

        # Add timestamps if there isnt one but is a datetime
        if('return' in after):
            if(isinstance(after['return'], list)):
                for x in xrange(0, len(after['return'])):
                    if(isinstance(after['return'][x], dict)):
                        if('datetime' in after['return'][x] and 'timestamp' not in after['return'][x]):
                            after['return'][x]['timestamp'] = float(createTimeStamp(after['return'][x]['datetime']))
                            
        return after

    def api_query(self, command, req={}):

        if(command == "returnTicker" or command == "return24Volume"):
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + command))
            return json.loads(ret.read())
        elif(command == "returnOrderBook"):
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + command + '&currencyPair=' + str(req['currencyPair'])))
            return json.loads(ret.read())
        elif(command == "returnMarketTradeHistory"):
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + "returnTradeHistory" + '&currencyPair=' + str(req['currencyPair'])))
            return json.loads(ret.read())
        elif (command == "returnChartData"):
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + command + '&currencyPair='+ pair + '&start=' + startTime + '&end=' + endTime + '&period=' + period))
            return json.loads(ret.read()) 
        else:
            req['command'] = command
            req['nonce'] = int(time.time()*1000)
            post_data = urllib.urlencode(req)

            sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest()
            headers = {
                'Sign': sign,
                'Key': self.APIKey
            }

            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/tradingApi', post_data, headers))
            jsonRet = json.loads(ret.read())
            return self.post_process(jsonRet)


    def returnTicker(self):
        return self.api_query("returnTicker")

    def return24Volume(self):
        return self.api_query("return24Volume")

    def returnOrderBook (self, currencyPair):
        return self.api_query("returnOrderBook", {'currencyPair': currencyPair})

    def returnMarketTradeHistory (self, currencyPair):
        return self.api_query("returnMarketTradeHistory", {'currencyPair': currencyPair})
    def returnChartData(self, pair, startTime, endTime, period):
        return self.api_query("returnChartData",{"currencyPair":pair,"start":startTime,"end":endTime,"period":period})


    # Returns all of your balances.
    # Outputs: 
    # {"BTC":"0.59098578","LTC":"3.31117268", ... }
    def returnBalances(self):
        return self.api_query('returnBalances')

    # Returns your open orders for a given market, specified by the "currencyPair" POST parameter, e.g. "BTC_XCP"
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs: 
    # orderNumber   The order number
    # type          sell or buy
    # rate          Price the order is selling or buying at
    # Amount        Quantity of order
    # total         Total value of order (price * quantity)
    def returnOpenOrders(self,currencyPair):
        return self.api_query('returnOpenOrders',{"currencyPair":currencyPair})


    # Returns your trade history for a given market, specified by the "currencyPair" POST parameter
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs: 
    # date          Date in the form: "2014-02-19 03:44:59"
    # rate          Price the order is selling or buying at
    # amount        Quantity of order
    # total         Total value of order (price * quantity)
    # type          sell or buy
    def returnTradeHistory(self,currencyPair):
        return self.api_query('returnTradeHistory',{"currencyPair":currencyPair})

    # Places a buy order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is buying at
    # amount        Amount of coins to buy
    # Outputs: 
    # orderNumber   The order number
    def buy(self,currencyPair,rate,amount):
        return self.api_query('buy',{"currencyPair":currencyPair,"rate":rate,"amount":amount})

    # Places a sell order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is selling at
    # amount        Amount of coins to sell
    # Outputs: 
    # orderNumber   The order number
    def sell(self,currencyPair,rate,amount):
        return self.api_query('sell',{"currencyPair":currencyPair,"rate":rate,"amount":amount})

    # Cancels an order you have placed in a given market. Required POST parameters are "currencyPair" and "orderNumber".
    # Inputs:
    # currencyPair  The curreny pair
    # orderNumber   The order number to cancel
    # Outputs: 
    # succes        1 or 0
    def cancel(self,currencyPair,orderNumber):
        return self.api_query('cancelOrder',{"currencyPair":currencyPair,"orderNumber":orderNumber})

    # Immediately places a withdrawal for a given currency, with no email confirmation. In order to use this method, the withdrawal privilege must be enabled for your API key. Required POST parameters are "currency", "amount", and "address". Sample output: {"response":"Withdrew 2398 NXT."} 
    # Inputs:
    # currency      The currency to withdraw
    # amount        The amount of this coin to withdraw
    # address       The withdrawal address
    # Outputs: 
    # response      Text containing message about the withdrawal
    def withdraw(self, currency, amount, address):
        return self.api_query('withdraw',{"currency":currency, "amount":amount, "address":address})

class Memoize(object):
    def __init__(self,f):
        self.f = f
        self.memo = {}
    def __call__(self,*args):
        if args in self.memo:
            return self.memo[args]
        result = self.f(*args)
        self.memo[args] = result
        return result


#####################################################################    



conn = poloniex('key goes here','key goes here')
pair = "BTC_EMC2"
startTime = str (time.mktime(datetime.datetime.strptime("15/11/2017 00:00:00", "%d/%m/%Y %H:%M:%S").timetuple()))
endTime = str(time.time())
period = str (1800)

x = conn.returnChartData(pair, startTime, endTime, period)


def close(date):
    for i in range (len(x)):
        if date == x[i]["date"]:
            return x[i]["close"]

def SMA(date, n):
    y = 0
    for i in range (n):
        y+= close(x[i]["date"])
    return float(y) / n




@Memoize
def EMA(pair, date, n):
    if date ==x[n-1]["date"]:
        return SMA(date, n)
    z = (close(date) - EMA(pair, date - int(period), n) )* 2 / (n+1) + EMA(pair, date - int(period), n)
    return z


def MACD(date, f, s):
    z = EMA(pair, date, f) - EMA(pair, date, s)
    return z



@Memoize
def MACD_signal(pair, date, f, s, p):
    list_MACD = []
    for i in range (s-1, s-1+p):
        list_MACD.append(MACD(x[i]["date"], f, s))
    y = sum(list_MACD)/p
    if date == x[s-2+p]["date"]:
        return y
    z = (MACD(date, f, s) - MACD_signal(pair,date - int(period), f, s, p))*2/float(p+1) + MACD_signal(pair, date-int(period), f, s, p)
    return z


def MACD_histo(date, f, s, p):
    z = MACD(date, f, s) - MACD_signal(pair, date, f, s, p)
    return z


@Memoize
def GAIN(date, p , pair):
    g = 0
    for i in range (p):
        s = x[i+1]["close"] - x[i]["close"]
        if s > 0:
            g += s
    if date == x[p]["date"]:
        return float(g) / p
    f = close(date) - close(date - int(period))
    if f > 0:
        z = float(GAIN(date - int(period), p , pair) * (p-1) + f) / p
        return z
    else:
        z = float(GAIN(date - int(period), p , pair) * (p-1)) / p
        return z


@Memoize
def LOSS(date, p ,pair):
    l = 0
    for i in range (p):
        s = x[i+1]["close"] - x[i]["close"]
        if s < 0:
            l += -s
    if date == x[p]["date"]:
        return float(l) / p
    f = close(date) - close(date - int(period))
    if f < 0:
        z = float(LOSS(date - int(period), p , pair) * (p-1) - f) / p
        return z
    else:
        z = float(LOSS(date - int(period), p , pair) * (p-1)) / p
        return z

def RSI(date , p):
    z = 100 - 100 / float(1 + GAIN(date, p , pair) / float(LOSS(date, p , pair)))
    return z

def date (d):
    z = int(time.mktime(datetime.datetime.strptime(d, "%d/%m/%Y %H:%M:%S").timetuple()))
    return z

def fdate (d):
    z =  datetime.datetime.fromtimestamp( int(d) ).strftime('%Y-%m-%d %H:%M:%S')
    return z
    
list_pairs = ["USDT_NXT","USDT_BTC","USDT_STR","USDT_XMR","USDT_ETC","USDT_XRP","USDT_LTC","USDT_ETH","USDT_ZEC","USDT_REP","USDT_DASH","USDT_BCH"]

"""for date in range (date("12/12/2017 00:00:00"), int(float(endTime)),1800):
	m = fdate(date)
	print (float("%.2f"%RSI(date, 14)), float("%.2f"%MACD_histo(date, 12, 26, 9)), m)"""
