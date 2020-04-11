# -*- coding: utf-8 -*-

# - OrderBook Websocket Thread -
# 🦏 **** quan.digital **** 🦏

# authors: canokaue & thomgabriel
# date: 03/2020
# kaue.cano@quan.digital

# Simplified implementation of connecting to BitMEX websocket for streaming realtime orderbook data.
# Optimized for OrderBookL2 handling using Red and Black Binary Search Trees - https://www.programiz.com/dsa/red-black-tree
# Originally developed for Quan Digital's Whale Watcher project - https://github.com/quan-digital/whale-watcher

# Code based on stock Bitmex API connectors - https://github.com/BitMEX/api-connectors/tree/master/official-ws/python/bitmex_websocket.py
# As well as pmaji's GDAX OrderBook thread - https://github.com/pmaji/crypto-whale-watching-app/blob/master/gdax_book.py

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
from operator import itemgetter
from tqdm import tqdm

# Websocket timeout in seconds
CONN_TIMEOUT = 5

# It's recommended not to grow a table larger than 200. Helps cap memory usage.
MAX_TABLE_LEN = 200

# Get other data besides orderBookL2 (instrument, quote and trade). 
# Set to 'False' to reduce bandwidth and optimize performance. 
OTHER_DATA = True

# When True, data will only be handled as RBTrees (bids and asks).
# When False, orderBookL2 data will also be stored as dict.
RB_ONLY = False

# Satoshi to XBT converter
def XBt_to_XBT(XBt):
    return float(XBt) / 100000000

class BitMEXBook:

    def __init__(self, endpoint="https://www.bitmex.com/api/v1", symbol='XBTUSD'):
        '''Connect to the websocket and initialize data stores.'''
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing WebSocket.")

        # If we're getting other websocket data, RB_ONLY must be false
        if OTHER_DATA and RB_ONLY:
            raise Exception('OTHER_DATA and RB_ONLY can\'t be both true.')

        self.endpoint = endpoint
        self.symbol = symbol

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
        self.logger.info('Connected to WS, waiting for partials.')

        # Connected. Wait for partials
        self.__wait_for_symbol(symbol)
        self.logger.info('Got all market data. Starting.')

    def init(self):
        self.logger.debug("Initializing WebSocket...")

        self.data = {}
        self.keys = {}
        self.exited = False

        wsURL = self.__get_url()
        self.logger.info("Connecting to URL -- %s" % wsURL)
        self.__connect(wsURL, self.symbol)
        self.logger.info('Connected to WS, waiting for partials.')

        # Connected. Wait for partials
        self.__wait_for_symbol(self.symbol)
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
        if OTHER_DATA:
            instrument = self.data['instrument'][0]
            return instrument
        else:
            return None

    def get_ticker(self):
        '''Return a ticker object. Generated from quote and trade.'''
        if OTHER_DATA:
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
        else:
            return None

    def market_depth(self):
        '''Get whole market depth (orderbook). Returns all levels.'''
        return self.data['orderBookL2']

    def get_trade_price(self):
        if OTHER_DATA:
            last_trade = self.data['trade']
            price_trade = [order['price'] for order in last_trade]
            return price_trade[-1]
        else:
            return None

    def get_volume(self):
        if OTHER_DATA:
            instrument = self.data['instrument']
            volume = instrument[0]['volume']
            return volume
        else:
            return None

    def get_last_price(self):
        if OTHER_DATA:
            instrument = self.data['instrument']
            last_price = instrument[0]['lastPrice']
            return last_price
        else:
            None

    def get_volume24h(self):
        if OTHER_DATA:
            volume24h = self.data['instrument'][0]['volume24h']
            return volume24h
        else:
            return None

    def get_prevprice24h(self):
        if OTHER_DATA:
            prevprice24h = self.data['instrument'][0]['prevPrice24h']
            return prevprice24h
        else:
            return None

    ### Ask (sell) functions

    def get_aks_orders(self,fromTree = True):
        if OTHER_DATA and not fromTree:
            orderbook = self.data['orderBookL2']
            order_asks = [order for order in orderbook if order['side']  == 'Sell']
            return (order_asks)
        else:
            return [value[0] for value in self._asks.values()]

    def get_ask_price(self, fromTree = True):
        if OTHER_DATA and not fromTree:
            orderbook = self.data['orderBookL2']
            order_prices = [order['price'] for order in orderbook if order['side']  == 'Sell']
            return sorted((order_prices))[0]
        else:
            return self._asks.min_item()[1][-1]['price']

    def get_ask_largest_size(self, fromTree = True):
        if OTHER_DATA and not fromTree:    
            orderbook = self.data["orderBookL2"]
            order_sizes = [order['size'] for order in orderbook if order['side']  == 'Sell']
            return sorted((order_sizes))[-1]
        else:
            return sorted([value[0]['size'] for value in self._asks.values()])[-1]

    def get_ask_sizes(self, fromTree = True):
        if OTHER_DATA and not fromTree:    
            orderbook = self.data["orderBookL2"]
            order_sizes = [order['size'] for order in orderbook if order['side']  == 'Sell']
            return sorted((order_sizes))
        else:
            return sorted([value[0]['size'] for value in self._asks.values()])

    def get_ask_prices(self, fromTree = True):
        if OTHER_DATA and not fromTree:
            orderbook = self.data["orderBookL2"]
            ask_prices = [order['price'] for order in orderbook if order['side']  == 'Sell']
            return ask_prices
        else:
            return sorted([key for key in self._asks.keys()])

    ### Bid (buy) functions

    def get_bid_orders(self,fromTree = True):
        if OTHER_DATA and not fromTree:
            orderbook = self.data['orderBookL2']
            order_bids = [order for order in orderbook if order['side']  == 'Buy']
            return (order_bids)
        else:
            return [value[0] for value in self._bids.values()]

    def get_bid_price(self, fromTree = True):
        if OTHER_DATA and not fromTree:
            orderbook = self.data['orderBookL2']
            order_prices = [order['price'] for order in orderbook if order['side']  == 'Buy']
            return sorted((order_prices))[-1]
        else:
            return self._bids.max_key()

    def get_bid_largest_size(self, fromTree = True):
        if OTHER_DATA and not fromTree:    
            orderbook = self.data["orderBookL2"]
            order_sizes = [order['size'] for order in orderbook if order['side']  == 'Buy']
            return sorted((order_sizes))[-1]
        else:
            return sorted([value[0]['size'] for value in self._bids.values()])[-1]
    
    def get_bid_sizes(self, fromTree = True):
        if OTHER_DATA and not fromTree:    
            orderbook = self.data["orderBookL2"]
            order_sizes = [order['size'] for order in orderbook if order['side']  == 'Buy']
            return sorted((order_sizes))
        else:
            return sorted([value[0]['size'] for value in self._bids.values()])

    def get_bid_prices(self, fromTree = True):
        if OTHER_DATA and not fromTree:
            orderbook = self.data["orderBookL2"]
            bid_prices = [order['price'] for order in orderbook if order['side']  == 'Buy']
            return bid_prices
        else:
            return sorted([key for key in self._bids.keys()])

    ### Main orderbook function

    def get_current_book(self):
        result = {
            'asks': [],
            'bids': []
        }
        for ask in self._asks:
            try:
                # There can be a race condition here, where a price point is removed
                # between these two ops
                this_ask = self._asks[ask]
            except KeyError:
                continue
            for order in this_ask:
                result['asks'].append([order['price'],(order['size']/Decimal(order['price'])), order['id']]) #(order['size']/Decimal(order['price']))
        # Same procedure for bids
        for bid in self._bids:
            try:
                this_bid = self._bids[bid]
            except KeyError:
                continue

            for order in this_bid:
                result['bids'].append([order['price'], (order['size']/Decimal(order['price'])) , order['id']])  #(order['size']/Decimal(order['price']))
        return result

    # -----------------------------------------------------------------------------------------
    # ----------------------RBTrees Handling---------------------------------------------------
    # -----------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------

    # Get current minimum ask price from tree
    def get_ask(self):
        return self._asks.min_key()

    # Get ask given price
    def get_asks(self, price):
        return self._asks.get(price)

    # Remove ask form tree
    def remove_asks(self, price):
        self._asks.remove(price)

    # Insert ask into tree
    def set_asks(self, price, asks):
        self._asks.insert(price, asks)

    # Get current maximum bid price from tree
    def get_bid(self):
        return self._bids.max_key()

    # Get bid given price
    def get_bids(self, price):
        return self._bids.get(price)

    # Remove bid form tree
    def remove_bids(self, price):
        self._bids.remove(price)

    # Insert bid into tree
    def set_bids(self, price, bids):
        self._bids.insert(price, bids)

    # Add order to out watched orders
    def add(self, order):
        order = {
            'id': order['id'], # Order id data
            'side': order['side'], # Order side data
            'size': Decimal(order['size']), # Order size data
            'price': order['price'] # Order price data
        }
        if order['side'] == 'Buy':
            bids = self.get_bids(order['price'])
            if bids is None:
                bids = [order]
            else:
                bids.append(order)
            self.set_bids(order['price'], bids)
        else:
            asks = self.get_asks(order['price'])
            if asks is None:
                asks = [order]
            else:
                asks.append(order)
            self.set_asks(order['price'], asks)

    # Order is done, remove it from watched orders
    def remove(self, order):
        oid = order['id']
        if order['side'] == 'Buy':
            bids = self.get_bids(oid)
            if bids is not None:
                bids = [o for o in bids if o['id'] != order['id']]
                if len(bids) > 0:
                    self.set_bids(oid, bids)
                else:
                    self.remove_bids(oid)
        else:
            asks = self.get_asks(oid)
            if asks is not None:
                asks = [o for o in asks if o['id'] != order['id']]
                if len(asks) > 0:
                    self.set_asks(oid, asks)
                else:
                    self.remove_asks(oid)

    # Updating order price and size
    def change(self, order):
        new_size = Decimal(order['size'])
        # Bitmex updates don't come with price, so we use the id to match it instead
        oid = order['id']

        if order['side'] == 'Buy':
            bids = self.get_bids(oid)
            if bids is None or not any(o['id'] == order['id'] for o in bids):
                return
            index = map(itemgetter('id'), bids).index(order['id'])
            bids[index]['size'] = new_size
            self.set_bids(oid, bids)
        else:
            asks = self.get_asks(oid)
            if asks is None or not any(o['id'] == order['id'] for o in asks):
                return
            index = map(itemgetter('id'), asks).index(order['id'])
            asks[index]['size'] = new_size
            self.set_asks(oid, asks)

        tree = self._asks if order['side'] == 'Sell' else self._bids
        node = tree.get(oid)

        if node is None or not any(o['id'] == order['id'] for o in node):
            return

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
        if OTHER_DATA:
            symbolSubs = ["instrument", "orderBookL2", "quote", "trade"]
        else:
            symbolSubs = ["orderBookL2"]

        subscriptions = [sub + ':' + self.symbol for sub in symbolSubs]

        urlParts = list(urllib.parse.urlparse(self.endpoint))
        urlParts[0] = urlParts[0].replace('http', 'ws')
        urlParts[2] = "/realtime?subscribe={}".format(','.join(subscriptions))
        return urllib.parse.urlunparse(urlParts)

    def __wait_for_symbol(self, symbol):
        '''On subscribe, this data will come down. Wait for it.'''
        pbar = tqdm(total=160)
        if OTHER_DATA:
            # Wait for every subscription
            while not {'orderBookL2', 'instrument', 'trade', 'quote'} <= set(self.data):
                sleep(0.1)
                pbar.update(3)
        else:
            # Wait until data reaches our RBTrees
            while self._asks.is_empty() and self._bids.is_empty():
                sleep(0.1)
                pbar.update(3)
        pbar.close()

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
            if not RB_ONLY:
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

            # RBTrees for orderBook
            if table == 'orderBookL2':
                # For every order received
                try:
                    for order in message['data']:
                        if action == 'partial':
                            self.logger.debug('%s: adding partial %s' % (table, order))
                            self.add(order)
                        elif action == 'insert':
                            self.logger.debug('%s: inserting %s' % (table, order))
                            self.add(order)
                        elif action == 'update':
                            self.logger.debug('%s: updating %s' % (table, order))
                            self.change(order)
                        elif action == 'delete':
                            self.logger.debug('%s: deleting %s' % (table, order))
                            self.remove(order)
                        else:
                            raise Exception("Unknown action: %s" % action)
                except:
                    self.logger.error('Error handling RBTrees: %s' % traceback.format_exc())

            # Uncomment this to watch RBTrees evolution in real time 
            # self.logger.info('==============================================================')
            # self.logger.info('=============================ASKS=============================')
            # self.logger.info('==============================================================')
            # self.logger.info(self._asks)
            # self.logger.info('==============================================================')
            # self.logger.info('=============================BIDS=============================')
            # self.logger.info('==============================================================')
            # self.logger.info(self._bids)

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