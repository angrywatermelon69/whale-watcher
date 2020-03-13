from ws_bitmex import BitMEXWebsocket
import secret as keys
import logging
from time import sleep
import json
from decimal import Decimal


# Basic use of websocket.
def run():
    logger = setup_logger()

    # Instantiating the WS will make it connect. Be sure to add your api_key/api_secret.
    # ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1", symbol="XBTUSD",
    ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1", symbol="XBTUSD",
                         api_key=keys.bitmex_key, api_secret=keys.bitmex_secret)

    #logger.info("Instrument data: %s" % ws.get_whole_instrument())
    #ws.set_logSize()

    # Run forever
    while(ws.ws.sock.connected):
       
        # logger.info("Last ask price: %s", ws.last_order_price('asks'))
        # logger.info("Last bid price: %s", ws.last_order_price('bids'))

        # orderbook = logger.info("Orderbook: %s", ws.market_depth()) 
        

        # -----------------------------------------------------------------------------------------------------------------------------------------------------------
        # ---------------------------------------------------Bitmex Orderbook----------------------------------------------------------------------------------------
        # -----------------------------------------------------------------------------------------------------------------------------------------------------------
        # -----------------------------------------------------------------------------------------------------------------------------------------------------------
        orderbook_data = ws.market_depth()
        
        # with open ('orderbook_data', 'w') as json_file:
        #     json.dump(orderbook_data, json_file)

        print(get_maxprice_bids(orderbook_data))
        sleep(2)
        

# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------Bitmex Data Fields--------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------
def get_last_orderid(orderbook_data):
    last_orderid = [order['id'] for order in orderbook_data]
    return last_orderid[-1]

def get_minprice_asks(orderbook_data):
    order_asks = [order for order in orderbook_data if order['side']  == 'Sell']
    price_asks = [order['price'] for order in order_asks]
    return min(price_asks)

def get_largest_ask(orderbook_data):
    order_asks = [order for order in orderbook_data if order['side']  == 'Sell']
    largest_ask = [order['size'] for order in order_asks]
    return max(largest_ask)

def get_largest_bid(orderbook_data):
    order_bids = [order for order in orderbook_data if order['side']  == 'Buy']
    largest_bid = [order['size'] for order in order_bids]
    return max(largest_bid)

# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------Bitmex Actual Price-------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------
def get_maxprice_bids(orderbook_data):
    order_bids = [order for order in orderbook_data if order['side']  == 'Buy']
    price_bids = [order['price'] for order in order_bids]
    return max(price_bids)
    


def setup_logger():
    # Prints logger info to terminal
    logger = logging.getLogger()
   
    
    #logger.setLevel(logging.DEBUG)  # Change this to DEBUG if you want a lot more info
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


if __name__ == "__main__":
    run()
