from bitmex_book import BitMEXBook
import logging
from time import sleep
#import json
# Simplejson allows serialization of Decimal
import simplejson as json
import sys

DATA_DIR = 'data/'


# Basic use of websocket.
def run():
    logger = setup_logger()

    # Instantiating the WS will make it connect.
    ws = BitMEXBook()

    #logger.info("Instrument data: %s" % ws.get_whole_instrument())
    #ws.set_logSize()

    # Run forever
    while(ws.ws.sock.connected):
       
        sleep(2)
        # ## A grotesque difference between the order sizes of the orderbook and Tree in the ~10% lower Asks and dissemblance in the quantity of orders in the distinction of prices bitween the last ask price of Tree and Orderbook.
        # # Get all asks orders from orderbook.
        # rbAskOrders = ws.get_aks_orders()
        # # logger.info('All asks orders from Tree: %s', rbAskOrders)
        # with open(DATA_DIR + 'rbAskOrders.json', 'w') as f:
        #     json.dump(rbAskOrders, f)
        # with open(DATA_DIR + 'len_rbAskOrders.json', 'w') as f:
        #     json.dump(len(rbAskOrders), f)
        # obAskOrders = ws.get_aks_orders(fromTree=False)
        # # logger.info('All asks orders from orderbook: %s', obAskOrders)
        # with open(DATA_DIR + 'obAskOrders.json', 'w') as f:
        #     json.dump(obAskOrders, f)
        # with open(DATA_DIR + 'len_obAskOrders.json', 'w') as f:
        #     json.dump(len(obAskOrders), f)

        # ## Dissemblance in the quantity of orders in the distinction of prices between the last ask price of Tree and Orderbook.
        # # When fromTree = True, get last ask price from the Tree, need fix to become the last of the orderbook. Need fix!
        # rbLastAskPrice = ws.get_ask_price()
        # #logger.info('The last ask price : %s', rbLastAskPrice)
        # with open(DATA_DIR + 'rbLastAskPrice.json', 'w') as f:
        #     json.dump(rbLastAskPrice, f)
        # obLastAskPrice = ws.get_ask_price(fromTree=False)
        # #logger.info('The last ask price : %s', obLastAskPrice)
        # with open(DATA_DIR + 'obLastAskPrice.json', 'w') as f:
        #     json.dump(obLastAskPrice, f)

        # ## Working correctly.
        # rbLargestAskSize = ws.get_ask_largest_size()
        # # logger.info('The largest ask order size from the Tree : %s', rbLargestAskSize)
        # with open(DATA_DIR + 'rbLargestAskSize.json', 'w') as f:
        #     json.dump(rbLargestAskSize, f)
        # obLargestAskSize = ws.get_ask_largest_size(fromTree=False)
        # # logger.info('The largest ask order size from the orderbook : %s', obLargestAskSize)
        # with open(DATA_DIR + 'obLargestAskSize.json', 'w') as f:
        #     json.dump(obLargestAskSize, f)
        
        # ## A subtle difference of minus than 1% in the length of the order sizes
        # # Get all asks order sizes from orderbook.
        # rbAsksSizes = ws.get_aks_sizes()
        # # logger.info('All asks order sizes from Tree : %s', rbAsksSizes)
        # with open(DATA_DIR + 'rbAsksSizes.json', 'w') as f:
        #     json.dump(rbAsksSizes, f)
        # with open(DATA_DIR + 'len_rbAsksSizes.json', 'w') as f:
        #     json.dump(len(rbAsksSizes), f)
        # obAsksSizes = ws.get_aks_sizes(fromTree=False)
        # # logger.info('All asks order sizes from orderbook : %s', obAsksSizes)
        # with open(DATA_DIR + 'obAsksSizes.json', 'w') as f:
        #     json.dump(obAsksSizes, f)
        # with open(DATA_DIR + 'len_obAsksSizes.json', 'w') as f:
        #     json.dump(len(obAsksSizes), f)

        # ## The same difference in the length as the sizes of minus than 1% and 16 asks prices of Tree lower than the orderbook.
        # # Get all asks prices from orderbook.
        # rbAsksPrices = ws.get_ask_prices()
        # # logger.info('All asks prices from Tree : %s', rbAsksPrices())
        # with open(DATA_DIR + 'rbAsksPrices.json', 'w') as f:
        #     json.dump(rbAsksPrices, f)
        # with open(DATA_DIR + 'len_rbAsksPrices.json', 'w') as f:
        #     json.dump(len(rbAsksPrices), f)
        # obAsksPrices = ws.get_ask_prices(fromTree=False)
        # # logger.info('All asks prices from orderbook : %s', obAsksPrices)
        # with open(DATA_DIR + 'obAsksPrices.json', 'w') as f:
        #     json.dump(obAsksPrices, f)
        # with open(DATA_DIR + 'len_obAsksPrices.json', 'w') as f:
        #     json.dump(len(obAsksPrices), f)
        
        # ## The same problem as the ask orders: A grotesque difference between the order sizes and dissemblance in the quantity of orders in the same proportion as Asks.
        # # Get all bids orders from orderbook.
        # rbBidOrders = ws.get_bid_orders()
        # #logger.info('All bids orders from Tree: %s', rbBidOrders)
        # with open(DATA_DIR + 'rbBidOrders.json', 'w') as f:
        #     json.dump(rbBidOrders, f)
        # with open(DATA_DIR + 'len_rbBidOrders.json', 'w') as f:
        #     json.dump(len(rbBidOrders), f)
        # obBidOrders = ws.get_bid_orders(fromTree=False)
        # # logger.info('All bids orders from oderbook : %s', obBidOrders)
        # with open(DATA_DIR + 'obBidOrders.json', 'w') as f:
        #     json.dump(obBidOrders, f)
        # with open(DATA_DIR + 'len_obBidOrders.json', 'w') as f:
        #     json.dump(len(obBidOrders), f)

        # ## The same problem as Asks: dissemblance in the quantity of orders in the distinction of prices between the last ask price of Tree and Orderbook.
        # # When pull bid data without sleep(), an error occurs saying that the Tree is empty.
        # # When fromTree = True, get max bid price from the Tree, need fix to become the max of the orderbook.  Need fix!
        # rbLastBidPrice = ws.get_bid_price()
        # #logger.info('The max bid price : %s', rbLastBidPrice)
        # with open(DATA_DIR + 'rbLastBidPrice.json', 'w') as f:
        #     json.dump(rbLastBidPrice, f)
        # obLastBidPrice = ws.get_bid_price(fromTree=False)
        # # logger.info('The max bid price : %s', obLastBidPrice)
        # with open(DATA_DIR + 'obLastBidPrice.json', 'w') as f:
        #     json.dump(obLastBidPrice, f)

        # ## Working correctly.
        # # Get the largest bid order size from the orderbook
        # rbLargestBidSize = ws.get_bid_largest_size()
        # #logger.info('The largest bid order size from the Tree : %s', rbLargestBidSize)
        # with open(DATA_DIR + 'rbLargestBidSize.json', 'w') as f:
        #     json.dump(rbLargestBidSize, f)
        # obLargestBidSize = ws.get_bid_largest_size(fromTree=False)
        # # logger.info('The largest bid order size from the orderbook : %s', obLargestBidSize)
        # with open(DATA_DIR + 'obLargestBidSize.json', 'w') as f:
        #     json.dump(obLargestBidSize, f)

        # ## The same problem as Asks: a subtle difference of minus than 1% in the length of the order sizes
        # # Get all bids order sizes from orderbook
        # rbBidSizes = ws.get_bid_sizes()       
        # #logger.info('All bids order sizes from Tree : %s', rbBidSizes)
        # with open(DATA_DIR + 'rbBidSizes.json', 'w') as f:
        #     json.dump(rbBidSizes, f)
        # with open(DATA_DIR + 'len_rbBidSizes.json', 'w') as f:
        #     json.dump(len(rbBidSizes), f)
        # obBidSizes = ws.get_bid_sizes(fromTree=False)
        # # logger.info('All bids order sizes from orderbook : %s', obBidSizes)
        # with open(DATA_DIR + 'obBidSizes.json', 'w') as f:
        #     json.dump(obBidSizes, f)
        # with open(DATA_DIR + 'len_obBidSizes.json', 'w') as f:
        #     json.dump(len(obBidSizes), f)

        # ## The same difference in the length as the sizes of minus than 1% and 58 asks prices of Tree lower than the orderbook.
        # # Get all bids prices from orderbook
        # rbBidPrices = ws.get_bid_prices()
        # #logger.info('All bids prices from Tree : %s', rbBidPrices)
        # with open(DATA_DIR + 'rbBidPrices.json', 'w') as f:
        #     json.dump(rbBidPrices, f)
        # with open(DATA_DIR + 'len_rbBidPrices.json', 'w') as f:
        #     json.dump(len(rbBidPrices), f)
        # obBidPrices = ws.get_bid_prices(fromTree=False)
        # # logger.info('All bids prices from orderbook : %s', obBidPrices)
        # with open(DATA_DIR + 'obBidPrices.json', 'w') as f:
        #     json.dump(obBidPrices, f)
        # with open(DATA_DIR + 'len_obBidPrices.json', 'w') as f:
        #     json.dump(len(obBidPrices), f)

        # # Get all bids and asks data from orderbook
        # # logger.info('Current orderbook : %s', ws.get_current_book())

        # # Get the instrument data from Bitmex orderbook.
        # #logger.info('Instrument data: %s', ws.get_instrument())

        # # Return a ticker object. Generated from quote and trade.
        # #logger.info('Ticker : %s', ws.get_ticker())

        # # Get whole orderbook from Bitmex. Returns all levels.
        # #logger.info('orderbook : %s', ws.market_depth())

        # # Get Actual trade price from Bitmex orderbook.
        # #logger.info('Actual trade price : %s', ws.get_trade_price())

        # # Get volume from Bitmex orderbook.
        # #logger.info('Bitmex volume : %s', ws.get_volume())

        # # Get volume 24h from Bitmex orderbook.
        # #logger.info('Bitmex volume 24h: %s', ws.get_volume24h())

        # # Get prevprice 24h from Bitmex orderbook.
        # #logger.info('Bitmex prevprice 24h: %s', ws.get_prevprice24h())

        # # return
        logger.info(ws.data['instrument'])
        return 

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
