import time
import requests
import hashlib
import hmac
import xlrd
import sys,os

# Give the location of the file
path = (os.path.dirname(os.path.realpath(__file__)))
loc = (path + '\input.xlsx')
 
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)
 
# For row 0 and column 0
sheet.cell_value(0, 0)

TICK_INTERVAL = 20  # seconds
API_KEY = '85b78349c6ae4021afa1f6e6f8998f83'
API_SECRET_KEY = b'4df4a7af2b36447ca943db741b49ed65'

def main():
    print('Starting trader bot...')

    while True:
        start = time.time()
        tick()
        end = time.time()

        # Sleep the thread if needed
        if end - start < TICK_INTERVAL:
            time.sleep(TICK_INTERVAL - (end - start))


def tick():
    print('Running routine')

    for i in range(sheet.nrows):
        #Retreive row of input - one position per row
        mkt = sheet.cell_value(i,0)
        quantity = sheet.cell_value(i,1)
        stopPrice = sheet.cell_value(i,2)
        targetPrice = sheet.cell_value(i,3)
        print('\nMarket:' + mkt + ', Qty:' + str(quantity) + ', Stop:' + "%.8f" % stopPrice + ', Target:' + "%.8f" % targetPrice)

      
        market_summaries = simple_reqest('https://bittrex.com/api/v1.1/public/getmarketsummary?market=BTC-' + mkt)

        for summary in market_summaries['result']:
            market = summary['MarketName']
            day_close = summary['PrevDay']
            last = summary['Last']
            currBid = summary['Bid']
            activator = 0
            actStop = 0
            actTgt = 0

            activateStop = stopPrice*1.02
            activateTarget = targetPrice*0.98

            #ONLY ACTIVATE ORDER ENTRY WHEN PRICE IS CLOSE TO OUR DESIRED LEVELS
            if last <= activateStop:
                activator = 1
                actStop = 1
                actTgt = 0
                print(' - ' + mkt + ' Last Price:' + "%.8f" % last + ' - STOP ORDER ACTIVATED!')
            elif last >= activateTarget:
                activator = 1
                actStop=0
                actTgt=1
                pprint(' - ' + mkt + ' Last Price:' + "%.8f" % last + ' - TARGET ORDER ACTIVATED!')              
            else:
                activator = 0

        #TEST FOR ACTIVATION
        if activator:
            #TEST ORDER LOGIC
            if last <= stopPrice:
                #do we have any open orders?
                if has_open_order(market, 'LIMIT_SELL'):
                    print('\n' + market + " already has an order in place.")
                else:
                    print(" - Sell stop order sent!") #res = sell_limit(market, quantity, stopPrice)
            elif actStop:
                print('Last price is still above sell level! Last: ' "%.8f" % last + ' Stop: ' + "%.8f" % stopPrice)

           #TEST ORDER LOGIC
            if last >= targetPrice:
                #do we have any open orders?
                if has_open_order(market, 'LIMIT_SELL'):
                    print('\n' + market + " already has an order in place.")
                else:
                   print('Sell target order sent!') #res = sell_limit(market, quantity, targetPrice)
            elif actTgt:
                print('Last price is still below target level! Last: ' "%.8f" % last + ' Target: ' + "%.8f" % targetPrice)
        else:
            print(" - Price is within normal parameters, No activation for " + mkt)        
            

def buy_limit(market, quantity, rate):
    url = 'https://bittrex.com/api/v1.1/market/buylimit?apikey=' + API_KEY + '&market=' + market + '&quantity=' + str(quantity) + '&rate=' + format_float(rate)
    return signed_request(url)


def sell_limit(market, quantity, rate):
    url = 'https://bittrex.com/api/v1.1/market/selllimit?apikey=' + API_KEY + '&market=' + market + '&quantity=' + str(quantity) + '&rate=' + format_float(rate)
    return signed_request(url)


def get_open_orders(market):
    url = 'https://bittrex.com/api/v1.1/market/getopenorders?apikey=' + API_KEY + '&market=' + market
    return signed_request(url)


def has_open_order(market, order_type):
    orders_res = get_open_orders(market)
    orders = orders_res['result']

    if orders is None or len(orders) == 0:
        return False

    # Check all orders for a LIMIT_BUY
    for order in orders:
        if order['OrderType'] == order_type:
            return True

    return False


def signed_request(url):
    now = time.time()
    url += '&nonce=' + str(now)
    signed = hmac.new(API_SECRET_KEY, url.encode('utf-8'), hashlib.sha512).hexdigest()
    headers = {'apisign': signed}
    r = requests.get(url, headers=headers)
    return r.json()


def simple_reqest(url):
    r = requests.get(url)
    return r.json()


def format_float(f):
    return "%.8f" % f


if __name__ == "__main__":
    main()