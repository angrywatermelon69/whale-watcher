from ws_bitmex import BitMEXWebsocket
import logging
from time import sleep
import json
from decimal import Decimal



# Basic use of websocket.
def run():
    logger = setup_logger()

    # Instantiating the WS will make it connect.
    ws = BitMEXWebsocket()

    #logger.info("Instrument data: %s" % ws.get_whole_instrument())
    #ws.set_logSize()

    # Run forever
    while(ws.ws.sock.connected):
       
        # logger.info("Last ask price: %s", ws.last_order_price('asks'))
        # logger.info("Last bid price: %s", ws.last_order_price('bids'))

        # orderbook = logger.info("Orderbook: %s", ws.market_depth()) 
        

        # with open ('orderbook_data', 'w') as json_file:
        #     json.dump(orderbook_data, json_file)
    
        print(ws.get_ask_price())
        sleep(2)

        
        

def setup_logger():
    # Prints logger info to terminal
    logger = logging.getLogger()
   
    
    logger.setLevel(logging.DEBUG)  # Change this to DEBUG if you want a lot more info
    #logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


if __name__ == "__main__":
    run()
