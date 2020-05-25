from bitmex_book import BitMEXBook
import logging
from time import sleep
#import json
# Simplejson allows serialization of Decimal
import simplejson as json
import sys
import datetime as dt
DATA_DIR = 'data/'
today = dt.datetime.today().strftime('%Y-%m-%d')
import bitmex

# Basic use of websocket.
def getLastPrice():
    result = bitmex.bitmex(test=False).Instrument.Instrument_get(symbol='XBTUSD', reverse=True).result()[0][0]['timestamp']
    return result


def run():
    logger = setup_logger()

    # Instantiating the WS will make it connect.
    ws = BitMEXBook()
    #logger.info("Instrument data: %s" % ws.get_whole_instrument())
    #ws.set_logSize()

    # Run forever
    while(ws.ws.sock.connected):
       
        # sleep(2)
        
        # try:
        # with open(DATA_DIR + 'orders/orders' + '_' + today + '.json') as f:
        #     orders = json.load(f)
            # except:
            #     orders = {}
        
        
        logger.info(ws._asks)
        
        # logger.info(getLastPrice())
        # logger.info(dt.datetime.utcnow())
        # logger.info('---------------------------------')
        sleep(1)
        # return 



def setup_logger():
    # Prints logger info to terminal
    logger = logging.getLogger()
    
    # logger.setLevel(logging.DEBUG)  # Change this to DEBUG if you want a lot more info
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
