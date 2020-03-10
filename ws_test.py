from ws_bitmex import BitMEXWebsocket
import secret as keys
import logging
from time import sleep


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

        # https://www.geeksforgeeks.org/reading-writing-text-files-python/
        orderbook = logger.info("Orderbook: %s", ws.market_depth())
        #logger.info("Last ask price: %s", ws.last_order_price('asks'))
        #logger.info("Last bid price: %s", ws.last_order_price('bids'))

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
