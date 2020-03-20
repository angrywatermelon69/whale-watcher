# -*- coding: utf-8 -*-

# - OrderBook Websocket Thread -
# 🦏 **** quan.digital **** 🦏

# authors: canokaue & thomgabriel
# date: 03/2020
# kaue@engineer.com

# Simplified implementation of connecting to BitMEX websocket for streaming realtime orderbook data.

# Code based on stock Bitmex API connectors - https://github.com/BitMEX/api-connectors/tree/master/official-ws/python

# The Websocket offers a bunch of data as raw properties right on the object.
# On connect, it synchronously asks for a push of all this data then returns.
# Docs: https://www.bitmex.com/app/wsAPI

import websocket
import threading
import traceback
from time import sleep
import json
import logging
import urllib
import math
from decimal import Decimal
from bintrees import RBTree

# Websocket timeout in seconds
CONN_TIMEOUT = 5

# Don't grow a table larger than this amount. Helps cap memory usage.
MAX_TABLE_LEN = 200

class BitMEXWebsocket:

    def __init__(self, endpoint="https://www.bitmex.com/api/v1", symbol='XBTUSD', api_key=None, api_secret=None):
        '''Connect to the websocket and initialize data stores.'''
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing WebSocket.")

        self.endpoint = endpoint
        self.symbol = symbol

        if api_key is not None and api_secret is None:
            raise ValueError('api_secret is required if api_key is provided')
        if api_key is None and api_secret is not None:
            raise ValueError('api_key is required if api_secret is provided')

        self.api_key = api_key
        self.api_secret = api_secret

        self.data = {}
        self.keys = {}
        self.exited = False
        self._asks = RBTree()
        self._bids = RBTree()

        # We can subscribe right in the connection querystring, so let's build that.
        # Subscribe to all pertinent endpoints
        wsURL = self.__get_url()
        self.logger.info("Connecting to %s" % wsURL)
        self.__connect(wsURL, symbol)
        self.logger.info('Connected to WS.')

        # Connected. Wait for partials
        self.__wait_for_symbol(symbol)
        if api_key:
            self.__wait_for_account()
        self.logger.info('Got all market data. Starting.')

    def init(self):
        self.logger.debug("Initializing WebSocket...")

        self.data = {}
        self.keys = {}
        self.exited = False

        wsURL = self.__get_url()
        self.logger.info("Connecting to URL -- %s" % wsURL)
        self.__connect(wsURL, self.symbol)
        self.logger.info('Connected to WS.')

        # Connected. Wait for partials
        self.__wait_for_symbol(self.symbol)
        if self.api_key:
            self.__wait_for_account()
        self.logger.info('Got all market data. Starting.')

    def error(self, err):
        self._error = err
        self.logger.error(err)
        #self.exit()

    def __del__(self):
        self.exit()

    def reset(self):
        self.logger.warning('Websocket resetting...')
        self.ws.close()
        self.logger.info('Weboscket closed.')
        self.logger.info('Restarting...')
        self.init()

    def exit(self):
        '''Call this to exit - will close websocket.'''
        self.exited = True
        self.ws.close()

    # -----------------------------------------------------------------------------------------
    # ----------------------Bitmex Data Fields-------------------------------------------------
    # -----------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------

    def get_instrument(self):
        '''Get the raw instrument data for this symbol.'''
        instrument = self.data['instrument'][0]
        return instrument

    def get_ticker(self):
        '''Return a ticker object. Generated from quote and trade.'''
        lastQuote = self.data['quote'][-1]
        lastTrade = self.data['trade'][-1]
        ticker = {
            "last": lastTrade['price'],
            "buy": lastQuote['bidPrice'],
            "sell": lastQuote['askPrice'],
            "mid": (float(lastQuote['bidPrice'] or 0) + float(lastQuote['askPrice'] or 0)) / 2
        }

        # The instrument has a tickSize. Use it to round values.
        instrument = self.data['instrument'][0]
        return {k: toNearest(float(v or 0), instrument['tickSize']) for k, v in ticker.items()}

    def market_depth(self):
        '''Get whole market depth (orderbook). Returns all levels.'''
        return self.data['orderBookL2']
   
    ### Ask (sell) functions

    def get_ask_price(self):
        orderbook = self.data["orderBookL2"]
        order_asks = [order for order in orderbook if order['side']  == 'Sell']
        price_asks = [order['price'] for order in order_asks]
        return min(price_asks)

    def get_largest_ask(self):
        orderbook = self.data["orderBookL2"]
        order_asks = [order for order in orderbook if order['side']  == 'Sell']
        largest_ask = [order['size'] for order in order_asks]
        return max(largest_ask)
    
    def get_ask_prices(self):
        orderbook = self.data["orderBookL2"]
        ask_prices = [order['price'] for order in orderbook if order['side']  == 'Sell']
        return ask_prices

    ### Bid (buy) functions

    def get_bid_price(self):
        orderbook = self.data['orderBookL2']
        order_bids = [order for order in orderbook if order['side']  == 'Buy']
        price_bids = [order['price'] for order in order_bids]
        return max(price_bids)

    def get_largest_bid(self):
        orderbook = self.data["orderBookL2"]
        order_bids = [order for order in orderbook if order['side']  == 'Buy']
        size_bids = [order['size'] for order in order_bids]
        return max(size_bids)

    def get_bid_prices(self):
        orderbook = self.data["orderBookL2"]
        bid_prices = [order['price'] for order in orderbook if order['side']  == 'Buy']
        return bid_prices

    ### Miscelaneous Bitmex data functions

    def get_trade_price(self):
        last_trade = self.data['trade']
        price_trade = [order['price'] for order in last_trade]
        return price_trade[-1]

    def get_volume(self):
        instrument = self.data['instrument']
        volume = instrument['instrument'][0]['volume']
        return volume
    
    def get_volume24h(self):
        volume24h = self.data['instrument'][0]['volume24h']
        return volume24h

    def get_prevprice24h(self):
        prevprice24h = self.data['instrument'][0]['prevPrice24h']
        return prevprice24h

    # -----------------------------------------------------------------------------------------
    # ----------------------WS Private Methods-------------------------------------------------
    # -----------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------

    def __connect(self, wsURL, symbol):
        '''Connect to the websocket in a thread.'''
        self.logger.debug("Starting thread")

        self.ws = websocket.WebSocketApp(wsURL,
                                         on_message=self.__on_message,
                                         on_close=self.__on_close,
                                         on_open=self.__on_open,
                                         on_error=self.__on_error)

        self.wst = threading.Thread(target=lambda: self.ws.run_forever())
        self.wst.daemon = True
        self.wst.start()
        self.logger.debug("Started thread")

        # Wait for connect before continuing
        conn_timeout = CONN_TIMEOUT
        while (not self.ws.sock or not self.ws.sock.connected) and conn_timeout:
            sleep(1)
            conn_timeout -= 1
        if not conn_timeout:
            self.logger.error("Couldn't connect to WS! Exiting.")
            self.exit()
            raise websocket.WebSocketTimeoutException('Couldn\'t connect to WS! Exiting.')

    def __get_url(self):
        '''
        Generate a connection URL. We can define subscriptions right in the querystring.
        Most subscription topics are scoped by the symbol we're listening to.
        '''

        symbolSubs = ["instrument", "orderBookL2", "quote", "trade"]

        subscriptions = [sub + ':' + self.symbol for sub in symbolSubs]

        urlParts = list(urllib.parse.urlparse(self.endpoint))
        urlParts[0] = urlParts[0].replace('http', 'ws')
        urlParts[2] = "/realtime?subscribe={}".format(','.join(subscriptions))
        return urllib.parse.urlunparse(urlParts)

    def __wait_for_account(self):
        '''On subscribe, this data will come down. Wait for it.'''
        # Wait for the keys to show up from the ws
        while not {'orderBookL2'} <= set(self.data):
            sleep(0.1)

    def __wait_for_symbol(self, symbol):
        '''On subscribe, this data will come down. Wait for it.'''
        while not {'instrument', 'trade', 'quote'} <= set(self.data):
            sleep(0.1)

    def __send_command(self, command, args=None):
        '''Send a raw command.'''
        if args is None:
            args = []
        self.ws.send(json.dumps({"op": command, "args": args}))

    def __on_message(self, message):
        '''Handler for parsing WS messages.'''
        message = json.loads(message)
        self.logger.debug(json.dumps(message))

        table = message.get("table")
        action = message.get("action")
        try:
            if 'subscribe' in message:
                self.logger.debug("Subscribed to %s." % message['subscribe'])
            elif action:

                if table not in self.data:
                    self.data[table] = []

                # There are four possible actions from the WS:
                # 'partial' - full table image
                # 'insert'  - new row
                # 'update'  - update row
                # 'delete'  - delete row

                if action == 'partial':
                    self.logger.debug("%s: partial" % table)
                    self.data[table] = message['data']
                    # Keys are communicated on partials to let you know how to uniquely identify
                    # an item. We use it for updates.
                    self.keys[table] = message['keys']

                elif action == 'insert':
                    self.logger.debug('%s: inserting %s' % (table, message['data']))
                    self.data[table] += message['data']
                    # Limit the max length of the table to avoid excessive memory usage.
                    # Don't trim orders because we'll lose valuable state if we do.
                    if table not in ['orderBookL2'] and len(self.data[table]) > MAX_TABLE_LEN:
                        self.data[table] = self.data[table][MAX_TABLE_LEN // 2:]

                elif action == 'update':
                    self.logger.debug('%s: updating %s' % (table, message['data']))
                    # Locate the item in the collection and update it.
                    for updateData in message['data']:
                        item = find_by_keys(self.keys[table], self.data[table], updateData)
                        if not item:
                            return  # No item found to update. Could happen before push
                        item.update(updateData)

                elif action == 'delete':
                    self.logger.debug('%s: deleting %s' % (table, message['data']))
                    # Locate the item in the collection and remove it.
                    for deleteData in message['data']:
                        item = find_by_keys(self.keys[table], self.data[table], deleteData)
                        self.data[table].remove(item)
                else:
                    raise Exception("Unknown action: %s" % action)
        except:
            self.logger.error(traceback.format_exc())

    def __on_error(self, error):
        '''Called on fatal websocket errors. We exit on these.'''
        if not self.exited:
            self.logger.error("Error : %s" % error)
            raise websocket.WebSocketException(error)

    def __on_open(self):
        '''Called when the WS opens.'''
        self.logger.debug("Websocket Opened.")

    def __on_close(self):
        '''Called on websocket close.'''
        self.logger.info('Websocket Closed')


# Utility method for finding an item in the store.
# When an update comes through on the websocket, we need to figure out which item in the array it is
# in order to match that item.
# Helpfully, on a data push (or on an HTTP hit to /api/v1/schema), we have a "keys" array. These are the
# fields we can use to uniquely identify an item. Sometimes there is more than one, so we iterate through 
# all provided keys.
def find_by_keys(keys, table, matchData):
    for item in table:
        if all(item[k] == matchData[k] for k in keys):
            return item

# Given a number, round it to the nearest tick. 
# Use this after adding/subtracting/multiplying numbers.
# More reliable than round()
def toNearest(num, tickSize = 1):
    tickDec = Decimal(str(tickSize))
    return float((Decimal(round(num / tickSize, 0)) * tickDec))

# Satoshi to XBT converter
def XBt_to_XBT(XBt):
    return float(XBt) / 100000000
