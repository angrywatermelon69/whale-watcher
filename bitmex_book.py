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
from decimal import Decimal
from bintrees import RBTree
from operator import itemgetter
from tqdm import tqdm

# Websocket timeout in seconds
CONN_TIMEOUT = 5

# It's recommended not to grow a table larger than 200. Helps cap memory usage.
MAX_TABLE_LEN = 200

class BitMEXBook:

    def __init__(self, endpoint="https://www.bitmex.com/api/v1", symbol='XBTUSD'):
        '''Connect to the websocket and initialize data stores.'''
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing WebSocket.")

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
        self.logger.debug("Connecting to %s" % wsURL)
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
        self.logger.debug("Connecting to URL -- %s" % wsURL)
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
                result['bids'].append([order['price'], (order['size']/Decimal(order['price'])), order['id']])  #(order['size']/Decimal(order['price']))
        return result

    # -----------------------------------------------------------------------------------------
    # ----------------------RBTrees Handling---------------------------------------------------
    # -----------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------

    # Get current minimum ask price from tree
    def get_ask(self):
        return self._asks.min_key()

    # Get ask given id
    def get_asks(self, id):
        return self._asks.get(id)

    # Remove ask form tree
    def remove_asks(self, id):
        self._asks.remove(id)

    # Insert ask into tree
    def set_asks(self, id, asks):
        self._asks.insert(id, asks)

    # Get current maximum bid price from tree
    def get_bid(self):
        return self._bids.max_key()

    # Get bid given id
    def get_bids(self, id):
        return self._bids.get(id)

    # Remove bid form tree
    def remove_bids(self, id):
        self._bids.remove(id)

    # Insert bid into tree
    def set_bids(self, id, bids):
        self._bids.insert(id, bids)

    # Add order to out watched orders
    def add(self, order):
        order = {
            'id': order['id'], # Order id data
            'side': order['side'], # Order side data
            'size': Decimal(order['size']), # Order size data
            'price': order['price'] # Order price data
        }
        if order['side'] == 'Buy':
            bids = self.get_bids(order['id'])
            if bids is None:
                bids = [order]
            else:
                bids.append(order)
            self.set_bids(order['id'], bids)
        else:
            asks = self.get_asks(order['id'])
            if asks is None:
                asks = [order]
            else:
                asks.append(order)
            self.set_asks(order['id'], asks)

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
            index = list(map(itemgetter('id'), bids)).index(order['id'])
            bids[index]['size'] = new_size
            self.set_bids(oid, bids)
        else:
            asks = self.get_asks(oid)
            if asks is None or not any(o['id'] == order['id'] for o in asks):
                return
            index = list(map(itemgetter('id'), asks)).index(order['id'])
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
            # self.exit()
            # raise websocket.WebSocketTimeoutException('Couldn\'t connect to WS! Exiting.')
            self.reset()

    def __get_url(self):
        '''
        Generate a connection URL. We can define subscriptions right in the querystring.
        Most subscription topics are scoped by the symbol we're listening to.
        '''
        symbolSubs = ["orderBookL2"]
        subscriptions = [sub + ':' + self.symbol for sub in symbolSubs]

        urlParts = list(urllib.parse.urlparse(self.endpoint))
        urlParts[0] = urlParts[0].replace('http', 'ws')
        urlParts[2] = "/realtime?subscribe={}".format(','.join(subscriptions))
        return urllib.parse.urlunparse(urlParts)

    def __wait_for_symbol(self, symbol):
        '''On subscribe, this data will come down. Wait for it.'''
        pbar = tqdm(total=160)
        
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
        # self.logger.debug(json.dumps(message))

        table = message['table'] if 'table' in message else None
        action = message['action'] if 'action' in message else None
        # table = message.get("table")
        # action = message.get("action")
        
        try:
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
