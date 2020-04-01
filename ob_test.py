from bitmex_book import BitMEXBook
import logging
from time import sleep
#import json
# Simplejson allows serialization of Decimal
import simplejson as json
import sys
from decimal import Decimal



# Basic use of websocket.
def run():
    logger = setup_logger()

    # Instantiating the WS will make it connect.
    ws = BitMEXBook()

    #logger.info("Instrument data: %s" % ws.get_whole_instrument())
    #ws.set_logSize()

    # Run forever
    while(ws.ws.sock.connected):
       
        # sleep(2)

        # Get all asks orders from orderbook. Working!
        rbAskOrders = ws.get_aks_orders()
        logger.info('All asks orders from orderbook: %s', rbAskOrders)
        with open('rbAskOrders.json', 'w') as f:
            json.dump(rbAskOrders, f)

        # When fromTree = True, get last ask price from the Tree, need fix to become the last of the orderbook. Need fix!
        rbLastAskPrice = ws.get_ask_price()
        logger.info('The last ask price : %s', rbLastAskPrice)
        with open('rbLastAskPrice.json', 'w') as f:
            json.dump(rbLastAskPrice, f)

        sys.exit()

        # Get the largest ask order size from the orderbook. Working!
        logger.info('The largest ask order size from the orderbook : %s', ws.get_ask_largest_size())
        
        # Get all asks order sizes from orderbook. Working!
        logger.info('All asks order sizes from orderbook : %s', ws.get_aks_sizes())
        
        # Get all asks prices from orderbook. Working!
        logger.info('All asks prices from orderbook : %s', ws.get_ask_prices())
        
        # Get all bids orders from orderbook. Working!
        #logger.info('All bids orders from oderbook: %s', ws.get_bid_orders())

        # When pull bid data without sleep(), an error occurs saying that the Tree is empty.
        # When fromTree = True, get max bid price from the Tree, need fix to become the max of the orderbook.  Need fix!
        #logger.info('The max bid price : %s', ws.get_bid_price())

        # Get the largest bid order size from the orderbook.Working!
        #logger.info('The largest bid order size from the orderbook : %s', ws.get_bid_largestsize())
        
        # Get all bids order sizes from orderbook.Working!
        #logger.info('All bids order sizes from orderbook : %s', ws.get_bid_sizes())
        
        # Get all bids prices from orderbook.Working!
        #logger.info('All bids prices from orderbook : %s', ws.get_bid_prices())

        # Get all bids and asks data from orderbook.Working!
        # logger.info('Current orderbook : %s', ws.get_current_book())

        # Get the instrument data from Bitmex orderbook. Working!
        #logger.info('Instrument data: %s', ws.get_instrument())

        # Return a ticker object. Generated from quote and trade. Working!
        #logger.info('Ticker : %s', ws.get_ticker())

        # Get whole orderbook from Bitmex. Returns all levels. Working!
        #logger.info('orderbook : %s', ws.market_depth())

        # Get Actual trade price from Bitmex orderbook. Working!
        #logger.info('Actual trade price : %s', ws.get_trade_price())

        # Get volume from Bitmex orderbook. Working!
        #logger.info('Bitmex volume : %s', ws.get_volume())

        # Get volume 24h from Bitmex orderbook. Working!
        #logger.info('Bitmex volume 24h: %s', ws.get_volume24h())

        # Get prevprice 24h from Bitmex orderbook. Working!
        #logger.info('Bitmex prevprice 24h: %s', ws.get_prevprice24h())
        
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
